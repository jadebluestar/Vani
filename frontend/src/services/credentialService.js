import api from './api'

export const credentialService = {
  generate: async () => {
    const response = await api.post('/credential/generate')
    return response.data
  },

  verify: async (certificateId) => {
    const response = await api.get(`/credential/${certificateId}/verify`)
    return response.data
  },

  getShareLink: async (id) => {
    const response = await api.get(`/credential/share/${id}`)
    return response.data
  },

  download: async (id) => {
    const response = await api.get(`/credential/download/${id}`, { responseType: 'blob' })
    return response.data
  },

  mintBlockchain: async (credentialId) => {
    const response = await api.post('/blockchain/mint', { credential_id: credentialId })
    return response.data
  }
}