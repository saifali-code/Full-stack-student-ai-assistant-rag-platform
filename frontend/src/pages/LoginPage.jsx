// frontend/src/pages/LoginPage.jsx

import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'

function LoginPage() {
  // useState hook: creates a state variable and a function to update it
  // useState("") means initial value is empty string ""
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')      // Error message to display
  const [loading, setLoading] = useState(false)  // Show spinner while waiting
  
  const navigate = useNavigate()  // Hook for programmatic navigation

  const handleLogin = async (e) => {
    e.preventDefault()  // Prevent browser from refreshing the page (default form behavior)
    
    // Validate inputs
    if (!email || !password) {
      setError('Please enter both email and password')
      return
    }
    
    setLoading(true)  // Show loading spinner
    setError('')      // Clear any previous errors
    
    try {
      // Call the login API
      const response = await authAPI.login(email, password)
      
      // response.data is what the backend returned
      const { access_token, user_name } = response.data
      
      // Save token and name to browser's localStorage
      // localStorage persists even after browser refresh!
      localStorage.setItem('token', access_token)
      localStorage.setItem('userName', user_name)
      
      // Redirect to upload page after successful login
      navigate('/upload')
      
    } catch (err) {
      // err.response.data.detail is the error message from FastAPI
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setLoading(false)  // Always hide spinner when done
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: '450px', marginTop: '60px' }}>
      <div className="card">
        <h1 className="page-title" style={{ textAlign: 'center' }}>👋 Welcome Back</h1>
        <p className="page-subtitle" style={{ textAlign: 'center' }}>
          Login to your study account
        </p>
        
        {/* Show error if any */}
        {error && <div className="alert alert-error">{error}</div>}
        
        {/* Login form */}
        {/* onSubmit runs handleLogin when form is submitted */}
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="ali@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              // onChange fires on every keystroke
              // e.target.value is the current input value
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? (
              <><span className="loading-spinner"></span>Logging in...</>
            ) : (
              'Login'
            )}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: '20px', color: '#718096' }}>
          Don't have an account? <Link to="/register" style={{ color: '#4a6cf7' }}>Register here</Link>
        </p>
      </div>
    </div>
  )
}

export default LoginPage