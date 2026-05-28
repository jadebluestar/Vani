import React from 'react'
import { Award, Download, Share2, ExternalLink } from 'lucide-react'

export default function CertificateCard({ certificate, onDownload, onShare, onVerify }) {
  const getLevelColor = (level) => {
    switch(level) {
      case 'Beginner': return 'text-green-500 bg-green-50 dark:bg-green-900/20'
      case 'Intermediate': return 'text-blue-500 bg-blue-50 dark:bg-blue-900/20'
      case 'Advanced': return 'text-purple-500 bg-purple-50 dark:bg-purple-900/20'
      default: return 'text-gray-500 bg-gray-50 dark:bg-gray-700'
    }
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center flex-shrink-0">
          <Award size={24} className="text-primary-600 dark:text-primary-400" />
        </div>
        
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {certificate.title || 'Communication Skills Certificate'}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Issued: {new Date(certificate.issued_at).toLocaleDateString()}
              </p>
            </div>
            <span className={`text-xs px-2 py-1 rounded-full ${getLevelColor(certificate.level)}`}>
              {certificate.level || 'Beginner'}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-2 mt-3">
            <button
              onClick={() => onDownload(certificate.id)}
              className="btn-outline py-1 px-3 text-sm flex items-center gap-1"
            >
              <Download size={14} />
              Download
            </button>
            <button
              onClick={() => onShare(certificate.id)}
              className="btn-outline py-1 px-3 text-sm flex items-center gap-1"
            >
              <Share2 size={14} />
              Share
            </button>
            <button
              onClick={() => onVerify(certificate.certificate_id)}
              className="btn-outline py-1 px-3 text-sm flex items-center gap-1"
            >
              <ExternalLink size={14} />
              Verify
            </button>
          </div>
          
          {certificate.blockchain_tx_hash && (
            <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 break-all">
              Blockchain: {certificate.blockchain_tx_hash.slice(0, 20)}...
            </div>
          )}
        </div>
      </div>
    </div>
  )
}