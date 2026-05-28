import { useAuthStore } from '../store/authStore'

export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    sendOTP,
    verifyOTP,
    logout,
    checkAuth,
    updateUser
  } = useAuthStore()

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    sendOTP,
    verifyOTP,
    logout,
    checkAuth,
    updateUser
  }
}