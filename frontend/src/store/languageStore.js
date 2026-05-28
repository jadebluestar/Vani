import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useLanguageStore = create(
  persist(
    (set) => ({
      language: 'kn',
      setLanguage: (language) => set({ language }),
      getLanguageName: (code) => {
        const names = {
          kn: 'Kannada',
          hi: 'Hindi',
          ta: 'Tamil',
          te: 'Telugu',
          ml: 'Malayalam',
          bn: 'Bengali',
          mr: 'Marathi',
          en: 'English'
        }
        return names[code] || 'English'
      }
    }),
    {
      name: 'vani-language',
    }
  )
)