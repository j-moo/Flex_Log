# Flex-log

> 사진과 짧은 영상으로 소비를 기록하고, 월별 소비 패턴을 분석하는 스토리형 소비 로그 웹 애플리케이션

<br>

## 1. 프로젝트 개요

**Flex-log**는 사용자가 일상 속 소비를 사진 또는 짧은 영상과 함께 기록하고, 이를 스토리 형태로 확인할 수 있는 소비 기록 서비스입니다.  
기존 가계부처럼 금액과 카테고리만 남기는 방식에서 벗어나, 소비가 발생한 순간의 맥락까지 함께 저장하는 것을 목표로 합니다.

사용자는 소비 로그를 작성하고, 월별·카테고리별 소비 패턴을 분석할 수 있습니다. 이후 확장 기능으로는 팔로우 기반 피드, 좋아요와 댓글, AI 소비 분석, 금융상품 추천, 보유 주식 수익률 확인 기능을 계획하고 있습니다.

<br>

## 2. 프로젝트 선정 배경

일상에서 소비 내역을 관리하려는 사람은 많지만, 실제로 가계부를 꾸준히 작성하는 것은 쉽지 않습니다. 기존 가계부 서비스는 대부분 사용자가 금액, 소비처, 카테고리, 메모를 직접 입력하는 방식이기 때문에 기록 과정이 번거롭고, 시간이 지나면 기록을 중단하기 쉽다는 한계가 있습니다.

또한 카드 사용 내역이나 숫자 중심의 소비 기록만으로는 소비 당시의 상황을 떠올리기 어렵습니다. 사용자는 월말에 총 지출 금액은 확인할 수 있지만, 어떤 상황에서 소비가 반복되었고 왜 과소비가 발생했는지 직관적으로 파악하기 어렵습니다.

Flex-log는 이러한 문제를 해결하기 위해 **사진 기반 소비 기록**과 **소비 패턴 분석**을 결합한 서비스로 기획되었습니다. 소비 순간을 이미지와 함께 남기고, 누적된 소비 데이터를 분석하여 사용자가 자신의 소비 습관을 더 쉽게 돌아볼 수 있도록 하는 것이 핵심 목표입니다.

<br>

## 3. 주제 선정에 활용한 기법

Flex-log의 주제 선정은 단순한 아이디어 발상이 아니라, 정보처리기사에서 학습한 소프트웨어 설계 개념을 바탕으로 진행했습니다.

### 3.1 요구사항 도출

먼저 사용자 관점에서 기존 소비 기록 방식의 불편함을 정리했습니다.  
그 결과 다음과 같은 문제가 도출되었습니다.

- 소비 기록을 꾸준히 유지하기 어렵다.
- 숫자 중심의 소비 내역만으로는 소비 당시의 맥락을 파악하기 어렵다.
- 월별 소비 패턴을 직관적으로 분석하기 어렵다.
- 소비 기록이 금융상품 추천이나 자산 관리로 자연스럽게 이어지지 않는다.

### 3.2 브레인스토밍

소비 기록과 금융 서비스를 주제로 자유롭게 기능 아이디어를 도출했습니다.

- 사진 기반 소비 기록
- 짧은 영상 소비 로그
- 오늘의 소비 스토리
- 월별 소비 분석
- 카테고리별 소비 차트
- 팔로우 기반 피드
- 좋아요와 댓글
- AI 소비 분석
- 금융상품 추천
- 보유 주식 수익률 확인

이후 아이디어를 정리한 결과, Flex-log의 핵심 가치는 **소비를 쉽게 기록하고, 소비 패턴을 직관적으로 확인하는 것**이라고 판단했습니다.

### 3.3 프로토타이핑

초기에는 소비 기록, 소셜 피드, 금융상품 추천, 주식 관리 등 다양한 기능 아이디어가 존재했습니다. 따라서 바로 구현에 들어가지 않고, 사용자가 서비스를 이용하는 흐름을 먼저 가정했습니다.

```text
소비 발생
→ 사진 또는 짧은 영상 기록
→ 금액, 소비처, 카테고리 입력
→ 소비 로그 저장
→ 오늘의 소비 스토리 확인
→ 월별 소비 분석 확인
→ 금융상품 또는 혜택 추천 확인
```

이 흐름을 통해 Flex-log의 중심 기능은 **소비 로그 작성**과 **소비 분석**이라는 점을 확인했습니다.

### 3.4 유스케이스 분석

사용자가 시스템에서 수행할 행위를 기준으로 초기 기능을 도출했습니다.

- 비회원: 회원가입, 로그인
- 회원: 소비 로그 작성, 조회, 수정, 삭제
- 회원: 월별 소비 분석 확인
- 회원: 다른 사용자 팔로우
- 회원: 피드 조회, 좋아요, 댓글 작성
- 회원: 금융상품 추천 확인
- 외부 API: 금융상품 데이터 제공, 주식 현재가 제공
- AI 서비스: 소비 패턴 분석 결과 제공

이를 통해 Flex-log를 단순 가계부가 아니라, **소비 기록·분석·공유·금융 정보 탐색이 연결되는 서비스**로 구체화했습니다.

### 3.5 자료 흐름도 관점

소비 로그 데이터가 시스템 내부에서 어떻게 활용되는지 흐름을 정리했습니다.

```text
사용자 입력
→ 소비 로그 저장
→ 월별/카테고리별 집계
→ 분석 결과 생성
→ 차트 출력
→ 금융상품 추천 기준으로 활용
```

이를 통해 Flex-log의 핵심 데이터는 `소비 로그`이며, 소비 로그가 쌓일수록 분석과 추천 기능으로 확장될 수 있다는 점을 확인했습니다.

### 3.6 HIPO

브레인스토밍으로 도출된 기능을 하향식으로 분해했습니다.

```text
Flex-log
├── 계정 관리
├── 소비 로그 관리
├── 소비 분석
├── 소셜 기능
└── 금융 기능
```

이 과정을 통해 1차 MVP는 `계정 관리`, `소비 로그 관리`, `소비 분석`으로 좁히고, 소셜 기능과 금융 기능은 단계별 확장 기능으로 분리했습니다.

<br>

## 4. 문제 정의와 해결 방향

| 발견한 문제 | 해결 방향 | 도출된 기능 |
|---|---|---|
| 가계부 입력이 번거롭다 | 빠르고 직관적인 기록 방식 제공 | 사진/영상 기반 소비 로그 |
| 소비 당시 상황이 기억나지 않는다 | 소비 순간의 맥락을 함께 저장 | 이미지, 소비처, 메모 기록 |
| 월별 소비 패턴을 알기 어렵다 | 소비 데이터를 시각적으로 분석 | 월별/카테고리별 소비 차트 |
| 혼자 기록하면 지속성이 떨어진다 | 공유와 반응을 통한 동기부여 제공 | 팔로우, 피드, 좋아요, 댓글 |
| 소비 습관 개선으로 이어지지 않는다 | 분석 결과 기반 피드백 제공 | AI 소비 분석, 금융상품 추천 |
| 금융 정보가 흩어져 있다 | 소비·금융 정보를 한 서비스에서 확인 | 금융상품 API, 보유 주식 관리 |

<br>

## 5. 핵심 기능

### 5.1 1차 MVP

- 회원가입
- 로그인 / 로그아웃
- 프로필 조회 및 수정
- 소비 로그 작성
- 소비 금액, 소비처, 카테고리, 메모 입력
- 사진 업로드
- 소비 로그 목록 조회
- 소비 로그 상세 조회
- 소비 로그 수정 / 삭제
- 월별 소비 합계 조회
- 카테고리별 소비 분석

### 5.2 2차 확장 기능

- 사용자 검색
- 팔로우 / 언팔로우
- 팔로잉 사용자의 소비 로그 피드
- 좋아요
- 댓글
- 공개 범위 설정

### 5.3 심화 기능

- AI 기반 소비 분석
- 과소비 카테고리 분석
- 금융상품 추천
- 금융감독원 예금/적금 API 연동
- 보유 주식 등록
- Finnhub API 기반 현재가 조회
- 보유 주식 평가금액 및 수익률 계산
- 주가 그래프 시각화

<br>

## 6. 기술 스택

### Backend

- Python
- Django
- Django REST Framework
- SQLite / PostgreSQL

### Frontend

- Vue 3
- Vite
- JavaScript
- Axios
- Chart.js 또는 ECharts

### External API

- 금융감독원 금융상품통합비교공시 API
- Finnhub API
- AI 분석 API

### Tools

- Git / GitHub
- VS Code
- Postman
- Figma 또는 화면 설계 도구

<br>

## 7. 예상 프로젝트 구조

```text
Flex-log/
├── README.md
├── docs/
│   ├── 00_project_idea.md
│   ├── 01_requirements.md
│   ├── 02_data_research.md
│   ├── 03_erd.md
│   ├── 04_usecase.md
│   ├── 05_screen_flow.md
│   ├── 06_api_spec.md
│   ├── 07_wbs.md
│   ├── 08_troubleshooting.md
│   └── 09_retrospective.md
├── backend/
│   └── Django project
├── frontend/
│   └── Vue project
├── assets/
│   ├── erd.png
│   ├── usecase.png
│   └── wireframes/
└── .gitignore
```

<br>

## 8. 주요 데이터 모델 초안

| 모델 | 설명 |
|---|---|
| User | 사용자 계정 정보 |
| Profile | 닉네임, 프로필 이미지, 소개글 |
| ExpenseCategory | 소비 카테고리 |
| ExpenseLog | 소비 금액, 소비처, 메모, 이미지, 소비일자 |
| Follow | 사용자 간 팔로우 관계 |
| Like | 소비 로그 좋아요 |
| Comment | 소비 로그 댓글 |
| MonthlyAnalysis | 월별 소비 분석 결과 |
| AIAnalysis | AI 소비 분석 결과 |
| FinancialProduct | 금융상품 정보 |
| Recommendation | 사용자별 금융상품 추천 결과 |
| StockHolding | 보유 주식 종목, 수량, 평단가 |

<br>

## 9. API 설계 초안

### Accounts

| Method | URL | 설명 |
|---|---|---|
| POST | `/api/accounts/signup/` | 회원가입 |
| POST | `/api/accounts/login/` | 로그인 |
| POST | `/api/accounts/logout/` | 로그아웃 |
| GET | `/api/accounts/profile/` | 내 프로필 조회 |
| PATCH | `/api/accounts/profile/` | 프로필 수정 |

### Expenses

| Method | URL | 설명 |
|---|---|---|
| GET | `/api/expenses/` | 소비 로그 목록 조회 |
| POST | `/api/expenses/` | 소비 로그 작성 |
| GET | `/api/expenses/{id}/` | 소비 로그 상세 조회 |
| PATCH | `/api/expenses/{id}/` | 소비 로그 수정 |
| DELETE | `/api/expenses/{id}/` | 소비 로그 삭제 |

### Analysis

| Method | URL | 설명 |
|---|---|---|
| GET | `/api/analysis/monthly/` | 월별 소비 분석 |
| GET | `/api/analysis/category/` | 카테고리별 소비 분석 |
| POST | `/api/analysis/ai/` | AI 소비 분석 요청 |

### Social

| Method | URL | 설명 |
|---|---|---|
| GET | `/api/users/search/` | 사용자 검색 |
| POST | `/api/users/{id}/follow/` | 팔로우 / 언팔로우 |
| GET | `/api/feed/` | 팔로잉 기반 피드 조회 |
| POST | `/api/expenses/{id}/like/` | 좋아요 / 좋아요 취소 |
| POST | `/api/expenses/{id}/comments/` | 댓글 작성 |

### Finance & Stocks

| Method | URL | 설명 |
|---|---|---|
| GET | `/api/finance/products/` | 금융상품 목록 조회 |
| GET | `/api/finance/recommendations/` | 금융상품 추천 조회 |
| GET | `/api/stocks/holdings/` | 보유 주식 목록 조회 |
| POST | `/api/stocks/holdings/` | 보유 주식 등록 |
| GET | `/api/stocks/quote/` | 주식 현재가 조회 |

<br>

## 10. 비기능 요구사항

| 항목 | 내용 |
|---|---|
| 보안 | API Key는 `.env` 또는 환경변수로 관리한다. |
| 접근 제어 | 소비 로그 수정/삭제는 작성자 본인만 가능해야 한다. |
| 개인정보 보호 | 소비 기록과 보유 주식 정보는 민감 정보로 보고 접근 권한을 제한한다. |
| 사용성 | 모바일 환경에서도 주요 기능을 사용할 수 있도록 반응형 UI를 구성한다. |
| 파일 제한 | 이미지/영상 업로드 시 확장자와 파일 크기를 제한한다. |
| 성능 | 월별 분석은 필요한 기간의 데이터만 조회하여 처리한다. |
| 금융 고지 | 금융상품 및 주식 정보는 투자 권유가 아닌 참고 정보임을 명시한다. |

<br>

## 11. GitHub 기록 전략

이 프로젝트는 구현 결과뿐 아니라, 초기 구상부터 설계와 구현 과정을 GitHub에 기록하는 것을 목표로 합니다.

### 문서화 계획

| 문서 | 내용 |
|---|---|
| `00_project_idea.md` | 문제 인식, 주제 선정 배경, 활용 기법 |
| `01_requirements.md` | 기능 요구사항, 비기능 요구사항, 우선순위 |
| `02_data_research.md` | 내부 데이터, 외부 API, 활용 가능성 |
| `03_erd.md` | 데이터 모델과 관계 설계 |
| `04_usecase.md` | Actor와 Use Case 정리 |
| `05_screen_flow.md` | 화면 흐름과 주요 UI 구성 |
| `06_api_spec.md` | API URL, Method, 요청/응답 구조 |
| `08_troubleshooting.md` | 구현 중 발생한 문제와 해결 과정 |
| `09_retrospective.md` | 학습 내용, 어려웠던 점, 개선 방향 |

### 커밋 흐름 예시

```bash
docs: 프로젝트 주제 선정 배경 작성
docs: 요구사항 도출 기법과 초기 문제 정의 작성
docs: 기능 요구사항과 비기능 요구사항 정의
docs: 데이터 탐색 및 외부 API 후보 정리
docs: ERD 초안 작성
docs: Use Case Diagram 작성
docs: API 명세 초안 작성
chore: Django 백엔드 프로젝트 초기 설정
chore: Vue 프론트엔드 프로젝트 초기 설정
feat: 소비 로그 CRUD API 구현
feat: 월별 소비 분석 API 구현
feat: 팔로우 기반 피드 기능 구현
fix: 소비 로그 권한 검증 로직 수정
refactor: 소비 분석 로직 분리
docs: 트러블슈팅 및 회고 작성
```

<br>

## 12. 예상되는 어려움과 해결 방향

### 미디어 업로드 처리

사진과 짧은 영상을 업로드해야 하므로 파일 크기, 확장자, 저장 위치, 삭제 처리를 고려해야 합니다. 초기에는 이미지 업로드를 먼저 구현하고, 영상 업로드는 심화 기능으로 분리합니다.

### 팔로우 관계 처리

팔로우는 사용자와 사용자가 연결되는 자기참조 관계입니다. `follower`와 `following`을 명확히 구분하고, 자기 자신을 팔로우하지 못하도록 검증합니다.

### 월별 소비 분석

소비 로그를 월별로 필터링하고 카테고리별로 합산해야 합니다. Django ORM의 `filter`, `annotate`, `Sum` 등을 활용하여 구현할 계획입니다.

### AI 분석 기능

AI에게 소비 로그 전체를 그대로 전달하지 않고, 월별 총액, 카테고리별 금액, 가장 많이 소비한 카테고리 등 요약 데이터를 전달하는 방식으로 설계합니다.

### 외부 API 연동

금융상품 API와 주식 현재가 API는 인증키 관리와 호출 제한을 고려해야 합니다. API Key는 코드에 직접 작성하지 않고 환경변수로 분리합니다.

<br>

## 13. 프로젝트를 통해 학습하고자 하는 것

- 아이디어를 요구사항으로 구체화하는 과정
- 기능 요구사항과 비기능 요구사항 분리
- ERD와 Use Case 기반 설계
- Django REST Framework 기반 API 개발
- Vue와 Axios를 활용한 비동기 통신
- 소비 데이터 집계 및 차트 시각화
- 외부 금융 API 연동
- GitHub 기반 형상관리와 개발 기록
- 트러블슈팅 문서화

<br>

## 14. 최종 목표

Flex-log는 단순한 가계부가 아니라, 소비를 스토리처럼 기록하고 분석하는 서비스입니다.  
이 프로젝트를 통해 초기 아이디어 도출, 요구사항 정의, 데이터 설계, API 설계, 구현, 테스트, 트러블슈팅까지 하나의 흐름으로 기록하여 포트폴리오로 활용하는 것을 목표로 합니다.

<br>

## FinLife 금융상품 데이터와 추천 기능

### 환경변수

`backend/.env`에 금융감독원 금융상품 한눈에 API 키를 설정합니다. `.env`는 Git에 올리지 않습니다.

```env
api_key=발급받은_금융상품한눈에_API_KEY
```

호환을 위해 `FINLIFE_API_KEY`도 사용할 수 있지만, 프로젝트 기본 키 이름은 `api_key`입니다.

### fixture 생성과 로드

API 키가 있는 개발자는 아래 순서로 최신 금융상품 fixture를 생성하고 DB에 로드합니다.

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py make_finlife_fixture
python manage.py loaddata financial_products.json
python manage.py runserver
```

생성되는 fixture 경로는 `backend/finance/fixtures/financial_products.json`입니다.

다른 개발 환경에서는 API 키 없이도 Git에 포함된 fixture를 DB에 로드할 수 있습니다.

```bash
cd backend
python manage.py migrate
python manage.py loaddata financial_products.json
python manage.py runserver
```

DB에 바로 저장하려면 아래 command를 사용할 수 있습니다.

```bash
python manage.py fetch_finlife_products
```

### 금융상품 API

```text
GET  /api/v1/finance/products/
GET  /api/v1/finance/products/deposits/
GET  /api/v1/finance/products/savings/
GET  /api/v1/finance/products/<product_id>/
```

목록 API는 `type`, `bank`, `term`, `min_rate` query parameter를 지원합니다.

### AI 금융상품 추천 API

```text
POST /api/v1/finance/recommend/
GET  /api/v1/finance/recommend/latest/
GET  /api/v1/finance/recommend/history/
```

추천은 외부 FinLife API를 매번 호출하지 않고, DB에 로드된 `FinancialProduct`와 `FinancialProductOption` 후보만 사용합니다. GMS AI 호출이 실패하거나 JSON 파싱에 실패하면 최신 월별 소비 분석의 `risk_level`과 금리 조건을 기준으로 fallback 추천을 생성합니다.
