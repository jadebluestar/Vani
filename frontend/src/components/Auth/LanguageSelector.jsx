import React from 'react'
import { Globe } from 'lucide-react'
import { useLanguageStore } from '../../store/languageStore'

const languages = [
  { code: 'kn', name: 'Kannada', script: 'ಕನ್ನಡ' },
  { code: 'hi', name: 'Hindi', script: 'हिन्दी' },
  { code: 'ta', name: 'Tamil', script: 'தமிழ்' },
  { code: 'te', name: 'Telugu', script: 'తెలుగు' },
  { code: 'ml', name: 'Malayalam', script: 'മലയാളം' },
  { code: 'bn', name: 'Bengali', script: 'বাংলা' },
  { code: 'mr', name: 'Marathi', script: 'मराठी' },
  { code: 'en', name: 'English', script: 'English' }
]

export default function LanguageSelector({ onSelect, compact }) {
  const { language, setLanguage } = useLanguageStore()

  const handleSelect = (code) => {
    setLanguage(code)
    if (onSelect) onSelect(code)
  }

  if (compact) {
    return (
      <select
        value={language}
        onChange={(e) => handleSelect(e.target.value)}
        className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm rounded-lg px-3 py-2 border-0 focus:ring-2 focus:ring-primary-500"
      >
        {languages.map(lang => (
          <option key={lang.code} value={lang.code}>{lang.name}</option>
        ))}
      </select>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Globe size={20} className="text-primary-500" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Choose your language</h3>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => handleSelect(lang.code)}
            className={`p-4 rounded-lg border-2 transition-all text-center ${
              language === lang.code
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
            }`}
          >
            <div className="text-lg font-medium text-gray-900 dark:text-gray-100">
              {lang.script}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {lang.name}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}