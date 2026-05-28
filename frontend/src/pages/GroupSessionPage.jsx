import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Mic, Square, Users, Phone, PhoneOff, Copy, Check } from 'lucide-react'
import { groupService } from '../services/groupService'
import { useLanguageStore } from '../store/languageStore'
import { useSpeechStore } from '../store/speechStore'

export default function GroupSessionPage() {
  const { code } = useParams()
  const navigate = useNavigate()
  const { language, getLanguageName } = useLanguageStore()
  const { transcribeAudio, analyzeFeedback, isProcessing } = useSpeechStore()
  
  const [session, setSession] = useState(null)
  const [participants, setParticipants] = useState([])
  const [messages, setMessages] = useState([])
  const [isRecording, setIsRecording] = useState(false)
  const [isJoined, setIsJoined] = useState(false)
  const [copied, setCopied] = useState(false)
  const mediaRecorderRef = useRef(null)
  const wsRef = useRef(null)

  useEffect(() => {
    if (code) {
      joinSession()
    }
    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [code])

  const joinSession = async () => {
    try {
      const data = await groupService.joinGroup(code)
      setSession(data.session)
      setParticipants(data.participants)
      setIsJoined(true)
      
      // Connect WebSocket
      const ws = new WebSocket(`ws://localhost:8000/group/${code}/ws`)
      wsRef.current = ws
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'message') {
          setMessages(prev => [...prev, data])
        } else if (data.type === 'participant_joined') {
          setParticipants(prev => [...prev, data.participant])
        } else if (data.type === 'participant_left') {
          setParticipants(prev => prev.filter(p => p.id !== data.participant_id))
        }
      }
    } catch (error) {
      console.error('Failed to join session:', error)
      navigate('/group')
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const chunks = []
      
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        const transcription = await transcribeAudio(blob, language)
        if (transcription?.text) {
          const feedback = await analyzeFeedback(transcription.text, language)
          wsRef.current.send(JSON.stringify({
            type: 'message',
            text: transcription.text,
            feedback: feedback
          }))
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

  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleLeave = () => {
    if (wsRef.current) wsRef.current.close()
    navigate('/group')
  }

  if (!isJoined) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-gray-500 dark:text-gray-400">Joining session...</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {session?.name || 'Group Session'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Practicing in {getLanguageName(language)}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <code className="font-mono text-sm">{code}</code>
              <button onClick={handleCopyCode} className="hover:text-primary-600">
                {copied ? <Check size={14} /> : <Copy size={14} />}
              </button>
            </div>
            <button
              onClick={handleLeave}
              className="btn-outline flex items-center gap-2 text-red-600 border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              <PhoneOff size={16} />
              Leave
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-2">
          <div className="card h-[500px] flex flex-col">
            <div className="flex items-center gap-2 p-3 border-b border-gray-200 dark:border-gray-700">
              <Users size={16} className="text-gray-400" />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {participants.length} participants
              </span>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.user_id === 'me' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className="max-w-[80%]">
                    <div className={`p-3 rounded-lg ${
                      msg.user_id === 'me'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                    }`}>
                      <p className="text-sm">{msg.text}</p>
                    </div>
                    {msg.feedback && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Feedback: {msg.feedback.overall_score}%
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-200 dark:border-gray-700 p-4">
              <div className="flex justify-center">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isProcessing}
                  className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${
                    isRecording
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                      : 'bg-primary-500 hover:bg-primary-600'
                  } disabled:opacity-50`}
                >
                  {isRecording ? <Square size={24} className="text-white" /> : <Mic size={24} className="text-white" />}
                </button>
              </div>
              <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-3">
                {isRecording ? 'Recording... tap to stop' : 'Tap to speak'}
              </p>
            </div>
          </div>
        </div>

        {/* Participants Panel */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Participants</h3>
            <div className="space-y-2">
              {participants.map((p) => (
                <div key={p.id} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-700">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{p.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Session Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-start gap-2">
                <div className="w-4 h-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mt-0.5">
                  <span className="text-xs text-primary-600">1</span>
                </div>
                Take turns speaking
              </li>
              <li className="flex items-start gap-2">
                <div className="w-4 h-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mt-0.5">
                  <span className="text-xs text-primary-600">2</span>
                </div>
                Listen actively to others
              </li>
              <li className="flex items-start gap-2">
                <div className="w-4 h-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mt-0.5">
                  <span className="text-xs text-primary-600">3</span>
                </div>
                Use feedback to improve
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}