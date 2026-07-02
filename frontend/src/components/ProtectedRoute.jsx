// frontend/src/components/ProtectedRoute.jsx
// Wraps pages that require login. Redirects to /login if not authenticated.

import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children }) {
  // Check if token exists in localStorage
  const token = localStorage.getItem('token')
  
  if (!token) {
    // Not logged in — redirect to login page
    return <Navigate to="/login" replace />
    // replace=true means we replace the history entry
    // so "Back" button won't take them to the protected page
  }
  
  // Logged in — show the page
  return children
}

export default ProtectedRoute