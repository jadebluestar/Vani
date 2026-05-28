import React from 'react'
import { CheckCircle, AlertCircle, TrendingUp, Mic, BookOpen, Volume2 } from 'lucide-react'

export default function FeedbackCard({ feedback }) {
  if (!feedback) return null

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const metrics = [
    { label: 'Fluency', value: feedback.fluency_score, icon: Volume2 },
    { label: 'Pronunciation', value: feedback.pronunciation_score, icon: Mic },
    { label: 'Grammar', value: feedback.grammar_score, icon: BookOpen },
  ]

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Feedback</h3>
        <div className="flex items-center gap-2">
          <TrendingUp size={16} className="text-primary-500" />
          <span className={`text-2xl font-bold ${getScoreColor(feedback.overall_score)}`}>
            {feedback.overall_score}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="text-center">
            <metric.icon size={16} className="mx-auto mb-1 text-gray-400" />
            <p className="text-xs text-gray-500 dark:text-gray-400">{metric.label}</p>
            <p className={`text-lg font-semibold ${getScoreColor(metric.value)}`}>
              {metric.value}%
            </p>
          </div>
        ))}
      </div>

      {feedback.filler_words > 0 && (
        <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          <AlertCircle size={16} className="text-yellow-500" />
          <p className="text-sm text-yellow-700 dark:text-yellow-300">
            Filler words detected: {feedback.filler_words}
          </p>
        </div>
      )}

      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Improvements:</p>
        <ul className="space-y-1">
          {feedback.improvements?.map((item, index) => (
            <li key={index} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
              <CheckCircle size={14} className="text-green-500 mt-0.5" />
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}