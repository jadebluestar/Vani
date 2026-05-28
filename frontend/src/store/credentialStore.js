import { create } from 'zustand'
import { credentialService } from '../services/credentialService'

// Mock data for fallback
const MOCK_CREDENTIALS = [
  {
    id: "cred1",
    certificate_id: "VANI-ABC123",
    level: "Beginner",
    skills: ["Speaking", "Listening"],
    issued_at: "2024-04-15T00:00:00Z",
    blockchain_tx_hash: null,
    verified: false
  },
  {
    id: "cred2",
    certificate_id: "VANI-DEF456",
    level: "Intermediate",
    skills: ["Speaking", "Listening", "Vocabulary", "Grammar"],
    issued_at: "2024-05-20T00:00:00Z",
    blockchain_tx_hash: "0x7b34c5d8e9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5",
    verified: true
  }
]

const MOCK_GENERATED_CREDENTIAL = {
  id: "cred3",
  certificate_id: "VANI-GHI789",
  level: "Intermediate",
  skills: ["Speaking", "Listening", "Vocabulary", "Grammar", "Fluency"],
  overall_score: 78,
  issued_at: "2024-05-26T00:00:00Z"
}

const MOCK_VERIFICATION_RESULT = {
  verified: true,
  certificate_id: "VANI-DEF456",
  user_name: "Priya",
  level: "Intermediate",
  skills: ["Speaking", "Listening", "Vocabulary", "Grammar"],
  issued_at: "2024-05-20T00:00:00Z",
  blockchain_tx_hash: "0x7b34c5d8e9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5",
  verification_url: "https://vani.app/verify/VANI-DEF456"
}

export const useCredentialStore = create((set, get) => ({
  credentials: [],
  verificationResult: null,
  isLoading: false,

  loadCredentials: async () => {
    set({ isLoading: true })
    try {
      const response = await fetch('http://localhost:8000/credential/list')
      const data = await response.json()
      set({ credentials: data.credentials || [] })
    } catch (error) {
      console.error('Failed to load credentials:', error)
      set({ credentials: MOCK_CREDENTIALS })
    } finally {
      set({ isLoading: false })
    }
  },

  generateCredential: async () => {
    set({ isLoading: true })
    try {
      const response = await fetch('http://localhost:8000/credential/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: 'Beginner' })
      })
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Failed to generate credential:', error)
      return MOCK_GENERATED_CREDENTIAL
    } finally {
      set({ isLoading: false })
    }
  },

  verifyCredential: async (certificateId) => {
    set({ isLoading: true })
    try {
      const response = await fetch(`http://localhost:8000/credential/${certificateId}/verify`)
      const data = await response.json()
      set({ verificationResult: data })
      return data
    } catch (error) {
      console.error('Failed to verify credential:', error)
      set({ verificationResult: MOCK_VERIFICATION_RESULT })
      return MOCK_VERIFICATION_RESULT
    } finally {
      set({ isLoading: false })
    }
  }
}))