import React from 'react'
import { Link } from 'react-router-dom'
import { Mic, Users, Award, Shield, ArrowRight, Globe, MessageSquare, TrendingUp, CheckCircle } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/90 dark:bg-gray-900/90 backdrop-blur-md z-50 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">Vani</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors">
                Sign In
              </Link>
              <Link to="/login" className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2">
                Get Started
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            Find Your Voice.
            <span className="text-primary-600 dark:text-primary-400"> Speak with Confidence.</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10">
            AI-powered communication coach for first-gen learners. Practice in your language, 
            get real-time feedback, and build the confidence you need for interviews and daily conversations.
          </p>
          <Link to="/login" className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg text-lg font-medium inline-flex items-center gap-2 transition-colors">
            Start Practicing Free
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">Practice the way that works for you</h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Everything you need to improve your communication skills, from daily practice to expert guidance.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Mic className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">AI Speech Practice</h3>
              <p className="text-gray-600 dark:text-gray-400">Practice daily conversations with AI that understands your language.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Interview Prep</h3>
              <p className="text-gray-600 dark:text-gray-400">Real interview questions with AI feedback.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Peer Tutors</h3>
              <p className="text-gray-600 dark:text-gray-400">Connect with tutors who can help you practice.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Award className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Blockchain Credentials</h3>
              <p className="text-gray-600 dark:text-gray-400">Earn verifiable certificates for your skills.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Languages */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-primary-50 dark:bg-primary-900/30 px-4 py-2 rounded-full mb-6">
            <Globe className="w-4 h-4 text-primary-600" />
            <span className="text-sm text-primary-700 dark:text-primary-300">8 Languages Supported</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">Practice in your mother tongue</h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
            Start speaking in Kannada, Hindi, Tamil, Telugu, Malayalam, Bengali, Marathi, or English.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {['Kannada', 'Hindi', 'Tamil', 'Telugu', 'Malayalam', 'Bengali', 'Marathi', 'English'].map((lang) => (
              <span key={lang} className="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-full text-sm text-gray-700 dark:text-gray-300">
                {lang}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-primary-600 dark:bg-primary-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Start your journey today</h2>
          <p className="text-primary-100 mb-8">Join thousands of learners building confidence every day.</p>
          <Link to="/login" className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 rounded-lg font-medium inline-flex items-center gap-2 transition-colors">
            Create Free Account
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-500 dark:text-gray-400">
          <p>Vani — AI Communication Coach for First-Gen Learners</p>
        </div>
      </footer>
    </div>
  )
}