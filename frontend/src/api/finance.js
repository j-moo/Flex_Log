const mockStocks = [
  {
    id: 1,
    symbol: '005930',
    name: '삼성전자',
    quantity: 12,
    average_price: 64500,
    current_price: 61200,
  },
  {
    id: 2,
    symbol: '000660',
    name: 'SK하이닉스',
    quantity: 4,
    average_price: 178000,
    current_price: 184500,
  },
  {
    id: 3,
    symbol: '035420',
    name: 'NAVER',
    quantity: 6,
    average_price: 198000,
    current_price: 203500,
  },
  {
    id: 4,
    symbol: '005380',
    name: '현대차',
    quantity: 3,
    average_price: 251000,
    current_price: 244000,
  },
]

const delay = (value, ms = 250) =>
  new Promise((resolve) => {
    window.setTimeout(() => resolve(value), ms)
  })

const toStockView = (stock) => {
  const investedAmount = stock.quantity * stock.average_price
  const valuationAmount = stock.quantity * stock.current_price
  const profitLoss = valuationAmount - investedAmount
  const profitRate = investedAmount ? (profitLoss / investedAmount) * 100 : 0

  return {
    ...stock,
    invested_amount: investedAmount,
    valuation_amount: valuationAmount,
    profit_loss: profitLoss,
    profit_rate: profitRate,
  }
}

const buildChartPoints = (basePrice, minutes = 48) => {
  const points = []
  const now = new Date()
  now.setSeconds(0, 0)

  let price = basePrice * 0.985
  for (let index = minutes - 1; index >= 0; index -= 1) {
    const time = new Date(now.getTime() - index * 60 * 1000)
    const drift = Math.sin(index / 4) * basePrice * 0.0015
    const noise = (Math.random() - 0.48) * basePrice * 0.003
    price = Math.max(100, price + drift + noise)
    points.push({
      time: time.toISOString(),
      price: Math.round(price / 100) * 100,
    })
  }

  points[points.length - 1].price = basePrice
  return points
}

export const getStocks = () => delay(mockStocks.map(toStockView))

export const getChart = (symbol, period = '1m') => {
  const stock = mockStocks.find((item) => item.symbol === symbol) || mockStocks[0]
  return delay(buildChartPoints(stock.current_price, period === '1d' ? 30 : 48))
}

export const createRealtimePrice = (currentPrice) => {
  const movement = currentPrice * (Math.random() * 0.012 - 0.006)
  const nextPrice = Math.max(100, currentPrice + movement)
  return Math.round(nextPrice / 100) * 100
}
