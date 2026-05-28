import api from './api'

export const groupService = {
  createGroup: async (name, language, maxParticipants = 4) => {
    const response = await api.post('/group/create', {
      name,
      language,
      max_participants: maxParticipants
    })
    return response.data
  },

  joinGroup: async (code) => {
    const response = await api.post(`/group/${code}/join`)
    return response.data
  },

  startSession: async (groupId) => {
    const response = await api.post('/group/session/start', { group_id: groupId })
    return response.data
  },

  getGroupDetails: async (groupId) => {
    const response = await api.get(`/group/${groupId}`)
    return response.data
  },

  leaveGroup: async (groupId) => {
    const response = await api.post(`/group/${groupId}/leave`)
    return response.data
  }
}