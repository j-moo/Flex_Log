# 07. 필수 기능 DB 설계

## 문서 목적

이 문서는 Flex Log의 필수 기능이 어떤 DB 모델과 API, 프론트엔드 화면으로 연결되는지 설명합니다. ERD가 전체 관계를 보여준다면, 이 문서는 기능 구현 관점에서 “왜 이 테이블이 필요하고 어떤 정책으로 쓰이는지”를 정리합니다.

## 전체 데이터 흐름

```text
User
  ├─ Profile
  ├─ Friend
  ├─ ExpenseLog ── Like / Comment
  │     └─ MonthlyAnalysis / MonthlyAIAnalysis
  │             └─ FinancialProductRecommendation
  ├─ UserFinancialProduct ── FinancialProductOption ── FinancialProduct
  ├─ StockHolding
  └─ Notification

Commodity ── CommodityPrice
```

핵심 원칙:

- 사용자별 데이터는 항상 `request.user` 기준으로 필터링합니다.
- 공개 범위 판정은 백엔드 queryset에서 최종 수행합니다.
- 이메일과 금융 상품 가입 목록은 조회자 권한에 따라 응답이 달라집니다.
- 외부 API 데이터는 필요한 내부 모델 또는 응답 DTO로 정규화합니다.

## 1. 회원가입, 로그인, 사용자 식별

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `accounts.User` | 로그인 계정, 이메일, 이름, 모든 사용자별 데이터의 기준 |
| `profiles.Profile` | 사용자 공개 프로필 |

### DB 설계

`User`는 Django `AbstractUser`를 확장합니다. `email`은 unique이며, `Profile`은 `User`와 OneToOne으로 연결됩니다.

회원가입 시 트랜잭션 안에서 다음 작업을 수행합니다.

1. `User` 생성
2. `Profile(user=user, nickname=username)` 생성
3. JWT refresh/access token 발급

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 회원가입 | `POST /api/v1/accounts/signup/` | `/signup` |
| 로그인 | `POST /api/v1/accounts/login/` | `/login` |
| 내 정보 | `GET /api/v1/accounts/me/` | 전역 account store |
| 로그아웃 | `POST /api/v1/accounts/logout/` | TopBar/MyPage |

### 설계 포인트

- refresh token은 blacklist 처리됩니다.
- access token은 Axios interceptor가 자동으로 붙입니다.
- 프론트엔드는 토큰을 sessionStorage에 저장합니다.

## 2. 프로필과 공개 정보

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `profiles.Profile` | 닉네임, 이미지, 자기소개 |
| `friends.Friend` | 가입 상품 공개 여부 판정 |
| `finance.UserFinancialProduct` | 프로필에서 보여줄 가입 상품 |

### 응답 정책

프로필 serializer는 조회자에 따라 응답을 바꿉니다.

| 데이터 | 본인 | accepted 친구 | 그 외 |
| --- | --- | --- | --- |
| 이메일 | 노출 | 비노출 | 비노출 |
| 가입 금융 상품 | 노출 | 노출 | 빈 배열 |
| 친구 수 | 노출 | 노출 | 노출 |
| 닉네임/이미지/bio | 노출 | 노출 | 노출 |

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 내 프로필 조회/수정 | `GET/PATCH /api/v1/profiles/me/` | `/profile`, `/mypage` |
| 타인 프로필 조회 | `GET /api/v1/profiles/<user_id>/` | `/profile/:userId` |

### 설계 포인트

- 프로필 이미지는 `ImageField(upload_to='profiles/')`로 저장합니다.
- 사용자 이름 `name`은 Profile serializer에서 `source='user.name'`으로 수정됩니다.
- 이메일은 serializer의 `to_representation()`에서 제거합니다.

## 3. 친구 관계

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `friends.Friend` | 요청자/수신자/상태 저장 |
| `notifications.Notification` | 친구 요청 알림 |

### 상태

| 상태 | 의미 |
| --- | --- |
| `pending` | 요청 발송 후 대기 |
| `accepted` | 친구 관계 성립 |
| `rejected` | 요청 거절 |

### 제약 조건

- 자기 자신에게 요청할 수 없습니다.
- 같은 방향 `(user, friend)` 요청은 중복될 수 없습니다.
- 역방향 관계도 `clean()`에서 막습니다.
- 수락/거절은 요청 수신자만 할 수 있습니다.

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 사용자 검색 | `GET /api/v1/friends/users/?search=...` | `/friends` |
| 친구 추천 | `GET /api/v1/friends/users/?recommend=1` | `/friends` |
| 친구 목록 | `GET /api/v1/friends/` | `/friends` |
| 요청 생성 | `POST /api/v1/friends/` | `/friends` |
| 수락/거절 | `PATCH /api/v1/friends/<id>/` | `/friends`, 알림 |
| 삭제 | `DELETE /api/v1/friends/<id>/` | `/friends` |

### 설계 포인트

- 친구 검색은 email을 사용하지 않습니다.
- accepted 관계만 소비 로그 친구 공개 범위와 프로필 가입 상품 공개에 사용됩니다.
- 친구 요청 생성 시 `friend_request` 알림을 만듭니다.

## 4. 소비 로그와 피드

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `expenses.Category` | 소비 분류 |
| `expenses.ExpenseLog` | 소비 기록 본문 |
| `expenses.Like` | 좋아요 |
| `expenses.Comment` | 댓글 |
| `notifications.Notification` | 좋아요/댓글 알림 |

### ExpenseLog 설계

`ExpenseLog`는 소비 금액과 공개 정책을 함께 저장합니다.

| 필드 | 이유 |
| --- | --- |
| `amount` | 월별 분석과 피드 표시의 핵심 값 |
| `category` | 카테고리별 집계 기준 |
| `media`, `media_data` | 새 파일 저장과 legacy data URL 호환 |
| `visibility` | 전체 공개/친구 공개/비공개 |
| `hide_amount` | 소비 맥락은 공유하되 금액은 숨기는 기능 |
| `expires_at` | 피드 노출 24시간 제한 |
| `is_visible` | 서버에서 강제로 숨길 수 있는 플래그 |
| `overlay_style` | 프론트 이미지 오버레이 설정 저장 |

### 공개 범위 판정

피드와 타인 조회는 다음 조건을 사용합니다.

```text
본인 로그
OR public + is_visible + expires_at > now
OR accepted 친구 로그 + (public 또는 friends) + is_visible + expires_at > now
```

목록별 차이:

| API | 정책 |
| --- | --- |
| `GET /expenses/` | 내 로그 전체, 만료 포함 |
| `GET /expenses/feed/` | 본인/친구 로그 중 피드 노출 가능한 것만 |
| `GET /expenses/users/<user_id>/` | 본인이면 전체, 타인이면 접근 가능한 것만 |
| `GET /expenses/<id>/` | 접근 가능한 로그만 |
| `PATCH/DELETE /expenses/<id>/` | 작성자 본인만 |

### 좋아요와 댓글

- `Like`는 `(user, log)` unique로 중복 좋아요를 막습니다.
- 좋아요 API는 토글 방식입니다.
- 댓글은 접근 가능한 로그에만 작성할 수 있습니다.
- 댓글 수정/삭제는 댓글 작성자 본인만 가능합니다.
- 좋아요/댓글은 grouped notification으로 묶어 알림 과다 생성을 줄입니다.

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 카테고리 | `GET /expenses/categories/` | 로그 작성 화면 |
| 내 로그 목록 | `GET /expenses/` | `/logs` |
| 로그 작성 | `POST /expenses/` | `/logs/new` |
| 로그 상세 | `GET /expenses/<id>/` | `/logs/:id` |
| 로그 수정 | `PATCH /expenses/<id>/` | `/logs/:id/edit` |
| 피드 | `GET /expenses/feed/` | `/feed` |
| 좋아요 | `POST /expenses/<id>/like/` | 피드/상세 |
| 댓글 | `/expenses/<id>/comments/` | 상세 |

## 5. 월별 소비 분석

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `analysis.MonthlyAnalysis` | 기본 집계 |
| `analysis.MonthlyAIAnalysis` | AI 분석 결과 |
| `expenses.ExpenseLog` | 집계 원천 |
| `notifications.Notification` | 분석 완료 알림 |

### 집계 기준

월별 분석은 `ExpenseLog.created_at`을 기준으로 지정 월의 본인 로그만 집계합니다.

기본 집계:

```json
{
  "total_amount": 420000,
  "log_count": 12,
  "average_amount": 35000,
  "category_summary": {
    "식비": {
      "total": 250000,
      "count": 8
    }
  }
}
```

저장 방식:

- `MonthlyAnalysis.category_summary`: `{카테고리명: 금액}`
- `MonthlyAIAnalysis.category_summary`: `{카테고리명: {total, count}}`

### 월 수입 설계

월 수입은 DB 모델에 저장하지 않습니다. 프론트엔드가 사용자별 localStorage key로 저장하고, AI 분석 요청 시 `monthly_income`으로 전달합니다.

```text
flexlog.monthlyIncome.<userId>
```

이 설계의 장점:

- 같은 브라우저의 여러 계정 값이 섞이지 않습니다.
- 분석 요청마다 명시적으로 전달되어 서버가 공용 설정을 잘못 읽을 위험이 없습니다.

한계:

- 다른 브라우저나 기기에서는 동기화되지 않습니다.
- 서버 기반 설정이 필요해지면 별도 `UserSetting` 모델을 추가해야 합니다.

### AI 분석과 fallback

POST `/analysis/monthly/`는 다음 순서로 동작합니다.

1. 요청 연/월 검증
2. 해당 월 소비 로그 집계
3. `MonthlyAnalysis` upsert
4. GMS API 분석 요청
5. 실패 시 fallback 분석 생성
6. `MonthlyAIAnalysis` 저장
7. `ai_analysis` 알림 생성

위험도:

- `monthly_income > 0`: 소비/수입 비율 기준
- 수입 미입력: 총 소비 금액 기준 fallback

## 6. 금융 상품과 가입 상태

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `finance.FinancialProduct` | 상품 기본 정보 |
| `finance.FinancialProductOption` | 기간/금리 옵션 |
| `finance.UserFinancialProduct` | 사용자 가입 상태 |

### 상품/옵션 분리 이유

금융 상품 하나는 6개월, 12개월, 24개월처럼 여러 기간과 금리 조건을 가집니다. 따라서 상품 기본 정보와 옵션을 분리해야 검색, 추천, 가입이 자연스럽습니다.

```text
FinancialProduct 1 ── N FinancialProductOption
```

### 가입 상태

`UserFinancialProduct`는 실제 금융기관 가입이 아니라 서비스 내부 관심/가입 관리입니다.

| 상태 | 의미 |
| --- | --- |
| `active` | 사용자가 가입/관심 상태로 둔 상품 옵션 |
| `cancelled` | 사용자가 취소한 상품 옵션 |

상태 일관성:

- `active`이면 `cancelled_at`은 null
- `cancelled`이면 `cancelled_at`은 필수

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 상품 목록 | `GET /finance/products/` | `/finance/products` |
| 예금 목록 | `GET /finance/products/deposits/` | `/finance/products` |
| 적금 목록 | `GET /finance/products/savings/` | `/finance/products` |
| 상품 상세 | `GET /finance/products/<id>/` | 상품 상세 UI |
| 가입 목록 | `GET /finance/subscriptions/` | 프로필/금융 화면 |
| 가입 | `POST /finance/subscriptions/` | 상품 카드 |
| 취소 | `POST /finance/subscriptions/<id>/cancel/` | 상품 카드 |

### 검증 포인트

- `term` 필터는 숫자이며 1 이상이어야 합니다.
- `min_rate`는 숫자여야 합니다.
- `option_id`는 활성 상품의 옵션이어야 합니다.
- 이미 active인 옵션은 중복 가입할 수 없습니다.

## 7. 금융 상품 추천

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `finance.FinancialProductRecommendation` | 추천 결과 저장 |
| `analysis.MonthlyAIAnalysis` | 추천 근거 |
| `finance.FinancialProduct` | 추천 상품 |
| `finance.FinancialProductOption` | 추천 옵션 |
| `notifications.Notification` | 추천 생성 알림 |

### 설계 이유

추천 결과는 단순히 product id만 저장하지 않습니다. 추천 당시의 은행명, 상품명, 상품 유형, 기간, 금리를 snapshot으로 저장합니다. 상품 원본 데이터가 이후 바뀌어도 과거 추천 내용을 이해할 수 있게 하기 위해서입니다.

### 추천 생성 흐름

1. 사용자가 `/finance/recommend/` 요청
2. 최신 월별 AI 분석 조회
3. 활성 금융 상품과 옵션 조회
4. 소비 패턴과 상품 조건을 기준으로 추천 생성
5. 추천 결과 저장
6. 상품 추천 알림 생성

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 추천 생성 | `POST /finance/recommend/` | `/finance/recommend` |
| 최신 추천 | `GET /finance/recommend/latest/` | 금융 허브/추천 화면 |
| 추천 이력 | `GET /finance/recommend/history/` | 추천 화면 |

## 8. 원자재 가격

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `finance.Commodity` | 원자재 마스터 |
| `finance.CommodityPrice` | 일자별 가격 |

### 설계

`Commodity.code`는 `GOLD`, `SILVER`만 허용합니다. 가격은 `CommodityPrice`에 일자별로 저장하고, 같은 원자재의 같은 날짜는 하나만 존재합니다.

```text
Commodity 1 ── N CommodityPrice
```

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 원자재 목록 | `GET /finance/commodities/` | `/finance/commodities` |
| 가격 조회 | `GET /finance/commodities/<code>/prices/` | `/finance/commodities` |
| 가격 import | `POST /finance/commodities/prices/import/` | 관리자/API 전용 |

### 검증 포인트

- 날짜 형식은 `YYYY-MM-DD`
- `start <= end`
- 가격은 0 이상
- `high_price`와 `low_price`의 상하 관계 검증

## 9. YouTube와 은행 검색

### 저장 정책

YouTube 영상 검색과 Kakao 은행 검색/경로는 현재 별도 영속 모델을 두지 않습니다. 외부 API 응답을 바로 정규화해 프론트엔드에 반환합니다.

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| YouTube 검색 | `GET /finance/youtube/search/?q=...` | `/finance/youtube` |
| YouTube 상세 | `GET /finance/youtube/videos/<video_id>/` | `/finance/youtube/:videoId` |
| 은행 검색 | `GET /finance/banks/nearby/?query=...` | `/finance/banks` |
| 은행 경로 | `GET /finance/banks/route/?x=...&y=...` | `/finance/banks` |

### 설계 포인트

- 외부 API 키가 없거나 실패하면 `503`을 반환합니다.
- 은행 검색 반경은 100~20000m 사이로 제한합니다.
- 길찾기 출발지는 서버 환경 변수로 관리합니다.

## 10. 주식 보유 종목

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `finance.StockHolding` | 사용자별 보유 주식 |
| `notifications.Notification` | 주가 변동 알림 |

### DB 설계

사용자와 종목 코드를 기준으로 unique를 둡니다.

```text
unique(user, symbol)
```

같은 종목을 다시 추가하면 새 row를 만들지 않고 기존 row를 갱신합니다.

평균 단가 재계산:

```text
new_quantity = old_quantity + added_quantity
new_average_price =
  (old_quantity * old_average_price + added_quantity * added_average_price)
  / new_quantity
```

계산 응답:

| 응답 필드 | 계산식 |
| --- | --- |
| `invested_amount` | `quantity * average_price` |
| `valuation_amount` | `quantity * current_price` |
| `profit_loss` | `valuation_amount - invested_amount` |
| `profit_rate` | `profit_loss / invested_amount * 100` |

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 현재가 | `GET /finance/quote/?symbol=...` | `/stocks` |
| 차트 | `GET /finance/chart/?symbol=...&period=...` | `/stocks` |
| 보유 목록 | `GET /finance/stocks/` | `/stocks` |
| 현재가 갱신 목록 | `GET /finance/stocks/?refresh=1` | 필요 시 |
| 추가 | `POST /finance/stocks/` | `/stocks` |
| 수정 | `PATCH /finance/stocks/<id>/` | `/stocks` |
| 삭제/수량 차감 | `DELETE /finance/stocks/<id>/` | `/stocks` |

### 설계 포인트

- 목록 조회는 기본적으로 외부 API를 호출하지 않습니다.
- `refresh=1`일 때만 현재가 갱신을 시도합니다.
- 현재가가 바뀌면 주가 변동 알림을 생성할 수 있습니다.
- 차트는 DB 저장이 아니라 Kiwoom API 응답을 사용합니다.
- 프론트엔드는 종목 추가/변경 후 차트를 재생성해 빈 그래프를 방지합니다.

## 11. 알림

### 관련 모델

| 모델 | 용도 |
| --- | --- |
| `notifications.Notification` | 사용자 알림 |

### 알림 유형

| 유형 | 생성 시점 |
| --- | --- |
| `friend_request` | 친구 요청 생성 |
| `like` | 소비 로그 좋아요 |
| `comment` | 소비 로그 댓글 |
| `ai_analysis` | 월별 AI 분석 완료 |
| `product_recommendation` | 금융 상품 추천 생성 |
| `stock_movement` | 주식 현재가 변경 감지 |

### 라우팅 설계

알림에는 프론트엔드 이동 정보를 함께 저장합니다.

| 필드 | 용도 |
| --- | --- |
| `target_route` | Vue Router route name |
| `target_params` | route params |
| `target_query` | route query |

예:

```json
{
  "target_route": "log-detail",
  "target_params": { "id": 10 },
  "target_query": {}
}
```

### API와 화면

| 기능 | API | 화면 |
| --- | --- | --- |
| 알림 목록 | `GET /notifications/` | `/notifications`, TopBar |
| unread count | `GET /notifications/unread-count/` | TopBar |
| 개별 읽음 | `PATCH /notifications/<id>/read/` | 알림 목록 |
| 전체 읽음 | `POST /notifications/read-all/` | 알림 목록 |

## 12. 프론트엔드 저장소 설계

### Pinia account store

| 값 | 저장 위치 | 이유 |
| --- | --- | --- |
| `accessToken` | sessionStorage | 브라우저 세션 범위 인증 |
| `refreshToken` | sessionStorage | access token 갱신 |
| `user` | sessionStorage | 새로고침 후 사용자 상태 복원 |

### 월 수입 저장소

| 값 | 저장 위치 | 이유 |
| --- | --- | --- |
| `monthlyIncome` | localStorage, 사용자별 key | 분석 입력값을 계정별로 유지 |

legacy migration:

1. 새 key에 값이 없으면 기존 `flexlog.monthlyIncome`을 확인합니다.
2. legacy 값이 있으면 현재 사용자 key로 옮깁니다.
3. legacy key를 삭제합니다.

## 13. 운영 전 확인해야 할 DB 관련 사항

| 항목 | 현재 | 운영 권장 |
| --- | --- | --- |
| DB | SQLite | PostgreSQL 등 운영 DB |
| 미디어 | 로컬 `MEDIA_ROOT` | S3 호환 오브젝트 스토리지 |
| 정적 파일 | Django 기본 설정 | 별도 정적 파일 배포 |
| 외부 API 로그 | 기능별 처리 | 공통 logging/monitoring |
| pagination | 일부 endpoint만 | 공통 pagination |
| 사용자 설정 | 월 수입 client 저장 | 필요 시 서버 모델 추가 |

## 검증 기준

| 기능 | 확인 내용 |
| --- | --- |
| 인증 | 회원가입 시 User/Profile 생성, JWT 발급 |
| 프로필 | 타인 프로필 이메일 비노출 |
| 친구 | 자기 요청/중복 요청 방지, 수신자만 상태 변경 |
| 소비 로그 | 공개 범위, 만료, 금액 숨김, 삭제 확인 |
| 피드 | 친구 관계와 `expires_at` 조건 적용 |
| 분석 | 사용자별 로그만 집계, 월 수입 반영 |
| 금융 상품 | term/min_rate 검증, 가입 상태 일관성 |
| 추천 | 최신 분석 기반 추천, snapshot 필드 저장 |
| 원자재 | 날짜/가격 검증, 관리자 import |
| 주식 | unique symbol, 평균 단가 재계산, 부분 삭제 |
| 알림 | 사용자별 조회, 읽음 처리, dedupe key |
