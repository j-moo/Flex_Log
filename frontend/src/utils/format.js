export const formatAmount = (amount) => {
  if (amount === null || amount === undefined || amount === '') return '금액 비공개'
  return `${Math.round(Number(amount || 0)).toLocaleString('ko-KR')}원`
}

export const formatNumber = (value, digits = 0) =>
  Number(value || 0).toLocaleString('ko-KR', {
    maximumFractionDigits: digits,
  })

export const formatRate = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  return `${Number(value).toFixed(2)}%`
}

export const formatDate = (value) => {
  if (!value) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export const formatShortDate = (value) => {
  if (!value) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))
}

export const isVideo = (url) => {
  const value = String(url || '').toLowerCase()
  return value.startsWith('data:video/') || /\.(mp4|webm|ogg)(?:[?#].*)?$/i.test(value)
}
