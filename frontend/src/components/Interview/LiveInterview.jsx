import React, { useState, useEffect, useRef } from 'react'
import { Mic, Square, Volume2, Loader2 } from 'lucide-react'

export default function LiveInterview({ sessionId, onComplete }) {
  const [isConnected, setIsConnected] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([])
  const [isAISpeaking, setIsAISpeaking] = useState(false)
  const wsRef = useRef(null)
  const mediaRecorderRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/interview/live/${sessionId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      ws.send(JSON.stringify({ type: 'start' }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'question') {
        setMessages(prev => [...prev, { role: 'ai', content: data.question }])
        speakText(data.question)
      } else if (data.type === 'feedback') {
        setMessages(prev => [...prev, { role: 'ai', content: data.feedback, isFeedback: true }])
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
    }

    return () => ws.close()
  }, [sessionId])

  const speakText = (text) => {
    setIsAISpeaking(true)
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-IN'
    utterance.onend = () => setIsAISpeaking(false)
    window.speechSynthesis.speak(utterance)
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const chunks = []
      
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        const reader = new FileReader()
        reader.onloadend = () => {
          wsRef.current.send(JSON.stringify({
            type: 'answer',
            audio: reader.result.split(',')[1]
          }))
        }
        reader.readAsDataURL(blob)
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

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Live Interview</h2>
        <div className={`flex items-center gap-2 text-sm ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          {isConnected ? 'Connected' : 'Connecting...'}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 max-h-96">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg ${
              msg.role === 'ai'
                ? msg.isFeedback
                  ? 'bg-yellow-50 dark:bg-yellow-900/20 mr-8'
                  : 'bg-gray-100 dark:bg-gray-700 mr-8'
                : 'bg-primary-100 dark:bg-primary-900/30 ml-8'
            }`}
          >
            <p className="text-sm text-gray-700 dark:text-gray-300">{msg.content}</p>
          </div>
        ))}
        {isAISpeaking && (
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <Loader2 size={14} className="animate-spin" />
            <span className="text-sm">AI is speaking...</span>
          </div>
        )}
      </div>

      <div className="flex justify-center pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!isConnected || isAISpeaking}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
            isRecording
              ? 'bg-red-500 hover:bg-red-600 animate-pulse'
              : 'bg-primary-500 hover:bg-primary-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isRecording ? <Square size={24} className="text-white" /> : <Mic size={24} className="text-white" />}
        </button>
      </div>
    </div>
  )
}