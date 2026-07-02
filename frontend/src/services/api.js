// frontend/src/services/api.js

import axios from 'axios'

// The base URL of our backend
const BASE_URL = 'http://localhost:8000'

// Create an axios instance with default settings
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ============================================================
// REQUEST INTERCEPTOR — adds token to every request
// ============================================================
// An "interceptor" runs BEFORE every request is sent
// Here we automatically add the JWT token to every request header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  // localStorage is the browser's built-in key-value storage
  // We store the JWT token here when user logs in
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // This header tells the backend: "Here's proof of who I am"
    // Format: "Bearer eyJ..." (Bearer is just a keyword, then the token)
  }
  return config
})

// ============================================================
// RESPONSE INTERCEPTOR — handle errors globally
// ============================================================
api.interceptors.response.use(
  (response) => response,  // If success, return as-is
  (error) => {
    if (error.response?.status === 401) {
      // 401 = Unauthorized — token expired or invalid
      localStorage.removeItem('token')  // Clear old token
      localStorage.removeItem('userName')
      window.location.href = '/login'   // Redirect to login
    }
    return Promise.reject(error)
  }
)

// ============================================================
// AUTH API FUNCTIONS
// ============================================================

export const authAPI = {
  register: (name, email, password) => 
    api.post('/register', { name, email, password }),
  
  login: (email, password) => 
    api.post('/login', { email, password }),
}

// ============================================================
// DOCUMENTS API FUNCTIONS
// ============================================================

export const documentsAPI = {
  upload: (formData) => 
    api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
      // Special header needed for file uploads
    }),
  
  getDocuments: () => 
    api.get('/documents'),
}

// ============================================================
// CHAT API FUNCTIONS
// ============================================================

export const chatAPI = {
  askQuestion: (question) => 
    api.post('/ask', { question }),
  
  getHistory: () => 
    api.get('/chat-history'),
}

// ============================================================
// QUIZ API FUNCTIONS
// ============================================================

export const quizAPI = {
  generate: (topic, numQuestions) => 
    api.post('/generate-quiz', { topic, num_questions: numQuestions }),
  
  submit: (topic, answers, correctAnswers) => 
    api.post('/submit-quiz', { 
      topic, 
      answers, 
      correct_answers: correctAnswers 
    }),
}

// ============================================================
// DASHBOARD API FUNCTIONS
// ============================================================

export const dashboardAPI = {
  getData: () => api.get('/dashboard'),
}

// ============================================================
// PREDICTION API FUNCTIONS
// ============================================================

export const predictionAPI = {
  predict: (studyHours, quizScore, practiceCount) => 
    api.post('/predict', {
      study_hours: studyHours,
      quiz_score: quizScore,
      practice_count: practiceCount
    }),
}