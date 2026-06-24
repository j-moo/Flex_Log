# 04. WBS

## 목적

이 문서는 Flex Log의 기능을 작업 단위로 분해하고, 현재 코드에서 어떤 모듈과 화면으로 구현되어 있는지 정리합니다. 새 팀원이 프로젝트를 이어받을 때 “어떤 기능이 어느 앱/화면/API에 있는지”를 빠르게 확인하는 것이 목적입니다.

## 전체 작업 구조

| 단계 | 작업 영역 | 주요 산출물 | 현재 상태 |
| --- | --- | --- | --- |
| 1 | 기획 | 서비스 주제, 사용자 흐름, 기능 범위 | 완료 |
| 2 | 데이터 설계 | Django 모델, 제약 조건, ERD | 완료 |
| 3 | 인증 | User 모델, JWT, 회원가입/로그인/로그아웃 | 완료 |
| 4 | 프로필 | 프로필 조회/수정, 공개 정책 | 완료 |
| 5 | 친구 | 검색, 추천, 요청, 수락/거절, 삭제 | 완료 |
| 6 | 소비 로그 | CRUD, 미디어, 공개 범위, 삭제 확인 | 완료 |
| 7 | 피드 | 친구 피드, 만료 정책, 좋아요, 댓글 | 완료 |
| 8 | 월별 분석 | 월별 집계, AI 분석, fallback, 알림 | 완료 |
| 9 | 금융 상품 | 상품 조회, 필터, 옵션, 가입/취소 | 완료 |
| 10 | 추천 | 분석 기반 추천 생성/조회 | 완료 |
| 11 | 원자재 | 금/은 마스터, 가격 조회/import | 완료 |
| 12 | 외부 API | FinLife, GMS, Kiwoom, YouTube, Kakao | 조건부 완료 |
| 13 | 주식 | 보유 종목, 현재가, 차트, 손익 계산 | 완료 |
| 14 | 알림 | 목록, unread count, 읽음 처리 | 완료 |
| 15 | 프론트엔드 | 라우팅, 화면, 상태 관리, API client | 완료 |
| 16 | 품질 개선 | 권한/보안/성능/회귀 테스트 | 진행 |
| 17 | 문서 | README, API, ERD, DB 설계 | 진행 |

## Backend WBS

### accounts

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| 커스텀 User 모델 | `backend/accounts/models.py` | 완료 | `AUTH_USER_MODEL='accounts.User'` |
| 회원가입 serializer | `backend/accounts/serializers.py` | 완료 | username/email 중복, password_confirm 검증 |
| 회원가입 API | `backend/accounts/views.py` | 완료 | 가입 후 Profile 생성, JWT 반환 |
| 내 정보 API | `backend/accounts/views.py` | 완료 | 인증 사용자 정보 반환 |
| 로그아웃 API | `backend/accounts/views.py` | 완료 | refresh token blacklist 처리 |

### profiles

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| Profile 모델 | `backend/profiles/models.py` | 완료 | User와 OneToOne |
| 내 프로필 조회/수정 | `backend/profiles/views.py` | 완료 | 이미지 multipart, name 업데이트 |
| 공개 프로필 조회 | `backend/profiles/views.py` | 완료 | `user_id` lookup |
| 이메일 비공개 | `backend/profiles/serializers.py` | 완료 | 타인 조회 시 `email` 제거 |
| 가입 상품 공개 정책 | `backend/profiles/serializers.py` | 완료 | 본인 또는 친구만 `joined_products` 조회 |

### friends

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| Friend 모델 | `backend/friends/models.py` | 완료 | 자기 요청, 중복/역방향 중복 방지 |
| 사용자 검색 | `backend/friends/views.py` | 완료 | username/name/nickname 검색, 이메일 제외 |
| 친구 추천 | `backend/friends/views.py` | 완료 | mutual friend count 기준 |
| 친구 요청 생성 | `backend/friends/views.py` | 완료 | 수신자에게 알림 생성 |
| 친구 요청 처리 | `backend/friends/views.py` | 완료 | 수신자만 수락/거절 가능 |

### expenses

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| Category 모델 | `backend/expenses/models.py` | 완료 | name unique |
| ExpenseLog 모델 | `backend/expenses/models.py` | 완료 | amount positive, visibility check |
| 미디어 업로드 | `backend/expenses/serializers.py` | 완료 | 확장자/10MB 제한 |
| 기본 제목 생성 | `backend/expenses/serializers.py` | 완료 | title 누락 시 fallback 생성 |
| 금액 숨김 | `backend/expenses/serializers.py` | 완료 | 비작성자 `amount=null` |
| 내 로그 목록 | `backend/expenses/views.py` | 완료 | 만료와 관계없이 본인 로그 반환 |
| 피드 목록 | `backend/expenses/views.py` | 완료 | 친구, 공개 범위, 만료, visible 조건 적용 |
| 삭제 확인 | `backend/expenses/views.py` | 완료 | `confirmation_code`, `confirmation_text` 검증 |
| 좋아요 토글 | `backend/expenses/views.py` | 완료 | unique user/log, grouped notification |
| 댓글 CRUD | `backend/expenses/views.py` | 완료 | 접근 가능한 로그, 작성자 권한 |

### analysis

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| 기본 월별 집계 | `backend/analysis/views.py` | 완료 | `MonthlyAnalysis` upsert |
| AI 분석 요청 | `backend/analysis/views.py` | 완료 | GMS API 호출, JSON 파싱 |
| fallback 분석 | `backend/analysis/views.py` | 완료 | 외부 API 실패 시 서버 문구 저장 |
| 위험도 계산 | `backend/analysis/views.py` | 완료 | 월 수입 있으면 수입 대비 비율 사용 |
| 최신/이력 조회 | `backend/analysis/views.py` | 완료 | 사용자별 결과만 반환 |

### finance

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| 금융 상품 모델 | `backend/finance/models.py` | 완료 | product/option 분리 |
| 상품 필터 | `backend/finance/views.py` | 완료 | type, bank, term, min_rate 검증 |
| 상품 가입 | `backend/finance/views.py` | 완료 | `option_id`, 중복 active 방지 |
| 상품 취소 | `backend/finance/views.py` | 완료 | status/date consistency |
| 추천 생성 | `backend/finance/recommendation_utils.py` | 완료 | 최신 분석 기반 추천 |
| 원자재 가격 조회 | `backend/finance/views.py` | 완료 | start/end 날짜 검증 |
| 원자재 import | `backend/finance/views.py` | 완료 | 관리자 권한, 가격 검증 |
| YouTube 검색 | `backend/finance/services/youtube_api.py` | 완료 | q/max_results 검증 |
| 은행 검색/경로 | `backend/finance/services/kakao_local.py` | 완료 | radius/x/y 검증 |
| 주식 현재가/차트 | `backend/finance/services/kiwoom_api.py` | 완료 | symbol/period 검증 |
| 보유 주식 CRUD | `backend/finance/views.py` | 완료 | 중복 symbol 평균 단가 재계산 |

### notifications

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| 알림 모델 | `backend/notifications/models.py` | 완료 | receiver, actor, type, route 정보 |
| 알림 생성 helper | `backend/notifications/helpers.py` | 완료 | dedupe/grouped notification |
| 목록 조회 | `backend/notifications/views.py` | 완료 | 사용자별 최신 80개 |
| unread count | `backend/notifications/views.py` | 완료 | 읽지 않은 수 반환 |
| 읽음 처리 | `backend/notifications/views.py` | 완료 | 개별/전체 읽음 |

## Frontend WBS

### 공통 구조

| 작업 | 구현 파일 | 상태 | 검증 기준 |
| --- | --- | --- | --- |
| 라우터 구성 | `frontend/src/router/index.js` | 완료 | guestOnly/requiresAuth guard |
| API client | `frontend/src/api/client.js` | 완료 | access token header, refresh retry |
| 계정 store | `frontend/src/stores/account.js` | 완료 | sessionStorage 기반 persist |
| 월 수입 유틸 | `frontend/src/utils/monthlyIncome.js` | 완료 | 사용자별 key, legacy migration |
| 공통 UI | `frontend/src/components/common/` | 완료 | TopBar, BottomNav, ConfirmDialog |

### 화면별 작업

| 화면 | 구현 파일 | 연결 API |
| --- | --- | --- |
| 회원가입 | `SignUpView.vue` | `/accounts/signup/` |
| 로그인 | `LogInView.vue` | `/accounts/login/` |
| 피드 | `ExpenseFeedView.vue` | `/expenses/feed/`, like/comment |
| 로그 목록 | `ExpenseListView.vue` | `/expenses/`, `/expenses/users/<id>/` |
| 로그 작성/수정 | `ExpenseFormView.vue` | `/expenses/`, `/expenses/<id>/` |
| 로그 상세 | `ExpenseDetailView.vue` | `/expenses/<id>/`, comments |
| 프로필 | `ProfileView.vue` | `/profiles/me/`, `/profiles/<id>/` |
| 친구 | `FriendsView.vue` | `/friends/users/`, `/friends/` |
| 알림 | `NotificationView.vue` | `/notifications/` |
| 분석 | `AnalysisView.vue` | `/analysis/monthly/` |
| 금융 허브 | `FinanceHubView.vue` | analysis, finance summary |
| 금융 상품 | `FinanceProductsView.vue` | `/finance/products/` |
| 추천 | `FinancialRecommendationView.vue` | `/finance/recommend/` |
| 원자재 | `CommodityPricesView.vue` | `/finance/commodities/<code>/prices/` |
| YouTube | `YoutubeSearchView.vue`, `YoutubeDetailView.vue` | `/finance/youtube/*` |
| 은행 | `NearbyBanksView.vue` | `/finance/banks/*` |
| 주식 | `StockHoldingView.vue` | `/finance/stocks/`, `/finance/chart/` |

## 최근 반영된 품질 개선

| 영역 | 문제 | 조치 |
| --- | --- | --- |
| 개인정보 | 타인 프로필에 이메일이 노출될 수 있음 | 본인이 아니면 serializer에서 `email` 제거 |
| 친구 검색 | 이메일 검색으로 사용자 이메일 유추 가능 | 검색 대상에서 email 제외 |
| 피드 만료 | 만료된 로그가 타인 조회에 남을 수 있음 | `expires_at__gt=now` 조건 적용 |
| 기록 보존 | 본인 로그도 만료로 사라질 수 있음 | 본인 목록은 만료 조건 제외 |
| 월 수입 | 같은 브라우저의 다른 계정에 월 수입이 공유됨 | `flexlog.monthlyIncome.<userId>` key 사용 |
| 주식 차트 | 종목 추가 후 차트가 비어 보임 | 종목/로딩 변경 시 차트 인스턴스 재생성 |
| 주식 현재가 | 목록 조회마다 외부 API 호출 가능 | `refresh=1`일 때만 갱신 |
| 보안 설정 | 운영 SECRET_KEY 기본값 위험 | `DEBUG=False`에서 SECRET_KEY 필수 |
| 프론트 성능 | 라우트 초기 번들 증가 | route component lazy loading |

## 검증 체크리스트

### 기능 검증

- 회원가입 후 User와 Profile이 함께 생성된다.
- 로그인 후 protected route 접근이 가능하다.
- access token 만료 시 refresh 요청이 한 번만 재시도된다.
- 타인 프로필 응답에 `email`이 없다.
- 친구 검색에서 이메일로 사용자를 찾을 수 없다.
- 친구가 아닌 사용자는 `friends` 공개 로그를 볼 수 없다.
- 만료된 로그는 피드와 타인 목록에서 제외된다.
- 본인 로그 목록은 만료된 로그도 조회된다.
- `hide_amount=true` 로그는 비작성자에게 금액이 숨겨진다.
- 월 수입은 계정별로 다르게 저장된다.
- 상품 필터 `term`에 문자를 넣으면 400 응답이 반환된다.
- 주식 추가 후 `/stocks` 화면 차트가 표시된다.

### 자동 검증

```powershell
cd backend
python manage.py test
python manage.py check --deploy
```

```powershell
cd frontend
npm run build
```

## 남은 작업 후보

| 우선순위 | 작업 | 이유 |
| --- | --- | --- |
| 높음 | 운영 DB를 PostgreSQL 등으로 전환 | SQLite는 동시성/운영 안정성 한계가 있음 |
| 높음 | 미디어 파일 저장소 분리 | 로컬 `MEDIA_ROOT`는 배포 확장에 부적합 |
| 높음 | 외부 API 호출 로깅과 모니터링 | 장애 원인과 응답 지연 추적 필요 |
| 중간 | 공통 페이지네이션 적용 | 피드, 알림, 상품 목록 대량 데이터 대응 |
| 중간 | 사용자 메시지 인코딩 정리 | 코드 내 일부 한글 문자열이 깨져 있어 사용자 표시 품질 저하 가능 |
| 중간 | 추천 결과 근거 표시 강화 | 금융 추천 신뢰도 보완 |
| 낮음 | 접근성 점검 | 키보드/스크린리더 사용성 개선 |
