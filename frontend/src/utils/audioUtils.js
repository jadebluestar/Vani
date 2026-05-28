export const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

export const base64ToBlob = (base64, mimeType = 'audio/webm') => {
  const byteCharacters = atob(base64)
  const byteArrays = []
  for (let i = 0; i < byteCharacters.length; i++) {
    byteArrays.push(byteCharacters.charCodeAt(i))
  }
  const byteArray = new Uint8Array(byteArrays)
  return new Blob([byteArray], { type: mimeType })
}

export const createAudioElement = (blob) => {
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  return { audio, url }
}

export const revokeAudioUrl = (url) => {
  URL.revokeObjectURL(url)
}

export const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export const getAudioDuration = (blob) => {
  return new Promise((resolve) => {
    const { audio, url } = createAudioElement(blob)
    audio.addEventListener('loadedmetadata', () => {
      resolve(audio.duration)
      revokeAudioUrl(url)
    })
    audio.addEventListener('error', () => {
      resolve(0)
      revokeAudioUrl(url)
    })
  })
}