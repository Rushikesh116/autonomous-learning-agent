import { Link, useLocation } from 'react-router-dom';
import { Home, LayoutDashboard, History, BookOpen } from 'lucide-react';
import './App.css';

function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active-link' : '';

  return (
    <nav className="glass-nav fade-in">
      <div className="nav-logo">
        <BookOpen size={24} className="logo-icon" />
        <span>AutoTutor</span>
      </div>

      <div className="nav-links">
        <Link to="/" className={`nav-item ${isActive('/')}`}>
          <Home size={18} />
          <span>Path</span>
        </Link>

        <Link to="/dashboard" className={`nav-item ${isActive('/dashboard')}`}>
          <LayoutDashboard size={18} />
          <span>Stats</span>
        </Link>

        <Link to="/history" className={`nav-item ${isActive('/history')}`}>
          <History size={18} />
          <span>History</span>
        </Link>
      </div>
    </nav>
  );
}

export default Navbar;