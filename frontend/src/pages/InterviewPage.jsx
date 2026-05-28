import React, { useState, useEffect, useRef } from 'react'
import { Mic, Square, Star, Clock, Loader2 } from 'lucide-react'
import { useInterviewStore } from '../store/interviewStore'
import { useSpeechStore } from '../store/speechStore'
import { useLanguageStore } from '../store/languageStore'
import FeedbackCard from '../components/Speech/FeedbackCard'

export default function InterviewPage() {
  const { language, getLanguageName } = useLanguageStore()
  const { transcribeAudio, analyzeFeedback, isProcessing, feedback, clearTranscript } = useSpeechStore()
  const { questions, currentQuestion, loadQuestions, submitResponse, history, isLoading } = useInterviewStore()
  
  const [isRecording, setIsRecording] = useState(false)
  const [answerText, setAnswerText] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('behavioral')
  const mediaRecorderRef = useRef(null)

  const categories = [
    { value: 'behavioral', label: 'Behavioral' },
    { value: 'technical', label: 'Technical' },
    { value: 'situational', label: 'Situational' }
  ]

  useEffect(() => {
    loadQuestions(selectedCategory, null, language)
    return () => clearTranscript()
  }, [selectedCategory, language])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const chunks = []
      
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        const transcription = await transcribeAudio(blob, language)
        if (transcription?.text && currentQuestion) {
          await submitResponse(currentQuestion.id, transcription.text, language)
          await analyzeFeedback(transcription.text, language)
        }
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start()
      mediaRecorderRef.current = mediaRecorder
      setIsRecording(true)
    } catch (error) {
      console.error('Microphone error:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleTextSubmit = async () => {
    if (!answerText.trim() || !currentQuestion) return
    await submitResponse(currentQuestion.id, answerText, language)
    await analyzeFeedback(answerText, language)
    setAnswerText('')
  }

  const progress = questions.length > 0 && currentQuestion
    ? ((questions.findIndex(q => q.id === currentQuestion.id) + 1) / questions.length) * 100
    : 0

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Interview Practice</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Practice real interview questions in {getLanguageName(language)}
        </p>
      </div>

      <div className="mb-6">
        <div className="flex gap-2">
          {categories.map(cat => (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === cat.value
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Question Area */}
        <div className="lg:col-span-2">
          <div className="card">
            {isLoading ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading questions...</div>
            ) : questions.length > 0 && currentQuestion ? (
              <>
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Question {questions.findIndex(q => q.id === currentQuestion.id) + 1} of {questions.length}
                    </span>
                    <div className="flex items-center gap-1">
                      {[...Array(currentQuestion.difficulty_level)].map((_, i) => (
                        <Star key={i} size={14} className="fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-primary-500 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
                  </div>
                </div>

                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg mb-6">
                  <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {currentQuestion.text}
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="flex gap-3">
                    <button
                      onClick={isRecording ? stopRecording : startRecording}
                      disabled={isProcessing}
                      className={`flex-1 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                        isRecording
                          ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                          : 'bg-primary-500 hover:bg-primary-600 text-white'
                      }`}
                    >
                      <Mic size={18} />
                      {isRecording ? 'Recording...' : 'Record Answer'}
                    </button>
                  </div>

                  <div className="relative">
                    <textarea
                      value={answerText}
                      onChange={(e) => setAnswerText(e.target.value)}
                      placeholder="Or type your answer here..."
                      rows={4}
                      className="input w-full"
                      disabled={isProcessing}
                    />
                    <button
                      onClick={handleTextSubmit}
                      disabled={!answerText.trim() || isProcessing}
                      className="absolute bottom-3 right-3 bg-primary-500 text-white px-3 py-1 rounded-lg text-sm disabled:opacity-50"
                    >
                      Submit
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                No questions available. Try another category.
              </div>
            )}
          </div>
        </div>

        {/* Feedback & History */}
        <div className="space-y-6">
          {feedback && <FeedbackCard feedback={feedback} />}
          
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Recent Attempts</h3>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {history?.slice(0, 5).map((item, index) => (
                <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">{item.question}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400">{item.category}</span>
                    <span className={`text-sm font-semibold ${
                      item.score >= 70 ? 'text-green-500' : item.score >= 50 ? 'text-yellow-500' : 'text-red-500'
                    }`}>
                      {item.score}%
                    </span>
                  </div>
                </div>
              ))}
              {(!history || history.length === 0) && (
                <p className="text-center text-gray-500 dark:text-gray-400 py-4">No interview attempts yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}