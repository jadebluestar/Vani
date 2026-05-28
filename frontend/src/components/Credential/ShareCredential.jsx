import React, { useState } from 'react'

export default function ShareCredential({ certificate, shareUrl, onCopy, onClose }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    if (shareUrl) {
      await navigator.clipboard.writeText(shareUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const shareLinks = [
    {
      name: 'LinkedIn',
      icon: '🔗',
      color: 'bg-[#0077b5]',
      url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl || '')}`
    },
    {
      name: 'Twitter',
      icon: '🐦',
      color: 'bg-[#1DA1F2]',
      url: `https://twitter.com/intent/tweet?text=I just earned my certificate on Vani!&url=${encodeURIComponent(shareUrl || '')}`
    },
    {
      name: 'Email',
      icon: '📧',
      color: 'bg-gray-600',
      url: `mailto:?subject=I earned a certificate on Vani&body=Check out my certificate: ${shareUrl}`
    }
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-primary-500">📤</span>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Share Your Achievement</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <span className="text-gray-500">✕</span>
        </button>
      </div>

      <div className="p-4">
        <div className="mb-4">
          <label className="label">Shareable Link</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={shareUrl || ''}
              readOnly
              className="input flex-1 bg-gray-50 dark:bg-gray-700 text-sm"
            />
            <button onClick={handleCopy} className="btn-outline">
              {copied ? '✓' : '📋'}
            </button>
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm text-gray-600 dark:text-gray-400">Share on social media:</p>
          <div className="flex gap-3">
            {shareLinks.map((link) => (
              <a
                key={link.name}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`${link.color} text-white p-2 rounded-lg hover:opacity-90 transition-opacity flex items-center gap-2`}
              >
                <span className="text-base">{link.icon}</span>
                <span className="text-sm hidden sm:inline">{link.name}</span>
              </a>
            ))}
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Your certificate is verified. Anyone can verify its authenticity.
          </p>
        </div>
      </div>
    </div>
  )
}