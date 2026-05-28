import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'
import { useThemeStore } from './store/themeStore'

// Layout Components
import Layout from './components/Layout/Layout'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PracticePage from './pages/PracticePage'
import InterviewPage from './pages/InterviewPage'
import TutorsPage from './pages/TutorsPage'
import GroupSessionPage from './pages/GroupSessionPage'
import ProgressPage from './pages/ProgressPage'
import CredentialsPage from './pages/CredentialsPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore()
  const { theme } = useThemeStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  return (
    <BrowserRouter>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/practice" element={<PracticePage />} />
          <Route path="/interview" element={<InterviewPage />} />
          <Route path="/tutors" element={<TutorsPage />} />
          <Route path="/group" element={<GroupSessionPage />} />
          <Route path="/group/session/:code" element={<GroupSessionPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/credentials" element={<CredentialsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;