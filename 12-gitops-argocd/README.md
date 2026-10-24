# 12단계: GitOps Self-Healing & Availability Lab (Argo CD)

## 1. 개요 및 학습 목표
- **학습 주제**: GitOps 패러다임, Argo CD, 지속적 배포(CD), Desired State(선언된 형상) vs Live State(실제 상태), Drift 감지, 자동 동기화(Automated Sync), Self-Heal, 고가용성(High Availability, HA)
- **비용**: 0원 (로컬 kind 클러스터 및 오픈소스 Argo CD 기반)
- **목표**:
  1. Git 저장소를 단일 진실 공급원(Single Source of Truth)으로 삼아 Kubernetes 인프라 배포 설정을 선언형으로 관리합니다.
  2. Argo CD Application을 생성하여 원격 GitHub 저장소(`12-gitops-argocd/k8s`)의 변경 사항을 클러스터에 자동 동기화(Sync)합니다.
  3. 운영자가 클러스터에서 임의로 설정을 변경(Drift 발생: `replicas=1` 축소)했을 때, Argo CD의 `selfHeal: true` 정책이 이를 감지하여 Git에 선언된 원래 상태(`replicas: 2`)로 자동 복원하는 과정을 검증합니다.
  4. Kubernetes 자체의 Pod 장애 복구(ReplicaSet Self-Healing)와 Argo CD의 설정 불일치 복구(GitOps Self-Heal)의 차이를 명확히 구분하여 체득합니다.

---

## 2. 프로젝트 파일 구성
```text
12-gitops-argocd/
├── application.yaml           # Argo CD Application 선언 명세 (Git 저장소 및 syncPolicy 정의)
├── k8s/
│   ├── namespace.yaml         # 격리된 gitops-lab 네임스페이스
│   ├── deployment.yaml        # Nginx 웹 서버 (replicas: 2, readinessProbe, 롤링 전략)
│   ├── service.yaml           # ClusterIP Service (web:80)
│   └── kustomization.yaml     # 3대 매니페스트 Kustomize 번들 명세
├── tests/
│   └── test_manifests.py      # 정적 구조 및 정책 유효성 검증 단위 테스트 (3건)
├── docs/
│   └── learning-log.md        # 배포 및 Self-Heal 실습 로그
├── verify.sh                  # 클러스터 및 서비스 정상 작동 검증 스크립트
├── .gitignore
└── README.md                  # 12단계 실습 안내서
```

---

## 3. GitOps 아키텍처 및 2대 Self-Healing 메커니즘

```mermaid
flowchart TD
    subgraph GitRepo ["단일 진실 원천 (Single Source of Truth)"]
        GitHub["GitHub Repository<br>12-gitops-argocd/k8s<br>(Desired State: replicas=2)"]
    end

    subgraph ArgoCDPlane ["Argo CD 컨트롤러 (argocd 네임스페이스)"]
        ArgoApp["Application: cloud-gitops-lab<br>syncPolicy: automated (selfHeal: true)"]
        DriftDetector["Drift 감지 엔진 (Git vs Live 클러스터 비교)"]
    end

    subgraph LiveCluster ["실제 실행 클러스터 (gitops-lab 네임스페이스)"]
        APIServer["Kubernetes API Server"]
        Deploy["Deployment: web (Live State)"]
        RS["ReplicaSet"]
        Pod1["Pod 1: nginx"]
        Pod2["Pod 2: nginx"]
        Svc["ClusterIP Service: web:80"]
    end

    GitHub -->|1. 선언 형상 폴링| ArgoApp
    ArgoApp -->|2. Automated Sync| APIServer
    APIServer --> Deploy --> RS
    RS --> Pod1
    RS --> Pod2
    Svc --> Pod1
    Svc --> Pod2

    %% 1. GitOps Self-Heal 흐름
    Admin1["운영자 실수: kubectl scale --replicas=1"] -.->|임의 수정 (Drift 발생)| Deploy
    Deploy -.->|Live State 불일치| DriftDetector
    DriftDetector -->|3. OutOfSync 감지 & selfHeal 복원| ArgoApp
    ArgoApp -->|4. replicas=2 강제 재동기화| Deploy

    %% 2. K8s Pod Self-Healing 흐름
    Admin2["Pod 1 강제 종료 (kubectl delete pod)"] -.->|Pod 유실| Pod1
    RS -->|Desired 2개 복구| NewPod["새 Pod 생성"]
```

---

## 4. Mac zsh 실행 명령어 가이드

```zsh
cd 12-gitops-argocd

# 1. 오프라인 정적 단위 테스트 (3건)
python3 -m unittest discover -s tests -p "test_*.py" -v

# 2. 변경사항 Git 커밋 & 원격 푸시 (Argo CD가 읽을 수 있도록 사전 푸시 필수)
cd ..
git add 12-gitops-argocd
git commit -m "feat(12-gitops): Argo CD 자동 동기화 및 복구 PoC"
git push origin main
cd 12-gitops-argocd

# 3. kind 클러스터 생성 (기존 클러스터 없을 경우)
kind create cluster --name cloud-study --wait 120s

# 4. Argo CD 컨트롤러 설치
kubectl --context kind-cloud-study create namespace argocd
kubectl --context kind-cloud-study apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl --context kind-cloud-study -n argocd rollout status deploy/argocd-server --timeout=180s

# 5. GitOps Application 배포
kubectl --context kind-cloud-study apply -f application.yaml

# 6. 배포 및 서비스 통합 검증
bash verify.sh

# 7. Argo CD Self-Heal 검증 (클러스터 설정을 1로 축소 -> Argo CD가 다시 2로 자동 복원)
kubectl --context kind-cloud-study -n gitops-lab scale deployment/web --replicas=1
kubectl --context kind-cloud-study -n gitops-lab get deployment web -w

# 8. 클러스터 정리
kind delete cluster --name cloud-study
```
