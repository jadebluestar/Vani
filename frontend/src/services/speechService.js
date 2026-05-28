import api from './api'

export const speechService = {
  transcribe: async (audioFile, language = 'kn') => {
    const formData = new FormData()
    formData.append('audio', audioFile)
    formData.append('language', language)
    const response = await api.post('/speech/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  getFeedback: async (text, language) => {
    const response = await api.post('/speech/feedback', { text, language })
    return response.data
  },

  analyzeFluency: async (audioFile) => {
    const formData = new FormData()
    formData.append('audio', audioFile)
    const response = await api.post('/speech/analyze-fluency', formData)
    return response.data
  },

  getSupportedLanguages: async () => {
    const response = await api.get('/speech/supported-languages')
    return response.data
  }
}