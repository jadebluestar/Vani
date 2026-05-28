import React from 'react'
import { CheckCircle, XCircle } from 'lucide-react'

export default function StreakCalendar({ activity, currentStreak, bestStreak }) {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  
  const getActivityForDay = (dayIndex) => {
    const today = new Date()
    const dayOfWeek = today.getDay()
    const adjustedDayIndex = (dayIndex + 1) % 7
    const date = new Date(today)
    date.setDate(today.getDate() - (dayOfWeek - adjustedDayIndex))
    const dateStr = date.toISOString().split('T')[0]
    return activity?.[dateStr]
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Current Streak</p>
          <p className="text-3xl font-bold text-primary-600 dark:text-primary-400">{currentStreak || 0} days</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500 dark:text-gray-400">Best Streak</p>
          <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{bestStreak || 0} days</p>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.map((day, index) => {
          const hasActivity = getActivityForDay(index)
          return (
            <div key={day} className="text-center">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">{day}</div>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center mx-auto ${
                hasActivity 
                  ? 'bg-green-100 dark:bg-green-900/30' 
                  : 'bg-gray-100 dark:bg-gray-700'
              }`}>
                {hasActivity ? (
                  <CheckCircle size={20} className="text-green-500" />
                ) : (
                  <XCircle size={20} className="text-gray-400" />
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}