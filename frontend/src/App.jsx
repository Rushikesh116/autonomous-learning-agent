import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Confetti from 'react-confetti';
import Navbar from './Navbar'; // Ensure you created Navbar.jsx from the previous step
import './App.css';

// ==========================================
// 1. HOME VIEW (The Zig-Zag Map 🗺️)
// ==========================================
const HomeView = ({ topics, dashboard, handleStart }) => {
  return (
    <div className="view-container fade-in">
      <div className="hero-section">
        <h1>🚀 Your Learning Path</h1>
        <p>Master Machine Learning, one checkpoint at a time.</p>
      </div>

      {/* 👇 THIS IS YOUR EXACT MAP LOGIC 👇 */}
      <div className="learning-path">
        {topics.map((t, i) => {
          // --- Status Logic ---
          const isMastered = dashboard?.mastered_topics.includes(t.topic);
          const isPreviousMastered = i === 0 || dashboard?.mastered_topics.includes(topics[i-1].topic);
          const isCurrent = !isMastered && isPreviousMastered;
          const isLocked = !isMastered && !isCurrent;

          // --- Zig-Zag Math ---
          const amplitude = 70;
          const xOffset = Math.sin(i / 1.5) * amplitude;
          const nextXOffset = Math.sin((i + 1) / 1.5) * amplitude;

          // Calculate Angle
          const deltaX = nextXOffset - xOffset;
          const deltaY = 110;
          const angle = Math.atan2(deltaX, deltaY) * (180 / Math.PI) * -1;

          // --- Dynamic Icons ---
          const getTopicIcon = (title) => {
             if (title.includes("Introduction")) return "🏁";
             if (title.includes("Data")) return "🧹";
             if (title.includes("Supervised")) return "🏷️";
             if (title.includes("Regression")) return "📈";
             if (title.includes("Classification")) return "🗂️";
             if (title.includes("Overfitting")) return "🎯";
             if (title.includes("Evaluation")) return "📏";
             if (title.includes("Trees")) return "🌳";
             if (title.includes("Clustering")) return "🌌";
             if (title.includes("Neural")) return "🧠";
             return "⭐";
          };

          let statusClass = "locked";
          if (isMastered) statusClass = "completed";
          if (isCurrent) statusClass = "current";

          return (
            <div key={i} className="path-step-container" style={{ transform: `translateX(${xOffset}px)` }}>

              {/* Connector Line */}
              {i < topics.length - 1 && (
                <div
                  className={`connector-line ${dashboard?.mastered_topics.includes(t.topic) ? 'active' : ''}`}
                  style={{
                    transform: `rotate(${angle}deg)`,
                    height: `${Math.sqrt(deltaX**2 + deltaY**2) + 10}px`
                  }}
                ></div>
              )}

              {/* Decorations (Trees & Flags) */}
              {i % 3 === 1 && <div className="map-decoration" style={{ left: '120px' }}>🌲</div>}
              {i % 3 === 2 && <div className="map-decoration" style={{ right: '120px', animationDelay: '1s' }}>🚩</div>}

              {/* The Node Button */}
              <button
                onClick={() => !isLocked && handleStart(t)}
                className={`node-btn ${statusClass}`}
                disabled={isLocked}
                title={t.topic}
              >
                <span className="topic-emoji">{getTopicIcon(t.topic)}</span>
                <div className="node-label">{t.topic}</div>
              </button>
            </div>
          )
        })}
      </div>
    </div>
  );
};

// ==========================================
// 2. DASHBOARD VIEW (Stats 📊)
// ==========================================
const DashboardView = ({ dashboard, topics }) => {
  if (!dashboard) return <div className="spinner"></div>;

  const percentage = Math.round((dashboard.mastered_count / (topics.length || 1)) * 100);

  return (
    <div className="view-container fade-in">
      <h1>📊 Student Dashboard</h1>

      <div className="card dashboard-card">
        <div className="stats-row">
          <div className="stat-box">
            <h3>{dashboard.mastered_count} / {topics.length}</h3>
            <p>Topics Mastered</p>
          </div>
          <div className="stat-box">
            <h3>{dashboard.total_quizzes}</h3>
            <p>Quizzes Taken</p>
          </div>
          <div className="stat-box">
            <h3>{percentage}%</h3>
            <p>Total Mastery</p>
          </div>
        </div>

        <h3 style={{marginTop: '2rem'}}>Overall Progress</h3>
        <div className="progress-container">
          <div className="progress-fill" style={{width: `${percentage}%`}}></div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 3. HISTORY VIEW (Logs 📜)
// ==========================================
const HistoryView = ({ dashboard }) => {
  if (!dashboard) return <div className="spinner"></div>;

  return (
    <div className="view-container fade-in">
      <h1>📜 Activity History</h1>
      <div className="card">
        {dashboard.recent_activity.length === 0 ? (
          <p style={{textAlign: 'center', color: '#666'}}>No activity yet. Start learning!</p>
        ) : (
          <div className="history-list">
            {dashboard.recent_activity.map((act, i) => (
              <div key={i} className="history-item">
                <div className="history-left">
                  <span className="history-topic">{act.topic}</span>
                  <span className="history-date">{act.date}</span>
                </div>
                <div className={`history-score ${act.score >= 70 ? 'pass' : 'fail'}`}>
                  {act.score.toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ==========================================
// MAIN APP COMPONENT
// ==========================================
function App() {
  // State Management
  const [phase, setPhase] = useState("select"); // "select" means showing the Router. Others mean showing the Lesson.
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState("");
  const [quiz, setQuiz] = useState([]);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(0);
  const [showReview, setShowReview] = useState(false);
  const [dashboard, setDashboard] = useState(null);
  const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });

  const STUDENT_ID = "student_01";

  // Effects
  useEffect(() => {
    fetchData();
    window.addEventListener('resize', () => setWindowSize({ width: window.innerWidth, height: window.innerHeight }));
    return () => window.removeEventListener('resize', () => {});
  }, [phase]); // Refresh data when phase changes (e.g. after a quiz)

  const fetchData = async () => {
    try {
      const topicRes = await axios.get("http://localhost:8000/topics");
      setTopics(topicRes.data);
      const dashRes = await axios.get(`http://localhost:8000/dashboard/${STUDENT_ID}`);
      setDashboard(dashRes.data);
    } catch (err) { console.error(err); }
  };

  // --- Handlers ---

  const handleStart = async (topic) => {
    setLoading(true);
    setSelectedTopic(topic);
    try {
      const res = await axios.post("http://localhost:8000/explain", { topic: topic.topic, retry_count: 0 });
      setContext(res.data.teaching_context);
      setPhase("learn");
    } catch (e) { alert("Error generating explanation."); }
    setLoading(false);
  };

  const handleFeynman = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/explain", { topic: selectedTopic.topic, retry_count: 1 });
      setContext(res.data.teaching_context);
      setPhase("feynman");
    } catch (e) { alert("Error generating simplification."); }
    setLoading(false);
  };

  const handleGenerateQuiz = async () => {
    setLoading(true);
    const res = await axios.post("http://localhost:8000/quiz", { teaching_context: context, num_questions: 5 });
    setQuiz(res.data.mcqs);
    setPhase("quiz");
    setAnswers({});
    setLoading(false);
  };

  const handleSubmit = async () => {
    setLoading(true);
    const answerList = quiz.map((_, i) => answers[i] !== undefined ? answers[i] : -1);
    const res = await axios.post("http://localhost:8000/evaluate", {
      mcqs: quiz, user_answers: answerList, topic: selectedTopic.topic, student_id: STUDENT_ID
    });
    setScore(res.data.score);
    setPhase("result");
    setLoading(false);
  };

  // --- Render Logic ---

  // 1. ACTIVE LEARNING MODE (No Navbar, Full Screen)
  if (phase !== "select") {
    return (
      <div className="container">
        {loading && <div className="loader-container"><div className="spinner"></div><p>AI is thinking...</p></div>}

        {/* Learn View */}
        {!loading && phase === "learn" && (
          <div className="card fade-in">
            <div className="card-header"><h2>📘 {selectedTopic.topic}</h2></div>
            <div className="markdown-content">{context.split('\n').map((l,i)=><p key={i}>{l}</p>)}</div>
            <div className="action-row">
              <button onClick={() => setPhase("select")} className="secondary-btn">Back to Path</button>
              <button onClick={handleGenerateQuiz} className="primary-btn">Start Quiz</button>
            </div>
          </div>
        )}

        {/* Feynman View */}
        {!loading && phase === "feynman" && (
          <div className="card fade-in feynman-card">
            <div className="card-header"><h2>💡 Simplified: {selectedTopic.topic}</h2><span className="badge">Feynman Mode</span></div>
            <div className="markdown-content">{context.split('\n').map((l,i)=><p key={i}>{l}</p>)}</div>
            <div className="action-row">
              <button onClick={() => setPhase("select")} className="secondary-btn">Back</button>
              <button onClick={handleGenerateQuiz} className="primary-btn">Take Simplified Quiz</button>
            </div>
          </div>
        )}

        {/* Quiz View */}
        {!loading && phase === "quiz" && (
          <div className="card fade-in">
            <h2>📝 Knowledge Check</h2>
            <div className="quiz-progress-track" style={{background: '#f3f4f6', height: '8px', borderRadius: '4px', marginBottom: '20px'}}>
              <div className="quiz-progress-fill" style={{width: `${(Object.keys(answers).length / quiz.length) * 100}%`, background: '#4f46e5', height: '100%'}}></div>
            </div>
            {quiz.map((q, i) => (
              <div key={i} className="question-box">
                <p><strong>Q{i+1}: {q.question}</strong></p>
                {q.options.map((opt, idx) => (
                  <label key={idx} className={`radio-label ${answers[i] === idx ? 'selected' : ''}`}>
                    <input type="radio" checked={answers[i] === idx} onChange={() => setAnswers({...answers, [i]: idx})} /> {opt}
                  </label>
                ))}
              </div>
            ))}
            <button onClick={handleSubmit} className="primary-btn full-width">Submit Answers</button>
          </div>
        )}

        {/* Result View */}
        {!loading && phase === "result" && (
          <div className="card result-center fade-in">
            {score >= 70 && <Confetti width={windowSize.width} height={windowSize.height} recycle={false}/>}
            <div className="score-circle"><span>{score.toFixed(0)}%</span></div>
            {score >= 70 ?
              <div className="status success"><h3>🎉 Mastery Achieved!</h3><p>Checkpoint Completed.</p></div> :
              <div className="status failure"><h3>⚠️ Needs Improvement</h3><p>Try simplifying the concept.</p></div>
            }
            <div className="action-row centered">
              <button onClick={() => setPhase("select")} className="secondary-btn">🏠 Home</button>
              {score < 70 ?
                <button onClick={handleFeynman} className="primary-btn feynman-btn">💡 Simplify & Retry</button> :
                <button onClick={() => { setPhase("select"); }} className="primary-btn">⏭️ Next Topic</button>
              }
            </div>
          </div>
        )}
      </div>
    );
  }

  // 2. NAVIGATION MODE (Home / Dashboard / History)
  return (
    <Router>
      <div className="app-layout">
        <Navbar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<HomeView topics={topics} dashboard={dashboard} handleStart={handleStart} />} />
            <Route path="/dashboard" element={<DashboardView dashboard={dashboard} topics={topics} />} />
            <Route path="/history" element={<HistoryView dashboard={dashboard} />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;