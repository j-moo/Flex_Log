const STORAGE_KEY = 'flexlog.monthlyIncome'
export const MONTHLY_INCOME_EVENT = 'flexlog:monthly-income-updated'

export const normalizeMonthlyIncome = (value) => {
  const amount = Math.round(Number(value || 0))
  return Number.isFinite(amount) && amount > 0 ? amount : 0
}

export const getMonthlyIncome = () => {
  if (typeof window === 'undefined') return 0
  return normalizeMonthlyIncome(window.localStorage.getItem(STORAGE_KEY))
}

export const setMonthlyIncome = (value) => {
  const amount = normalizeMonthlyIncome(value)
  if (typeof window === 'undefined') return amount
  window.localStorage.setItem(STORAGE_KEY, String(amount))
  window.dispatchEvent(new CustomEvent(MONTHLY_INCOME_EVENT, { detail: amount }))
  return amount
}
