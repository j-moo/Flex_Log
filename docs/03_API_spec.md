# 03. API 명세

## 기본 정보

| 항목 | 값 |
| --- | --- |
| Base URL | `http://127.0.0.1:8000/api/v1` |
| 인증 방식 | JWT Bearer Token |
| 기본 권한 | 인증 필요 |
| 토큰 발급 | SimpleJWT |
| Access token 수명 | 60분 |
| Refresh token 수명 | 7일 |
| Refresh 정책 | rotation + blacklist |

인증이 필요한 요청은 다음 헤더를 포함합니다.

```http
Authorization: Bearer <access_token>
```

파일 업로드가 없는 API는 JSON을 기본으로 사용합니다. 소비 로그와 프로필 이미지는 `multipart/form-data`도 허용합니다.

## 응답과 오류 규칙

성공 응답은 endpoint별 serializer 필드 그대로 반환합니다. 검증 오류는 DRF 기본 형식으로 필드별 배열을 반환하고, 일반 오류는 `detail`을 사용합니다.

```json
{
  "detail": "오류 메시지"
}
```

```json
{
  "field_name": ["검증 오류 메시지"]
}
```

외부 API 의존 기능은 키 누락, timeout, 외부 장애 시 `503 Service Unavailable` 또는 서비스별 fallback 응답을 반환할 수 있습니다.

## Accounts

### POST `/accounts/signup/`

회원가입 후 즉시 로그인 상태로 사용할 수 있도록 access/refresh token을 반환합니다. 가입 성공 시 `Profile`도 함께 생성되며 기본 닉네임은 username입니다.

권한: `AllowAny`

요청:

```json
{
  "username": "hong",
  "email": "hong@example.com",
  "name": "홍길동",
  "password": "password123!",
  "password_confirm": "password123!"
}
```

검증:

- `username`은 대소문자 무시 중복 검사
- `email`은 소문자 정규화 후 대소문자 무시 중복 검사
- `password`와 `password_confirm` 일치 필요
- Django password validator 통과 필요

응답 `201`:

```json
{
  "message": "회원가입 완료 메시지",
  "user": {
    "id": 1,
    "username": "hong",
    "email": "hong@example.com",
    "name": "홍길동",
    "profile_image": null
  },
  "access": "access.jwt",
  "refresh": "refresh.jwt"
}
```

### POST `/accounts/login/`

SimpleJWT `TokenObtainPairView`를 사용합니다.

권한: `AllowAny`

요청:

```json
{
  "username": "hong",
  "password": "password123!"
}
```

응답 `200`:

```json
{
  "refresh": "refresh.jwt",
  "access": "access.jwt"
}
```

### POST `/accounts/token/refresh/`

refresh token으로 access token을 갱신합니다. refresh rotation이 켜져 있으므로 응답에 새 refresh token이 포함될 수 있습니다.

요청:

```json
{
  "refresh": "refresh.jwt"
}
```

### GET `/accounts/me/`

현재 인증 사용자의 기본 정보를 반환합니다.

응답 필드:

| 필드 | 설명 |
| --- | --- |
| `id` | 사용자 ID |
| `username` | 로그인 ID |
| `email` | 이메일 |
| `name` | 이름 |
| `profile_image` | 프로필 이미지 URL |

### POST `/accounts/logout/`

refresh token을 blacklist 처리합니다.

요청:

```json
{
  "refresh": "refresh.jwt"
}
```

응답: `204 No Content`

## Profiles

### GET `/profiles/me/`

내 프로필을 반환합니다. 프로필이 없으면 생성 후 조회합니다.

응답 주요 필드:

| 필드 | 설명 |
| --- | --- |
| `user_id`, `username`, `email`, `name` | 사용자 기본 정보 |
| `nickname`, `image`, `bio` | 프로필 정보 |
| `friend_count` | accepted 친구 관계 수 |
| `joined_products` | 활성 금융 상품 가입 목록 |
| `can_view_joined_products` | 가입 상품 조회 가능 여부 |

### PATCH `/profiles/me/`

닉네임, 이미지, 자기소개, 사용자 이름을 수정합니다.

요청 예시:

```json
{
  "name": "홍길동",
  "nickname": "절약왕",
  "bio": "소비 기록 중"
}
```

### GET `/profiles/<user_id>/`

다른 사용자의 공개 프로필을 조회합니다.

정책:

- 요청자가 본인이 아니면 `email` 필드를 제거합니다.
- `joined_products`는 본인이거나 accepted 친구일 때만 반환합니다.
- 친구가 아니면 `joined_products`는 빈 배열입니다.

## Friends

### GET `/friends/users/`

사용자 검색 또는 친구 추천 목록을 반환합니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `search` | username, name, profile.nickname 검색어 |
| `recommend` | `1`, `true`, `True`이면 친구의 친구 추천 |

정책:

- 본인은 검색 결과에서 제외됩니다.
- 이메일은 검색 대상이 아닙니다.
- 최대 20명까지 반환합니다.
- 추천은 mutual friend 수가 높은 순, username 오름차순입니다.

응답 사용자 필드:

| 필드 | 설명 |
| --- | --- |
| `id`, `username`, `name` | 사용자 기본 정보 |
| `display_name` | 닉네임 우선 표시 이름 |
| `profile_image` | 프로필 이미지 URL |
| `mutual_friend_count` | 공통 친구 수 |

### GET `/friends/`

내가 요청자 또는 수신자인 친구 관계를 최신 수정순으로 반환합니다.

응답 주요 필드:

| 필드 | 설명 |
| --- | --- |
| `id` | 친구 관계 ID |
| `user` | 요청자 |
| `friend` | 수신자 |
| `counterpart` | 현재 사용자 기준 상대 사용자 |
| `status` | `pending`, `accepted`, `rejected` |

### POST `/friends/`

친구 요청을 생성하고 수신자에게 알림을 생성합니다.

요청:

```json
{
  "friend": 2
}
```

검증:

- 자기 자신 요청 불가
- 같은 방향 또는 역방향 중복 관계 불가

### PATCH `/friends/<id>/`

친구 요청 수신자만 수락/거절할 수 있습니다.

요청:

```json
{
  "status": "accepted"
}
```

허용 값: `accepted`, `rejected`

### DELETE `/friends/<id>/`

친구 관계 또는 요청을 삭제합니다. 요청자와 수신자 모두 자신의 관계만 삭제할 수 있습니다.

## Expenses

### GET `/expenses/categories/`

소비 카테고리 목록입니다.

응답:

```json
[
  { "id": 1, "name": "식비" }
]
```

### GET `/expenses/`

내 소비 로그 전체 목록입니다. 본인 기록 보존을 위해 `expires_at` 만료 여부와 관계없이 반환합니다.

### POST `/expenses/`

소비 로그를 작성합니다.

요청 예시:

```json
{
  "category": 1,
  "title": "점심",
  "amount": 12000,
  "product_name": "김치찌개",
  "merchant": "역삼식당",
  "content": "팀 점심",
  "overlay_text": "오늘의 소비",
  "overlay_style": {
    "color": "#ffffff",
    "x": 20,
    "y": 20
  },
  "visibility": "friends",
  "hide_amount": false
}
```

`title`이 비어 있으면 본문 첫 줄, 오버레이 문구, 상품명, 구매처, 기본 제목 순으로 자동 생성됩니다.

미디어 업로드:

- 필드명: `media`
- 허용 확장자: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.mp4`, `.webm`
- 최대 크기: 10MB

응답 주요 필드:

| 필드 | 설명 |
| --- | --- |
| `user_id`, `username`, `display_name`, `profile_image` | 작성자 정보 |
| `category`, `category_name` | 카테고리 |
| `media` | 미디어 URL 또는 legacy data URL |
| `amount` | 금액, `hide_amount=true`이고 비작성자면 `null` |
| `visibility`, `hide_amount`, `is_visible`, `expires_at` | 공개 정책 |
| `is_feed_visible` | 피드 노출 가능 여부 |
| `like_count`, `comment_count`, `is_liked` | 반응 상태 |
| `can_edit` | 현재 사용자의 수정 가능 여부 |

### GET `/expenses/feed/`

피드 목록입니다.

포함 조건:

- 본인 또는 accepted 친구의 로그
- `visibility`가 `public` 또는 `friends`
- `is_visible=true`
- `expires_at > now`

쿼리:

| 이름 | 설명 |
| --- | --- |
| `limit` | 선택, 1~30 사이로 보정 |
| `offset` | 선택, 0 이상으로 보정 |

`limit` 또는 `offset`이 없으면 배열을 바로 반환합니다. 둘 중 하나라도 있으면 다음 형식으로 반환합니다.

```json
{
  "count": 42,
  "next_offset": 20,
  "results": []
}
```

### GET `/expenses/users/<user_id>/`

특정 사용자의 소비 로그를 조회합니다.

정책:

- `user_id`가 본인이면 모든 로그를 반환합니다.
- 타인이면 `accessible_log_queryset()` 기준으로 공개 범위, 친구 관계, 만료 여부를 적용합니다.

### GET `/expenses/<id>/`

소비 로그 상세입니다. 접근 가능한 로그만 조회됩니다.

### PATCH/PUT `/expenses/<id>/`

작성자 본인의 로그만 수정할 수 있습니다.

### DELETE `/expenses/<id>/`

작성자 본인의 로그만 삭제할 수 있습니다. 실수 삭제 방지를 위해 확인 코드와 확인 문구가 필요합니다.

요청:

```json
{
  "confirmation_code": "1234",
  "confirmation_text": "프론트엔드가 서버 요구 문구와 확인 코드를 합쳐 전달하는 삭제 확인 문구"
}
```

서버는 `confirmation_code`가 4자리 숫자인지와 `confirmation_text`가 서버 상수와 일치하는지 검사합니다.

### POST `/expenses/<id>/like/`

좋아요 토글 API입니다. 접근 가능한 로그에만 호출할 수 있습니다.

응답:

```json
{
  "liked": true,
  "like_count": 3
}
```

새 좋아요가 생성되면 작성자에게 grouped notification을 생성하거나 갱신합니다.

### GET/POST `/expenses/<id>/comments/`

접근 가능한 로그의 댓글 목록 또는 댓글 작성입니다.

작성 요청:

```json
{
  "content": "좋은 기록이에요"
}
```

댓글 생성 시 작성자에게 grouped notification을 생성하거나 갱신합니다.

### GET/PATCH/DELETE `/expenses/<id>/comments/<comment_id>/`

댓글 작성자 본인의 댓글만 상세/수정/삭제할 수 있습니다.

## Analysis

### GET `/analysis/monthly/`

특정 월의 소비 로그를 집계하고 `MonthlyAnalysis`를 upsert한 뒤 반환합니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `year` | 선택, 기본 현재 연도 |
| `month` | 선택, 기본 현재 월 |

응답:

```json
{
  "id": 1,
  "year": 2026,
  "month": 6,
  "total_amount": 420000,
  "category_summary": {
    "식비": 250000
  },
  "category_items": [
    {
      "name": "식비",
      "amount": 250000,
      "ratio": 59.5
    }
  ],
  "log_count": 12,
  "average_amount": 35000
}
```

### POST `/analysis/monthly/`

월별 AI 분석을 생성합니다. GMS API 응답을 JSON으로 파싱하고, 실패하면 서버 fallback 분석을 저장합니다.

요청:

```json
{
  "year": 2026,
  "month": 6,
  "monthly_income": 3000000
}
```

검증:

- `year`: 2000~2100
- `month`: 1~12
- `monthly_income`: 0 이상, 선택값

정책:

- `monthly_income`은 DB 전역 설정이 아니라 프론트엔드 사용자별 localStorage에서 읽어 요청마다 전달합니다.
- `monthly_income > 0`이면 수입 대비 소비 비율로 `risk_level`을 다시 계산합니다.
- 생성 성공 시 `ai_analysis` 알림을 생성합니다.

### GET `/analysis/monthly/latest/`

현재 사용자의 최신 AI 분석을 반환합니다. 없으면 `404`입니다.

### GET `/analysis/monthly/history/`

현재 사용자의 AI 분석 이력을 최신순으로 반환합니다.

## Finance Products

### GET `/finance/products/`

활성 금융 상품 목록입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `type` | `deposit` 또는 `saving` |
| `bank` | 금융회사명 부분 검색 |
| `term` | 저축 기간, 양의 정수 |
| `min_rate` | 기본 금리 또는 최고 우대 금리 최소값 |

검증:

- `type`은 `deposit`, `saving`만 허용
- `term`은 숫자이며 1 이상
- `min_rate`는 숫자

응답 상품 필드:

| 필드 | 설명 |
| --- | --- |
| `product_type`, `fin_prdt_cd`, `dcls_month` | 상품 식별 정보 |
| `kor_co_nm`, `fin_prdt_nm` | 금융회사와 상품명 |
| `join_way`, `mtrt_int`, `spcl_cnd`, `join_deny`, `join_member`, `etc_note` | 상품 조건 |
| `max_limit`, `is_active`, `fetched_at`, `created_at` | 한도와 상태 |
| `best_rate`, `best_option` | 최고 금리 기준 옵션 |
| `options` | 전체 기간/금리 옵션 |

### GET `/finance/products/deposits/`

`type=deposit`이 고정된 상품 목록입니다.

### GET `/finance/products/savings/`

`type=saving`이 고정된 상품 목록입니다.

### GET `/finance/products/<product_id>/`

활성 상품 상세입니다.

## Finance Subscriptions

### GET `/finance/subscriptions/`

현재 사용자의 금융 상품 가입/관심 목록입니다. 취소된 항목도 포함됩니다.

### POST `/finance/subscriptions/`

상품 옵션을 가입 상태로 저장합니다.

요청:

```json
{
  "option_id": 10
}
```

정책:

- 같은 옵션이 이미 `active`이면 `400`입니다.
- 과거에 취소한 옵션이면 새 row를 만들지 않고 `active`로 되살립니다.
- 응답에는 `product`와 `option` 상세가 함께 포함됩니다.

### POST `/finance/subscriptions/<subscription_id>/cancel/`

현재 사용자의 가입 항목을 취소합니다.

정책:

- 이미 취소된 항목이면 `400`입니다.
- 취소 성공 시 `status=cancelled`, `cancelled_at=now`가 됩니다.

## Commodities

### GET `/finance/commodities/`

원자재 목록입니다. 현재 모델 제약상 `GOLD`, `SILVER`만 허용됩니다.

### GET `/finance/commodities/<code>/prices/`

원자재 가격 데이터입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `start` | 선택, `YYYY-MM-DD` |
| `end` | 선택, `YYYY-MM-DD` |

응답:

```json
{
  "commodity": {
    "code": "GOLD",
    "name": "Gold",
    "unit": "USD/troy oz",
    "currency": "USD",
    "created_at": "2026-06-24T00:00:00+09:00"
  },
  "prices": [
    {
      "price_date": "2026-06-01",
      "open_price": "2300.000000",
      "high_price": "2350.000000",
      "low_price": "2280.000000",
      "close_price": "2320.000000",
      "source": "manual"
    }
  ]
}
```

### POST `/finance/commodities/prices/import/`

관리자 전용 가격 적재 API입니다.

권한: `IsAdminUser`

요청:

```json
{
  "code": "GOLD",
  "name": "Gold",
  "unit": "USD/troy oz",
  "currency": "USD",
  "source": "manual",
  "prices": [
    {
      "price_date": "2026-06-01",
      "close_price": "2320.000000",
      "open_price": "2300.000000",
      "high_price": "2350.000000",
      "low_price": "2280.000000"
    }
  ]
}
```

검증:

- `code`: `GOLD`, `SILVER`
- 같은 요청 안에서 `price_date` 중복 불가
- `high_price`는 비교 가격보다 작을 수 없음
- `low_price`는 비교 가격보다 클 수 없음

## YouTube

### GET `/finance/youtube/search/`

금융 영상 검색입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `q` | 검색어, 필수 |
| `max_results` | 선택, 숫자, 1~25로 보정, 기본 12 |

응답:

```json
{
  "query": "예금",
  "videos": []
}
```

### GET `/finance/youtube/videos/<video_id>/`

영상 상세 정보입니다.

## Banks

### GET `/finance/banks/nearby/`

Kakao Local API 기반 은행 검색입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `query` | 검색 기준 위치 또는 키워드, 필수 |
| `radius` | 반경 meter, 100~20000, 기본 2000 |

### GET `/finance/banks/route/`

Kakao Mobility API 기반 자동차 경로입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `x` | 목적지 경도 |
| `y` | 목적지 위도 |
| `name` | 목적지 이름, 선택 |

출발지는 서버 환경 변수 `KAKAO_ROUTE_ORIGIN_X`, `KAKAO_ROUTE_ORIGIN_Y`, `KAKAO_ROUTE_ORIGIN_NAME`을 사용합니다.

## Recommendations

### POST `/finance/recommend/`

현재 사용자의 소비 분석과 금융 상품 데이터를 기준으로 추천을 생성합니다.

정책:

- 추천 결과가 생성되면 `product_recommendation` 알림을 생성합니다.
- 응답은 생성된 추천 목록입니다.
- 최신 분석이 없으면 추천 유틸에서 가능한 fallback 흐름을 사용합니다.

### GET `/finance/recommend/latest/`

최신 추천 목록입니다.

정책:

- 생성 시각 최신순으로 훑으며 중복 상품을 제거합니다.
- 최대 5개까지 반환합니다.

### GET `/finance/recommend/history/`

전체 추천 이력입니다.

응답 추천 필드:

| 필드 | 설명 |
| --- | --- |
| `analysis_id`, `product_id`, `option_id` | 추천 근거와 대상 |
| `title`, `description`, `reason`, `action_text` | 사용자 노출 문구 |
| `bank_name`, `product_name`, `product_type` | 상품 스냅샷 |
| `save_trm`, `interest_rate`, `max_interest_rate` | 옵션 스냅샷 |
| `ai_comment`, `caution`, `priority`, `created_at` | 부가 설명 |

## Stocks

### GET `/finance/quote/`

Kiwoom 현재가 조회입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `symbol` | 종목 코드, 필수 |

`symbol` 누락은 `400`, Kiwoom 인증/통신 실패는 상황에 따라 `400` 또는 `503`입니다.

### GET `/finance/chart/`

Kiwoom 차트 조회입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `symbol` | 종목 코드, 필수 |
| `period` | 기간, 기본 `1m` |

프론트엔드는 차트 응답이 없거나 외부 API가 실패할 때 빈 상태 또는 mock/fallback 데이터를 표시할 수 있습니다.

### GET `/finance/stocks/`

현재 사용자의 보유 종목 목록입니다.

쿼리:

| 이름 | 설명 |
| --- | --- |
| `refresh` | `1`, `true`, `True`이면 현재가 갱신 시도 |

정책:

- 기본 목록 조회는 저장된 현재가를 그대로 반환합니다.
- `refresh`가 있을 때만 Kiwoom 현재가를 조회합니다.
- 현재가가 바뀌면 `stock_movement` 알림을 만들 수 있습니다.

### POST `/finance/stocks/`

보유 종목을 추가합니다.

요청:

```json
{
  "symbol": "005930",
  "name": "삼성전자",
  "quantity": 10,
  "average_price": "70000.00",
  "current_price": "71000.00",
  "memo": "장기 보유"
}
```

검증:

- `symbol`은 공백 제거 후 대문자 정규화
- `quantity`는 serializer 기준 정수 1 이상
- `average_price`, `current_price`는 0 이상

정책:

- 같은 사용자가 같은 `symbol`을 다시 추가하면 새 row를 만들지 않습니다.
- 기존 수량과 새 수량을 합산하고, 평균 단가를 가중 평균으로 재계산합니다.
- 중복 추가 응답은 `200`, 신규 생성은 `201`입니다.

응답 계산 필드:

| 필드 | 계산 |
| --- | --- |
| `invested_amount` | `quantity * average_price` |
| `valuation_amount` | `quantity * current_price` |
| `profit_loss` | `valuation_amount - invested_amount` |
| `profit_rate` | `profit_loss / invested_amount * 100` |

### GET/PATCH `/finance/stocks/<id>/`

현재 사용자의 보유 종목 상세 조회 또는 수정입니다.

### DELETE `/finance/stocks/<id>/`

보유 종목 삭제 또는 일부 수량 삭제입니다.

요청 없이 호출하면 전체 삭제:

```http
DELETE /finance/stocks/1/
```

일부 수량 삭제:

```json
{
  "quantity": 3
}
```

정책:

- `quantity`가 없으면 전체 삭제 후 `204`
- `quantity`가 보유 수량과 같으면 전체 삭제 후 `204`
- `quantity`가 보유 수량보다 작으면 수량 차감 후 `200`
- 삭제 수량은 양수 정수이며 보유 수량을 초과할 수 없습니다.

## Notifications

### GET `/notifications/`

현재 사용자 알림을 최신순 최대 80개 반환합니다.

응답 필드:

| 필드 | 설명 |
| --- | --- |
| `notification_type` | 알림 유형 코드 |
| `type_label` | Django choices 표시값 |
| `title`, `message` | 알림 문구 |
| `actor`, `actor_name` | 행위자 |
| `target_route`, `target_params`, `target_query` | 프론트 라우팅 정보 |
| `is_read`, `read_at`, `created_at` | 읽음 상태 |

### GET `/notifications/unread-count/`

읽지 않은 알림 수입니다.

응답:

```json
{
  "unread_count": 3
}
```

### PATCH `/notifications/<id>/read/`

현재 사용자의 특정 알림을 읽음 처리합니다. 이미 읽은 알림이면 변경하지 않습니다.

### POST `/notifications/read-all/`

현재 사용자의 읽지 않은 모든 알림을 읽음 처리합니다.

응답: `204 No Content`
