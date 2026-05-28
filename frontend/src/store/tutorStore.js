import { create } from 'zustand'
import { tutorService } from '../services/tutorService'

// Mock data for fallback
const MOCK_TUTORS = [
  {
    id: "tutor1",
    name: "Arjun Kumar",
    languages: ["en", "kn", "hi"],
    hourly_rate: 200,
    rating: 4.8,
    total_sessions: 45,
    verified: true,
    bio: "Experienced English coach with 3+ years of experience helping first-gen learners.",
    district: "Bangalore"
  },
  {
    id: "tutor2",
    name: "Priya Sharma",
    languages: ["en", "hi"],
    hourly_rate: 250,
    rating: 4.9,
    total_sessions: 78,
    verified: true,
    bio: "MA in English Literature. Specializes in interview preparation.",
    district: "Mumbai"
  },
  {
    id: "tutor3",
    name: "Rahul Reddy",
    languages: ["en", "te", "kn"],
    hourly_rate: 150,
    rating: 4.5,
    total_sessions: 23,
    verified: false,
    bio: "Friendly tutor focusing on daily conversation practice.",
    district: "Hyderabad"
  }
]

const MOCK_SESSIONS_HISTORY = {
  sessions: [
    { id: "s1", tutor_name: "Arjun", status: "completed", scheduled_at: "2024-05-20T10:00:00Z", duration_minutes: 60, rating: 4.5 },
    { id: "s2", tutor_name: "Priya", status: "scheduled", scheduled_at: "2024-05-28T15:00:00Z", duration_minutes: 60, rating: null }
  ],
  role: "learner"
}

export const useTutorStore = create((set, get) => ({
  tutors: [],
  mySessions: [],
  isLoading: false,

  searchTutors: async (filters) => {
    set({ isLoading: true })
    try {
      const data = await tutorService.search(filters)
      set({ tutors: data.tutors || [] })
      return data
    } catch (error) {
      console.error('Failed to search tutors:', error)
      set({ tutors: MOCK_TUTORS })
      return { tutors: MOCK_TUTORS }
    } finally {
      set({ isLoading: false })
    }
  },

  bookSession: async (tutorId, scheduledAt, duration) => {
    set({ isLoading: true })
    try {
      const data = await tutorService.bookSession(tutorId, scheduledAt, duration)
      await get().loadMySessions()
      return data
    } catch (error) {
      console.error('Failed to book session:', error)
      return null
    } finally {
      set({ isLoading: false })
    }
  },

  loadMySessions: async () => {
    try {
      const data = await tutorService.getHistory()
      set({ mySessions: data.sessions || [] })
    } catch (error) {
      set({ mySessions: MOCK_SESSIONS_HISTORY.sessions })
      console.error('Failed to load sessions:', error)
    }
  }
}))