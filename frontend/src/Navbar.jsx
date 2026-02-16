import { Link, useLocation } from 'react-router-dom';
import { Home, LayoutDashboard, History, BookOpen, Moon, Sun, LogOut } from 'lucide-react';
import './App.css';

function Navbar({ isDark, toggleTheme, user, onLogout }) {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'active-link' : '';

  return (
    <nav className="glass-nav fade-in">
      <div className="nav-logo">
        <div className="logo-icon-box"><BookOpen size={24} color="white" /></div>
        <span>AutoTutor</span>
      </div>

      {user && (
        <div className="nav-links">
          <Link to="/" className={`nav-item ${isActive('/')}`}><Home size={18} /><span>Path</span></Link>
          <Link to="/dashboard" className={`nav-item ${isActive('/dashboard')}`}><LayoutDashboard size={18} /><span>Stats</span></Link>
          <Link to="/history" className={`nav-item ${isActive('/history')}`}><History size={18} /><span>History</span></Link>
        </div>
      )}

      <div className="nav-actions">
        <button onClick={toggleTheme} className="theme-btn" title="Toggle Theme">
          {isDark ? <Sun size={20} className="sun-icon"/> : <Moon size={20} className="moon-icon"/>}
        </button>

        {user ? (
          <button onClick={onLogout} className="theme-btn" title="Logout" style={{marginLeft: '10px'}}>
            <LogOut size={20} />
          </button>
        ) : (
          <div style={{ fontWeight: 'bold', color: 'var(--primary)', marginLeft: '10px' }}>
            Guest
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;