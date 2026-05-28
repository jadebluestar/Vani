import React from 'react'
import { Calendar, TrendingUp, Award } from 'lucide-react'

export default function InterviewHistory({ history }) {
  if (!history || history.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500 dark:text-gray-400">No interview attempts yet</p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">Start practicing to see your progress</p>
      </div>
    )
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const averageScore = history.reduce((acc, item) => acc + item.score, 0) / history.length
  const bestScore = Math.max(...history.map(item => item.score))
  const totalAttempts = history.length

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <div className="card text-center">
          <TrendingUp size={20} className="mx-auto mb-2 text-primary-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{averageScore.toFixed(0)}%</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Average Score</p>
        </div>
        <div className="card text-center">
          <Award size={20} className="mx-auto mb-2 text-yellow-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{bestScore}%</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Best Score</p>
        </div>
        <div className="card text-center">
          <Calendar size={20} className="mx-auto mb-2 text-green-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{totalAttempts}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Attempts</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Recent Attempts</h3>
        <div className="space-y-3">
          {history.slice(0, 10).map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-1">
                  {item.question}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className={`text-lg font-bold ${getScoreColor(item.score)}`}>
                {item.score}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}