import { create } from 'zustand'
import { conversationService } from '../services/conversationService'

// Mock data for fallback
const MOCK_SESSION_START = {
  session_id: "mock-session-123",
  language: "kn",
  language_name: "Kannada",
  greeting: "ನಮಸ್ಕಾರ! ನಾನು ವಾಣಿ, ನಿಮ್ಮ AI ಸಂವಹನ ತರಬೇತುದಾರ. ಇಂದು ನಾವು ಏನು ಅಭ್ಯಾಸ ಮಾಡೋಣ?",
  expires_in: 3600
}

const MOCK_CONVERSATION_HISTORY = {
  conversations: [
    {
      id: "conv1",
      language: "kn",
      user_message: "ನಾನು ನಾಳೆ ಇಂಟರ್ವ್ಯೂಗೆ ಹೋಗಬೇಕು",
      ai_response: "ಒಳ್ಳೆಯದು! ನಿಮ್ಮ ಉಚ್ಚಾರಣೆ ಚೆನ್ನಾಗಿದೆ.",
      fluency_score: 72,
      grammar_score: 78,
      created_at: "2024-05-25T10:30:00Z"
    },
    {
      id: "conv2",
      language: "en",
      user_message: "I want to improve my English",
      ai_response: "That's great! Let's practice together.",
      fluency_score: 65,
      grammar_score: 70,
      created_at: "2024-05-24T15:20:00Z"
    }
  ],
  pagination: { page: 1, per_page: 20, total: 2, pages: 1 }
}

export const useConversationStore = create((set, get) => ({
  currentSession: null,
  messages: [],
  history: [],
  isLoading: false,
  error: null,

  startSession: async (language) => {
    set({ isLoading: true, error: null })
    try {
      const data = await conversationService.start(language)
      set({ currentSession: data, messages: [{ role: 'ai', content: data.greeting }] })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to start conversation', currentSession: MOCK_SESSION_START, messages: [{ role: 'ai', content: MOCK_SESSION_START.greeting }] })
      return MOCK_SESSION_START
    } finally {
      set({ isLoading: false })
    }
  },

  sendMessage: async (sessionId, message, language) => {
    set({ isLoading: true, error: null })
    try {
      const data = await conversationService.respond(sessionId, message, language)
      set((state) => ({
        messages: [...state.messages, { role: 'user', content: message }, { role: 'ai', content: data.ai_response }]
      }))
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to send message' })
      return null
    } finally {
      set({ isLoading: false })
    }
  },

  loadHistory: async () => {
    set({ isLoading: true })
    try {
      const data = await conversationService.getHistory()
      set({ history: data.conversations || [] })
    } catch (error) {
      console.error('Failed to load history:', error)
      set({ history: MOCK_CONVERSATION_HISTORY.conversations })
    } finally {
      set({ isLoading: false })
    }
  }
}))