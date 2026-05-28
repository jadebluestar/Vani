import React, { useEffect, useState } from 'react'
import { Shield, Award, Download, Share2, ExternalLink, Loader2 } from 'lucide-react'
import { useCredentialStore } from '../store/credentialStore'
import BlockchainVerify from '../components/Credential/BlockchainVerify'
import ShareCredential from '../components/Credential/ShareCredential'

export default function CredentialsPage() {
  const { 
    credentials,
    verificationResult,
    loadCredentials, 
    generateCredential, 
    verifyCredential, 
    getShareLink, 
    downloadCredential, 
    mintBlockchain, 
    isLoading 
  } = useCredentialStore()
  
  const [selectedCert, setSelectedCert] = useState(null)
  const [shareUrl, setShareUrl] = useState(null)
  const [showShareModal, setShowShareModal] = useState(false)

  useEffect(() => {
    loadCredentials()
  }, [])

  const handleGenerate = async () => {
    await generateCredential()
    await loadCredentials()
  }

  const handleVerify = async (certificateId) => {
    await verifyCredential(certificateId)
  }

  const handleShare = async (id) => {
    const cert = credentials.find(c => c.id === id)
    const url = await getShareLink(id)
    setShareUrl(url)
    setSelectedCert(cert)
    setShowShareModal(true)
  }

  const handleMint = async (credentialId) => {
    await mintBlockchain(credentialId)
    await loadCredentials()
  }

  const closeShareModal = () => {
    setShowShareModal(false)
    setSelectedCert(null)
    setShareUrl(null)
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">My Credentials</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Earn and verify blockchain-secured certificates
        </p>
      </div>

      {/* Generate Button */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Ready for a certificate?</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Generate a credential based on your progress</p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Award size={16} />}
            Generate Certificate
          </button>
        </div>
      </div>

      {/* Verification Section */}
      <div className="mb-8">
        <BlockchainVerify onVerify={handleVerify} verificationResult={verificationResult} isLoading={isLoading} />
      </div>

      {/* My Certificates */}
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">My Certificates</h2>
      
      {isLoading && credentials.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading certificates...</div>
      ) : credentials.length === 0 ? (
        <div className="card text-center py-8">
          <Shield size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500 dark:text-gray-400">No certificates yet</p>
          <p className="text-sm text-gray-400 dark:text-gray-500">Complete practice sessions to earn your first certificate</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {credentials.map((cert) => (
            <div key={cert.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                  <Award size={20} className="text-primary-600 dark:text-primary-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                    {cert.title || 'Communication Skills Certificate'}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Issued: {new Date(cert.issued_at).toLocaleDateString()}
                  </p>
                  <div className="flex flex-wrap gap-3 mt-3">
                    <button
                      onClick={() => downloadCredential(cert.id)}
                      className="text-xs flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    >
                      <Download size={12} />
                      Download
                    </button>
                    <button
                      onClick={() => handleShare(cert.id)}
                      className="text-xs flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    >
                      <Share2 size={12} />
                      Share
                    </button>
                    {!cert.blockchain_tx_hash && (
                      <button
                        onClick={() => handleMint(cert.id)}
                        className="text-xs flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                      >
                        <ExternalLink size={12} />
                        Mint on Blockchain
                      </button>
                    )}
                  </div>
                  {cert.blockchain_tx_hash && (
                    <p className="text-xs text-green-600 dark:text-green-400 mt-2 truncate">
                      ✓ Verified on blockchain: {cert.blockchain_tx_hash.slice(0, 20)}...
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && shareUrl && selectedCert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={closeShareModal}>
          <div onClick={(e) => e.stopPropagation()}>
            <ShareCredential 
              certificate={selectedCert} 
              shareUrl={shareUrl}
              onCopy={() => {}}
              onClose={closeShareModal}
            />
          </div>
        </div>
      )}
    </div>
  )
}