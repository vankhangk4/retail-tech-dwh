import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Note: StrictMode intentionally removed to avoid double-invocation of event handlers
// (especially logout) and useEffect cleanup cycles in production
ReactDOM.createRoot(document.getElementById('root')).render(
  <App />
)
