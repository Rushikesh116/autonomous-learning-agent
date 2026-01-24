import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Confetti from 'react-confetti';

function App() {
  const [phase, setPhase] = useState("select");
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState("");
  const [quiz, setQuiz] = useState([]);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(0);
  const [showReview, setShowReview] = useState(false);

  // 🆕 Dashboard State
  const [dashboard, setDashboard] = useState(null);
  const STUDENT_ID = "student_01"; // Hardcoded for MVP

  // 📏 Window Size State (For Confetti)
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  // Track window resize for accurate confetti
  useEffect(() => {
    const handleResize = () => {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Load topics AND dashboard on startup
  useEffect(() => {
    fetchData();
  }, [phase]);

  const fetchData = async () => {
    try {
      const topicRes = await axios.get("http://localhost:8000/topics");
      setTopics(topicRes.data);

      const dashRes = await axios.get(`http://localhost:8000/dashboard/${STUDENT_ID}`);
      setDashboard(dashRes.data);
    } catch (err) {
      console.error("Failed to load data", err);
    }
  };

  // 1. START LEARNING
  const handleStart = async (topic) => {
    setLoading(true);
    setSelectedTopic(topic);
    setShowReview(false);
    try {
      const res = await axios.post("http://localhost:8000/explain", {
        topic: topic.topic,
        retry_count: 0
      });
      setContext(res.data.teaching_context);
      setPhase("learn");
    } catch (e) {
      alert("Error generating explanation.");
    }
    setLoading(false);
  };

  // 2. FEYNMAN MODE
  const handleFeynman = async () => {
    setLoading(true);
    setShowReview(false);
    try {
      const res = await axios.post("http://localhost:8000/explain", {
        topic: selectedTopic.topic,
        retry_count: 1
      });
      setContext(res.data.teaching_context);
      setPhase("feynman");
    } catch (e) {
      alert("Error generating simplified explanation.");
    }
    setLoading(false);
  };

  // 3. GENERATE QUIZ
  const handleGenerateQuiz = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/quiz", {
        teaching_context: context,
        num_questions: 5
      });
      setQuiz(res.data.mcqs);
      setPhase("quiz");
      setAnswers({});
    } catch (e) {
      alert("Error generating quiz");
    }
    setLoading(false);
  };

  // 4. SUBMIT ANSWERS
  const handleSubmit = async () => {
    setLoading(true);
    const answerList = quiz.map((_, i) => answers[i] !== undefined ? answers[i] : -1);

    // Save result to DB
    const res = await axios.post("http://localhost:8000/evaluate", {
      mcqs: quiz,
      user_answers: answerList,
      topic: selectedTopic.topic,
      student_id: STUDENT_ID
    });
    setScore(res.data.score);
    setPhase("result");
    setLoading(false);
  };

  const handleNextTopic = () => {
    if (!selectedTopic) return;
    const currentIndex = topics.findIndex(t => t.topic === selectedTopic.topic);
    if (currentIndex >= 0 && currentIndex < topics.length - 1) {
      handleStart(topics[currentIndex + 1]);
    } else {
      alert("You have completed all available topics!");
      setPhase("select");
    }
  };

  return (
    <div className="container">
      <header className="app-header">
        <h1>🧠 Autonomous Learning Agent</h1>
        <p>AI-Powered Tutoring System</p>
      </header>

      {loading && (
        <div className="loader-container">
          <div className="spinner"></div>
          <p>AI is thinking...</p>
        </div>
      )}

      {/* PHASE 1: DASHBOARD & SELECT */}
      {!loading && phase === "select" && (
        <>
          {dashboard && (
            <div className="card dashboard-card fade-in">
              <h2>👋 Welcome Back, Student!</h2>
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
                  <h3>{Math.round((dashboard.mastered_count / (topics.length || 1)) * 100)}%</h3>
                  <p>Completion</p>
                </div>
              </div>

              <div className="progress-container">
                <div
                  className="progress-fill"
                  style={{width: `${(dashboard.mastered_count / (topics.length || 1)) * 100}%`}}
                ></div>
              </div>

              {dashboard.recent_activity.length > 0 && (
                <div className="recent-activity">
                  <h4>🕒 Recent Activity</h4>
                  {dashboard.recent_activity.map((act, i) => (
                    <div key={i} className="activity-item">
                      <span>{act.topic}</span>
                      <span className={act.score >= 70 ? "tag-success" : "tag-fail"}>
                        {act.score.toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ✨ NEW: DUOLINGO STYLE LEARNING PATH MAP */}
          <div className="card fade-in" style={{background: 'transparent', boxShadow: 'none', border: 'none'}}>
            <h2 style={{textAlign: 'center', marginBottom: '2rem', color: '#4f46e5'}}>🚀 Your Learning Path</h2>

            <div className="learning-path">
              {topics.map((t, i) => {
                // --- STATUS LOGIC ---
                // 1. Check if this topic is already mastered
                const isMastered = dashboard?.mastered_topics.includes(t.topic);

                // 2. Check if the previous topic is mastered (or if this is the very first topic)
                const isPreviousMastered = i === 0 || dashboard?.mastered_topics.includes(topics[i-1].topic);

                // 3. It is "Current" if: Not mastered yet, but the path up to here is clear
                const isCurrent = !isMastered && isPreviousMastered;

                // 4. It is "Locked" if: Not mastered and previous one is not done
                const isLocked = !isMastered && !isCurrent;

                // Determine CSS Class based on status
                let statusClass = "locked";
                if (isMastered) statusClass = "completed";
                if (isCurrent) statusClass = "current";

                return (
                  <div key={i} className="path-step">

                    {/* CONNECTOR LINE (Show for all except the first one) */}
                    {i > 0 && (
                      <div className={`connector-line ${isPreviousMastered ? 'active' : ''}`}></div>
                    )}

                    {/* CIRCLE BUTTON */}
                    <button
                      onClick={() => !isLocked && handleStart(t)}
                      className={`node-btn ${statusClass}`}
                      disabled={isLocked}
                      title={isLocked ? "Complete previous topic to unlock" : t.topic}
                    >
                      {/* Icon Logic */}
                      {isMastered ? '🏆' : isLocked ? '🔒' : '⭐'}

                      {/* Floating Label (Shows name next to circle) */}
                      <div className="node-label">
                        {t.topic}
                        {isMastered && <span style={{marginLeft:'5px', color:'green'}}>✔</span>}
                      </div>
                    </button>

                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}

      {/* PHASE 2: LEARN */}
      {!loading && phase === "learn" && (
        <div className="card fade-in">
          <div className="card-header">
            <h2>📘 {selectedTopic.topic}</h2>
          </div>
          <div className="markdown-content">
            {context.split('\n').map((line, i) => <p key={i}>{line}</p>)}
          </div>
          <div className="action-row">
            <button onClick={() => setPhase("select")} className="secondary-btn">Back</button>
            <button onClick={handleGenerateQuiz} className="primary-btn">📝 Take Quiz</button>
          </div>
        </div>
      )}

      {/* PHASE 2.5: FEYNMAN */}
      {!loading && phase === "feynman" && (
        <div className="card fade-in feynman-card">
          <div className="card-header">
            <h2>💡 Simplified: {selectedTopic.topic}</h2>
            <span className="badge">Feynman Mode</span>
          </div>
          <div className="markdown-content">
            {context.split('\n').map((line, i) => <p key={i}>{line}</p>)}
          </div>
          <div className="action-row">
            <button onClick={() => setPhase("select")} className="secondary-btn">Back</button>
            <button onClick={handleGenerateQuiz} className="primary-btn">📝 Take Simplified Quiz</button>
          </div>
        </div>
      )}

      {/* PHASE 3: QUIZ (With New Progress Bar) */}
      {!loading && phase === "quiz" && (
        <div className="card fade-in">
          <h2>📝 Knowledge Check</h2>

          <div className="quiz-progress-track" style={{background: '#f3f4f6', height: '8px', borderRadius: '4px', marginBottom: '20px', overflow: 'hidden'}}>
            <div
              className="quiz-progress-fill"
              style={{
                width: `${(Object.keys(answers).length / quiz.length) * 100}%`,
                background: 'linear-gradient(90deg, #4f46e5, #818cf8)',
                height: '100%',
                transition: 'width 0.3s ease'
              }}
            ></div>
          </div>

          {quiz.map((q, i) => (
            <div key={i} className="question-box">
              <p className="question-text"><strong>Q{i+1}. {q.question}</strong></p>
              <div className="options-list">
                {q.options.map((opt, optIdx) => (
                  <label key={optIdx} className={`radio-label ${answers[i] === optIdx ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name={`q-${i}`}
                      checked={answers[i] === optIdx}
                      onChange={() => setAnswers({...answers, [i]: optIdx})}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <button onClick={handleSubmit} className="primary-btn full-width">✅ Submit Answers</button>
        </div>
      )}

      {/* PHASE 4: RESULT (With Confetti) */}
      {!loading && phase === "result" && (
        <div className="card result-center fade-in">

          {score >= 70 && (
             <Confetti
               width={windowSize.width}
               height={windowSize.height}
               recycle={false}
               numberOfPieces={500}
               gravity={0.2}
             />
          )}

          <div className="score-circle">
            <span>{score.toFixed(0)}%</span>
          </div>

          {score >= 70 ? (
            <div className="status success">
              <h3>🎉 Mastery Achieved!</h3>
              <p>You have successfully completed this checkpoint.</p>
            </div>
          ) : (
            <div className="status failure">
              <h3>⚠️ Needs Improvement</h3>
              <p>Let's simplify the concept and try again.</p>
            </div>
          )}

          <button
            onClick={() => setShowReview(!showReview)}
            className="secondary-btn review-toggle"
          >
            {showReview ? "Hide Details 🔼" : "🔍 Review Answers & Explanations 🔽"}
          </button>

          {showReview && (
            <div className="detailed-review fade-in">
              {quiz.map((q, i) => {
                const userAnsIdx = answers[i];
                const correctIdx = q.correct_answer_index;
                const isCorrect = userAnsIdx === correctIdx;

                return (
                  <div key={i} className={`review-card ${isCorrect ? 'correct-border' : 'wrong-border'}`}>
                    <p><strong>Q{i+1}: {q.question}</strong></p>
                    <div className="review-options">
                       <div className={`review-option ${isCorrect ? 'green-bg' : 'red-bg'}`}>
                          <strong>You Chose:</strong> {q.options[userAnsIdx] || "Skipped"}
                       </div>
                       {!isCorrect && (
                         <div className="review-option green-bg">
                            <strong>Correct Answer:</strong> {q.options[correctIdx]}
                         </div>
                       )}
                    </div>
                    <div className="insight-box">
                      💡 <strong>Insight:</strong> {q.explanation}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          <div className="action-row centered">
            <button onClick={() => setPhase("select")} className="secondary-btn">🏠 Home</button>
            {score < 70 ? (
               <button onClick={handleFeynman} className="primary-btn feynman-btn">
                 💡 Simplify (Feynman) & Retry
               </button>
            ) : (
               <button onClick={handleNextTopic} className="primary-btn">⏭️ Next Topic</button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;