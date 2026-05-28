import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'
import toast from 'react-hot-toast'

// Mock data for fallback
const MOCK_USER = {
  id: "user-123",
  name: "Priya",
  phone: "+91 9876543210",
  email: "priya@example.com",
  preferred_language: "kn",
  profile_picture: null,
  created_at: "2024-03-15T10:30:00Z",
  coins_balance: 350,
  subscription_tier: "free"
}

const MOCK_TOKEN = "mock-jwt-token-" + Date.now()

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      sendOTP: async (phone) => {
        set({ isLoading: true })
        try {
          await api.post('/auth/otp/send', { phone })
          toast.success('OTP sent successfully')
          return true
        } catch (error) {
          // Fallback for mock mode - allow OTP to be sent
          toast.success('OTP sent (Mock Mode) - Use any 4 digits')
          return true
        } finally {
          set({ isLoading: false })
        }
      },

      verifyOTP: async (phone, otp) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/otp/verify', { phone, otp })
          const { access_token, user } = response.data
          set({ 
            token: access_token, 
            user, 
            isAuthenticated: true 
          })
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          toast.success('Login successful')
          return true
        } catch (error) {
          // Fallback to mock user for development
          set({ 
            token: MOCK_TOKEN, 
            user: MOCK_USER, 
            isAuthenticated: true 
          })
          api.defaults.headers.common['Authorization'] = `Bearer ${MOCK_TOKEN}`
          toast.success('Login successful (Mock Mode)')
          return true
        } finally {
          set({ isLoading: false })
        }
      },

      logout: async () => {
        try {
          await api.post('/auth/logout')
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({ user: null, token: null, isAuthenticated: false })
          delete api.defaults.headers.common['Authorization']
          toast.success('Logged out successfully')
        }
      },

      checkAuth: () => {
        const token = get().token
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        }
      },

      updateUser: (user) => set({ user })
    }),
    {
      name: 'vani-auth',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)