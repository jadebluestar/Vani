import React, { useState, useEffect } from 'react'
import { Search, Filter, Star, MapPin, Clock, IndianRupee } from 'lucide-react'
import { useTutorStore } from '../store/tutorStore'
import { useLanguageStore } from '../store/languageStore'
import BookingModal from '../components/Tutor/BookingModal'

export default function TutorsPage() {
  const { language, getLanguageName } = useLanguageStore()
  const { tutors, searchTutors, bookSession, isLoading } = useTutorStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [priceRange, setPriceRange] = useState('all')
  const [selectedTutor, setSelectedTutor] = useState(null)
  const [showBookingModal, setShowBookingModal] = useState(false)

  useEffect(() => {
    searchTutors({ language })
  }, [language])

  const filteredTutors = tutors?.filter(tutor => {
    const matchesSearch = tutor.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          tutor.languages?.some(l => l.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesPrice = priceRange === 'all' || 
                         (priceRange === 'low' && tutor.hourly_rate < 300) ||
                         (priceRange === 'medium' && tutor.hourly_rate >= 300 && tutor.hourly_rate < 600) ||
                         (priceRange === 'high' && tutor.hourly_rate >= 600)
    return matchesSearch && matchesPrice
  })

  const handleBook = (tutor) => {
    setSelectedTutor(tutor)
    setShowBookingModal(true)
  }

  const handleConfirmBooking = async (tutorId, scheduledAt, duration) => {
    await bookSession(tutorId, scheduledAt, duration)
    setShowBookingModal(false)
    setSelectedTutor(null)
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Find a Tutor</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Practice 1-on-1 with tutors who speak {getLanguageName(language)}
        </p>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name or language..."
              className="input pl-10"
            />
          </div>
          <select
            value={priceRange}
            onChange={(e) => setPriceRange(e.target.value)}
            className="input w-full sm:w-40"
          >
            <option value="all">All prices</option>
            <option value="low">Under ₹300/hr</option>
            <option value="medium">₹300-600/hr</option>
            <option value="high">₹600+/hr</option>
          </select>
        </div>
      </div>

      {/* Tutors List */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">Loading tutors...</div>
      ) : filteredTutors?.length === 0 ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          No tutors found matching your criteria.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTutors?.map((tutor) => (
            <div key={tutor.id} className="card hover:shadow-md transition-shadow">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                    {tutor.name?.charAt(0) || 'T'}
                  </span>
                </div>
                
                <div className="flex-1">
                  <div className="flex flex-wrap justify-between items-start gap-2">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{tutor.name}</h3>
                      <div className="flex items-center gap-3 mt-1">
                        <div className="flex items-center gap-1">
                          <Star size={14} className="fill-yellow-400 text-yellow-400" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">{tutor.rating?.toFixed(1)}</span>
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {tutor.total_sessions} sessions
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-primary-600 dark:text-primary-400 flex items-center gap-1">
                        <IndianRupee size={16} />{tutor.hourly_rate}
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
                      <span>Online</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                      <Clock size={12} />
                      <span>{tutor.languages?.join(', ') || 'English'}</span>
                    </div>
                    {tutor.verified && (
                      <span className="text-xs text-green-600 dark:text-green-400">Verified</span>
                    )}
                  </div>
                  
                  <button
                    onClick={() => handleBook(tutor)}
                    className="btn-primary w-full mt-4 py-2 text-sm"
                  >
                    Book a Session
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Booking Modal */}
      {showBookingModal && selectedTutor && (
        <BookingModal
          tutor={selectedTutor}
          onClose={() => {
            setShowBookingModal(false)
            setSelectedTutor(null)
          }}
          onConfirm={handleConfirmBooking}
        />
      )}
    </div>
  )
}