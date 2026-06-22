# Flex-log API 명세

기본 경로는 `/api/v1`이며, 별도 표기가 없으면 JWT 인증이 필요하다.

## 인증

| Method | URL | 설명 |
|---|---|---|
| POST | `/accounts/logout/` | 전달한 refresh token 폐기 |

```json
{ "refresh": "refresh-token" }
```

## 금융상품 가입·해지

| Method | URL | 설명 |
|---|---|---|
| GET | `/finance/subscriptions/` | 내 가입·해지 상품 전체 조회 |
| POST | `/finance/subscriptions/` | 금융상품 옵션 가입 |
| POST | `/finance/subscriptions/{subscription_id}/cancel/` | 가입상품 해지 |

가입 요청:

```json
{
  "option_id": 1
}
```

동일한 활성 옵션은 중복 가입할 수 없다. 해지한 옵션에 다시 가입하면 기존 가입 건이 활성화되고 가입일이 갱신된다.

## 프로필 가입상품

| Method | URL | 설명 |
|---|---|---|
| GET | `/profiles/me/` | 내 프로필과 현재 가입상품 조회 |
| GET | `/profiles/{user_id}/` | 사용자 프로필과 현재 가입상품 조회 |

프로필 응답의 `joined_products`에는 `active` 상태인 가입상품만 반환한다.

## 금·은 시세

| Method | URL | 설명 | 권한 |
|---|---|---|---|
| GET | `/finance/commodities/` | 금·은 자산 목록 | 인증 사용자 |
| GET | `/finance/commodities/{code}/prices/` | 기간별 일별 시세 조회 | 인증 사용자 |
| POST | `/finance/commodities/prices/import/` | 일별 시세 일괄 업서트 | 관리자 |

시세 조회 query parameter:

- `start`: 시작일, `YYYY-MM-DD`
- `end`: 종료일, `YYYY-MM-DD`

적재 요청:

```json
{
  "code": "GOLD",
  "name": "금",
  "unit": "USD/troy oz",
  "currency": "USD",
  "source": "data-provider",
  "prices": [
    {
      "price_date": "2026-06-22",
      "open_price": "2300.000000",
      "high_price": "2350.000000",
      "low_price": "2290.000000",
      "close_price": "2340.000000"
    }
  ]
}
```

`code`는 `GOLD` 또는 `SILVER`만 허용한다. 같은 자산과 날짜가 이미 존재하면 해당 시세를 갱신한다.

저장된 원본 JSON은 `Backend/finance/data`에 있으며 다음 명령으로 일괄 적재한다.

```bash
python manage.py load_commodity_prices
```

## YouTube 관심 영상

| Method | URL | 설명 |
|---|---|---|
| GET | `/finance/youtube/search/?q={검색어}` | YouTube 영상 검색 |
| GET | `/finance/youtube/videos/{video_id}/` | 영상 상세 조회 |

백엔드 환경변수 `YOUTUBE_API_KEY`가 필요하다.

## 주변 은행

| Method | URL | 설명 |
|---|---|---|
| GET | `/finance/banks/nearby/?query={위치}&radius=2000` | 위치 좌표와 주변 은행 조회 |

`radius`는 100~20000m 범위다. 백엔드에는 `KAKAO_REST_API_KEY`, 프론트 지도 표시에는 `VITE_KAKAO_JS_KEY`가 필요하다.
