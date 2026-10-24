# 08단계: Automated CI Pipeline Lab (GitHub Actions)

## 1. 개요 및 학습 목표
- **학습 주제**: CI/CD (지속적 통합), GitHub Actions 워크플로, 파이프라인 자동화, 최소 권한 원칙(Least Privilege)
- **비용**: 0원 (GitHub Actions 무료 티어 및 로컬 환경)
- **목표**:
  1. 개발자가 코드를 `git push`하거나 PR(Pull Request)을 생성할 때 GitHub Actions Runner가 코드를 자동으로 체크아웃하고 테스트를 실행하도록 워크플로를 구성합니다.
  2. `needs: python-tests` 지시어를 사용하여 테스트가 통과했을 때만 Docker 이미지 빌드 및 컨테이너 스모크 테스트(Smoke Test)가 수행되는 의존성 파이프라인을 구축합니다.
  3. 최소 권한 원칙(`permissions: contents: read`)을 적용하여 CI 워크플로의 보안을 강화합니다.

---

## 2. 프로젝트 파일 구성
```text
cloud-computing-practice/
├── .github/
│   └── workflows/
│       └── cloud-ci.yml       # GitHub Actions CI 파이프라인 선언 파일
├── 07-compose-network/        # 07단계 멀티 컨테이너 실습
└── 08-ci-actions/
    ├── app.py                 # CI 대상 경량 웹 API (ThreadingHTTPServer)
    ├── test_app.py            # 자동화 단위 테스트 (상태 코드, JSON, 404)
    ├── Dockerfile             # Python 3.11-slim 기반 컨테이너 이미지 명세
    └── README.md              # 08단계 실습 안내서
```

---

## 3. CI 파이프라인 흐름도

```mermaid
flowchart TD
    subgraph Trigger ["트리거 이벤트"]
        Push["git push origin main"]
        PR["Pull Request"]
        Manual["workflow_dispatch (수동 실행)"]
    end

    subgraph GitHubActions ["GitHub Actions Runner (ubuntu-latest)"]
        subgraph Job1 ["Job 1: python-tests"]
            Checkout1["actions/checkout"]
            SetupPy["actions/setup-python (3.11)"]
            UnitTest["unittest discover (08-ci-actions & 07-compose-network)"]
        end

        subgraph Job2 ["Job 2: docker-build (needs: python-tests)"]
            Checkout2["actions/checkout"]
            DockerBuild["docker build -t cloud-ci-lab:ci"]
            SmokeTest["Smoke Test: 컨테이너 실행 및 /health HTTP 200 폴링"]
            PrevBuild["07-compose-network 빌드 검증"]
        end
    end

    Push --> Checkout1
    PR --> Checkout1
    Manual --> Checkout1
    Checkout1 --> SetupPy --> UnitTest
    UnitTest -->|테스트 통과 (Success)| Checkout2
    UnitTest -.->|테스트 실패 (Fail)| Stop["빌드 중단 (Job 2 미실행)"]
    Checkout2 --> DockerBuild --> SmokeTest --> PrevBuild
```

---

## 4. 로컬 및 GitHub 검증 방법

### 4.1 로컬 단위 테스트 실행
```zsh
python3 -m unittest discover -s 08-ci-actions -p 'test_*.py' -v
```

### 4.2 로컬 Docker 이미지 빌드
```zsh
docker build -t cloud-ci-lab:local ./08-ci-actions
```

### 4.3 GitHub 전송 및 Actions 확인
```zsh
git add .github/workflows/cloud-ci.yml 08-ci-actions
git commit -m "feat(08-ci): GitHub Actions 자동 테스트 및 Docker 빌드"
git push origin main
```
Push 완료 후 GitHub 저장소의 **Actions** 탭에서 `Cloud Computing CI` 워크플로가 정상 통과(녹색 체크)되는지 확인합니다.
