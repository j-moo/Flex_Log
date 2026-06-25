# [오늘 리뷰 대상]
PR/커밋: `e80c3e1854830d83db125968792a0beb1b4d7ac3`

# [변경 의도]
- 2026-06-25 기준 Flex Log 프로젝트의 백엔드/프론트엔드 코드 안정성을 점검한 리뷰입니다.
- 주요 검토 범위는 JWT 인증 갱신 흐름, 저장소 추적 파일 관리, 알림 중복 방지, 피드 성능, 댓글 검증, 주식 화면의 목업 데이터 처리, 업로드 파일 검증, CORS 설정, 저장소 경로 대소문자 일관성입니다.
- 이번 요청에서는 `frontend/src/components/feed/CommentSection.vue`의 댓글 행 정렬 문제를 수정하여 댓글 첫 줄과 수정/삭제 버튼의 수평 기준선을 맞춘 내용도 함께 반영되었습니다.

# [중점적으로 볼 부분]
- Access Token 만료 시 여러 API 요청이 동시에 401을 받았을 때 refresh token rotation이 안전하게 처리되는지
- 알림 생성 시 같은 `dedupe_key`를 가진 알림이 중복 생성되지 않도록 DB 레벨에서 보장되는지
- 피드 목록 API에서 좋아요 여부, 좋아요 수, 댓글 수, 미디어 응답이 N+1 쿼리나 과도한 응답 크기를 만들지 않는지
- 댓글 길이 제한과 공백 댓글 검증이 프론트엔드뿐 아니라 백엔드에서도 적용되는지
- 주식 화면에서 목업 데이터와 실제 데이터가 사용자에게 혼동되지 않도록 분리되어 있는지
- 업로드 파일 검증이 단순 확장자 검증에만 의존하지 않는지
- CORS 설정과 저장소 경로 대소문자가 협업/배포 환경에서도 안전한지

# [리뷰 체크]
- 요구사항 충족: 로그인, 피드, 알림, 프로필, 주식 화면 등 주요 기능은 동작 가능한 상태로 보이나, 인증 갱신 경합과 목업 데이터 노출처럼 실제 사용 흐름에서 불안정해질 수 있는 부분이 남아 있음.
- 예외 처리: refresh token 갱신 실패 시 세션을 지우는 흐름은 있으나, 동시 401 상황에서 요청들이 각각 refresh를 시도해 정상 사용자도 로그아웃될 수 있음. 외부/업로드/피드 응답에서도 운영 상황을 고려한 방어 로직 보강이 필요함.
- 가독성: 앱별 파일 위치와 문제 지점은 비교적 명확하게 분리되어 있으나, `Backend/`와 `backend/` 경로가 혼재되어 협업자 환경이나 Linux CI에서 혼란이 생길 수 있음.
- 테스트: 테스트 통과
- 성능/보안: 피드 목록 응답도 N+1 쿼리와 base64 미디어 응답으로 커질 가능성이 있음.
- 영향 범위: 인증, 알림, 피드, 댓글, 업로드 미디어, 주식 화면, CORS, 저장소 관리 등 프로젝트 전반에 영향이 있음.

# [리뷰 결과]
## 반드시 수정
- `frontend/src/api/client.js`와 `frontend/src/stores/account.js`의 refresh token 갱신 흐름을 single-flight 방식으로 수정해야 함. 현재는 여러 API가 동시에 401을 받으면 각 요청이 독립적으로 `refreshAccessToken()`을 호출하고, 첫 요청이 refresh token을 회전/폐기한 뒤 나머지 요청이 폐기된 refresh token으로 갱신을 시도할 수 있음. 전역 `refreshPromise`를 두고 갱신 중인 요청은 같은 Promise를 기다리도록 변경하기.
- 루트 `.gitignore`를 보강하여 `Backend/`와 `backend/` 대소문자 양쪽 경로를 모두 커버해야 함. Windows에서는 같은 경로처럼 보여도 Linux/CI 환경에서는 다른 디렉터리로 인식될 수 있음.
- 알림 중복 방지를 DB 레벨에서 보장해야 함. 현재는 `dedupe_key`를 `filter(...).first()` 후 `create()` 또는 update하는 방식이라 동시에 알림이 생성되면 중복 데이터가 생길 수 있음. 빈 `dedupe_key`를 제외한 조건부 `UniqueConstraint(user, dedupe_key)`와 `update_or_create` 또는 트랜잭션 기반 처리를 검토하기.

## 개선 제안
- 피드 목록 API의 좋아요 여부, 좋아요 수, 댓글 수 계산을 `Exists`, `Count` annotation으로 처리해 N+1 쿼리를 줄이기. 현재 `get_is_liked()`가 객체마다 `obj.likes.filter(user=request.user).exists()`를 호출할 가능성이 있음.
- 미디어 응답은 가능하면 URL 방식으로 통일하고, 과거 `BinaryField` 기반 `base64` data URL 응답은 마이그레이션 후 제거하거나 상세 API에서만 제한적으로 사용하기. 공개 피드 목록에는 pagination을 강제하는 편이 좋음.
- `CommentSerializer`에 `content = serializers.CharField(max_length=500, trim_whitespace=True)`를 선언하고, 공백-only 댓글을 거부하는 검증을 추가하기. 가능하면 모델에도 `MaxLengthValidator`를 두기.
- 주식 화면의 목업 데이터는 명시적인 데모 모드 환경변수에서만 활성화하기. 운영 기본값에서는 빈 상태 또는 오류 상태를 표시하고, 목업 모드에서는 매수/판매 액션을 비활성화하거나 데모 배지를 강하게 표시하기.
- 업로드 파일 검증을 확장자 중심에서 MIME 또는 파일 시그니처 기반 검증으로 보강하기. 이미지에는 Pillow 기반 검증을, 동영상에는 허용 MIME 검증을 추가하는 것이 좋음.
- 개발용 CORS regex는 `DEBUG`일 때만 열거나 환경변수 기반으로 전환하기. 현재 `localhost:5170-5179`, `127.0.0.1:5170-5179`가 설정값과 무관하게 허용됨.

## 의도 확인 필요
- refresh token rotation을 유지할 것인지, 아니면 프론트 구현 난이도를 낮추기 위해 refresh token rotation 정책을 완화할 것인지 확인이 필요함. 유지한다면 single-flight 갱신 큐는 사실상 필수임.
- `Backend/media`에 포함된 84개 파일 중 데모 시연에 필요한 파일과 개인 업로드/테스트 파일을 구분해야 함. 필요한 파일은 `static/demo` 또는 fixture와 연결된 명시적인 데모 자산으로 이동하는 편이 안전함.
- 주식 화면에서 API 실패 시 예시 종목을 보여주는 정책이 의도된 것인지 확인이 필요함. 금융/자산 화면은 사용자가 실제 데이터로 오해하기 쉬우므로 기본 운영 모드에서는 목업을 숨기는 것이 적절함.
- 기존 `Backend/` 경로를 `backend/`로 통일할 경우 팀원 로컬 환경, import 경로, README 명령어, 배포 스크립트에 영향이 없는지 확인해야 함.

# [이번 요청으로 반영한 수정]
- `frontend/src/components/feed/CommentSection.vue`에서 피드 댓글 행의 grid 정렬을 `baseline`으로 변경.
- 수정/삭제 메뉴의 자체 baseline 정렬과 button line-height를 조정.
- 결과적으로 댓글 첫 줄과 수정/삭제 버튼이 같은 수평 기준선에 놓이도록 개선.

# [검증 결과]
- `python manage.py test` in `backend`: 통과, 68 tests.
- `npm.cmd run build` in `frontend`: 통과.
- `git diff --check`: 공백 오류 없음.
- 참고: Windows에서 `CommentSection.vue`의 LF가 다음 Git 처리 시 CRLF로 바뀔 수 있다는 경고가 있음.

# [다음 리뷰]
- 다음 리뷰 대상 1순위: refresh token single-flight 처리와 인증 갱신 안정성.
- 다음 리뷰 대상 2순위: 중복 알림 DB 유니크 제약 및 알림 생성 로직.
- 다음 리뷰 대상 3순위: 피드 serializer의 annotation/pagination 적용과 댓글 서버 검증 추가.
- 다음 리뷰 대상 4순위: 운영 모드에서 목업 주식 데이터가 노출되지 않도록 데모 모드 분리.
