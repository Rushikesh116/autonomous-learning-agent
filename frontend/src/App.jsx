import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Confetti from 'react-confetti';
import Navbar from './Navbar';
import Login from './Login';
import './App.css';

// 🌐 CLOUD URL CONFIGURATION
// Switches automatically: Vercel URL in cloud, localhost in development.
const API_BASE_URL = "";

// --- Global Loading Overlay ---
const LoadingOverlay = () => (
  <div className="loader-overlay fade-in">
    <div className="spinner"></div>
    <p>AI is generating your lesson...</p>
  </div>
);

// ==========================================
// 1. HOME VIEW
// ==========================================
const HomeView = ({ topics, dashboard, handleStart }) => {
  const masteredIds = dashboard?.mastered_topics || [];

  return (
    <div className="view-container fade-in">
      <div className="hero-section">
        <h1>🚀 Your Learning Path</h1>
        <p>Master Machine Learning, one checkpoint at a time.</p>
      </div>

      <div className="learning-path">
        {topics.map((t, i) => {
          const isMastered = masteredIds.includes(t.topic);
          const isPreviousMastered = i === 0 || masteredIds.includes(topics[i-1]?.topic);
          const isCurrent = !isMastered && isPreviousMastered;
          const isLocked = !isMastered && !isCurrent;

          const amplitude = 70;
          const xOffset = Math.sin(i / 1.5) * amplitude;
          const nextXOffset = Math.sin((i + 1) / 1.5) * amplitude;
          const deltaX = nextXOffset - xOffset;
          const deltaY = 110;
          const angle = Math.atan2(deltaX, deltaY) * (180 / Math.PI) * -1;

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
              {i < topics.length - 1 && (
                <div
                  className={`connector-line ${masteredIds.includes(t.topic) ? 'active' : ''}`}
                  style={{ transform: `rotate(${angle}deg)`, height: `${Math.sqrt(deltaX**2 + deltaY**2) + 10}px` }}
                ></div>
              )}
              {i % 3 === 1 && <div className="map-decoration" style={{ left: '120px' }}>🌲</div>}
              {i % 3 === 2 && <div className="map-decoration" style={{ right: '120px', animationDelay: '1s' }}>🚩</div>}

              <button
                onClick={() => !isLocked && handleStart(t)}
                className={`node-btn ${statusClass}`}
                disabled={isLocked}
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
// 2. DASHBOARD VIEW
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
// 3. HISTORY VIEW
// ==========================================
const HistoryView = ({ dashboard }) => {
  if (!dashboard) return <div className="spinner"></div>;

  return (
    <div className="view-container fade-in">
      <h1>📜 Activity History</h1>
      <div className="card">
        {dashboard.recent_activity.length === 0 ? (
          <p style={{textAlign: 'center', opacity: 0.7}}>No activity yet. Start learning!</p>
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
// MAIN APP CONTENT
// ==========================================
function AppContent() {
  const [user, setUser] = useState(null);
  const [phase, setPhase] = useState("select");
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState("");
  const [quiz, setQuiz] = useState([]);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(0);
  const [dashboard, setDashboard] = useState(null);
  const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [isDark, setIsDark] = useState(false);

  // Effects
  useEffect(() => {
    if (user) {
      fetchData();
    }
    const handleResize = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [phase, user]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const fetchData = async () => {
    try {
      // 🚀 UPDATE: Using API_BASE_URL
      const topicRes = await axios.get(`${API_BASE_URL}/topics`);
      setTopics(topicRes.data);
      if (user && user.user_id) {
        const dashRes = await axios.get(`${API_BASE_URL}/dashboard/${user.user_id}`);
        setDashboard(dashRes.data);
      }
    } catch (err) { console.error(err); }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setDashboard(null);
    setPhase("select");
  };

  const handleStart = async (topic) => {
    setLoading(true);
    setSelectedTopic(topic);
    try {
      // 🚀 UPDATE: Using API_BASE_URL
      const res = await axios.post(`${API_BASE_URL}/explain`, { topic: topic.topic, retry_count: 0 });
      setContext(res.data.teaching_context);
      setPhase("learn");
    } catch (e) { alert("Error generating explanation."); }
    setLoading(false);
  };

  const handleFeynman = async () => {
    setLoading(true);
    try {
      // 🚀 UPDATE: Using API_BASE_URL
      const res = await axios.post(`${API_BASE_URL}/explain`, { topic: selectedTopic.topic, retry_count: 1 });
      setContext(res.data.teaching_context);
      setPhase("feynman");
    } catch (e) { alert("Error generating simplification."); }
    setLoading(false);
  };

  const handleGenerateQuiz = async () => {
    setLoading(true);
    // 🚀 UPDATE: Using API_BASE_URL
    const res = await axios.post(`${API_BASE_URL}/quiz`, { teaching_context: context, num_questions: 5 });
    setQuiz(res.data.mcqs);
    setPhase("quiz");
    setAnswers({});
    setLoading(false);
  };

  const handleSubmit = async () => {
    setLoading(true);
    const answerList = quiz.map((_, i) => answers[i] !== undefined ? answers[i] : -1);
    // 🚀 UPDATE: Using API_BASE_URL
    const res = await axios.post(`${API_BASE_URL}/evaluate`, {
      mcqs: quiz, user_answers: answerList, topic: selectedTopic.topic,
      student_id: user.user_id
    });
    setScore(res.data.score);
    setPhase("result");
    setLoading(false);
  };

  if (!user) {
    return (
      <div className="app-layout">
        <Navbar isDark={isDark} toggleTheme={toggleTheme} user={null} />
        <Login onLogin={handleLogin} />
      </div>
    );
  }

  if (phase !== "select") {
    return (
      <div className="container">
        {loading && <LoadingOverlay />}

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

        {!loading && phase === "quiz" && (
          <div className="card fade-in">
            <h2>📝 Knowledge Check</h2>
            <div className="quiz-progress-track" style={{background: 'var(--bg-gradient)', height: '8px', borderRadius: '4px', marginBottom: '20px', opacity: 0.5}}>
              <div className="quiz-progress-fill" style={{width: `${(Object.keys(answers).length / quiz.length) * 100}%`, background: 'var(--primary)', height: '100%'}}></div>
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

  return (
    <div className="app-layout">
      {loading && <LoadingOverlay />}
      <Navbar isDark={isDark} toggleTheme={toggleTheme} user={user} onLogout={handleLogout} />

      <div className="main-content">
        <Routes>
          <Route path="/" element={<HomeView topics={topics} dashboard={dashboard} handleStart={handleStart} />} />
          <Route path="/dashboard" element={<DashboardView dashboard={dashboard} topics={topics} />} />
          <Route path="/history" element={<HistoryView dashboard={dashboard} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;