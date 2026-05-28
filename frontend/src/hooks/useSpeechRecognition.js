import { useState, useCallback, useRef } from 'react'

export const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const startListening = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        // Callback will be handled by parent
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsListening(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
    }
  }, [])

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsListening(false)
      
      return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          if (mediaRecorderRef.current.state === 'inactive') {
            clearInterval(checkInterval)
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
            resolve(audioBlob)
          }
        }, 100)
      })
    }
    return Promise.resolve(null)
  }, [])

  return {
    isListening,
    startListening,
    stopListening,
    transcript,
    setTranscript
  }
}