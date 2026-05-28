import React, { useState } from 'react'
import { Shield, CheckCircle, XCircle, Loader2, Search } from 'lucide-react'

export default function BlockchainVerify({ onVerify, verificationResult, isLoading }) {
  const [certificateId, setCertificateId] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (certificateId.trim() && onVerify) {
      onVerify(certificateId.trim())
    }
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Shield size={20} className="text-primary-500" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Blockchain Verification</h3>
      </div>

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={certificateId}
            onChange={(e) => setCertificateId(e.target.value)}
            placeholder="Enter Certificate ID (e.g., VANI-ABC123)"
            className="input flex-1"
          />
          <button 
            type="submit" 
            disabled={isLoading || !certificateId.trim()} 
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
            Verify
          </button>
        </div>
      </form>

      {verificationResult && (
        <div className={`p-4 rounded-lg ${
          verificationResult.verified
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
            : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }`}>
          <div className="flex items-start gap-3">
            {verificationResult.verified ? (
              <CheckCircle size={24} className="text-green-500 flex-shrink-0" />
            ) : (
              <XCircle size={24} className="text-red-500 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p className={`font-semibold ${
                verificationResult.verified
                  ? 'text-green-700 dark:text-green-300'
                  : 'text-red-700 dark:text-red-300'
              }`}>
                {verificationResult.verified ? 'Certificate Verified' : 'Invalid Certificate'}
              </p>
              {verificationResult.verified && (
                <div className="mt-2 space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><span className="font-medium">Issued to:</span> {verificationResult.user_name}</p>
                  <p><span className="font-medium">Issued on:</span> {new Date(verificationResult.issued_at).toLocaleDateString()}</p>
                  <p><span className="font-medium">Level:</span> {verificationResult.level || 'Beginner'}</p>
                  <p><span className="font-medium">Skills:</span> {verificationResult.skills?.join(', ') || 'Communication Skills'}</p>
                  {verificationResult.blockchain_tx_hash && (
                    <p className="text-xs font-mono break-all">
                      <span className="font-medium">Blockchain TX:</span> {verificationResult.blockchain_tx_hash}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          All certificates are stored on the Solana blockchain. Each certificate has a unique ID that cannot be forged.
        </p>
      </div>
    </div>
  )
}