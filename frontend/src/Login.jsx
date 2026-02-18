import { useState } from 'react';
import axios from 'axios';
import { BookOpen } from 'lucide-react';
import './App.css';

// 🌐 CLOUD URL CONFIGURATION
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const Login = ({ onLogin }) => {
  const [isSignup, setIsSignup] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (isSignup && password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    // 🚀 UPDATE: Dynamic URL
    const endpoint = `${API_BASE_URL}/auth/${isSignup ? 'signup' : 'login'}`;

    try {
      const payload = isSignup ? { name, email, password } : { email, password };
      const res = await axios.post(endpoint, payload);
      onLogin(res.data);
    } catch (err) {
      console.error("Login Error:", err);
      setError(err.response?.data?.detail || "Connection failed. Check console for details.");
    }
  };

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', marginTop: '10vh' }}>
      <div className="card fade-in" style={{ width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
          <div className="logo-icon-box" style={{ width: '50px', height: '50px' }}>
            <BookOpen size={32} color="white" />
          </div>
        </div>

        <h2>{isSignup ? "Create Account" : "Welcome Back"}</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          {isSignup ? "Start your journey." : "Login to continue."}
        </p>

        {error && <div className="status failure" style={{ padding: '0.5rem', marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {isSignup && (
            <input
              type="text"
              placeholder="Full Name"
              className="input-field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email Address"
            className="input-field"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {isSignup && (
            <input
              type="password"
              placeholder="Confirm Password"
              className="input-field"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          )}

          <button type="submit" className="primary-btn full-width">
            {isSignup ? "Sign Up" : "Login"}
          </button>
        </form>

        <p style={{ marginTop: '1.5rem', fontSize: '0.9rem' }}>
          {isSignup ? "Already have an account?" : "New here?"}
          <span
            onClick={() => { setIsSignup(!isSignup); setError(""); setConfirmPassword(""); }}
            style={{ color: 'var(--primary)', fontWeight: 'bold', cursor: 'pointer', marginLeft: '5px' }}
          >
            {isSignup ? "Login" : "Create Account"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default Login;