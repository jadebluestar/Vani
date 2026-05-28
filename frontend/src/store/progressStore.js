import { create } from 'zustand'
import { progressService } from '../services/progressService'

// Mock data for fallback
const MOCK_DASHBOARD = {
  user_name: "Priya",
  preferred_language: "kn",
  total_practice_minutes: 245,
  total_sessions: 18,
  confidence_score: 72,
  streak_days: 5,
  coins_balance: 350,
  weekly_activity: [
    { date: "2024-05-20", count: 3, day: "Mon" },
    { date: "2024-05-21", count: 2, day: "Tue" },
    { date: "2024-05-22", count: 4, day: "Wed" },
    { date: "2024-05-23", count: 1, day: "Thu" },
    { date: "2024-05-24", count: 3, day: "Fri" },
    { date: "2024-05-25", count: 2, day: "Sat" },
    { date: "2024-05-26", count: 3, day: "Sun" }
  ],
  session_breakdown: {
    conversations: 12,
    interviews: 4,
    tutor_sessions: 2
  },
  skill_summary: {
    speaking: 68,
    listening: 72,
    vocabulary: 65,
    grammar: 70,
    pronunciation: 75,
    fluency: 68
  },
  recent_activities: [
    { description: "Completed interview practice", time_ago: "2 hours ago" },
    { description: "Practiced conversation for 10 min", time_ago: "Yesterday" },
    { description: "Booked session with tutor Arjun", time_ago: "2 days ago" }
  ],
  recommendations: [
    { title: "Practice pronunciation", description: "Focus on 'th' sound" },
    { title: "Try 5 interview questions", description: "Behavioral questions" }
  ]
}

const MOCK_SKILLS = {
  speaking: { score: 68, trend: 5, history: [65, 66, 67, 68, 68] },
  listening: { score: 72, trend: 3, history: [68, 69, 70, 71, 72] },
  vocabulary: { score: 65, trend: 8, history: [58, 60, 62, 64, 65] },
  grammar: { score: 70, trend: 2, history: [68, 68, 69, 69, 70] },
  pronunciation: { score: 75, trend: 4, history: [70, 72, 73, 74, 75] },
  fluency: { score: 68, trend: 6, history: [62, 64, 65, 66, 68] }
}

const MOCK_RADAR_DATA = [
  { skill: "Speaking", score: 68, fullMark: 100 },
  { skill: "Listening", score: 72, fullMark: 100 },
  { skill: "Vocabulary", score: 65, fullMark: 100 },
  { skill: "Grammar", score: 70, fullMark: 100 },
  { skill: "Pronunciation", score: 75, fullMark: 100 },
  { skill: "Fluency", score: 68, fullMark: 100 }
]

const MOCK_CONFIDENCE_TIMELINE = [
  { date: "2024-05-20", confidence: 65, sessions: 2 },
  { date: "2024-05-21", confidence: 66, sessions: 1 },
  { date: "2024-05-22", confidence: 68, sessions: 3 },
  { date: "2024-05-23", confidence: 70, sessions: 2 },
  { date: "2024-05-24", confidence: 71, sessions: 1 },
  { date: "2024-05-25", confidence: 72, sessions: 4 },
  { date: "2024-05-26", confidence: 72, sessions: 2 }
]

const MOCK_RECOMMENDATIONS = [
  { priority: "high", skill: "speaking", recommendation: "Practice 5 minutes of daily conversation", time_required: "5 min", exercise_type: "speaking" },
  { priority: "high", skill: "vocabulary", recommendation: "Learn 10 new English words this week", time_required: "10 min", exercise_type: "vocabulary" },
  { priority: "medium", skill: "pronunciation", recommendation: "Focus on the 'th' sound", time_required: "5 min", exercise_type: "speaking" },
  { priority: "low", skill: "grammar", recommendation: "Review past tense usage", time_required: "10 min", exercise_type: "grammar" }
]

export const useProgressStore = create((set, get) => ({
  dashboard: null,
  skills: null,
  confidenceTimeline: null,
  recommendations: [],
  isLoading: false,
  error: null,

  loadDashboard: async () => {
    set({ isLoading: true, error: null })
    try {
      const data = await progressService.getDashboard()
      set({ dashboard: data })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to load dashboard', dashboard: MOCK_DASHBOARD })
      return MOCK_DASHBOARD
    } finally {
      set({ isLoading: false })
    }
  },

  loadSkills: async () => {
    set({ isLoading: true, error: null })
    try {
      const data = await progressService.getSkills()
      set({ skills: data })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to load skills', skills: { skills: MOCK_SKILLS, radar_chart_data: MOCK_RADAR_DATA } })
      return { skills: MOCK_SKILLS, radar_chart_data: MOCK_RADAR_DATA }
    } finally {
      set({ isLoading: false })
    }
  },

  loadConfidenceTimeline: async () => {
    set({ isLoading: true, error: null })
    try {
      const data = await progressService.getConfidenceTimeline()
      set({ confidenceTimeline: data })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to load timeline', confidenceTimeline: MOCK_CONFIDENCE_TIMELINE })
      return MOCK_CONFIDENCE_TIMELINE
    } finally {
      set({ isLoading: false })
    }
  },

  loadRecommendations: async () => {
    set({ isLoading: true, error: null })
    try {
      const data = await progressService.getRecommendations()
      set({ recommendations: data })
      return data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to load recommendations', recommendations: MOCK_RECOMMENDATIONS })
      return MOCK_RECOMMENDATIONS
    } finally {
      set({ isLoading: false })
    }
  },

  loadAll: async () => {
    await Promise.all([
      get().loadDashboard(),
      get().loadSkills(),
      get().loadConfidenceTimeline(),
      get().loadRecommendations()
    ])
  },

  clearError: () => set({ error: null })
}))