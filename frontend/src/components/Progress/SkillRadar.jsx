import React, { useEffect, useRef } from 'react'
import Chart from 'chart.js/auto'

export default function SkillRadar({ skills }) {
  const chartRef = useRef(null)
  const chartInstanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current || !skills) return

    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy()
    }

    const labels = skills.map(s => s.name)
    const data = skills.map(s => s.score)

    chartInstanceRef.current = new Chart(chartRef.current, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Current Level',
            data: data,
            backgroundColor: 'rgba(99, 102, 241, 0.2)',
            borderColor: '#6366f1',
            borderWidth: 2,
            pointBackgroundColor: '#6366f1',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4
          },
          {
            label: 'Target',
            data: skills.map(() => 80),
            backgroundColor: 'rgba(156, 163, 175, 0.1)',
            borderColor: '#9ca3af',
            borderWidth: 1,
            borderDash: [5, 5],
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0,
            max: 100,
            ticks: {
              stepSize: 20,
              callback: (value) => `${value}%`
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => `${context.dataset.label}: ${context.raw}%`
            }
          }
        }
      }
    })

    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy()
      }
    }
  }, [skills])

  return (
    <div className="w-full h-80">
      <canvas ref={chartRef} />
    </div>
  )
}