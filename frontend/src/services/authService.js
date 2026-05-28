import api from './api'

export const authService = {
  sendOTP: async (phone) => {
    const response = await api.post('/auth/otp/send', { phone })
    return response.data
  },

  verifyOTP: async (phone, otp) => {
    const response = await api.post('/auth/otp/verify', { phone, otp })
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  },

  getMe: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  updateProfile: async (data) => {
    const response = await api.put('/auth/profile', data)
    return response.data
  }
}