import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Mic, MessageSquare, Users, Award, TrendingUp, Calendar, ArrowRight } from 'lucide-react'
import { useProgressStore } from '../store/progressStore'
import { useAuthStore } from '../store/authStore'
import { useLanguageStore } from '../store/languageStore'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { getLanguageName } = useLanguageStore()
  const { dashboard, loadDashboard, isLoading } = useProgressStore()
  const [greeting, setGreeting] = useState('')

  useEffect(() => {
    loadDashboard()
    const hour = new Date().getHours()
    if (hour < 12) setGreeting('Good morning')
    else if (hour < 18) setGreeting('Good afternoon')
    else setGreeting('Good evening')
  }, [])

  const stats = [
    { label: 'Practice Sessions', value: dashboard?.total_sessions || 0, icon: Mic, color: 'primary', link: '/practice' },
    { label: 'Confidence Score', value: `${dashboard?.confidence_score || 0}%`, icon: TrendingUp, color: 'green', link: '/progress' },
    { label: 'Current Streak', value: `${dashboard?.streak || 0} days`, icon: Calendar, color: 'orange', link: '/progress' },
    { label: 'Certificates', value: dashboard?.certificates_count || 0, icon: Award, color: 'purple', link: '/credentials' },
  ]

  const quickActions = [
    { label: 'Practice Conversation', icon: MessageSquare, color: 'primary', link: '/practice', description: 'Improve daily speaking' },
    { label: 'Interview Practice', icon: Mic, color: 'green', link: '/interview', description: 'Prepare for interviews' },
    { label: 'Find a Tutor', icon: Users, color: 'purple', link: '/tutors', description: '1-on-1 sessions' },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-gray-500 dark:text-gray-400">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {greeting}, {user?.name || 'Learner'}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Continue your journey in {getLanguageName()}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Link key={stat.label} to={stat.link} className="block">
              <div className="card hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">{stat.value}</p>
                  </div>
                  <Icon className={`w-8 h-8 text-${stat.color}-500`} />
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {quickActions.map((action) => {
          const Icon = action.icon
          return (
            <Link key={action.label} to={action.link} className="block">
              <div className="card hover:shadow-md transition-shadow">
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-lg bg-${action.color}-100 dark:bg-${action.color}-900/20 flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 text-${action.color}-600 dark:text-${action.color}-400`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">{action.label}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{action.description}</p>
                  </div>
                  <ArrowRight size={16} className="text-gray-400" />
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Recent Activity</h2>
          <Link to="/progress" className="text-sm text-primary-600 dark:text-primary-400 hover:underline">
            View all
          </Link>
        </div>
        <div className="space-y-3">
          {dashboard?.recent_activities?.length > 0 ? (
            dashboard.recent_activities.slice(0, 5).map((activity, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-primary-500" />
                <div className="flex-1">
                  <p className="text-sm text-gray-700 dark:text-gray-300">{activity.description}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{activity.time_ago}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-500 dark:text-gray-400 py-4">
              No recent activity. Start practicing!
            </p>
          )}
        </div>
      </div>
    </div>
  )
}