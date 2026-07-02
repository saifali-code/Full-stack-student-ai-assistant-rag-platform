// frontend/src/main.jsx
// This is the ENTRY POINT — the very first file that runs

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// ReactDOM.createRoot() attaches React to the <div id="root"> in index.html
// Then .render() puts our App component inside it
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* StrictMode helps catch bugs during development */}
    <App />
  </React.StrictMode>
)