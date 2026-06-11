# Flex-log Git Branch 전략

## 1. 브랜치 전략 도입 배경

Flex-log는 2명이 2주 동안 진행하는 금융 웹 애플리케이션 프로젝트이다.
짧은 기간 안에 기획, 설계, 백엔드, 프론트엔드, 문서화 작업을 동시에 진행해야 하므로 Git을 활용한 명확한 형상 관리 전략이 필요하다.

특히 소비 기록, 소비 분석, 개선방안 제시 기능은 백엔드 API와 프론트엔드 화면이 밀접하게 연결되어 있기 때문에, 각자 작업한 코드가 충돌하거나 서로의 작업을 덮어쓰는 상황을 방지해야 한다.

따라서 Flex-log 프로젝트에서는 다음 목표를 기준으로 브랜치 전략을 수립하였다.

* 최종 안정 버전 보호
* 주차별 통합 코드 관리
* 개인 작업 공간 분리
* Pull Request 기반 코드 검토
* 충돌 최소화
* 문서와 코드 변경 이력 관리

---

## 2. 브랜치 구조

Flex-log 프로젝트에서는 다음 브랜치를 사용한다.

```text
main
project/week1
project/week2
feature/작업내용-githubID
docs/문서명-githubID
fix/수정내용-githubID
```

---

## 3. 브랜치별 역할

## 3.1 main 브랜치

`main` 브랜치는 프로젝트의 최종 안정 버전을 관리하는 브랜치이다.

### 역할

* 최종 제출 가능한 코드만 유지
* 직접 커밋 금지
* 검증 완료된 project 브랜치만 merge
* 발표 및 포트폴리오 기준 브랜치

### 규칙

```text
main 브랜치에는 직접 push하지 않는다.
모든 변경사항은 Pull Request를 통해 반영한다.
```

---

## 3.2 project/week 브랜치

`project/week1`, `project/week2` 브랜치는 주차별 통합 브랜치이다.

### 역할

* 해당 주차의 작업 결과를 모으는 통합 공간
* 각자 feature 브랜치 작업물이 합쳐지는 기준 브랜치
* 주차별 기능 테스트와 통합 테스트 대상

### 브랜치 예시

```text
project/week1
project/week2
```

### 사용 기준

```text
1주차 작업은 project/week1에서 진행한다.
2주차 작업은 project/week2에서 진행한다.
```

### 중요 규칙

```text
새로운 주차의 project 브랜치는 항상 main에서 생성한다.
이전 주차 project 브랜치에서 새 주차 브랜치를 만들지 않는다.
```

이 규칙을 적용하는 이유는 이전 주차 작업 중 승인되지 않은 코드나 불안정한 코드가 다음 주차 작업에 섞이는 것을 방지하기 위해서이다.

---

## 3.3 feature 브랜치

`feature` 브랜치는 개인 기능 작업 브랜치이다.

### 역할

* 하루 또는 하나의 기능 단위 작업 공간
* 개인 작업 중인 코드 보호
* 기능 완성 후 project 브랜치로 Pull Request 생성

### 이름 규칙

```text
feature/작업내용-githubID
```

### 예시

```text
feature/backend-auth-jmkim
feature/backend-expense-jmkim
feature/frontend-feed-kdkim
feature/frontend-analysis-kdkim
```

### 규칙

```text
feature 브랜치는 project/week 브랜치에서 생성한다.
작업 완료 후 project/week 브랜치로 Pull Request를 보낸다.
merge 완료 후 feature 브랜치는 삭제한다.
```

---

## 3.4 docs 브랜치

`docs` 브랜치는 문서 작업용 브랜치이다.

### 역할

* README 작성
* 프로젝트 선정 배경 정리
* 요구사항 정의
* ERD 문서 작성
* API 명세 작성
* WBS 작성
* 회고 작성

### 이름 규칙

```text
docs/문서명-githubID
```

### 예시

```text
docs/readme-jmkim
docs/erd-kdkim
docs/api-spec-jmkim
docs/retrospective-kdkim
```

---

## 3.5 fix 브랜치

`fix` 브랜치는 버그 수정용 브랜치이다.

### 역할

* 이미지 업로드 오류 수정
* API 응답 형식 오류 수정
* 로그인 유지 오류 수정
* 차트 데이터 계산 오류 수정
* CSS 깨짐 수정

### 이름 규칙

```text
fix/수정내용-githubID
```

### 예시

```text
fix/image-upload-jmkim
fix/login-token-kdkim
fix/category-chart-jmkim
```

---

# 4. 2주 프로젝트 브랜치 흐름

## 4.1 1주차 흐름

```text
main
  └── project/week1
        ├── feature/backend-auth-jmkim
        ├── feature/backend-expense-jmkim
        ├── feature/frontend-layout-kdkim
        ├── feature/frontend-expense-kdkim
        └── docs/requirements-kdkim
```

1주차에는 프로젝트 기획, ERD, API 명세, 백엔드 기본 기능, 프론트 기본 화면을 구현한다.

1주차가 끝나면 `project/week1` 브랜치에서 통합 테스트를 진행하고, 안정화된 코드를 `main`으로 merge한다.

---

## 4.2 2주차 흐름

```text
main
  └── project/week2
        ├── feature/backend-analysis-jmkim
        ├── feature/backend-feedback-jmkim
        ├── feature/frontend-analysis-kdkim
        ├── feature/frontend-feedback-kdkim
        └── docs/final-readme-kdkim
```

2주차에는 소비 분석, 개선방안 제시, 차트 시각화, 최종 README, 트러블슈팅 문서, 회고를 작성한다.

2주차가 끝나면 `project/week2` 브랜치에서 최종 테스트를 진행하고, 검증 완료 후 `main`으로 merge한다.

---

# 5. 개발자의 하루 작업 흐름

## 5.1 작업 시작 전

항상 최신 `project/week` 브랜치에서 작업을 시작한다.

```bash
git checkout project/week1
git pull origin project/week1
```

그다음 개인 작업 브랜치를 생성한다.

```bash
git checkout -b feature/backend-expense-jmkim
```

---

## 5.2 작업 중

작업은 본인의 feature 브랜치에서만 진행한다.

```bash
git add .
git commit -m "feat: 소비 로그 모델 및 작성 API 구현"
```

커밋은 너무 크게 묶지 않고, 기능 단위로 나누어 작성한다.

---

## 5.3 PR 올리기 전

Pull Request를 올리기 전에 반드시 최신 `project/week` 브랜치 내용을 가져와 충돌을 먼저 해결한다.

```bash
git checkout project/week1
git pull origin project/week1

git checkout feature/backend-expense-jmkim
git merge project/week1
```

충돌이 발생하면 본인 브랜치에서 먼저 해결한 뒤 다시 커밋한다.

```bash
git add .
git commit -m "fix: project 브랜치 병합 충돌 해결"
```

---

## 5.4 PR 생성

작업 완료 후 다음 방향으로 Pull Request를 생성한다.

```text
feature/작업브랜치 → project/week1
```

또는 문서 작업의 경우:

```text
docs/문서브랜치 → project/week1
```

---

## 5.5 PR 승인 후

리뷰어가 확인한 뒤 merge한다.
merge가 완료된 feature 브랜치는 삭제한다.

```text
작업 완료 브랜치는 남기지 않고 삭제하여 브랜치 목록을 깔끔하게 유지한다.
```

---

# 6. Pull Request 규칙

## 6.1 PR 제목 규칙

PR 제목은 다음 형식을 따른다.

```text
[타입] 작업 내용
```

### 예시

```text
[feat] 소비 로그 CRUD API 구현
[feat] 소비 분석 차트 화면 구현
[docs] ERD 설계 문서 작성
[fix] 이미지 업로드 경로 오류 수정
[refactor] 소비 분석 로직 분리
```

---

## 6.2 PR 설명 템플릿

```markdown
## 작업 내용

- 

## 변경 파일

- 

## 테스트 내용

- 

## 확인이 필요한 부분

- 

## 스크린샷

필요 시 첨부
```

---

# 7. 커밋 메시지 규칙

커밋 메시지는 다음 형식을 사용한다.

```text
타입: 작업 내용
```

## 7.1 타입 종류

| 타입       | 의미                       |
| -------- | ------------------------ |
| feat     | 새로운 기능 추가                |
| fix      | 버그 수정                    |
| docs     | 문서 작성 및 수정               |
| style    | 코드 포맷, CSS 등 기능 변경 없는 수정 |
| refactor | 기능 변화 없는 코드 구조 개선        |
| test     | 테스트 코드 추가                |
| chore    | 설정, 패키지, 빌드 관련 작업        |

## 7.2 커밋 예시

```bash
git commit -m "docs: 프로젝트 선정 배경 정리"
git commit -m "docs: ERD 설계 문서 작성"
git commit -m "feat: 회원가입 로그인 API 구현"
git commit -m "feat: 소비 로그 CRUD API 구현"
git commit -m "feat: 소비 분석 차트 화면 구현"
git commit -m "fix: 이미지 업로드 경로 오류 수정"
git commit -m "refactor: 소비 분석 로직 함수 분리"
```

---

# 8. 충돌 방지 규칙

2인 프로젝트에서 충돌을 줄이기 위해 다음 규칙을 적용한다.

## 8.1 같은 파일 동시 수정 최소화

다음 파일은 충돌이 자주 발생할 수 있으므로 수정 전 공유한다.

```text
README.md
settings.py
urls.py
router/index.js
axios.js
package.json
requirements.txt
```

## 8.2 작업 구역 분리

백엔드 담당자는 주로 다음 영역을 수정한다.

```text
backend/
docs/api_spec.md
docs/erd.md
```

프론트엔드 담당자는 주로 다음 영역을 수정한다.

```text
frontend/
docs/screen_flow.md
README.md
```

공통 문서는 작업 전 미리 말하고 수정한다.

---

## 8.3 PR 전 최신 코드 반영

Pull Request를 올리기 전에는 반드시 `project/week` 브랜치의 최신 코드를 본인 브랜치에 반영한다.

```text
PR 전 최신 project 브랜치 반영은 필수이다.
```

---

# 9. 승인 지연 작업 처리

당일 작업이 완료되었지만 리뷰 또는 merge가 지연될 수 있다.

이 경우 다음 규칙을 따른다.

```text
승인되지 않은 작업을 기준으로 새로운 브랜치를 만들지 않는다.
기존 feature 브랜치에서 계속 수정한다.
승인 완료 후 project/week 브랜치에 merge한다.
```

예시:

```text
feature/backend-expense-jmkim 브랜치의 PR 승인이 지연된 경우,
feature/backend-expense-jmkim 브랜치에서 계속 수정한다.
새로운 feature/backend-expense-v2 브랜치를 만들지 않는다.
```

---

# 10. 통합 및 배포 규칙

## 10.1 주차별 통합

각 주차 마지막에는 `project/week` 브랜치에서 통합 테스트를 진행한다.

확인 항목은 다음과 같다.

* 회원가입 가능 여부
* 로그인 가능 여부
* 소비 로그 작성 가능 여부
* 소비 로그 조회 가능 여부
* 소비 로그 수정/삭제 권한 확인
* 월별 소비 분석 결과 확인
* 카테고리별 소비 분석 결과 확인
* 개선방안 출력 여부
* 프론트와 백엔드 API 연동 여부

---

## 10.2 main 병합

통합 테스트가 완료된 `project/week` 브랜치만 `main`으로 merge한다.

```text
project/week1 → main
project/week2 → main
```

---

# 11. 일일 회의 규칙

매일 작업 시작 전 또는 종료 전에 10분 정도 짧게 공유한다.

## 공유 항목

```text
1. 어제 한 일
2. 오늘 할 일
3. 막힌 점
4. 상대방에게 필요한 것
```

## 예시

```text
Backend 담당:
어제 소비 로그 모델을 만들었고, 오늘 CRUD API를 구현할 예정입니다.
프론트에서 필요한 소비 로그 응답 필드를 확인해야 합니다.

Frontend 담당:
어제 피드 카드 UI를 만들었고, 오늘 소비 로그 작성 화면을 만들 예정입니다.
카테고리 목록 API 응답 형식이 필요합니다.
```

---

# 12. Flex-log 브랜치 전략 요약

Flex-log 프로젝트의 브랜치 전략은 다음과 같다.

```text
main
- 최종 안정 버전

project/week1
- 1주차 통합 브랜치

project/week2
- 2주차 통합 브랜치

feature/*
- 개인 기능 작업 브랜치

docs/*
- 문서 작업 브랜치

fix/*
- 버그 수정 브랜치
```

핵심 규칙은 다음과 같다.

```text
1. main에는 직접 push하지 않는다.
2. feature 브랜치는 project/week 브랜치에서 생성한다.
3. PR 전 project/week 최신 코드를 본인 브랜치에 반영한다.
4. 승인되지 않은 작업은 기존 브랜치에서 계속 수정한다.
5. 새로운 주차 project 브랜치는 항상 main에서 생성한다.
6. merge 완료된 feature 브랜치는 삭제한다.
7. 코드뿐 아니라 문서도 Git으로 관리한다.
```
