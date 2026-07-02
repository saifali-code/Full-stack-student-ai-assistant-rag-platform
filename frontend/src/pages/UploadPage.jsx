// frontend/src/pages/UploadPage.jsx

import { useState, useEffect } from 'react'
import { documentsAPI } from '../services/api'

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [documents, setDocuments] = useState([])  // List of uploaded files

  // useEffect runs after the component renders
  // The [] at the end means "run only once when page loads" (not every re-render)
  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await documentsAPI.getDocuments()
      setDocuments(response.data.documents)
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]  // Get the selected file
    
    if (file) {
      // Validate file type
      const validTypes = ['application/pdf', 'text/plain']
      if (!validTypes.includes(file.type)) {
        setError('Please select a PDF or TXT file only')
        setSelectedFile(null)
        return
      }
      
      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024  // 10MB in bytes
      if (file.size > maxSize) {
        setError('File too large. Maximum size is 10MB')
        setSelectedFile(null)
        return
      }
      
      setSelectedFile(file)
      setError('')
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }
    
    setUploading(true)
    setMessage('')
    setError('')
    
    // FormData is needed for file uploads
    // Regular JSON can't carry binary file data
    const formData = new FormData()
    formData.append('file', selectedFile)
    // 'file' must match the parameter name in our FastAPI endpoint
    
    try {
      const response = await documentsAPI.upload(formData)
      setMessage(response.data.rag_status || 'File uploaded successfully!')
      setSelectedFile(null)
      
      // Reset the file input
      document.getElementById('file-input').value = ''
      
      // Reload the documents list
      loadDocuments()
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="page-container">
      <h1 className="page-title">📁 Upload Notes</h1>
      <p className="page-subtitle">Upload your PDFs or text notes to get AI-powered answers</p>
      
      {/* Upload Card */}
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#4a5568' }}>Upload a Document</h2>
        
        {error && <div className="alert alert-error">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}
        
        {/* File drop/select area */}
        <div style={{
          border: '2px dashed #cbd5e0',
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          marginBottom: '20px',
          background: selectedFile ? '#f0fff4' : '#f7fafc'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>
            {selectedFile ? '✅' : '📄'}
          </div>
          
          {selectedFile ? (
            <div>
              <p style={{ fontWeight: '600', color: '#276749' }}>{selectedFile.name}</p>
              <p style={{ color: '#718096', fontSize: '14px' }}>
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div>
              <p style={{ color: '#718096', marginBottom: '12px' }}>
                Select a PDF or TXT file to upload
              </p>
            </div>
          )}
          
          <input
            id="file-input"
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            // Hidden — we'll click it via the button below
          />
          <button
            className="btn btn-secondary"
            onClick={() => document.getElementById('file-input').click()}
            // This click triggers the hidden file input
          >
            Choose File
          </button>
        </div>
        
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          style={{ width: '100%' }}
        >
          {uploading ? (
            <><span className="loading-spinner"></span>Uploading & Processing...</>
          ) : (
            '⬆️ Upload and Process'
          )}
        </button>
        
        <p style={{ color: '#a0aec0', fontSize: '13px', marginTop: '12px', textAlign: 'center' }}>
          After upload, the AI will read your notes so you can ask questions about them
        </p>
      </div>
      
      {/* Uploaded Documents List */}
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#4a5568' }}>
          Your Uploaded Documents ({documents.length})
        </h2>
        
        {documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '30px', color: '#a0aec0' }}>
            <div style={{ fontSize: '40px', marginBottom: '12px' }}>📭</div>
            <p>No documents uploaded yet</p>
          </div>
        ) : (
          <div>
            {documents.map((doc) => (
              // .map() creates one list item for each document
              <div key={doc.id} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '14px',
                borderBottom: '1px solid #e2e8f0',
                transition: 'background 0.2s'
              }}>
                <div>
                  <p style={{ fontWeight: '600', color: '#2d3748' }}>📄 {doc.filename}</p>
                  <p style={{ color: '#a0aec0', fontSize: '13px' }}>Uploaded: {doc.upload_date}</p>
                </div>
                <span style={{
                  background: '#c6f6d5', color: '#276749',
                  padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: '600'
                }}>
                  ✓ Ready
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadPage