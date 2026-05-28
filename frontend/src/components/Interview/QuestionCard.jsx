import React from 'react'
import { Star, Clock, Mic } from 'lucide-react'

export default function QuestionCard({ question, index, total, onAnswer, isProcessing }) {
  const [isRecording, setIsRecording] = React.useState(false)
  const [answer, setAnswer] = React.useState('')
  const mediaRecorderRef = React.useRef(null)

  const difficultyStars = Array(question?.difficulty_level || 1).fill('★')

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const chunks = []
      
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        if (onAnswer) onAnswer(blob)
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start()
      mediaRecorderRef.current = mediaRecorder
      setIsRecording(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleTextSubmit = () => {
    if (answer.trim() && onAnswer) {
      onAnswer(answer.trim())
      setAnswer('')
    }
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Question {index + 1} of {total}
        </span>
        <div className="flex items-center gap-1">
          {difficultyStars.map((star, i) => (
            <Star key={i} size={14} className="fill-yellow-400 text-yellow-400" />
          ))}
        </div>
      </div>

      <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg mb-6">
        <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
          {question?.text}
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
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Or type your answer here..."
            rows="4"
            className="input w-full"
            disabled={isProcessing}
          />
          <button
            onClick={handleTextSubmit}
            disabled={!answer.trim() || isProcessing}
            className="absolute bottom-3 right-3 btn-primary py-1 px-3 text-sm"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  )
}