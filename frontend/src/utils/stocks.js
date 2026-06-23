export const stockCandidates = [
  { symbol: '005930', name: '삼성전자', market: 'KOSPI', price: 61200 },
  { symbol: '000660', name: 'SK하이닉스', market: 'KOSPI', price: 184500 },
  { symbol: '035420', name: 'NAVER', market: 'KOSPI', price: 203500 },
  { symbol: '035720', name: '카카오', market: 'KOSPI', price: 54200 },
  { symbol: '005380', name: '현대차', market: 'KOSPI', price: 244000 },
  { symbol: '000270', name: '기아', market: 'KOSPI', price: 108000 },
  { symbol: '051910', name: 'LG화학', market: 'KOSPI', price: 356000 },
  { symbol: '373220', name: 'LG에너지솔루션', market: 'KOSPI', price: 392000 },
  { symbol: '207940', name: '삼성바이오로직스', market: 'KOSPI', price: 812000 },
  { symbol: '068270', name: '셀트리온', market: 'KOSPI', price: 186000 },
  { symbol: '105560', name: 'KB금융', market: 'KOSPI', price: 78500 },
  { symbol: '055550', name: '신한지주', market: 'KOSPI', price: 47400 },
  { symbol: '323410', name: '카카오뱅크', market: 'KOSPI', price: 21400 },
  { symbol: '035900', name: 'JYP Ent.', market: 'KOSDAQ', price: 64200 },
  { symbol: '041510', name: '에스엠', market: 'KOSDAQ', price: 80300 },
]

export const findStockCandidate = (keyword) => {
  const value = String(keyword || '').trim().toLowerCase()
  if (!value) return null
  return stockCandidates.find((item) =>
    item.symbol.toLowerCase() === value ||
    item.name.toLowerCase() === value,
  ) || null
}

export const searchStockCandidates = (keyword) => {
  const value = String(keyword || '').trim().toLowerCase()
  if (!value) return stockCandidates.slice(0, 8)
  return stockCandidates.filter((item) =>
    item.symbol.toLowerCase().includes(value) ||
    item.name.toLowerCase().includes(value) ||
    item.market.toLowerCase().includes(value),
  )
}
