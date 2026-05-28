import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Phone, ArrowRight, CheckCircle } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import LanguageSelector from '../components/Auth/LanguageSelector'

export default function LoginPage() {
  const navigate = useNavigate()
  const { sendOTP, verifyOTP, isLoading } = useAuthStore()
  const [step, setStep] = useState('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [countdown, setCountdown] = useState(0)

  const handleSendOTP = async (e) => {
    e.preventDefault()
    if (phone.length !== 10) return
    const success = await sendOTP(`+91${phone}`)
    if (success) {
      setStep('otp')
      setCountdown(60)
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) clearInterval(timer)
          return prev - 1
        })
      }, 1000)
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()
    if (otp.length !== 6) return
    const success = await verifyOTP(`+91${phone}`, otp)
    if (success) navigate('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-600 dark:text-primary-400">Vani</h1>
          <h2 className="mt-4 text-xl font-semibold text-gray-900 dark:text-gray-100">
            {step === 'phone' ? 'Welcome back' : 'Enter verification code'}
          </h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {step === 'phone' 
              ? 'Enter your phone number to continue'
              : `We sent a code to +91 ${phone}`}
          </p>
        </div>

        {step === 'phone' ? (
          <form onSubmit={handleSendOTP} className="space-y-6">
            <div>
              <label className="label">Phone Number</label>
              <div className="flex">
                <span className="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400">
                  +91
                </span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  placeholder="9876543210"
                  className="input rounded-l-none"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={isLoading || phone.length !== 10}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isLoading ? 'Sending...' : 'Continue'}
              <ArrowRight size={18} />
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOTP} className="space-y-6">
            <div>
              <label className="label">Verification Code</label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value.slice(0, 6))}
                placeholder="000000"
                className="input text-center text-2xl tracking-widest"
                maxLength={6}
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || otp.length !== 6}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isLoading ? 'Verifying...' : 'Verify'}
              <CheckCircle size={18} />
            </button>
            <button
              type="button"
              onClick={handleSendOTP}
              disabled={countdown > 0}
              className="w-full text-sm text-primary-600 dark:text-primary-400 hover:underline disabled:opacity-50"
            >
              {countdown > 0 ? `Resend code in ${countdown}s` : 'Resend code'}
            </button>
          </form>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <LanguageSelector compact />
        </div>
      </div>
    </div>
  )
}