import React, { useEffect, useRef } from 'react'

export default function Waveform({ isActive }) {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)

  useEffect(() => {
    if (!isActive) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      return
    }

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    let time = 0

    const draw = () => {
      canvas.width = canvas.clientWidth
      canvas.height = canvas.clientHeight

      const width = canvas.width
      const height = canvas.height
      const barWidth = 4
      const barCount = Math.floor(width / (barWidth + 2))

      ctx.clearRect(0, 0, width, height)

      for (let i = 0; i < barCount; i++) {
        const x = i * (barWidth + 2)
        const amplitude = Math.sin(time + i * 0.3) * 0.5 + 0.5
        const barHeight = 20 + amplitude * (height - 40)
        
        ctx.fillStyle = `rgba(99, 102, 241, ${0.3 + amplitude * 0.5})`
        ctx.fillRect(x, (height - barHeight) / 2, barWidth, barHeight)
      }

      time += 0.1
      animationRef.current = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isActive])

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-32 rounded-lg bg-gray-100 dark:bg-gray-800"
    />
  )
}