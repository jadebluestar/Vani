import React, { useEffect, useRef } from 'react'
import Chart from 'chart.js/auto'

export default function ConfidenceChart({ data, labels }) {
  const chartRef = useRef(null)
  const chartInstanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current || !data || !labels) return

    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy()
    }

    chartInstanceRef.current = new Chart(chartRef.current, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Confidence Score',
            data: data,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#6366f1',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: (context) => `Confidence: ${context.raw}%`
            }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            grid: {
              color: '#e5e7eb'
            },
            title: {
              display: true,
              text: 'Confidence Score (%)'
            }
          },
          x: {
            grid: {
              display: false
            },
            title: {
              display: true,
              text: 'Date'
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
  }, [data, labels])

  return (
    <div className="w-full h-64">
      <canvas ref={chartRef} />
    </div>
  )
}