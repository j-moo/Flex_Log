export const EXPENSE_DELETE_CONFIRM_TEXT =
  '정말 삭제하시겠습니까? 이거 삭제하면 로그 날아감 지인짜로오. AI 분석이랑 소비 통계에도 영향을 끼칩니다. 삭제된 피드는 복구할 수 없고, 월별 소비 분석과 추천 결과도 달라질 수 있습니다.'

export const DELETE_NAG_MESSAGES = [
  'AI: 손이 떨리시나요? 소비 로그도 울고 있습니다.',
  'AI: 한 글자 틀렸습니다. 지갑도 이렇게 새고 있었을지도...',
  'AI: 삭제는 신중하게. 카드값은 더 신중하게.',
  'AI: 로그는 지워도 소비는 지워지지 않습니다.',
  'AI: 방금 그 오타, 이번 달 소비 패턴만큼 수상합니다.',
  'AI: 지우기 전에 한 번만 더 생각해보시죠. 통계가 삐질 수도 있습니다.',
  'AI: 복붙은 막아뒀습니다. 진심으로 삭제할 거면 직접 입력해주세요.',
]

export const WALLET_ALERT_LIMIT = 100000

export const WALLET_ALERT_MESSAGES = [
  '지갑: 살려줘...',
  '카드가 오늘 유산소 운동 제대로 했습니다.',
  '소비 속도가 KTX급입니다. 잠시 브레이크를 밟아볼까요?',
  'AI가 분석 중 말을 잃었습니다.',
  '오늘의 지출, 생각보다 강력합니다.',
]

export const buildExpenseDeleteConfirmText = (code) =>
  `${EXPENSE_DELETE_CONFIRM_TEXT} 확인코드: ${code}`

export const normalizeExpenseDeleteConfirmText = (value) =>
  String(value ?? '').normalize('NFC').replace(/\s+/g, ' ').trim()

export const pickRandomMessage = (messages) =>
  messages[Math.floor(Math.random() * messages.length)] || ''
