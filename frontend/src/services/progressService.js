import api from './api'

export const progressService = {
  getDashboard: async () => {
    const response = await api.get('/progress/dashboard')
    return response.data
  },

  getSkills: async () => {
    const response = await api.get('/progress/skills')
    return response.data
  },

  getConfidenceTimeline: async () => {
    const response = await api.get('/progress/confidence-timeline')
    return response.data
  },

  getRecommendations: async () => {
    const response = await api.get('/progress/recommendations')
    return response.data
  }
}