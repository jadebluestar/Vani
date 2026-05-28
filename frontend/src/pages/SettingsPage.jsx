import React, { useState, useEffect } from 'react'
import { User, Bell, Globe, Shield, Moon, Sun, Smartphone, Save, Loader2 } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import { useLanguageStore } from '../store/languageStore'
import LanguageSelector from '../components/Auth/LanguageSelector'

export default function SettingsPage() {
  const { user, updateUser, isLoading } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()
  const { language, setLanguage } = useLanguageStore()
  
  const [name, setName] = useState(user?.name || '')
  const [phone, setPhone] = useState(user?.phone || '')
  const [email, setEmail] = useState(user?.email || '')
  const [notifications, setNotifications] = useState({
    email: true,
    whatsapp: true,
    practiceReminders: true
  })
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    if (user) {
      setName(user.name || '')
      setPhone(user.phone || '')
      setEmail(user.email || '')
    }
  }, [user])

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setIsSaving(true)
    setSaveSuccess(false)
    try {
      await updateUser({ name, email })
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (error) {
      console.error('Failed to save profile:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const sections = [
    {
      title: 'Profile Information',
      icon: User,
      fields: [
        { label: 'Full Name', value: name, setter: setName, type: 'text', placeholder: 'Enter your name' },
        { label: 'Phone Number', value: phone, setter: setPhone, type: 'tel', placeholder: '+91 9876543210', disabled: true },
        { label: 'Email Address', value: email, setter: setEmail, type: 'email', placeholder: 'you@example.com' }
      ]
    }
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your account preferences</p>
      </div>

      <div className="space-y-6">
        {/* Profile Section */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <User size={20} className="text-primary-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Profile Information</h2>
          </div>
          
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div>
              <label className="label">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="input"
              />
            </div>
            
            <div>
              <label className="label">Phone Number</label>
              <input
                type="tel"
                value={phone}
                disabled
                className="input bg-gray-50 dark:bg-gray-700 cursor-not-allowed"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Phone number cannot be changed. Contact support for assistance.
              </p>
            </div>
            
            <div>
              <label className="label">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="input"
              />
            </div>
            
            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={isSaving || isLoading}
                className="btn-primary flex items-center gap-2"
              >
                {isSaving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
              {saveSuccess && (
                <span className="text-sm text-green-600 dark:text-green-400">Saved successfully!</span>
              )}
            </div>
          </form>
        </div>

        {/* Language Section */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Globe size={20} className="text-primary-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Language Preferences</h2>
          </div>
          <LanguageSelector />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
            Choose your preferred language for practice sessions and feedback
          </p>
        </div>

        {/* Appearance Section */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={20} className="text-primary-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Appearance</h2>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-700 dark:text-gray-300">Theme</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Switch between light and dark mode</p>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>
          </div>
        </div>

        {/* Notifications Section */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Bell size={20} className="text-primary-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Notifications</h2>
          </div>
          
          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <p className="text-gray-700 dark:text-gray-300">Email Notifications</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Receive updates and tips via email</p>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-10 h-5 bg-gray-300 dark:bg-gray-600 rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
              </div>
            </label>
            
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <p className="text-gray-700 dark:text-gray-300">WhatsApp Notifications</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Get practice reminders on WhatsApp</p>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={notifications.whatsapp}
                  onChange={(e) => setNotifications({ ...notifications, whatsapp: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-10 h-5 bg-gray-300 dark:bg-gray-600 rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
              </div>
            </label>
            
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <p className="text-gray-700 dark:text-gray-300">Practice Reminders</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Daily reminders to keep your streak</p>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={notifications.practiceReminders}
                  onChange={(e) => setNotifications({ ...notifications, practiceReminders: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-10 h-5 bg-gray-300 dark:bg-gray-600 rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
              </div>
            </label>
          </div>
        </div>

        {/* Account Section */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Smartphone size={20} className="text-primary-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Account</h2>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-gray-700 dark:text-gray-300">Account Type</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Free Plan</p>
              </div>
              <button className="text-sm text-primary-600 dark:text-primary-400 hover:underline">
                Upgrade
              </button>
            </div>
            
            <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
              <button className="text-sm text-red-600 dark:text-red-400 hover:underline">
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}