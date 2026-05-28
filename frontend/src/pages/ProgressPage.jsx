import React, { useEffect } from 'react'
import { TrendingUp, Target, Award, Calendar, ArrowUp, ArrowDown } from 'lucide-react'
import { useProgressStore } from '../store/progressStore'
import ConfidenceChart from '../components/Progress/ConfidenceChart'
import SkillRadar from '../components/Progress/SkillRadar'
import StreakCalendar from '../components/Progress/StreakCalendar'

export default function ProgressPage() {
  const { 
    dashboard, skills, confidenceTimeline, recommendations,
    loadDashboard, loadSkills, loadConfidenceTimeline, loadRecommendations, isLoading 
  } = useProgressStore()

  useEffect(() => {
    loadDashboard()
    loadSkills()
    loadConfidenceTimeline()
    loadRecommendations()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-gray-500 dark:text-gray-400">Loading progress...</div>
      </div>
    )
  }

  const chartLabels = confidenceTimeline?.map(d => d.date) || []
  const chartData = confidenceTimeline?.map(d => d.score) || []

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Your Progress</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Track your improvement over time</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Hours</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{dashboard?.total_hours || 0}</p>
            </div>
            <Calendar size={24} className="text-primary-500" />
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Sessions</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{dashboard?.total_sessions || 0}</p>
            </div>
            <Target size={24} className="text-green-500" />
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Avg Score</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{dashboard?.average_score || 0}%</p>
            </div>
            <TrendingUp size={24} className="text-yellow-500" />
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Best Streak</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{dashboard?.best_streak || 0}d</p>
            </div>
            <Award size={24} className="text-purple-500" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Confidence Trend</h3>
          <ConfidenceChart data={chartData} labels={chartLabels} />
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Skill Breakdown</h3>
          <SkillRadar skills={skills} />
        </div>
      </div>

      {/* Streak Calendar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Activity Streak</h3>
          <StreakCalendar 
            activity={dashboard?.daily_activity} 
            currentStreak={dashboard?.streak}
            bestStreak={dashboard?.best_streak}
          />
        </div>

        {/* Recommendations */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Recommendations</h3>
          <div className="space-y-3">
            {recommendations?.map((rec, index) => (
              <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{rec.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{rec.description}</p>
              </div>
            ))}
            {(!recommendations || recommendations.length === 0) && (
              <p className="text-center text-gray-500 dark:text-gray-400 py-4">
                Complete more sessions to get personalized recommendations
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Milestones */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Recent Milestones</h3>
        <div className="space-y-3">
          {dashboard?.milestones?.map((milestone, index) => (
            <div key={index} className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                <Award size={14} className="text-primary-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900 dark:text-gray-100">{milestone.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{milestone.date}</p>
              </div>
            </div>
          ))}
          {(!dashboard?.milestones || dashboard.milestones.length === 0) && (
            <p className="text-center text-gray-500 dark:text-gray-400 py-4">
              Complete your first session to earn milestones
            </p>
          )}
        </div>
      </div>
    </div>
  )
}