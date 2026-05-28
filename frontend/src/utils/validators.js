export const validatePhone = (phone) => {
  const phoneRegex = /^[6-9]\d{9}$/
  return phoneRegex.test(phone)
}

export const validateOTP = (otp) => {
  const otpRegex = /^\d{6}$/
  return otpRegex.test(otp)
}

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const validateName = (name) => {
  return name && name.trim().length >= 2 && name.trim().length <= 50
}

export const validateAnswer = (answer) => {
  return answer && answer.trim().length >= 5 && answer.trim().length <= 2000
}

export const getValidationError = (field, value) => {
  switch (field) {
    case 'phone':
      if (!value) return 'Phone number is required'
      if (!validatePhone(value)) return 'Enter a valid 10-digit phone number'
      return null
    case 'otp':
      if (!value) return 'OTP is required'
      if (!validateOTP(value)) return 'OTP must be 6 digits'
      return null
    case 'name':
      if (!value) return 'Name is required'
      if (!validateName(value)) return 'Name must be 2-50 characters'
      return null
    case 'answer':
      if (!value) return 'Answer is required'
      if (!validateAnswer(value)) return 'Answer must be 5-2000 characters'
      return null
    default:
      return null
  }
}