import React, { useState, useCallback } from 'react'
import { Mic, Square, Loader2 } from 'lucide-react'
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition'

export default function VoiceRecorder({ onRecordingComplete, isProcessing, language }) {
  const { isListening, startListening, stopListening } = useSpeechRecognition()
  const [error, setError] = useState(null)

  const handleStartRecording = useCallback(async () => {
    setError(null)
    try {
      await startListening()
    } catch (err) {
      setError('Could not access microphone. Please check permissions.')
    }
  }, [startListening])

  const handleStopRecording = useCallback(async () => {
    const audioBlob = await stopListening()
    if (audioBlob && onRecordingComplete) {
      onRecordingComplete(audioBlob)
    }
  }, [stopListening, onRecordingComplete])

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={isListening ? handleStopRecording : handleStartRecording}
        disabled={isProcessing}
        className={`
          w-20 h-20 rounded-full flex items-center justify-center transition-all
          ${isListening 
            ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
            : 'bg-primary-500 hover:bg-primary-600'
          }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        {isProcessing ? (
          <Loader2 size={32} className="text-white animate-spin" />
        ) : isListening ? (
          <Square size={32} className="text-white" />
        ) : (
          <Mic size={32} className="text-white" />
        )}
      </button>
      
      {isListening && (
        <p className="text-sm text-gray-500 dark:text-gray-400 animate-pulse">
          Listening in {language}...
        </p>
      )}
      
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}