import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Check if running in Tauri
const isTauri = window.__TAURI__ !== undefined;

if (isTauri) {
  console.log('Running in Tauri desktop app');
} else {
  console.log('Running in web browser');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
