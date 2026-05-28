import { create } from 'zustand'
import { interviewService } from '../services/interviewService'

// Mock data for fallback
const MOCK_INTERVIEW_QUESTIONS = {
  questions: [
    { id: "q1", question: "Tell me about yourself", category: "behavioral", difficulty: 1 },
    { id: "q2", question: "What are your greatest strengths?", category: "behavioral", difficulty: 1 },
    { id: "q3", question: "Describe a challenge you faced at work", category: "situational", difficulty: 2 },
    { id: "q4", question: "Where do you see yourself in 5 years?", category: "behavioral", difficulty: 2 },
    { id: "q5", question: "Why do you want this job?", category: "behavioral", difficulty: 2 }
  ],
  total: 5
}

const MOCK_INTERVIEW_HISTORY = {
  interviews: [
    { id: "int1", question: "Tell me about yourself", score: 72, question_category: "behavioral", created_at: "2024-05-20T10:00:00Z" },
    { id: "int2", question: "What are your strengths?", score: 68, question_category: "behavioral", created_at: "2024-05-22T14:30:00Z" },
    { id: "int3", question: "Describe a challenge", score: 78, question_category: "situational", created_at: "2024-05-25T11:15:00Z" }
  ],
  average_score: 73,
  pagination: { page: 1, per_page: 20, total: 3, pages: 1 }
}

const MOCK_INTERVIEW_RESPONSE = {
  score: 78,
  evaluation: {
    score: 78,
    summary: "Good answer! You addressed the question well.",
    strengths: ["Clear communication", "Good structure", "Relevant examples"],
    improvements: ["Add more specific metrics", "Speak with more confidence", "Practice transitions"],
    sample_better_answer: "In my previous role, I led a team of 5 and increased efficiency by 20%.",
    communication_score: 75,
    content_score: 82,
    confidence_tips: "Maintain eye contact and speak slowly"
  },
  question: "Tell me about yourself"
}

export const useInterviewStore = create((set, get) => ({
  questions: [],
  currentQuestion: null,
  history: [],
  currentFeedback: null,
  isLoading: false,

  loadQuestions: async (category, difficulty, language) => {
    set({ isLoading: true })
    try {
      const data = await interviewService.getQuestions(category, difficulty, language)
      set({ questions: data.questions || [] })
      if (data.questions && data.questions.length > 0) {
        set({ currentQuestion: data.questions[0] })
      }
    } catch (error) {
      console.error('Failed to load questions:', error)
      set({ questions: MOCK_INTERVIEW_QUESTIONS.questions, currentQuestion: MOCK_INTERVIEW_QUESTIONS.questions[0] })
    } finally {
      set({ isLoading: false })
    }
  },

  submitResponse: async (questionId, answer, language) => {
    set({ isLoading: true })
    try {
      const data = await interviewService.submitResponse(questionId, answer, language)
      set({ currentFeedback: data.evaluation })
      await get().loadHistory()
      return data
    } catch (error) {
      console.error('Failed to submit response:', error)
      return null
    } finally {
      set({ isLoading: false })
    }
  },

  loadHistory: async () => {
    try {
      const data = await interviewService.getHistory()
      set({ history: data.interviews || [] })
    } catch (error) {
      set({ history: MOCK_INTERVIEW_HISTORY.interviews })
      console.error('Failed to load history:', error)
    }
  },

  nextQuestion: () => {
    const { questions, currentQuestion } = get()
    if (!currentQuestion) return
    const currentIndex = questions.findIndex(q => q.id === currentQuestion.id)
    if (currentIndex < questions.length - 1) {
      set({ currentQuestion: questions[currentIndex + 1], currentFeedback: null })
    }
  }
}))