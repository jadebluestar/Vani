export const SUPPORTED_LANGUAGES = {
  kn: { name: 'Kannada', code: 'kn', nativeName: 'ಕನ್ನಡ', direction: 'ltr' },
  hi: { name: 'Hindi', code: 'hi', nativeName: 'हिन्दी', direction: 'ltr' },
  ta: { name: 'Tamil', code: 'ta', nativeName: 'தமிழ்', direction: 'ltr' },
  te: { name: 'Telugu', code: 'te', nativeName: 'తెలుగు', direction: 'ltr' },
  ml: { name: 'Malayalam', code: 'ml', nativeName: 'മലയാളം', direction: 'ltr' },
  bn: { name: 'Bengali', code: 'bn', nativeName: 'বাংলা', direction: 'ltr' },
  mr: { name: 'Marathi', code: 'mr', nativeName: 'मराठी', direction: 'ltr' },
  en: { name: 'English', code: 'en', nativeName: 'English', direction: 'ltr' }
}

export const getLanguageName = (code) => {
  return SUPPORTED_LANGUAGES[code]?.name || 'English'
}

export const getNativeLanguageName = (code) => {
  return SUPPORTED_LANGUAGES[code]?.nativeName || 'English'
}

export const isValidLanguage = (code) => {
  return !!SUPPORTED_LANGUAGES[code]
}

export const getLanguageOptions = () => {
  return Object.values(SUPPORTED_LANGUAGES).map(lang => ({
    value: lang.code,
    label: lang.name,
    nativeLabel: lang.nativeName
  }))
}