import React, { useEffect } from 'react'
import { Video, Clock, Star, Users } from 'lucide-react'
import { useTutorStore } from '../../store/tutorStore'

export default function TutorDashboard() {
  const { mySessions, loadMySessions, isLoading } = useTutorStore()

  useEffect(() => {
    loadMySessions()
  }, [])

  const upcomingSessions = mySessions?.filter(s => s.status === 'scheduled') || []
  const pastSessions = mySessions?.filter(s => s.status === 'completed') || []

  const totalEarnings = pastSessions.reduce((sum, s) => sum + (s.amount_paid || 0), 0)
  const averageRating = pastSessions.reduce((sum, s) => sum + (s.rating || 0), 0) / (pastSessions.length || 1)

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <Users size={20} className="mx-auto mb-2 text-primary-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{mySessions?.length || 0}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Sessions</p>
        </div>
        <div className="card text-center">
          <Clock size={20} className="mx-auto mb-2 text-yellow-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{upcomingSessions.length}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Upcoming</p>
        </div>
        <div className="card text-center">
          <Star size={20} className="mx-auto mb-2 text-yellow-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{averageRating.toFixed(1)}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Rating</p>
        </div>
        <div className="card text-center">
          <Video size={20} className="mx-auto mb-2 text-green-500" />
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">₹{totalEarnings}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Earnings</p>
        </div>
      </div>

      {upcomingSessions.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Upcoming Sessions</h3>
          <div className="space-y-3">
            {upcomingSessions.map((session) => (
              <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{session.learner_name || 'Student'}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {new Date(session.scheduled_at).toLocaleString()}
                  </p>
                </div>
                <button className="btn-primary py-1 px-4 text-sm">Join</button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}