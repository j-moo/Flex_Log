# [오늘 리뷰 대상]
PR/커밋: `d02f16b feature:back&front`

# [변경 의도]
- Django REST API와 Vue 프론트엔드를 함께 추가한 대규모 기능 커밋입니다.
- 주요 기능은 회원가입/로그인, 프로필/친구, 지출 피드, 월별 소비 분석, 금융상품/추천, 원자재 가격, YouTube/카카오/키움 외부 API 연동.
- 특히 중요한 부분은 인증 토큰 처리, 사용자별 데이터 접근 범위, 외부 API 키/환경변수 설정, 파일 업로드/미디어 응답, 금융/분석 API의 입력 검증.

# [중점적으로 볼 부분]
- 백엔드 API가 인증된 사용자 자신의 데이터만 조회/수정하는지
- 프론트와 백엔드의 API/환경변수 계약이 실제 실행 환경에서 맞는지
- 외부 API 연동 실패, 잘못된 쿼리 파라미터, 파일 업로드 같은 예외 상황 처리
- 커밋에 포함된 환경 파일과 키 값 관리
- 테스트와 빌드가 재현 가능한 상태인지

# [리뷰 체크]
- 요구사항 충족: 백엔드/프론트의 주요 기능 골격은 갖춰져 있으나, 지도 SDK 환경변수 불일치로 은행 지도 표시 기능은 현재 설정 그대로는 동작하지 않음.
- 예외 처리: 대부분의 외부 API 호출은 예외를 감싸고 있지만, 월별 분석 GET API는 `year`, `month` 쿼리 파라미터를 바로 `int()`로 변환해 잘못된 값에서 500 오류가 날 수 있는 가능성이 있음.
- 가독성: 앱별로 모델/serializer/view가 분리되어 구조는 파악 가능.
- 테스트: 성공
- 성능/보안: `frontend/.env`가 커밋되어 있고 실제 Kakao JavaScript 키 값이 들어 있습니다. 클라이언트 키라도 도메인 제한/교체 여부 확인이 필요하고, `.env`는 커밋 대상에서 제외하기.
- 영향 범위: 인증, 지출 피드, 금융상품, AI 분석, 외부 지도/영상/주식 API 등 앱 전반에 영향이 큼.

# [리뷰 결과]
## 반드시 수정
- `frontend/.env`와 `frontend/src/views/NearbyBanksView.vue`의 Kakao 지도 키 환경변수 이름이 다름. `.env`는 `VITE_KAKAO_JAVASCRIPT_KEY`를 정의하지만 코드는 `VITE_KAKAO_JS_KEY`를 읽고 있어, 실제 `.env` 기준으로는 `loadKakaoSdk()`가 키 없음으로 reject되어 지도 SDK가 로드되지 않음. 둘 중 하나로 통일해야 하기.
- `backend/analysis/views.py`에서 GET 요청의 `year`, `month`를 바로 `int()`로 변환합니다. `?year=abc` 또는 `?month=13` 같은 입력에서 400 응답 대신 서버 오류가 발생할 수 있으므로 POST와 동일하게 serializer를 쓰거나 `try/except` 및 월 범위 검증을 추가.
- `frontend/.env`에 실제 Kakao JavaScript 키가 커밋되어 있습니다. 공개 가능한 브라우저 키라도 저장소에는 `.env.example`만 남기고 실제 `.env`는 제거.

## 개선 제안
- `backend/expenses/serializers.py`에서 업로드 파일을 DB `BinaryField`에 저장하고 응답 시 `base64` data URL로 내려줍니다. 10MB 파일은 base64 변환 시 응답 크기와 메모리 사용량이 커질 수 있으므로, 가능하면 `FileField` 저장 후 URL 응답 방식으로 단순화하기.
- `backend/finance/views.py`, `backend/finance/views.py`에서 키움 API 장애도 모두 400으로 내려감. 사용자 입력 오류와 외부 서비스 장애를 구분하기 위해 인증/네트워크/API 장애는 503 계열, symbol/period 검증 실패는 400으로 분리하면 클라이언트 처리가 쉬워짐.

## 의도 확인 필요
- 지출 피드 미디어를 파일 스토리지 대신 DB에 저장하도록 한 의도가 있는지 확인이 필요합니다. 배포 환경에서 DB 용량, 백업 크기, 응답 지연에 직접 영향을 줌.
- `backend/analysis/views.py`의 GMS 분석 실패 시 조용히 fallback 분석으로 전환하는 정책이 의도된 것인지 확인이 필요. 운영에서는 외부 AI 장애를 사용자에게 숨길지, 별도 상태로 노출할지 정책을 정해야 함.
- `frontend/.env`를 실제 배포/시연용 설정으로 커밋한 것인지 확인이 필요합니다. 팀 공유 목적이라면 `.env.example`에 placeholder만 두는 방식이 더 안전.

# [검증 결과]
- `python -m py_compile backend/finance/views.py`: 성공
- `python -m py_compile backend/expenses/models.py`: 성공
- `python backend/manage.py test`: 실패. `ModuleNotFoundError: No module named 'rest_framework_simplejwt'`
- `npm.cmd run build` in `frontend`: 실패. `vite` 실행 파일을 찾을 수 없음

# [다음 리뷰]
- 다음 리뷰 대상: 1순위는 인증/권한 및 사용자 데이터 접근 범위, 2순위는 지출 피드/미디어 업로드, 3순위는 금융 외부 API 연동으로 진행.
