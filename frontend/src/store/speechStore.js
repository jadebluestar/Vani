import { create } from 'zustand'
import { speechService } from '../services/speechService'

// Mock data for fallback
const MOCK_FEEDBACK = {
  fluency_score: 75,
  pronunciation_score: 70,
  grammar_score: 80,
  overall_score: 75,
  filler_words: { count: 2, words_found: ["um", "like"] },
  improvements: ["Speak more slowly", "Use fewer filler words", "Practice pause between sentences"],
  strengths: ["Good vocabulary", "Clear message", "Confident tone"],
  summary: "Good attempt! You're improving. Keep practicing daily.",
  next_practice_suggestion: "Try recording yourself and listen back"
}

export const useSpeechStore = create((set, get) => ({
  isRecording: false,
  isProcessing: false,
  transcript: null,
  feedback: null,
  fluencyAnalysis: null,
  supportedLanguages: [],
  audioBlob: null,
  error: null,

  setRecording: (recording) => set({ isRecording: recording }),

  transcribeAudio: async (audioFile, language) => {
    set({ isProcessing: true, error: null, transcript: null })
    try {
      const data = await speechService.transcribe(audioFile, language)
      set({ transcript: data.transcript, audioBlob: audioFile })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Transcription failed' })
      return null
    } finally {
      set({ isProcessing: false })
    }
  },

  analyzeFeedback: async (text, language) => {
    set({ isProcessing: true, error: null })
    try {
      const data = await speechService.getFeedback(text, language)
      set({ feedback: data })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Feedback analysis failed', feedback: MOCK_FEEDBACK })
      return MOCK_FEEDBACK
    } finally {
      set({ isProcessing: false })
    }
  },

  analyzeFluency: async (audioFile) => {
    set({ isProcessing: true, error: null })
    try {
      const data = await speechService.analyzeFluency(audioFile)
      set({ fluencyAnalysis: data })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Fluency analysis failed' })
      return null
    } finally {
      set({ isProcessing: false })
    }
  },

  loadSupportedLanguages: async () => {
    try {
      const data = await speechService.getSupportedLanguages()
      set({ supportedLanguages: data })
      return data
    } catch (error) {
      console.error('Failed to load languages:', error)
      return []
    }
  },

  clearTranscript: () => set({ transcript: null, feedback: null, fluencyAnalysis: null, audioBlob: null }),

  clearError: () => set({ error: null })
}))