import api from './api'

export const interviewService = {
  getQuestions: async (category = null, difficulty = null, language = 'kn') => {
    const params = { language }
    if (category) params.category = category
    if (difficulty) params.difficulty = difficulty
    const response = await api.get('/interview/questions', { params })
    return response.data
  },

  submitResponse: async (questionId, answer, language) => {
    const response = await api.post('/interview/respond', {
      question_id: questionId,
      user_answer: answer,
      language
    })
    return response.data
  },

  getFeedback: async (id) => {
    const response = await api.get(`/interview/feedback/${id}`)
    return response.data
  },

  getHistory: async () => {
    const response = await api.get('/interview/history')
    return response.data
  },

  createLiveSession: async () => {
    const response = await api.post('/interview/live/create')
    return response.data
  }
}