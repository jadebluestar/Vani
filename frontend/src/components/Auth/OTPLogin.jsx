import React, { useState } from 'react'
import { Phone, ArrowRight, CheckCircle } from 'lucide-react'

export default function OTPLogin({ onSuccess, isLoading: externalLoading }) {
  const [step, setStep] = useState('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [countdown, setCountdown] = useState(0)
  const [internalLoading, setInternalLoading] = useState(false)

  const isLoading = externalLoading || internalLoading

  const handleSendOTP = async (e) => {
    e.preventDefault()
    if (phone.length !== 10) return
    
    setInternalLoading(true)
    try {
      const response = await fetch('/api/auth/otp/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: `+91${phone}` })
      })
      
      if (response.ok) {
        setStep('otp')
        setCountdown(60)
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) clearInterval(timer)
            return prev - 1
          })
        }, 1000)
      }
    } catch (error) {
      console.error('Failed to send OTP:', error)
    } finally {
      setInternalLoading(false)
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()
    if (otp.length !== 6) return
    
    setInternalLoading(true)
    try {
      const response = await fetch('/api/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: `+91${phone}`, otp })
      })
      
      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('vani_token', data.access_token)
        if (onSuccess) onSuccess(data.user)
      }
    } catch (error) {
      console.error('Failed to verify OTP:', error)
    } finally {
      setInternalLoading(false)
    }
  }

  if (step === 'phone') {
    return (
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
              disabled={isLoading}
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
    )
  }

  return (
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
          disabled={isLoading}
        />
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Code sent to +91 {phone}
        </p>
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
  )
}