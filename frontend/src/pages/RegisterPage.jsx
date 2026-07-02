// frontend/src/pages/RegisterPage.jsx

import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'

function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    
    // Client-side validation (before even calling backend)
    if (!name || !email || !password) {
      setError('All fields are required')
      return
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      await authAPI.register(name, email, password)
      
      setSuccess('Account created! Redirecting to login...')
      
      // Wait 2 seconds then redirect
      setTimeout(() => navigate('/login'), 2000)
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: '450px', marginTop: '60px' }}>
      <div className="card">
        <h1 className="page-title" style={{ textAlign: 'center' }}>📚 Create Account</h1>
        <p className="page-subtitle" style={{ textAlign: 'center' }}>
          Start your smart study journey
        </p>
        
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        <form onSubmit={handleRegister}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input type="text" className="form-input" placeholder="Ali Ahmed"
              value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input type="email" className="form-input" placeholder="ali@example.com"
              value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input type="password" className="form-input" placeholder="Minimum 6 characters"
              value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          
          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input type="password" className="form-input" placeholder="Repeat password"
              value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          </div>
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? <><span className="loading-spinner"></span>Creating account...</> : 'Create Account'}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: '20px', color: '#718096' }}>
          Already have an account? <Link to="/login" style={{ color: '#4a6cf7' }}>Login here</Link>
        </p>
      </div>
    </div>
  )
}

export default RegisterPage