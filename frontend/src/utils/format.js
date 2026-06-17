export const formatAmount = (amount) =>
  `${Number(amount || 0).toLocaleString('ko-KR')}원`

export const formatDate = (value) => {
  if (!value) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export const isVideo = (url) => /\.(mp4|webm)(?:\?|$)/i.test(url || '')
