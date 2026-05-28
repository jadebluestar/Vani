import React from 'react'
import { Star, MapPin, Clock, Award } from 'lucide-react'

export default function TutorCard({ tutor, onBook }) {
  const renderStars = (rating) => {
    return (
      <div className="flex items-center gap-1">
        <Star size={14} className="fill-yellow-400 text-yellow-400" />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{rating.toFixed(1)}</span>
      </div>
    )
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center flex-shrink-0">
          <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {tutor.name?.charAt(0) || 'T'}
          </span>
        </div>
        
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{tutor.name}</h3>
              <div className="flex items-center gap-3 mt-1">
                {renderStars(tutor.rating)}
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {tutor.total_sessions} sessions
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xl font-bold text-primary-600 dark:text-primary-400">
                ₹{tutor.hourly_rate}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">per hour</p>
            </div>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
            {tutor.bio || 'Experienced tutor passionate about helping learners build confidence.'}
          </p>
          
          <div className="flex flex-wrap gap-3 mt-3">
            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
              <MapPin size={12} />
              <span>{tutor.location || 'Online'}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
              <Clock size={12} />
              <span>{tutor.languages?.join(', ') || 'English'}</span>
            </div>
            {tutor.verified && (
              <div className="flex items-center gap-1 text-xs text-green-500">
                <Award size={12} />
                <span>Verified</span>
              </div>
            )}
          </div>
          
          <button
            onClick={() => onBook(tutor)}
            className="btn-primary w-full mt-4 py-2 text-sm"
          >
            Book a Session
          </button>
        </div>
      </div>
    </div>
  )
}