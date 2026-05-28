import api from './api'

export const groupService = {
  createGroup: async (name, language, maxParticipants = 4) => {
    const response = await api.post('/group/create', { topic: name, language, max_participants: maxParticipants })
    return response.data
  },

  joinGroup: async (code) => {
    const response = await api.post(`/group/${code}/join`)
    return response.data
  },

  startSession: async (groupId) => {
    const response = await api.post('/group/session/start', { code: groupId })
    return response.data
  }
}