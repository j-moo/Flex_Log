const LEGACY_STORAGE_KEY = 'flexlog.monthlyIncome'
const STORAGE_PREFIX = 'flexlog.monthlyIncome'
export const MONTHLY_INCOME_MAX = 100000000
export const MONTHLY_INCOME_EVENT = 'flexlog:monthly-income-updated'

export const validateMonthlyIncome = (value) => {
  const rawValue = String(value ?? '').trim()
  if (!rawValue) return { valid: true, amount: 0 }

  const amount = Math.round(Number(rawValue))
  if (!Number.isFinite(amount) || amount < 0) {
    return {
      valid: false,
      amount: 0,
      message: '월 수입은 0원 이상의 숫자로 입력해 주세요.',
    }
  }
  if (amount > MONTHLY_INCOME_MAX) {
    return {
      valid: false,
      amount,
      message: `월 수입은 최대 ${MONTHLY_INCOME_MAX.toLocaleString('ko-KR')}원까지 입력할 수 있습니다.`,
    }
  }
  return { valid: true, amount }
}

export const normalizeMonthlyIncome = (value) => {
  const result = validateMonthlyIncome(value)
  return result.valid && result.amount > 0 ? result.amount : 0
}

const storageKeyForUser = (userId) => {
  const normalizedUserId = String(userId || '').trim()
  return normalizedUserId ? `${STORAGE_PREFIX}.${normalizedUserId}` : null
}

export const getMonthlyIncome = (userId) => {
  if (typeof window === 'undefined') return 0
  const storageKey = storageKeyForUser(userId)
  if (!storageKey) return 0

  const storedValue = window.localStorage.getItem(storageKey)
  if (storedValue !== null) return normalizeMonthlyIncome(storedValue)

  const legacyValue = window.localStorage.getItem(LEGACY_STORAGE_KEY)
  const legacyAmount = normalizeMonthlyIncome(legacyValue)
  if (legacyValue !== null) {
    if (legacyAmount) window.localStorage.setItem(storageKey, String(legacyAmount))
    window.localStorage.removeItem(LEGACY_STORAGE_KEY)
  }
  return legacyAmount
}

export const setMonthlyIncome = (value, userId) => {
  const amount = normalizeMonthlyIncome(value)
  if (typeof window === 'undefined') return amount
  const storageKey = storageKeyForUser(userId)
  if (!storageKey) return amount
  if (amount) {
    window.localStorage.setItem(storageKey, String(amount))
  } else {
    window.localStorage.removeItem(storageKey)
  }
  window.dispatchEvent(new CustomEvent(MONTHLY_INCOME_EVENT, { detail: { amount, userId } }))
  return amount
}
