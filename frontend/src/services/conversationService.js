import api from './api'

export const conversationService = {
  start: async (language) => {
    const response = await api.post('/conversation/start', { language })
    return response.data
  },

  respond: async (sessionId, message, language) => {
    const response = await api.post('/conversation/respond', { 
      session_id: sessionId, 
      user_message: message,
      language 
    })
    return response.data
  },

  getHistory: async (page = 1, limit = 20) => {
    const response = await api.get(`/conversation/history?page=${page}&limit=${limit}`)
    return response.data
  },

  save: async (id) => {
    const response = await api.put(`/conversation/${id}/save`)
    return response.data
  },

  delete: async (id) => {
    const response = await api.delete(`/conversation/${id}`)
    return response.data
  }
}