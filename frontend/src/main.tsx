import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import { App } from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* Landing Page — role selection */}
        <Route path="/" element={<LandingPage />} />

        {/* Login routes — no auth yet, just placeholder screens */}
        <Route path="/login/user" element={<LoginPage role="user" />} />
        <Route path="/login/driver" element={<LoginPage role="driver" />} />
        <Route path="/login/officer" element={<LoginPage role="officer" />} />

        {/* Main NER SafeRoute application — reached after login */}
        <Route path="/app" element={<App />} />

        {/* Fallback: any unknown route goes to landing */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
