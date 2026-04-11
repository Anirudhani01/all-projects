import React from 'react'
import ReactDOM from 'react-dom/client'
import SimpleApp from './SimpleApp.jsx'
import './index.css'

// Force refresh to clear cache
console.log('MoodBooster Simple App Loading...', new Date().toISOString());

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <SimpleApp />
  </React.StrictMode>,
)
