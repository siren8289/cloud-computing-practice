# ☁️ Cloud Computing Practice (클라우드 컴퓨팅 실습)

> **기준 로드맵**: [roadmap.sh — Cloud Computing 2026](https://roadmap.sh/cloud-computing)  
> **환경**: macOS (Apple Silicon / Intel, zsh)  
> **비용**: 0원 (로컬 PoC 및 오픈소스 기반 실습)

---

## 🗺️ 전체 12단계 학습 로드맵

| 단계 | 차시 | 핵심 기술 | 60분 PoC 결과물 | 상태 |
| :---: | :---: | :--- | :--- | :---: |
| **기초** | 01 | 클라우드 기초 · HTTP | 로컬 HTTP 서버와 요청 검증 | ✅ 완료 |
| | 02 | Linux · 프로세스 | 서버 프로세스 및 로그 분석 | ✅ 완료 |
| | 03 | TCP/IP · DNS | 네트워크 진단 도구 | ✅ 완료 |
| | 04 | 가상화 · 스토리지 | Docker 격리 및 데이터 영속성 | ✅ 완료 |
| **중급** | 05 | VPC · Subnet | CIDR 및 네트워크 구획 검증 | ✅ 완료 |
| | 06 | IAM · 보안 | 최소 권한 정책 및 SG/NACL 검증 | ✅ 완료 |
| | 07 | Docker · Compose | 멀티 컨테이너 서비스 DNS 및 네트워크 검증 | ✅ 완료 |
| | 08 | CI/CD | GitHub Actions 자동 테스트 및 Docker 빌드 | ✅ 완료 |
| **심화** | 09 | **Terraform** | **IaC State 및 네트워크 설계 생명주기 검증** | ✅ 완료 |
| | 10 | **Kubernetes** | **로컬 K8s Pod · Deployment · Service 배포** | 🚀 준비 완료 |
| | 11 | Monitoring | 메트릭·로그 수집 | ⏳ 대기 |
| | 12 | GitOps · HA | 배포 상태 및 장애 복구 검증 | ⏳ 대기 |

---

## 📁 디렉터리 구조

```text
cloud-computing-practice/
├── .github/
│   └── workflows/
│       └── cloud-ci.yml       # GitHub Actions CI 파이프라인 (자동 테스트 & Docker 빌드)
├── .gitignore
├── README.md
├── docs/                      # 프로젝트 관리 및 학습 로그
│   ├── ARCHITECTURE.md        # 아키텍처 및 시스템 설계 이력
│   ├── DEV_LOG.md             # 일자별 개발/실습 작업 로그
│   ├── ERROR_LOG.md           # 오류 원인 분석 및 해결 로그
│   └── TEST_LOG.md            # 단위/통합/API 테스트 검증 로그
├── 01-http-server/            # 01단계: 클라우드 기초 및 HTTP 서버 PoC
├── 02-linux-process/          # 02단계: Linux 서버 프로세스 모니터 PoC
├── 03-network-diagnostics/    # 03단계: TCP/IP · DNS · HTTP 네트워크 진단 PoC
├── 04-docker-storage/         # 04단계: Docker 컨테이너 및 볼륨 영속성 PoC
├── 05-vpc-network-planner/    # 05단계: VPC · Subnet · CIDR 네트워크 구획 PoC
├── 06-cloud-security/         # 06단계: IAM · Security Group · NACL 보안 PoC
├── 07-compose-network/        # 07단계: Docker Compose 멀티 컨테이너 네트워크 PoC
├── 08-ci-actions/             # 08단계: CI/CD GitHub Actions 자동 테스트 및 Docker 빌드 PoC
├── 09-terraform-iac/          # 09단계: Terraform IaC State 및 네트워크 라이프사이클 PoC
│   ├── main.tf                # VPC 및 서브넷 논리적 리소스 명세
│   ├── variables.tf           # 환경 변수 및 validation 규칙
│   ├── outputs.tf             # network_plan 출력값 정의
│   ├── tests/                 # 자동화 테스트 명세 (3개 run 블록)
│   ├── docs/                  # 학습 기록 (learning-log.md)
│   └── README.md              # 09단계 실습 안내서
└── 10-kubernetes/             # 10단계: Kubernetes 아키텍처 및 서비스 실습 준비
    └── README.md              # 10단계 안내서
```
