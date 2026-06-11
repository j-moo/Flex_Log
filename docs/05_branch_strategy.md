# Flex-log Git Branch 전략

> 본 문서는 SSAFY 멘토 칼럼에서 **좋은길벗** 닉네임의 멘토님이 작성한 **Git을 활용한 형상관리 사례**를 참고하여 작성하였다.
> 해당 칼럼에서 소개한 브랜치 운영 방식은 팀 규모가 커지고 협업이 많아질수록 발생할 수 있는 소스 충돌과 관리 어려움을 줄이기 위한 사례이다.
> Flex-log 프로젝트는 2인 2주 프로젝트라는 특성에 맞게 해당 사례를 그대로 적용하기보다, 프로젝트 규모와 일정에 맞게 단순화하여 브랜치 전략을 수립하였다.

---

## 1. 브랜치 전략 도입 배경

Flex-log는 2명이 2주 동안 진행하는 금융 웹 애플리케이션 프로젝트이다.

짧은 기간 안에 기획, 설계, 백엔드, 프론트엔드, 문서화 작업을 동시에 진행해야 하므로 Git을 활용한 명확한 형상 관리 전략이 필요하다.

특히 소비 기록, 소비 분석, 개선방안 제시 기능은 백엔드 API와 프론트엔드 화면이 밀접하게 연결되어 있다. 따라서 각자 작업한 코드가 충돌하거나 서로의 작업을 덮어쓰는 상황을 방지하기 위해 브랜치 전략을 수립하였다.

Flex-log 프로젝트의 브랜치 전략 목표는 다음과 같다.

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
master
project/week1
project/week2
feature/작업내용-githubID
docs/문서명-githubID
fix/수정내용-githubID
```

브랜치의 큰 흐름은 다음과 같다.

```text
master
  ├── project/week1
  │     ├── feature/*
  │     ├── docs/*
  │     └── fix/*
  │
  └── project/week2
        ├── feature/*
        ├── docs/*
        └── fix/*
```

---

## 3. 브랜치별 역할

## 3.1 master 브랜치

`master` 브랜치는 프로젝트의 최종 안정 버전을 관리하는 브랜치이다.

### 역할

* 최종 제출 가능한 코드만 유지한다.
* 직접 push하지 않는다.
* 검증 완료된 `project/week` 브랜치만 병합한다.
* 발표 및 포트폴리오 기준 브랜치로 사용한다.

### 규칙

```text
master 브랜치에는 직접 push하지 않는다.
모든 변경사항은 Pull Request를 통해 반영한다.
```

---

## 3.2 project/week 브랜치

`project/week1`, `project/week2` 브랜치는 주차별 통합 브랜치이다.

### 역할

* 해당 주차의 작업 결과를 모으는 통합 공간이다.
* 각자 feature 브랜치와 docs 브랜치의 작업물이 합쳐지는 기준 브랜치이다.
* 주차별 기능 테스트와 통합 테스트를 진행한다.

### 브랜치 예시

```text
project/week1
project/week2
```

### 사용 기준

```text
1주차 작업은 project/week1 브랜치에서 통합한다.
2주차 작업은 project/week2 브랜치에서 통합한다.
```

### 중요 규칙

```text
새로운 주차의 project 브랜치는 항상 master에서 생성한다.
이전 주차 project 브랜치에서 새 주차 브랜치를 만들지 않는다.
```

이 규칙을 적용하는 이유는 이전 주차 작업 중 승인되지 않은 코드나 불안정한 코드가 다음 주차 작업에 섞이는 것을 방지하기 위해서이다.

---

## 3.3 feature 브랜치

`feature` 브랜치는 개인 기능 작업 브랜치이다.

### 역할

* 기능 단위의 개인 작업 공간이다.
* 개인 작업 중인 코드를 독립적으로 관리한다.
* 기능 완성 후 `project/week` 브랜치로 Pull Request를 생성한다.

### 이름 규칙

```text
feature/작업내용-githubID
```

### 예시

```text
feature/backend-auth-jmkim
feature/backend-expense-jmkim
feature/backend-analysis-jmkim
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
* Git 브랜치 전략 작성
* 회고 작성

### 이름 규칙

```text
docs/문서명-githubID
```

### 예시

```text
docs/readme-jmkim
docs/project-background-jmkim
docs/requirements-jmkim
docs/erd-jmkim
docs/api-spec-jmkim
docs/wbs-jmkim
docs/branch-strategy-jmkim
docs/retrospective-jmkim
```

### 규칙

```text
docs 브랜치는 project/week 브랜치에서 생성한다.
문서 작성 완료 후 project/week 브랜치로 Pull Request를 보낸다.
merge 완료 후 docs 브랜치는 삭제한다.
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
* 문서 오탈자 수정

### 이름 규칙

```text
fix/수정내용-githubID
```

### 예시

```text
fix/image-upload-jmkim
fix/login-token-kdkim
fix/category-chart-jmkim
fix/docs-typo-jmkim
```

### 규칙

```text
fix 브랜치는 project/week 브랜치에서 생성한다.
수정 완료 후 project/week 브랜치로 Pull Request를 보낸다.
merge 완료 후 fix 브랜치는 삭제한다.
```

---

# 4. 2주 프로젝트 브랜치 흐름

## 4.1 1주차 흐름

```text
master
  └── project/week1
        ├── docs/project-background-jmkim
        ├── docs/requirements-jmkim
        ├── docs/erd-jmkim
        ├── docs/api-spec-jmkim
        ├── feature/backend-auth-jmkim
        ├── feature/backend-expense-jmkim
        ├── feature/frontend-layout-kdkim
        └── feature/frontend-expense-kdkim
```

1주차에는 프로젝트 기획, 요구사항 정의, ERD, API 명세, 백엔드 기본 기능, 프론트 기본 화면을 구현한다.

1주차가 끝나면 `project/week1` 브랜치에서 통합 테스트를 진행하고, 안정화된 코드를 `master`로 병합한다.

---

## 4.2 2주차 흐름

```text
master
  └── project/week2
        ├── feature/backend-analysis-jmkim
        ├── feature/backend-feedback-jmkim
        ├── feature/frontend-analysis-kdkim
        ├── feature/frontend-feedback-kdkim
        ├── fix/integration-error-jmkim
        ├── docs/final-readme-jmkim
        └── docs/retrospective-kdkim
```

2주차에는 소비 분석, 개선방안 제시, 차트 시각화, 최종 README, 트러블슈팅 문서, 회고를 작성한다.

2주차가 끝나면 `project/week2` 브랜치에서 최종 테스트를 진행하고, 검증 완료 후 `master`로 병합한다.

---

# 5. 브랜치 생성 및 작업 흐름

## 5.1 1주차 project 브랜치 생성

`project/week1` 브랜치는 `master` 브랜치에서 생성한다.

```bash
git switch master
git pull origin master

git switch -c project/week1
git push -u origin project/week1
```

---

## 5.2 2주차 project 브랜치 생성

`project/week2` 브랜치도 반드시 `master` 브랜치에서 생성한다.

```bash
git switch master
git pull origin master

git switch -c project/week2
git push -u origin project/week2
```

이전 주차 브랜치인 `project/week1`에서 `project/week2`를 생성하지 않는다.

---

# 6. 개발자의 하루 작업 흐름

## 6.1 작업 시작 전

항상 최신 `project/week` 브랜치에서 작업을 시작한다.

```bash
git switch project/week1
git pull origin project/week1
```

그다음 개인 작업 브랜치를 생성한다.

```bash
git switch -c feature/backend-expense-jmkim
```

문서 작업의 경우 다음과 같이 생성한다.

```bash
git switch -c docs/erd-jmkim
```

---

## 6.2 작업 중

작업은 본인의 작업 브랜치에서만 진행한다.

```bash
git add .
git commit -m "feat: 소비 로그 모델 및 작성 API 구현"
```

커밋은 너무 크게 묶지 않고 기능 단위로 나누어 작성한다.

---

## 6.3 작업 브랜치 원격 등록

작업한 브랜치로 Pull Request를 생성하려면 GitHub 원격 저장소에 브랜치를 올려야 한다.

처음 push할 때는 `-u` 옵션을 사용한다.

```bash
git push -u origin feature/backend-expense-jmkim
```

문서 브랜치라면 다음과 같이 push한다.

```bash
git push -u origin docs/erd-jmkim
```

`-u` 옵션은 로컬 브랜치와 원격 브랜치를 연결하는 역할을 한다.
한 번 연결한 이후에는 다음부터 간단히 `git push`만 사용하면 된다.

---

## 6.4 PR 올리기 전

Pull Request를 올리기 전에 반드시 최신 `project/week` 브랜치 내용을 본인 브랜치에 반영한다.

```bash
git switch feature/backend-expense-jmkim
git fetch origin
git merge origin/project/week1
```

문서 브랜치의 경우도 동일하다.

```bash
git switch docs/erd-jmkim
git fetch origin
git merge origin/project/week1
```

충돌이 발생하면 본인 브랜치에서 먼저 해결한 뒤 다시 커밋한다.

```bash
git add .
git commit -m "fix: project/week1 병합 충돌 해결"
git push
```

---

## 6.5 PR 생성

작업 완료 후 다음 방향으로 Pull Request를 생성한다.

```text
feature/작업브랜치 → project/week1
```

문서 작업의 경우 다음 방향으로 Pull Request를 생성한다.

```text
docs/문서브랜치 → project/week1
```

버그 수정의 경우 다음 방향으로 Pull Request를 생성한다.

```text
fix/수정브랜치 → project/week1
```

2주차 작업은 `project/week2`를 대상으로 Pull Request를 생성한다.

```text
feature/작업브랜치 → project/week2
docs/문서브랜치 → project/week2
fix/수정브랜치 → project/week2
```

---

## 6.6 PR 승인 후

리뷰어가 확인한 뒤 GitHub에서 `Merge pull request` 버튼을 눌러 병합한다.

merge가 완료된 작업 브랜치는 삭제한다.

```text
작업 완료 브랜치는 남기지 않고 삭제하여 브랜치 목록을 깔끔하게 유지한다.
```

GitHub에서 원격 브랜치를 삭제한 뒤, 로컬 브랜치도 삭제한다.

```bash
git switch project/week1
git pull origin project/week1

git branch -d feature/backend-expense-jmkim
```

문서 브랜치라면 다음과 같이 삭제한다.

```bash
git branch -d docs/erd-jmkim
```

---

# 7. Pull Request 규칙

## 7.1 PR 제목 규칙

PR 제목은 다음 형식을 따른다.

```text
[타입] 작업 내용
```

### 예시

```text
[feat] 소비 로그 CRUD API 구현
[feat] 소비 분석 차트 화면 구현
[docs] ERD 설계 문서 작성
[docs] Git 브랜치 전략 문서 작성
[fix] 이미지 업로드 경로 오류 수정
[refactor] 소비 분석 로직 분리
```

---

## 7.2 PR 설명 템플릿

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

# 8. 커밋 메시지 규칙

커밋 메시지는 다음 형식을 사용한다.

```text
타입: 작업 내용
```

## 8.1 타입 종류

| 타입       | 의미                       |
| -------- | ------------------------ |
| feat     | 새로운 기능 추가                |
| fix      | 버그 수정                    |
| docs     | 문서 작성 및 수정               |
| style    | 코드 포맷, CSS 등 기능 변경 없는 수정 |
| refactor | 기능 변화 없는 코드 구조 개선        |
| test     | 테스트 코드 추가                |
| chore    | 설정, 패키지, 빌드 관련 작업        |

---

## 8.2 커밋 예시

```bash
git commit -m "docs: 프로젝트 선정 배경 정리"
git commit -m "docs: 요구사항 정의 작성"
git commit -m "docs: ERD 설계 문서 작성"
git commit -m "docs: API 명세 작성"
git commit -m "docs: WBS 개발 일정 작성"
git commit -m "docs: Git 브랜치 전략 작성"
git commit -m "feat: 회원가입 로그인 API 구현"
git commit -m "feat: 소비 로그 CRUD API 구현"
git commit -m "feat: 소비 분석 차트 화면 구현"
git commit -m "fix: 이미지 업로드 경로 오류 수정"
git commit -m "refactor: 소비 분석 로직 함수 분리"
```

---

# 9. 충돌 방지 규칙

2인 프로젝트에서 충돌을 줄이기 위해 다음 규칙을 적용한다.

## 9.1 같은 파일 동시 수정 최소화

다음 파일은 충돌이 자주 발생할 수 있으므로 수정 전 공유한다.

```text
README.md
backend/config/settings.py
backend/config/urls.py
frontend/src/router/index.js
frontend/src/api/axios.js
frontend/package.json
backend/requirements.txt
```

---

## 9.2 작업 구역 분리

백엔드 담당자는 주로 다음 영역을 수정한다.

```text
backend/
docs/02_erd.md
docs/03_api_spec.md
```

프론트엔드 담당자는 주로 다음 영역을 수정한다.

```text
frontend/
docs/04_wbs.md
README.md
```

공통 문서는 작업 전 미리 공유하고 수정한다.

---

## 9.3 PR 전 최신 코드 반영

Pull Request를 올리기 전에는 반드시 `project/week` 브랜치의 최신 코드를 본인 브랜치에 반영한다.

```text
PR 전 최신 project/week 브랜치 반영은 필수이다.
```

추천 명령어는 다음과 같다.

```bash
git switch 본인작업브랜치
git fetch origin
git merge origin/project/week1
```

---

# 10. 충돌 발생 시 해결 방법

충돌이 발생하면 Git이 어떤 파일에서 충돌이 발생했는지 알려준다.

예시:

```text
CONFLICT (content): Merge conflict in docs/01_requirements.md
Automatic merge failed; fix conflicts and then commit the result.
```

충돌 파일을 열면 다음과 같은 표시가 나타난다.

```text
<<<<<<< HEAD
내 브랜치의 내용
=======
가져온 브랜치의 내용
>>>>>>> origin/project/week1
```

이때 최종적으로 남길 내용만 정리하고, 아래 충돌 표시를 모두 제거한다.

```text
<<<<<<< HEAD
=======
>>>>>>> origin/project/week1
```

수정 후 다시 커밋하고 push한다.

```bash
git add .
git commit -m "fix: project/week1 병합 충돌 해결"
git push
```

만약 병합 과정이 너무 꼬였다면 다음 명령어로 병합을 취소할 수 있다.

```bash
git merge --abort
```

---

# 11. 승인 지연 작업 처리

당일 작업이 완료되었지만 리뷰 또는 merge가 지연될 수 있다.

이 경우 다음 규칙을 따른다.

```text
승인되지 않은 작업을 기준으로 새로운 브랜치를 만들지 않는다.
기존 작업 브랜치에서 계속 수정한다.
승인 완료 후 project/week 브랜치에 merge한다.
```

예시:

```text
feature/backend-expense-jmkim 브랜치의 PR 승인이 지연된 경우,
feature/backend-expense-jmkim 브랜치에서 계속 수정한다.
새로운 feature/backend-expense-v2 브랜치를 만들지 않는다.
```

PR이 열린 상태에서 추가 수정이 필요한 경우에도 기존 브랜치에 커밋하고 push하면 기존 PR에 자동 반영된다.

```bash
git switch feature/backend-expense-jmkim
git add .
git commit -m "fix: 소비 로그 작성 API 예외 처리 추가"
git push
```

---

# 12. 통합 및 배포 규칙

## 12.1 주차별 통합

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
* README와 docs 문서 최신화 여부

---

## 12.2 master 병합

통합 테스트가 완료된 `project/week` 브랜치만 `master`로 병합한다.

```text
project/week1 → master
project/week2 → master
```

`master`로 병합된 코드는 최종 제출 가능한 안정 버전으로 간주한다.

---

# 13. 일일 회의 규칙

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

## 14. Flex-log 브랜치 전략 요약

Flex-log 프로젝트의 브랜치 전략은 다음과 같다.

```text
master
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
1. master에는 직접 push하지 않는다.
2. project/week 브랜치는 항상 master에서 생성한다.
3. feature, docs, fix 브랜치는 project/week 브랜치에서 생성한다.
4. PR 전 project/week 최신 코드를 본인 브랜치에 반영한다.
5. 승인되지 않은 작업은 기존 브랜치에서 계속 수정한다.
6. merge 완료된 작업 브랜치는 삭제한다.
7. 코드뿐 아니라 문서도 Git으로 관리한다.
```
