# [오늘 리뷰 대상]
PR/커밋: `f1920f0b91ad3a5559d18526fe84b588b3a99fca Merge branch 'feature/frontend-jmkim' into 'master'`

# [변경 의도]
- UI/UX 개선을 중심으로 피드 작성/삭제, 금융 허브, 분석 화면, 프로필/친구 화면의 사용성을 보강한 merge commit입니다.
- 주요 기능은 피드 삭제 확인 모달, 댓글 인라인 수정, 프로필 이미지 노출, 주식 보유 수량 병합/부분 판매, 은행 경로 조회, 월 수입 기반 소비 분석, 데모 데이터 추가입니다.
- 중요한 부분은 전역 피드 작성 모달의 작성/수정 구분, 저장 후 목록 갱신, 데모/업로드 미디어 파일 관리 입니다.

# [중점적으로 볼 부분]
- 상단 피드 작성 버튼이 어느 라우트에서든 새 글 작성과 기존 글 수정을 정확히 구분하는지
- 피드 작성/수정/삭제 후 목록과 상세 화면이 서버 상태와 즉시 일치하는지
- 삭제 확인 문구가 프론트와 백엔드에서 동일하게 검증되는지
- 주식 보유 수량 추가/부분 판매가 중복 종목 제약과 충돌하지 않는지
- Kakao 지도/모빌리티 API 환경변수와 장애 응답이 실제 실행 환경에서 안전한지
- 발표용 데이터와 일반 업로드 미디어가 저장소에서 명확히 분리되어 있는지

# [리뷰 체크]
- 요구사항 충족: UI/UX 기능은 넓게 추가되었고, 기존 06/23 리뷰의 Kakao JavaScript 환경변수 불일치와 월별 분석 GET 파라미터 검증은 개선되었습니다.
- 예외 처리: 피드 삭제는 서버에서도 확인 문구를 검증하도록 보강되었습니다. 다만 Kakao 경로 원점 좌표 env 값은 settings import 시점에 바로 `float()` 변환되어 잘못된 값에서 앱 시작이 실패할 수 있음.
- 가독성: 화면별 컴포넌트와 API 함수는 기능 단위로 나뉘어 있어 추적 가능합니다. 다만 `MainLayout`의 전역 작성 모달은 route param을 넓게 참조해 작성/수정 의미가 섞여 있습니다.
- 테스트: 필수구현 기능구현 완료.
- 성능/보안: `frontend/.env`는 커밋 대상에서 제외되었지만, `backend/.gitignore`에서 `media/` 제외가 제거되어 실제 업로드성 미디어가 다수 커밋되었습니다.(관통발표시 구현을위해 남겨둠)
- 영향 범위: 피드 작성/수정/삭제, 금융 허브, 주식 보유 현황, 은행 지도, AI 분석, 프로필/친구 피드 전반에 영향이 있습니다.

# [리뷰 결과]
## 반드시 수정
- `frontend/src/layouts/MainLayout.vue`의 `composeId`가 `route.query.composeEdit || route.params.id || null`로 계산됩니다. `/logs/:id` 상세 페이지에서 상단 피드 작성 버튼을 누르면 `compose=1`만 추가되고 기존 `route.params.id`가 그대로 `FeedComposerModal`의 `edit-id`로 전달됩니다. 사용자는 새 글 작성으로 생각하지만 실제로는 현재 로그 수정 모달이 열릴 수 있으므로, `route.name === 'log-edit'` 또는 명시적인 `composeEdit`일 때만 edit id를 넘기도록 제한해야 함.
- `FeedComposerModal` 저장 후 `MainLayout`은 `closeComposer`만 실행하고, `ExpenseFeedView.vue`의 `loadFeed()`는 `onMounted()`에서 한 번만 호출됩니다. `/feed?compose=1`에서 새 피드를 작성하면 서버에는 저장되지만 현재 피드 목록은 자동 갱신되지 않습니다. 저장 성공 이벤트를 피드 목록 재조회나 Pinia store 갱신으로 연결하기.
- `backend/.gitignore`에서 `media/` 제외가 제거되었고 `backend/media/expenses/2026/06/*`, `backend/media/profiles/*` 같은 실제 업로드성 파일이 커밋에 포함되었습니다. 데모용 `backend/media/**/demo/*`와 일반 업로드 산출물을 분리

## 개선 제안
- `backend/config/settings.py`의 `KAKAO_ROUTE_ORIGIN_X`, `KAKAO_ROUTE_ORIGIN_Y`는 settings import 시점에 바로 `float()`로 변환됩니다. 배포 환경변수가 비어 있거나 잘못 들어가면 Django 앱 자체가 시작되지 않으므로 안전 파싱 helper 또는 명확한 설정 검증으로 분리하는 편이 좋습니다.
- 발표용 미디어가 필요하다면 `backend/media`를 직접 추적하기보다 `seed_demo_data`가 fixture 전용 디렉터리나 생성 로직에서 `MEDIA_ROOT`로 복사/생성하도록 정리하는 편이 좋음.
- 피드 저장 후 재조회 문제는 단순 query refresh보다 피드 목록을 store로 올리는 방식이 장기적으로 안전. 작성, 삭제, 좋아요, 댓글 변경이 여러 화면에 걸쳐 반영되기 때문.

## 의도 확인 필요
- `backend/media/expenses/2026/06`와 해시 파일명 프로필 이미지들이 발표에 꼭 필요한 고정 데모 자산인지 확인이 필요. 일반 업로드 결과라면 저장소에서 제거하는 편이 맞음.
- 전역 작성 버튼이 상세 페이지에서도 항상 새 글 작성이어야 하는지, 아니면 특정 상황에서 현재 글 편집 진입을 의도한 것인지 확인이 필요. 현재 UI 라벨은 피드작성이라 새 글 작성으로 해석됨.
- `seed_demo_data.py`에 데모 사용자 공통 비밀번호와 대량 데모 데이터가 들어 있습니다. 발표용 의도라면 README나 실행 가이드에 시연 전용 계정임을 명확히 남기는 것이 좋습니다.

# [검증 결과]

- 필수 기능 구현 완료

# [다음 리뷰]
- 다음 리뷰 대상: 1순위는 전역 피드 작성/수정 라우팅과 저장 후 목록 갱신, 2순위는 `backend/media`와 seed/demo asset 정리, 3순위는 Kakao Mobility 경로 조회의 환경변수/장애 처리로 진행.
