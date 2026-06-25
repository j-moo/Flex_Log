# Flex Log 코드 리뷰

작성일: 2026-06-25

## 주요 발견 사항

### High: 동시 401 응답에서 refresh token rotation 경합으로 사용자가 로그아웃될 수 있음

- 위치: `backend/config/settings.py:150-151`, `frontend/src/api/client.js:28-43`, `frontend/src/stores/account.js:61`
- 증상: 백엔드는 `ROTATE_REFRESH_TOKENS=True`, `BLACKLIST_AFTER_ROTATION=True`로 refresh token을 회전/폐기합니다. 그런데 axios 응답 인터셉터는 401 요청마다 독립적으로 `account.refreshAccessToken()`을 호출합니다. 여러 API가 동시에 401을 받으면 첫 요청이 refresh token을 회전시키고, 나머지 요청은 이미 폐기된 refresh token으로 갱신을 시도한 뒤 `account.clearSession()`을 호출할 수 있습니다.
- 영향: 토큰 만료 시점에 피드/알림/프로필 API가 동시에 실패하면 정상 사용자가 강제 로그아웃되거나 일부 요청만 재시도되는 불안정한 상태가 됩니다.
- 권장 수정: 전역 `refreshPromise`를 둔 single-flight 갱신 큐를 만들고, 갱신 중인 요청은 같은 Promise를 기다리게 하세요. refresh 실패 시에만 세션을 지우고, logout은 refresh 인터셉터와 분리해 현재 refresh token을 정확히 폐기하도록 처리해야 합니다.

### High: DB, 업로드 미디어, pycache가 저장소에 추적되고 있음

- 위치: `Backend/db.sqlite3`, `Backend/media/**`, `Backend/**/__pycache__/*.pyc`, `backend/.gitignore:3-5`
- 증상: `.gitignore`는 `db.sqlite3`, `__pycache__/`, `*.py[cod]`를 무시하지만 이미 Git index에 들어간 파일은 계속 추적됩니다. 현재 `Backend/db.sqlite3`, pyc 37개, `Backend/media` 파일 84개가 추적되고 있습니다.
- 영향: 개인 업로드 이미지/영상과 로컬 DB가 저장소에 남아 개인정보, 테스트 데이터, 대용량 바이너리 이슈를 만들 수 있습니다. 또한 테스트 실행만으로 pyc diff가 생겨 리뷰 노이즈가 반복됩니다.
- 권장 수정: 필요한 데모 자산만 `fixtures` 또는 `static/demo`로 명시 이동하고, 나머지는 `git rm --cached`로 추적 해제하세요. 루트 `.gitignore`를 추가해 `Backend/`와 `backend/` 대소문자 양쪽 모두를 커버하는 규칙을 두는 편이 안전합니다.

### Medium: 알림 dedupe가 DB에서 원자적으로 보장되지 않음

- 위치: `backend/notifications/helpers.py:29-34`, `backend/notifications/helpers.py:75-87`, `backend/notifications/models.py:33`, `backend/notifications/models.py:40-42`
- 증상: `dedupe_key` 중복 방지는 `filter(...).first()` 후 `create()` 또는 update로 처리됩니다. 모델에는 `(user, dedupe_key)` 인덱스만 있고 유니크 제약은 없습니다.
- 영향: 동시에 좋아요/댓글/추천 알림이 생성되면 같은 `dedupe_key`를 가진 알림이 여러 개 생길 수 있습니다.
- 권장 수정: 빈 `dedupe_key`를 제외한 조건부 `UniqueConstraint(user, dedupe_key)`를 추가하고, `update_or_create` 또는 트랜잭션 기반 `select_for_update` 흐름으로 바꾸세요.

### Medium: 피드 직렬화가 N+1 쿼리와 큰 응답을 만들 수 있음

- 위치: `backend/expenses/views.py:64-69`, `backend/expenses/serializers.py:99-103`, `backend/expenses/serializers.py:118-135`
- 증상: 목록 queryset에서 `likes`를 prefetch하지만 `get_is_liked()`는 `obj.likes.filter(user=request.user).exists()`를 매 객체마다 호출할 수 있습니다. 또한 미디어마다 `storage.exists()`를 확인하고, `media_data`가 있으면 base64 data URL을 응답에 포함합니다.
- 영향: 피드 카드가 많아지면 DB 쿼리와 파일 스토리지 I/O가 증가합니다. 과거 BinaryField 미디어가 남아 있으면 목록 API 응답 크기가 급격히 커져 모바일 피드가 느려질 수 있습니다.
- 권장 수정: `Exists`와 `Count` annotation으로 `is_liked`, `like_count`, `comment_count`를 계산하세요. 미디어는 URL 응답으로 통일하고, BinaryField fallback은 마이그레이션 후 제거하거나 상세 API에만 제한하세요. 공개 피드 목록에는 항상 pagination을 강제하는 것이 좋습니다.

### Medium: 댓글 길이 제한이 프론트엔드에만 있음

- 위치: `backend/expenses/models.py:130`, `backend/expenses/serializers.py:205-233`, `frontend/src/components/feed/CommentSection.vue:154`, `frontend/src/components/feed/CommentSection.vue:177`
- 증상: 프론트 입력은 `maxlength="500"`이지만 백엔드 `Comment.content`는 `TextField`이고 serializer에도 최대 길이 검증이 없습니다.
- 영향: API를 직접 호출하면 매우 긴 댓글이 저장되어 응답 크기, 렌더링, 알림 메시지 구성에 부담을 줄 수 있습니다.
- 권장 수정: `CommentSerializer`에 `content = serializers.CharField(max_length=500, trim_whitespace=True)`를 선언하고 공백-only 댓글을 거부하는 테스트를 추가하세요. 가능하면 모델에도 `MaxLengthValidator`를 두세요.

### Medium: 주식 화면에서 목업 데이터가 실제 데이터 흐름에 섞임

- 위치: `frontend/src/views/StockHoldingView.vue:257-273`, `frontend/src/views/StockHoldingView.vue:403-407`, `frontend/src/views/StockHoldingView.vue:440`, `frontend/src/views/StockHoldingView.vue:505`
- 증상: 보유 주식 API가 비어 있거나 실패하면 예시 종목을 화면에 넣고, 판매 액션도 목업 상태에서는 로컬 배열을 수정합니다.
- 영향: 금융/자산 화면에서 사용자가 실제 보유 종목과 예시 데이터를 혼동할 수 있습니다. API 장애가 빈 상태처럼 가려져 운영 문제 발견도 늦어집니다.
- 권장 수정: 목업 데이터는 명시적인 데모 모드 환경변수에서만 활성화하세요. 운영 기본값은 빈 상태 또는 오류 상태로 보여주고, 목업 모드에서는 매수/판매 액션을 비활성화하거나 별도 배지를 더 강하게 표시하세요.

### Low: 업로드 파일 검증이 확장자 중심임

- 위치: `backend/expenses/serializers.py:189-197`
- 증상: 업로드 검증은 크기와 파일명 확장자를 확인하지만 실제 MIME/content signature는 확인하지 않습니다.
- 영향: 확장자를 위장한 파일이 저장될 수 있습니다. 배포 환경에서 media를 직접 서빙하면 보안 정책 설정에 따라 위험이 커질 수 있습니다.
- 권장 수정: Pillow/파일 시그니처 기반 검증을 추가하고, 동영상은 허용 MIME을 명시적으로 확인하세요. media 서빙 시 `Content-Type`, `Content-Disposition`, 바이러스 스캔 정책도 정리해야 합니다.

### Low: 개발 CORS regex가 설정값과 무관하게 넓게 열려 있음

- 위치: `backend/config/settings.py:161-172`
- 증상: `CORS_ALLOWED_ORIGIN_REGEXES`가 `localhost:5170-5179`, `127.0.0.1:5170-5179`를 항상 허용합니다.
- 영향: 토큰은 sessionStorage 기반이라 cookie 기반 CSRF와는 결이 다르지만, 운영 설정에서 의도하지 않은 로컬 origin이 허용될 수 있습니다.
- 권장 수정: DEBUG일 때만 regex를 추가하거나, `CORS_ALLOWED_ORIGIN_REGEXES`도 환경변수 기반으로 전환하세요.

### Low: 저장소 경로 대소문자가 혼재됨

- 위치: Git index의 `Backend/**`, 작업 트리의 `backend/**`
- 증상: Windows에서는 같은 경로처럼 동작하지만, case-sensitive 환경에서는 `Backend`와 `backend`가 다른 디렉터리입니다.
- 영향: Linux CI, Docker, 협업자 환경에서 문서/스크립트의 `backend` 경로와 Git index의 `Backend` 경로가 어긋날 수 있습니다.
- 권장 수정: `git mv`를 이용해 한 가지 표기로 통일하세요. 일반적으로 README와 실제 명령에 맞춰 `backend/` 소문자로 정리하는 편이 낫습니다.

## 이번 요청으로 반영한 수정

- 위치: `frontend/src/components/feed/CommentSection.vue:230`, `frontend/src/components/feed/CommentSection.vue:252`, `frontend/src/components/feed/CommentSection.vue:264`
- 내용: 피드 댓글 행의 grid 정렬을 `baseline`으로 바꾸고, 수정/삭제 메뉴의 자체 baseline 정렬과 button line-height를 맞췄습니다. 이로써 댓글 첫 줄과 수정/삭제 버튼이 같은 수평 기준선에 놓입니다.

## 검증 결과

- `python manage.py test` in `backend`: 통과, 68 tests.
- `npm.cmd run build` in `frontend`: 통과.
- `git diff --check`: 공백 오류 없음. 단, Windows에서 `CommentSection.vue`의 LF가 다음 Git 처리 시 CRLF로 바뀔 수 있다는 경고가 있습니다.

## 권장 처리 순서

1. refresh token single-flight 처리와 중복 알림 DB 유니크 제약을 먼저 수정하세요.
2. 추적 중인 DB, pyc, 업로드 미디어를 저장소에서 제거하고 루트 `.gitignore`를 보강하세요.
3. 피드 serializer의 annotation/pagination과 댓글 서버 검증을 추가하세요.
4. 운영 모드에서 목업 주식 데이터가 노출되지 않도록 데모 모드를 분리하세요.
