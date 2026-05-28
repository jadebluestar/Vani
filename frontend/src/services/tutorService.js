import api from './api'

export const tutorService = {
  search: async (filters) => {
    const response = await api.get('/tutors/search', { params: filters })
    return response.data
  },

  bookSession: async (tutorId, scheduledAt, duration = 60) => {
    const response = await api.post('/tutor/session/book', {
      tutor_id: tutorId,
      scheduled_at: scheduledAt,
      duration_minutes: duration
    })
    return response.data
  },

  getHistory: async () => {
    const response = await api.get('/tutor/sessions/history')
    return response.data
  }
}