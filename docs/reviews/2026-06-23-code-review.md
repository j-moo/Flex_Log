# 2026-06-23 코드 리뷰

## 오늘 리뷰 대상

PR/커밋: `e171fb7^..7991e93` 2026-06-23 변경 묶음

> 참고: 요청에 포함된 `d02f16b feature:back&front` 커밋은 현재 로컬 저장소에서 찾을 수 없어, 실제 확인 가능한 변경 범위 기준으로 리뷰했습니다.

## 변경 의도

프론트 UI/UX 개선과 함께 지출 피드 작성/삭제, 프로필 이미지, 금융 허브, 은행 지도/경로, 주식 보유 현황, 월별 분석 보강, 데모 데이터/미디어 추가가 포함된 대규모 기능 변경입니다.

## 중점적으로 볼 부분

- 사용자별 지출/피드 수정 및 삭제 권한
- 피드 작성 모달과 라우팅 계약
- 미디어 파일 저장 및 응답 방식
- 외부 API 실패 처리와 환경변수 계약
- 커밋에 포함된 DB, 미디어, 캐시 파일 관리
- 프론트 빌드와 백엔드 테스트 재현성

## 리뷰 체크

- 요구사항 충족: 주요 기능 골격은 추가됐고 프론트 빌드/백엔드 테스트는 통과합니다. 다만 피드 작성 모달 라우팅에서 상세 페이지의 새 작성 동작이 수정 모드로 열릴 수 있습니다.
- 예외 처리: 삭제 확인, 카카오/키움 API 예외 처리는 일부 보강됐습니다. 미디어 응답과 리스트 API 성능 예외는 추가 검토가 필요합니다.
- 가독성: 앱별 구조는 유지됐지만 변경량이 커서 리뷰 단위가 큽니다.
- 테스트: 성공
- 성능/보안: `Backend/media/**`, `Backend/db.sqlite3`, `__pycache__/*.pyc`가 커밋되어 저장소 위생과 데이터 노출 위험이 있습니다.
- 영향 범위: 인증 사용자 피드, 프로필, 금융, 지도, 주식, 분석, 미디어 업로드 전반에 영향이 큽니다.

## 리뷰 결과

### 반드시 수정

`frontend/src/layouts/MainLayout.vue`의 `composeId`가 `route.params.id`를 항상 사용합니다. `/logs/:id` 상세 페이지에서 상단 피드 작성 버튼을 누르면 새 작성이 아니라 현재 로그 수정 모달로 열릴 수 있습니다. `log-edit` 라우트에서만 `route.params.id`를 사용하도록 제한해야 합니다.

피드 저장 후 목록 갱신이 되지 않습니다. `FeedComposerModal` 저장 이벤트가 `closeComposer`만 호출하고, `ExpenseFeedView.vue`는 `onMounted`에서만 피드를 다시 불러옵니다. `/feed?compose=1`에서 새 글을 저장하면 새로고침 전까지 목록에 반영되지 않을 수 있으므로 저장 후 `loadFeed()`가 실행되도록 이벤트 흐름을 연결해야 합니다.

`Backend/.gitignore`에서 `media/`가 제거됐고, `Backend/media/**`, `Backend/db.sqlite3`, `__pycache__/*.pyc`가 커밋에 포함됐습니다. 업로드 파일, 로컬 DB, 파이썬 캐시는 저장소에서 제거하고 ignore 규칙을 복구해야 합니다.

### 개선 제안

`Backend/expenses/serializers.py`에서 미디어 파일 존재 확인을 객체마다 수행하고, `media_data`가 있으면 base64 data URL로 응답합니다. 피드 목록이 커질수록 파일 스토리지 I/O와 응답 크기가 커질 수 있으므로 FileField URL 응답 방식으로 단순화하거나 pagination을 추가하는 것이 좋습니다.

`git diff --check`에서 `Backend/.gitignore` EOF blank line 문제가 잡힙니다. 작은 문제지만 CI lint/check에 걸릴 수 있으므로 정리하는 편이 좋습니다.

### 의도 확인 필요

피드 미디어를 DB BinaryField로 저장하려는 의도가 있는지 확인이 필요합니다. 배포 환경에서는 DB 용량, 백업 크기, 응답 지연에 직접 영향을 줍니다.

데모 미디어와 실제 업로드로 보이는 미디어 파일을 저장소에 포함한 것이 시연 목적의 의도된 변경인지 확인이 필요합니다. 시연 자산이라면 별도 fixtures/static 경로와 명확한 ignore 정책이 필요합니다.

## 검증 결과

- `npm.cmd run build` in `frontend`: 성공
- `.\venv\Scripts\python.exe manage.py test` in `Backend`: 성공, 50 tests
- `git diff --check e171fb7^ 7991e93`: 실패, `Backend/.gitignore:6 new blank line at EOF`
- `d02f16b`: 로컬 저장소에서 찾을 수 없어 해당 커밋 단독 검증은 불가

## 다음 리뷰

다음 리뷰 대상: 1순위는 피드 작성/수정/삭제 라우팅과 데이터 갱신 흐름, 2순위는 미디어 업로드/응답 방식, 3순위는 저장소에 포함된 DB/미디어/캐시 파일 정리입니다.
