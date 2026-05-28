import React, { useState, useEffect, useRef } from 'react'
import { Mic, Square, Send, Loader2, Volume2, RefreshCw } from 'lucide-react'
import { useSpeechStore } from '../store/speechStore'
import { useConversationStore } from '../store/conversationStore'
import { useLanguageStore } from '../store/languageStore'
import FeedbackCard from '../components/Speech/FeedbackCard'

export default function PracticePage() {
  const { language, getLanguageName } = useLanguageStore()
  const { transcribeAudio, analyzeFeedback, isProcessing, feedback, clearTranscript } = useSpeechStore()
  const { currentSession, startSession, sendMessage, messages, isLoading } = useConversationStore()
  
  const [isRecording, setIsRecording] = useState(false)
  const [inputText, setInputText] = useState('')
  const mediaRecorderRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    startSession(language)
    return () => clearTranscript()
  }, [language])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

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
          await sendMessage(currentSession?.session_id, transcription.text, language)
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
    if (!inputText.trim()) return
    await sendMessage(currentSession?.session_id, inputText, language)
    await analyzeFeedback(inputText, language)
    setInputText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleTextSubmit()
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Practice Conversations</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Practice daily conversations in {getLanguageName(language)}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-2">
          <div className="card h-[500px] flex flex-col">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages?.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  Start speaking to begin the conversation
                </div>
              ) : (
                messages?.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-primary-500 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  </div>
                ))
              )}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                    <Loader2 size={16} className="animate-spin text-gray-500" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t border-gray-200 dark:border-gray-700 p-4">
              <div className="flex gap-3">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isProcessing}
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
                    isRecording
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                      : 'bg-primary-500 hover:bg-primary-600'
                  } disabled:opacity-50`}
                >
                  {isRecording ? <Square size={20} className="text-white" /> : <Mic size={20} className="text-white" />}
                </button>
                
                <div className="flex-1 relative">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    rows={1}
                    className="input w-full pr-12 resize-none"
                    disabled={isProcessing}
                  />
                  <button
                    onClick={handleTextSubmit}
                    disabled={!inputText.trim() || isProcessing}
                    className="absolute right-2 bottom-2 p-1.5 rounded-lg text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/30 disabled:opacity-50"
                  >
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feedback Panel */}
        <div className="space-y-6">
          {feedback && <FeedbackCard feedback={feedback} />}
          
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-start gap-2">
                <div className="w-4 h-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mt-0.5">
                  <span className="text-xs text-primary-600">1</span>
                </div>
                Speak clearly at a natural pace
              </li>
              <li className="flex items-start gap-2">
                <div className="w-4 h-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mt-0.5">
                  <span className="text-xs text-primary-600">2</span>
                </div>
                Try to use full sentences
              </li>
              <li className="flex items-start gap-2">
                <div className="w-4 h-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mt-0.5">
                  <span className="text-xs text-primary-600">3</span>
                </div>
                Review feedback to improve
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}