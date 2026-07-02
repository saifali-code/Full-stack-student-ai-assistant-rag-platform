// frontend/src/pages/ChatPage.jsx

import { useState, useEffect, useRef } from 'react'
import { chatAPI } from '../services/api'

function ChatPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])  // Array of {type, content} objects
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)  // Reference to auto-scroll to bottom

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleAsk = async () => {
    if (!question.trim()) return
    
    const myQuestion = question
    setQuestion('')  // Clear input immediately
    
    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: myQuestion }])
    // "prev => [...prev, newItem]" is the React way to add to an array
    // prev is the current messages array, we spread it and add the new message
    
    setLoading(true)
    
    try {
      const response = await chatAPI.askQuestion(myQuestion)
      const answer = response.data.answer
      
      // Add AI response to chat
      setMessages(prev => [...prev, { type: 'ai', content: answer }])
      
    } catch (err) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: 'Sorry, I could not get an answer. Please try again.' 
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    // Submit on Enter key (but not Shift+Enter)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleAsk()
    }
  }

  return (
    <div className="page-container">
      <h1 className="page-title">💬 Ask Your Notes</h1>
      <p className="page-subtitle">Ask any question — the AI will answer from your uploaded notes</p>
      
      {/* Chat messages area */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{
          height: '450px',
          overflowY: 'auto',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          
          {/* Welcome message */}
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: '#a0aec0', marginTop: '100px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤖</div>
              <p style={{ fontSize: '18px', fontWeight: '600' }}>Hello! I'm your Study Assistant</p>
              <p>Ask me anything from your uploaded notes!</p>
            </div>
          )}
          
          {/* Message list */}
          {messages.map((msg, index) => (
            <div key={index} style={{
              display: 'flex',
              justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '75%',
                padding: '12px 18px',
                borderRadius: msg.type === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                background: msg.type === 'user' ? '#4a6cf7' : 
                            msg.type === 'error' ? '#fff5f5' : '#f0f4f8',
                color: msg.type === 'user' ? 'white' : 
                       msg.type === 'error' ? '#c53030' : '#2d3748',
                fontSize: '15px',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap'  // Preserves line breaks in AI answers
              }}>
                {msg.type === 'ai' && <strong>🤖 AI: </strong>}
                {msg.content}
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{
                background: '#f0f4f8', borderRadius: '18px', padding: '12px 18px',
                color: '#718096'
              }}>
                <span className="loading-spinner" style={{ borderTopColor: '#4a6cf7' }}></span>
                AI is thinking...
              </div>
            </div>
          )}
          
          {/* Invisible div to scroll to */}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input area */}
        <div style={{
          borderTop: '1px solid #e2e8f0',
          padding: '16px 20px',
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-end'
        }}>
          <textarea
            className="form-input"
            placeholder="Ask a question... (Press Enter to send)"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={2}
            style={{ resize: 'none', flex: 1 }}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={handleAsk}
            disabled={loading || !question.trim()}
            style={{ padding: '12px 20px', whiteSpace: 'nowrap' }}
          >
            {loading ? '...' : 'Send 📨'}
          </button>
        </div>
      </div>
      
      <div className="alert alert-info">
        💡 <strong>Tip:</strong> Upload your notes first on the Upload page, then come here to ask questions about them!
      </div>
    </div>
  )
}

export default ChatPage