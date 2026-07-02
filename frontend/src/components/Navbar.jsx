// frontend/src/components/Navbar.jsx

import { Link, useNavigate, useLocation } from 'react-router-dom'

function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()  // Current URL path
  const token = localStorage.getItem('token')
  const userName = localStorage.getItem('userName')
  
  // Check if a nav link is the current page (for active styling)
  const isActive = (path) => location.pathname === path ? 'active' : ''
  
  const handleLogout = () => {
    // Clear all stored data
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    // Redirect to login
    navigate('/login')
  }
  
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        📚 Study Assistant
      </Link>
      
      {/* Only show nav links if logged in */}
      {token ? (
        <>
          <ul className="navbar-nav">
            <li><Link to="/upload" className={isActive('/upload')}>📁 Upload</Link></li>
            <li><Link to="/chat" className={isActive('/chat')}>💬 Chat</Link></li>
            <li><Link to="/quiz" className={isActive('/quiz')}>📝 Quiz</Link></li>
            <li><Link to="/dashboard" className={isActive('/dashboard')}>📊 Dashboard</Link></li>
          </ul>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span className="navbar-user">👤 {userName}</span>
            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '14px' }}>
              Logout
            </button>
          </div>
        </>
      ) : (
        <ul className="navbar-nav">
          <li><Link to="/login">Login</Link></li>
          <li><Link to="/register">Register</Link></li>
        </ul>
      )}
    </nav>
  )
}

export default Navbar