# Flex Log

Flex Log는 소비 기록을 소셜 피드처럼 남기고, 그 기록을 월별 소비 분석과 금융 상품 추천, 주식 보유 현황으로 연결하는 개인 금융 관리 서비스입니다. 백엔드는 Django REST Framework, 프론트엔드는 Vue 3와 Vite로 구성되어 있습니다.

## 서비스가 해결하는 문제

일반적인 가계부는 숫자를 정리하는 데 집중하지만, 소비가 발생한 맥락과 이후 행동까지 연결하기 어렵습니다. Flex Log는 사용자가 소비 순간을 사진, 금액, 카테고리, 공개 범위와 함께 기록하고, 친구와 일부 기록을 공유하며, 누적된 데이터를 바탕으로 월별 피드백과 금융 상품 추천을 받을 수 있게 합니다.

## 주요 기능

| 영역 | 기능 |
| --- | --- |
| 인증 | 회원가입, 로그인, 로그아웃, JWT refresh rotation |
| 프로필 | 닉네임, 이미지, 자기소개, 친구 수, 가입 금융 상품 공개 |
| 친구 | 사용자 검색, 친구 추천, 요청/수락/거절/삭제 |
| 소비 로그 | 작성, 수정, 삭제, 미디어 업로드, 공개 범위, 금액 숨김 |
| 피드 | 본인과 친구의 공개 소비 로그, 만료 정책, 좋아요, 댓글 |
| 분석 | 월별 소비 집계, 카테고리 비중, AI 분석, 위험도 |
| 금융 상품 | 예금/적금 상품 조회, 기간/은행/금리 필터, 가입 상태 관리 |
| 추천 | 소비 분석 기반 금융 상품 추천과 추천 이력 |
| 원자재 | 금/은 가격 조회와 관리자 가격 import |
| 외부 콘텐츠 | YouTube 금융 영상 검색, Kakao 은행 검색/경로 |
| 주식 | 보유 종목 추가/수정/삭제, 현재가, 평가금액, 손익률, 차트 |
| 알림 | 친구 요청, 좋아요, 댓글, AI 분석, 상품 추천, 주가 변동 |

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Backend | Python, Django 5, Django REST Framework |
| Auth | djangorestframework-simplejwt, token blacklist |
| Frontend | Vue 3, Vite, Vue Router, Pinia |
| API Client | Axios interceptor, JWT 자동 갱신 |
| UI | Bootstrap, custom Vue components |
| Chart | lightweight-charts |
| Database | SQLite 개발 환경 기준 |
| External APIs | FinLife, GMS/Gemini 호환 API, Kiwoom, YouTube Data API, Kakao Local/Mobility |

## 프로젝트 구조

```text
Flex_Log/
├── backend/
│   ├── accounts/        # User 모델, 회원가입, 내 정보, 로그아웃
│   ├── profiles/        # 프로필 조회/수정, 공개 범위 처리
│   ├── friends/         # 친구 검색, 추천, 요청 상태 관리
│   ├── expenses/        # 소비 로그, 피드, 카테고리, 좋아요, 댓글
│   ├── analysis/        # 월별 집계, AI 분석 생성/조회
│   ├── finance/         # 금융 상품, 추천, 원자재, 주식, 외부 API
│   ├── notifications/   # 알림 목록과 읽음 처리
│   └── config/          # settings, root urls, ASGI/WSGI
├── frontend/
│   ├── src/api/         # Axios 기반 API 함수
│   ├── src/stores/      # Pinia 계정/분석/프로필/알림 상태
│   ├── src/views/       # 라우트 단위 화면
│   ├── src/components/  # feed, finance, profile, common 컴포넌트
│   └── src/utils/       # 월 수입 저장, 포맷, 주식 유틸
└── docs/
    ├── assets/          # ERD 이미지
    └── *.md             # 설계/명세/회고 문서
```

## 백엔드 앱 역할

| 앱 | 핵심 모델 | 주요 API |
| --- | --- | --- |
| `accounts` | `User` | `/accounts/signup/`, `/accounts/me/`, `/accounts/logout/` |
| `profiles` | `Profile` | `/profiles/me/`, `/profiles/<user_id>/` |
| `friends` | `Friend` | `/friends/users/`, `/friends/`, `/friends/<id>/` |
| `expenses` | `Category`, `ExpenseLog`, `Like`, `Comment` | `/expenses/`, `/expenses/feed/`, `/expenses/<id>/like/` |
| `analysis` | `MonthlyAnalysis`, `MonthlyAIAnalysis` | `/analysis/monthly/`, `/analysis/monthly/latest/` |
| `finance` | `FinancialProduct`, `FinancialProductOption`, `UserFinancialProduct`, `StockHolding` | `/finance/products/`, `/finance/recommend/`, `/finance/stocks/` |
| `notifications` | `Notification` | `/notifications/`, `/notifications/unread-count/` |

## 프론트엔드 화면 흐름

| 경로 | 화면 | 설명 |
| --- | --- | --- |
| `/` | Home | 비로그인 첫 화면 |
| `/signup`, `/login` | 인증 | 가입/로그인 |
| `/feed` | ExpenseFeedView | 친구 피드 |
| `/logs` | ExpenseListView | 내 소비 로그 |
| `/logs/new`, `/logs/:id/edit` | ExpenseFormView | 소비 로그 작성/수정 |
| `/logs/:id` | ExpenseDetailView | 소비 로그 상세, 좋아요, 댓글 |
| `/profile`, `/profile/:userId` | ProfileView | 내/타인 프로필 |
| `/friends` | FriendsView | 친구 검색, 추천, 요청 처리 |
| `/notifications` | NotificationView | 알림 |
| `/analysis` | AnalysisView | 월별 분석과 월 수입 입력 |
| `/finance` | FinanceHubView | 금융 허브 |
| `/finance/products` | FinanceProductsView | 예금/적금 상품 |
| `/finance/recommend` | FinancialRecommendationView | 금융 상품 추천 |
| `/finance/commodities` | CommodityPricesView | 금/은 시세 |
| `/finance/youtube` | YoutubeSearchView | 금융 영상 검색 |
| `/finance/banks` | NearbyBanksView | 은행 검색/길찾기 |
| `/stocks` | StockHoldingView | 주식 보유 현황과 차트 |

모든 주요 서비스 화면은 `requiresAuth` 라우트입니다. 로그인 상태에서 `/`와 인증 화면에 접근하면 `/feed`로 이동합니다.

## 실행 방법

### 1. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

기본 주소:

```text
http://127.0.0.1:8000
```

### 2. Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

기본 주소:

```text
http://127.0.0.1:5173
```

## 환경 변수

### Backend `.env`

`backend/.env`에 설정합니다. 운영 환경에서는 `DEBUG=False`와 강한 `SECRET_KEY`가 필수입니다.

```env
SECRET_KEY=replace-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

GMS_KEY=
GMS_API_URL=https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions
GMS_MODEL=gpt-5.4-nano

FINLIFE_API_KEY=
FINLIFE_API_BASE_URL=https://finlife.fss.or.kr/finlifeapi
FINLIFE_TOP_FIN_GRP_NO=020000

KIWOOM_APP_KEY=
KIWOOM_SECRET_KEY=
KIWOOM_BASE_URL=https://api.kiwoom.com
KIWOOM_TOKEN_PATH=/oauth2/token
KIWOOM_REQUEST_TIMEOUT=10

YOUTUBE_API_KEY=
KAKAO_REST_API_KEY=
KAKAO_MOBILITY_API_KEY=
KAKAO_ROUTE_ORIGIN_X=127.039585
KAKAO_ROUTE_ORIGIN_Y=37.5012743
KAKAO_ROUTE_ORIGIN_NAME=멀티캠퍼스 역삼
EXTERNAL_API_TIMEOUT=10
```

운영 보안 관련 변수:

```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Frontend `.env`

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_KAKAO_JAVASCRIPT_KEY=Kakao_JavaScript_Key
```

## 외부 API 사용 조건

| 기능 | 필요한 키 | 키가 없거나 실패할 때 |
| --- | --- | --- |
| AI 분석 | `GMS_KEY` | 서버 fallback 분석 저장 |
| FinLife 상품 수집 | `FINLIFE_API_KEY` | fixture 또는 기존 DB 데이터 사용 |
| 주식 현재가/차트 | `KIWOOM_APP_KEY`, `KIWOOM_SECRET_KEY` | API는 오류 반환, 프론트는 fallback/빈 상태 처리 |
| YouTube 검색 | `YOUTUBE_API_KEY` | `503` 오류 |
| Kakao 은행 검색/경로 | `KAKAO_REST_API_KEY`, `KAKAO_MOBILITY_API_KEY` | `503` 오류 |

## 데이터와 보안 정책

- 이메일은 `/accounts/me/`와 본인 프로필에서만 직접 노출합니다.
- 친구 검색은 이메일을 검색 대상으로 사용하지 않습니다.
- 피드는 본인과 accepted 친구의 `public`, `friends` 로그만 보여주며 `expires_at`이 지난 로그는 제외합니다.
- 본인의 소비 로그 목록은 기록 보존 목적 때문에 만료 여부와 관계없이 조회됩니다.
- `hide_amount=true`인 소비 로그는 작성자가 아닌 사용자에게 `amount=null`로 응답합니다.
- 월 수입은 DB에 공용 값으로 저장하지 않고 브라우저 localStorage에 사용자별 key로 저장합니다.
- access/refresh token은 Pinia persistedstate를 통해 sessionStorage에 저장되어 브라우저 세션 범위로 제한됩니다.
- 주식 현재가 갱신은 목록 조회마다 실행하지 않고 `/finance/stocks/?refresh=1`일 때만 시도합니다.

월 수입 localStorage key:

```text
flexlog.monthlyIncome.<userId>
```

## 데이터 적재 명령

```powershell
cd backend
python manage.py seed_demo_data
python manage.py fetch_finlife_products
python manage.py load_commodity_prices
python manage.py make_finlife_fixture
```

명령 역할:

| 명령 | 설명 |
| --- | --- |
| `seed_demo_data` | 개발용 사용자, 소비, 금융 샘플 데이터 적재 |
| `fetch_finlife_products` | FinLife API에서 예금/적금 상품 수집 |
| `load_commodity_prices` | 원자재 가격 데이터 적재 |
| `make_finlife_fixture` | 현재 금융 상품 데이터를 fixture로 저장 |

## 검증 명령

백엔드:

```powershell
cd backend
python manage.py test
python manage.py check --deploy
```

프론트엔드:

```powershell
cd frontend
npm run build
```

## 문서

- [프로젝트 배경](docs/00_project_background.md)
- [요구사항 정의](docs/01_requirements.md)
- [ERD](docs/02_ERD.md)
- [API 명세](docs/03_API_spec.md)
- [WBS](docs/04_wbs.md)
- [브랜치 전략](docs/05_branch_strategy.md)
- [회고](docs/06_retrospective.md)
- [필수 기능 DB 설계](docs/07_required_features_db_design.md)

ERD 이미지:

- [docs/assets/flex_log_erd.png](docs/assets/flex_log_erd.png)
- [docs/assets/flex_log_erd.svg](docs/assets/flex_log_erd.svg)
