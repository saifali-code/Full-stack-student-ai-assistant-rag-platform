// frontend/src/pages/QuizPage.jsx

import { useState } from 'react'
import { quizAPI } from '../services/api'

function QuizPage() {
  const [topic, setTopic] = useState('')
  const [numQuestions, setNumQuestions] = useState(5)
  const [quiz, setQuiz] = useState(null)          // Quiz data from API
  const [userAnswers, setUserAnswers] = useState({})  // {questionIndex: selectedAnswer}
  const [result, setResult] = useState(null)      // Score result
  const [generating, setGenerating] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const generateQuiz = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }
    
    setGenerating(true)
    setError('')
    setQuiz(null)
    setResult(null)
    setUserAnswers({})
    
    try {
      const response = await quizAPI.generate(topic, numQuestions)
      setQuiz(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate quiz. Make sure you have uploaded notes.')
    } finally {
      setGenerating(false)
    }
  }

  const handleAnswerSelect = (questionIndex, selectedOption) => {
    // Update the selected answer for a specific question
    setUserAnswers(prev => ({
      ...prev,                    // Keep all previous answers
      [questionIndex]: selectedOption  // Update/add this question's answer
    }))
  }

  const handleSubmit = async () => {
    if (!quiz) return
    
    // Check all questions are answered
    if (Object.keys(userAnswers).length < quiz.questions.length) {
      setError('Please answer all questions before submitting')
      return
    }
    
    setSubmitting(true)
    setError('')
    
    // Build ordered arrays of answers
    const answers = quiz.questions.map((_, index) => userAnswers[index] || '')
    const correctAnswers = quiz.questions.map(q => q.correct_answer)
    
    try {
      const response = await quizAPI.submit(topic, answers, correctAnswers)
      setResult(response.data)
    } catch (err) {
      setError('Failed to submit quiz. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-container">
      <h1 className="page-title">📝 Quiz Generator</h1>
      <p className="page-subtitle">Generate AI-powered quizzes from your notes</p>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      {/* Quiz Setup */}
      {!quiz && !result && (
        <div className="card">
          <h2 style={{ marginBottom: '20px', color: '#4a5568' }}>Create a Quiz</h2>
          
          <div className="form-group">
            <label className="form-label">Topic</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Photosynthesis, World War 2, Python basics..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Number of Questions</label>
            <select
              className="form-input"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
            >
              <option value={3}>3 Questions</option>
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
          </div>
          
          <button
            className="btn btn-primary"
            onClick={generateQuiz}
            disabled={generating}
            style={{ width: '100%' }}
          >
            {generating ? (
              <><span className="loading-spinner"></span>Generating Quiz...</>
            ) : (
              '⚡ Generate Quiz'
            )}
          </button>
        </div>
      )}
      
      {/* Quiz Questions */}
      {quiz && !result && (
        <div>
          <div className="card">
            <h2 style={{ marginBottom: '6px' }}>📝 Quiz: {quiz.topic}</h2>
            <p style={{ color: '#718096', marginBottom: '24px' }}>
              Answer all {quiz.questions.length} questions, then submit
            </p>
            
            {quiz.questions.map((question, qIndex) => (
              <div key={qIndex} style={{
                marginBottom: '28px',
                padding: '20px',
                background: '#f7fafc',
                borderRadius: '10px',
                border: `2px solid ${userAnswers[qIndex] ? '#c6f6d5' : '#e2e8f0'}`
              }}>
                <p style={{ fontWeight: '700', marginBottom: '14px', color: '#2d3748' }}>
                  Question {qIndex + 1}: {question.question}
                </p>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {question.options.map((option, oIndex) => (
                    <label key={oIndex} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      cursor: 'pointer',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      background: userAnswers[qIndex] === option ? '#ebf8ff' : 'white',
                      border: `1px solid ${userAnswers[qIndex] === option ? '#4a6cf7' : '#e2e8f0'}`,
                      transition: 'all 0.2s'
                    }}>
                      <input
                        type="radio"
                        name={`question_${qIndex}`}
                        value={option}
                        checked={userAnswers[qIndex] === option}
                        onChange={() => handleAnswerSelect(qIndex, option)}
                        style={{ accentColor: '#4a6cf7' }}
                      />
                      <span style={{ color: '#4a5568' }}>{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
            
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: '#718096', marginBottom: '16px' }}>
                Answered: {Object.keys(userAnswers).length} / {quiz.questions.length}
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button className="btn btn-secondary" onClick={() => { setQuiz(null); setUserAnswers({}) }}>
                  ← Start Over
                </button>
                <button
                  className="btn btn-primary"
                  onClick={handleSubmit}
                  disabled={submitting || Object.keys(userAnswers).length < quiz.questions.length}
                >
                  {submitting ? <><span className="loading-spinner"></span>Grading...</> : 'Submit Quiz ✅'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Results */}
      {result && (
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>
            {result.score >= 80 ? '🌟' : result.score >= 60 ? '😊' : result.score >= 40 ? '😐' : '😔'}
          </div>
          <h2 style={{ fontSize: '48px', color: '#4a6cf7', marginBottom: '8px' }}>
            {result.score}%
          </h2>
          <p style={{ fontSize: '20px', color: '#4a5568', marginBottom: '8px' }}>
            {result.correct} out of {result.total} correct
          </p>
          <p style={{ color: '#718096', marginBottom: '30px', fontSize: '16px' }}>
            {result.message}
          </p>
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button className="btn btn-secondary" onClick={() => { setQuiz(null); setResult(null); setUserAnswers({}) }}>
              📝 Try Another Topic
            </button>
            <button className="btn btn-primary" onClick={() => { setResult(null); setUserAnswers({}) }}>
              🔄 Retry Same Quiz
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default QuizPage