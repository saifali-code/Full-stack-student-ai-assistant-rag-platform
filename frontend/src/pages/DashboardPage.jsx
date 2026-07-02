// frontend/src/pages/DashboardPage.jsx

import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { dashboardAPI, predictionAPI } from '../services/api'

function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Prediction form
  const [studyHours, setStudyHours] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [predicting, setPredicting] = useState(false)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await dashboardAPI.getData()
      setData(response.data)
    } catch (err) {
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    if (!data || !studyHours) return
    
    setPredicting(true)
    try {
      const response = await predictionAPI.predict(
        parseFloat(studyHours),
        data.average_score,
        data.total_quizzes
      )
      setPrediction(response.data)
    } catch (err) {
      setError('Prediction failed. Please try again.')
    } finally {
      setPredicting(false)
    }
  }

  if (loading) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '100px' }}>
      <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
      <p style={{ color: '#718096' }}>Loading your dashboard...</p>
    </div>
  )

  if (error) return (
    <div className="page-container">
      <div className="alert alert-error">{error}</div>
    </div>
  )

  return (
    <div className="page-container">
      <h1 className="page-title">📊 Dashboard</h1>
      <p className="page-subtitle">Welcome back, {data?.student_name}! Here's your progress overview.</p>
      
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div className="card" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '36px', fontWeight: '800', color: '#4a6cf7' }}>
            {data?.total_quizzes}
          </div>
          <div style={{ color: '#718096', marginTop: '4px' }}>Quizzes Taken</div>
        </div>
        
        <div className="card" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '36px', fontWeight: '800', color: '#48bb78' }}>
            {data?.average_score}%
          </div>
          <div style={{ color: '#718096', marginTop: '4px' }}>Average Score</div>
        </div>
        
        <div className="card" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '36px', fontWeight: '800', color: '#ed8936' }}>
            {data?.uploaded_documents}
          </div>
          <div style={{ color: '#718096', marginTop: '4px' }}>Notes Uploaded</div>
        </div>
      </div>
      
      {/* Score Chart */}
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#4a5568' }}>Recent Quiz Scores</h2>
        
        {data?.recent_scores.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.recent_scores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="topic" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#4a6cf7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#a0aec0' }}>
            <div style={{ fontSize: '40px', marginBottom: '12px' }}>📝</div>
            <p>Take some quizzes to see your score history!</p>
          </div>
        )}
      </div>
      
      {/* Weak Topics */}
      {data?.weak_topics.length > 0 && (
        <div className="card">
          <h2 style={{ marginBottom: '16px', color: '#4a5568' }}>⚠️ Topics to Improve</h2>
          <p style={{ color: '#718096', marginBottom: '16px' }}>
            You scored below 60% in these topics — focus your study here:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {data.weak_topics.map((topic, index) => (
              <span key={index} style={{
                background: '#fff5f5', color: '#c53030',
                padding: '8px 16px', borderRadius: '20px',
                fontWeight: '600', border: '1px solid #fed7d7'
              }}>
                📚 {topic}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* ML Prediction */}
      <div className="card">
        <h2 style={{ marginBottom: '8px', color: '#4a5568' }}>🔮 Pass/Fail Prediction</h2>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          Enter your daily study hours to get a prediction
        </p>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ margin: 0, flex: 1 }}>
            <label className="form-label">Daily Study Hours</label>
            <input
              type="number"
              className="form-input"
              placeholder="e.g., 3.5"
              min="0" max="24" step="0.5"
              value={studyHours}
              onChange={(e) => setStudyHours(e.target.value)}
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={handlePredict}
            disabled={predicting || !studyHours || data?.total_quizzes === 0}
            style={{ whiteSpace: 'nowrap' }}
          >
            {predicting ? 'Predicting...' : '🔮 Predict'}
          </button>
        </div>
        
        {data?.total_quizzes === 0 && (
          <p style={{ color: '#ed8936', marginTop: '10px', fontSize: '14px' }}>
            ⚠️ Take at least one quiz to enable prediction
          </p>
        )}
        
        {prediction && (
          <div style={{
            marginTop: '20px',
            padding: '20px',
            borderRadius: '10px',
            background: prediction.prediction === 'PASS' ? '#f0fff4' : '#fff5f5',
            border: `2px solid ${prediction.prediction === 'PASS' ? '#c6f6d5' : '#fed7d7'}`
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <span style={{ fontSize: '32px' }}>
                {prediction.prediction === 'PASS' ? '✅' : '❌'}
              </span>
              <div>
                <p style={{
                  fontSize: '22px', fontWeight: '800',
                  color: prediction.prediction === 'PASS' ? '#276749' : '#c53030'
                }}>
                  Prediction: {prediction.prediction}
                </p>
                <p style={{ color: '#718096' }}>
                  Confidence: {Math.round(prediction.confidence * 100)}%
                </p>
              </div>
            </div>
            <p style={{ color: '#4a5568', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
              {prediction.message}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage