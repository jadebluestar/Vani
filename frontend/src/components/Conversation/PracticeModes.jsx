import React from 'react'
import { MessageSquare, Briefcase, Users, TrendingUp } from 'lucide-react'

const modes = [
  {
    id: 'daily',
    name: 'Daily Conversation',
    description: 'Practice everyday conversations and common phrases',
    icon: MessageSquare,
    color: 'primary'
  },
  {
    id: 'interview',
    name: 'Interview Prep',
    description: 'Practice common interview questions and answers',
    icon: Briefcase,
    color: 'green'
  },
  {
    id: 'group',
    name: 'Group Discussion',
    description: 'Practice with other learners in real-time',
    icon: Users,
    color: 'purple'
  },
  {
    id: 'advanced',
    name: 'Advanced Topics',
    description: 'Challenge yourself with complex topics',
    icon: TrendingUp,
    color: 'orange'
  }
]

export default function PracticeModes({ selectedMode, onSelectMode }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {modes.map((mode) => {
        const Icon = mode.icon
        const isSelected = selectedMode === mode.id
        
        return (
          <button
            key={mode.id}
            onClick={() => onSelectMode(mode.id)}
            className={`p-4 rounded-xl text-left transition-all ${
              isSelected
                ? `bg-${mode.color}-50 dark:bg-${mode.color}-900/20 border-2 border-${mode.color}-500`
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className={`w-10 h-10 rounded-lg bg-${mode.color}-100 dark:bg-${mode.color}-900/30 flex items-center justify-center mb-3`}>
              <Icon size={20} className={`text-${mode.color}-600 dark:text-${mode.color}-400`} />
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">{mode.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{mode.description}</p>
          </button>
        )
      })}
    </div>
  )
}