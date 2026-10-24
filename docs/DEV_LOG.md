# 📝 Development Work Log (개발 작업 로그)

이 문서는 작업 일자별 구현 내용, 변경 파일, 실행 명령어, 검증 결과 및 Git 커밋 내역을 기록합니다.

---

## [2026-10-24 20:30] feat(09-terraform): IaC State 및 네트워크 설계 PoC
- **작업 목적**:
  - Terraform v1.17.0 기반의 `terraform_data` 리소스를 활용한 논리적 네트워크(VPC, Public/Private Subnet) HCL 선언
  - `cidrsubnet()` 함수를 활용한 서브넷 주소 자동 분할 및 리소스 간 부모-자식 의존성(Dependency Graph) 구성
  - `terraform test`를 통한 Plan 단언문 3건(`subnet_cidrs`, `resource_dependency`, `production_label`) 자동화 검증
  - `terraform apply`를 통한 State 생성, `terraform plan`을 통한 멱등성 검증, `terraform destroy`를 통한 클린업
  - 10단계 Kubernetes 실습을 위한 사전 디렉터리(`10-kubernetes/`) 준비
- **변경 파일**:
  - `09-terraform-iac/main.tf` (신규)
  - `09-terraform-iac/variables.tf` (신규)
  - `09-terraform-iac/outputs.tf` (신규)
  - `09-terraform-iac/.gitignore` (신규)
  - `09-terraform-iac/tests/network.tftest.hcl` (신규)
  - `09-terraform-iac/docs/learning-log.md` (신규)
  - `09-terraform-iac/README.md` (신규)
  - `10-kubernetes/README.md` (신규 - 10단계 준비)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
- **실행 명령어**:
  - `terraform init`
  - `terraform fmt -check -recursive`
  - `terraform validate`
  - `terraform test`
  - `terraform plan -out=study.tfplan`
  - `terraform apply study.tfplan`
  - `terraform state list`
  - `terraform output -json network_plan`
  - `terraform plan` (멱등성 확인)
  - `terraform plan -var='environment=stage'` (변경 계산 확인)
  - `terraform destroy -auto-approve`
- **검증 및 테스트 결과**:
  - `terraform validate`: Success (`The configuration is valid.`)
  - `terraform test`: Success! 3 passed, 0 failed (3건 전수 통과)
  - `terraform apply`: Resources: 3 added, 0 changed, 0 destroyed
  - 멱등성 확인: `No changes. Your infrastructure matches the configuration.`
  - `terraform destroy`: Resources: 3 destroyed 완료
- **Commit Hash**: `f545c96` (`feat(09-terraform): IaC State 및 네트워크 설계 PoC`)

---

## [2026-10-24 20:21] feat(08-ci): GitHub Actions 자동 테스트 및 Docker 빌드
- **작업 목적**:
  - GitHub Actions 워크플로(`.github/workflows/cloud-ci.yml`) 작성을 통한 CI(지속적 통합) 자동화 파이프라인 구축
  - `python-tests` Job(단위 테스트)과 `docker-build` Job(이미지 빌드 및 스모크 테스트) 간 `needs` 의존성(Fail-Fast) 구성
  - `permissions: contents: read`를 통한 최소 권한 보안 원칙 준수
  - 09단계 Terraform & IaC 실습을 위한 사전 디렉터리(`09-terraform/`) 준비
- **변경 파일**:
  - `.github/workflows/cloud-ci.yml` (신규)
  - `08-ci-actions/app.py` (신규)
  - `08-ci-actions/test_app.py` (신규)
  - `08-ci-actions/Dockerfile` (신규)
  - `08-ci-actions/README.md` (신규)
  - `09-terraform/README.md` (신규 - 09단계 준비)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
  - `docs/ERROR_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest discover -s 08-ci-actions -p 'test_*.py' -v`
  - `python3 -m unittest discover -s 07-compose-network -p 'test_local.py' -v`
  - `docker build -t cloud-ci-lab:local ./08-ci-actions`
  - `docker run -d --name cloud-ci-test -p 127.0.0.1:18081:8081 cloud-ci-lab:local`
  - `curl -i http://127.0.0.1:18081/health`
  - `docker rm -f cloud-ci-test`
- **검증 및 테스트 결과**:
  - `08-ci-actions` 단위 테스트 3건 전수 통과 (`Ran 3 tests in 0.530s - OK`)
  - `07-compose-network` 단위 테스트 3건 전수 통과 (`Ran 3 tests in 0.526s - OK`)
  - Docker 이미지 빌드 성공 및 컨테이너 스모크 테스트 HTTP 200 OK 수신 확인
- **Commit Hash**: `c726181` (`feat(08-ci): GitHub Actions 자동 테스트 및 Docker 빌드`)

---

## [2026-10-24 20:10] feat(07-compose): 서비스 DNS 및 컨테이너 네트워크 PoC 구현
- **작업 목적**:
  - Docker Compose를 활용한 멀티 컨테이너(`api`, `client`) 선언적 구성 및 사용자 정의 브리지 네트워크(`lab-net`) 격리
  - Docker 내장 DNS(`127.0.0.11`)를 통한 마이크로서비스 디스커버리(`api` -> `172.25.0.2`) 검증
  - 컨테이너 헬스체크(`condition: service_healthy`) 의존성 제어 및 호스트 루프백 포트 포워딩(`127.0.0.1:8081`) 검증
  - 08단계 CI/CD 자동화 실습을 위한 사전 디렉터리(`08-ci-cd/`) 준비
- **변경 파일**:
  - `07-compose-network/compose.yaml` (신규)
  - `07-compose-network/api/Dockerfile` (신규)
  - `07-compose-network/api/main.py` (신규)
  - `07-compose-network/client/Dockerfile` (신규)
  - `07-compose-network/client/check.py` (신규)
  - `07-compose-network/test_local.py` (신규)
  - `07-compose-network/README.md` (신규)
  - `08-ci-cd/README.md` (신규 - 08단계 준비)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_local.py`
  - `docker compose up -d --build api`
  - `docker compose ps`
  - `curl -i http://127.0.0.1:8081/health`
  - `docker compose run --rm client`
  - `docker compose down`
- **검증 및 테스트 결과**:
  - 단위 테스트 3건 전수 통과 (`Ran 3 tests in 0.544s - OK`)
  - `api` 컨테이너 헬스체크 정상 통과 (`Up About a minute (healthy)`)
  - 호스트 `curl -i http://127.0.0.1:8081/health` 응답 HTTP 200 수신
  - `client` 컨테이너에서 Docker DNS(`api` -> `172.25.0.2`) 해석, TCP 연결, HTTP 200 통신 전수 검증 완료
- **Commit Hash**: `1fee1c7` (`feat(07-compose): 서비스 DNS 및 컨테이너 네트워크 PoC 구현`)

---

## [2026-10-24 19:59] feat(06-security): IAM SG NACL 정책 검증 PoC 구현
- **작업 목적**:
  - IAM 정책 평가 엔진(명시적 Deny 최우선, 명시적 Allow, 기본 암시적 Deny) 구현
  - Security Group의 상태 저장(Stateful) 연결 추적 및 CIDR/포트 화이트리스트 검증
  - Network ACL의 상태 비저장(Stateless) 규칙 번호 우선순위 및 임시 포트(Ephemeral Port) 검증
  - 07단계 Docker Compose 멀티 컨테이너 실습 사전 폴더(`07-docker-compose/`) 준비
- **변경 파일**:
  - `06-cloud-security/security.py` (신규)
  - `06-cloud-security/test_security.py` (신규)
  - `06-cloud-security/README.md` (신규)
  - `07-docker-compose/README.md` (신규 - 07단계 준비)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_security.py`
  - `python3 security.py`
  - `python3 security.py --client-ip 198.51.100.10`
  - `python3 security.py --client-port 80`
- **검증 및 테스트 결과**:
  - 단위 테스트 8건 전수 통과 (`Ran 8 tests in 0.001s - OK`)
  - IAM 거부/허용 및 SG/NACL 인바운드/아웃바운드 3가지 시나리오 검증 완료
- **Commit Hash**: `499238f` (`feat(06-security): IAM SG NACL 정책 검증 PoC 구현`)

---

## [2026-10-24 19:18] feat(05-network): CIDR subnet routing PoC 구현
- **작업 목적**:
  - Python `ipaddress` 모듈 기반 VPC CIDR 및 서브넷 분할 유효성 검증 엔진 구현
  - 서브넷 간 주소 중첩(Overlap) 및 VPC 범위 이탈(Outside) 예외 방지
  - 라우트 테이블의 핵심 원리인 최장 접두사 일치(Longest Prefix Match) 알고리즘 모델링
  - 06단계 IAM 및 보안 실습을 위한 사전 디렉터리(`06-iam-security/`) 준비
- **변경 파일**:
  - `05-vpc-network-planner/planner.py` (신규)
  - `05-vpc-network-planner/test_planner.py` (신규)
  - `05-vpc-network-planner/README.md` (갱신)
  - `06-iam-security/README.md` (신규 - 06단계 준비)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_planner.py`
  - `python3 planner.py`
  - `python3 planner.py --destination 10.0.3.15`
  - `python3 planner.py --destination 8.8.8.8`
- **검증 및 테스트 결과**:
  - 단위 테스트 6건 전수 통과 (`Ran 6 tests in 0.000s - OK`)
  - 3개 목적지 IP(10.0.2.15, 10.0.3.15, 8.8.8.8) 대상 Longest Prefix Match 라우팅 시뮬레이션 성공
- **Commit Hash**: `c7a945e` (`feat(05-network): CIDR subnet routing PoC 구현`)

---

## [2026-10-24 17:45] feat(04-docker): 가상화 · Docker 컨테이너 격리 및 볼륨 영속성 PoC 구현
- **작업 목적**:
  - Python HTTP 서버를 Docker 이미지(`python:3.11-slim`)로 패키징 및 Compose 환경 구성
  - 호스트 포트 포워딩(`127.0.0.1:8081:8081`) 및 Docker Named Volume(`notes_data:/data`) 마운트
  - 컨테이너 완전 삭제(`docker compose down`) 후 재생성 시에도 데이터(`persist-me`)가 온전히 보존되는 영속성 검증
- **변경 파일**:
  - `04-docker-storage/Dockerfile` (신규)
  - `04-docker-storage/compose.yaml` (신규)
  - `04-docker-storage/main.py` (신규)
  - `04-docker-storage/test_main.py` (신규)
  - `04-docker-storage/README.md` (신규)
  - `05-vpc-subnet/README.md` (신규 - 05단계 준비 폴더)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_main.py`
  - `docker compose up -d --build`
  - `curl -i http://127.0.0.1:8081/health`
  - `curl -i -X POST http://127.0.0.1:8081/note -d '{"note":"persist-me"}'`
  - `docker compose down && docker compose up -d`
  - `curl -i http://127.0.0.1:8081/note`
- **검증 및 테스트 결과**:
  - 단위 테스트 3건 전수 통과 (`Ran 3 tests in 0.585s - OK`)
  - 컨테이너 재생성 후 영속 데이터(`persist-me`) 정상 조회 확인 완료
- **Commit Hash**: `1f36e8b` (`feat(04-docker): 가상화 · Docker 컨테이너 격리 및 볼륨 영속성 PoC 구현`)

---

## [2026-10-24 17:28] feat(03-network-diagnostics): DNS·TCP·HTTP 네트워크 진단 CLI 및 검증 PoC 구현
- **작업 목적**:
  - DNS 호스트명 주소 해석(`socket.getaddrinfo`), TCP 소켓 연결(`socket.create_connection`), HTTP 통신(`urllib.request.urlopen`)의 3단계 계층별 진단 도구 구현
  - 정상 응답(200), 미등록 경로(404), 미개방 포트(ConnectionRefused), 외부 도메인(DNS 해석)의 에러 케이스 구분 검증
- **변경 파일**:
  - `03-network-diagnostics/diagnose.py` (신규)
  - `03-network-diagnostics/test_diagnose.py` (신규)
  - `03-network-diagnostics/README.md` (신규)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_diagnose.py`
  - `python3 diagnose.py 127.0.0.1 --port 8081 --path /health`
  - `python3 diagnose.py 127.0.0.1 --port 8081 --path /missing`
  - `python3 diagnose.py 127.0.0.1 --port 9999`
  - `python3 diagnose.py example.com --port 80 --path /`
- **검증 및 테스트 결과**:
  - 단위 테스트 5건 전수 통과 (`Ran 5 tests in 0.199s - OK`)
  - 로컬 HTTP 서버 및 닫힌 포트, 외부 도메인 4가지 시나리오 완벽 검증
- **Commit Hash**: `835c480` (`feat(03-network-diagnostics): DNS·TCP·HTTP 네트워크 진단 CLI 및 검증 PoC 구현`)

---

## [2026-10-24 17:15] feat(02-linux-process): 서버 프로세스 모니터 PoC 구현 및 HTTP 서버 연동 검증
- **작업 목적**:
  - 운영체제(macOS/Linux 커널)의 프로세스 식별 및 자원 관리(PID, PPID, CPU, RSS, STAT) 모니터링 CLI 도구 구현
  - 01단계 HTTP 서버의 포트(8081) 점유 프로세스(`lsof`) 추적 및 정상 종료(`SIGTERM`) 생명주기 검증
- **변경 파일**:
  - `02-linux-process/monitor.py` (신규)
  - `02-linux-process/test_monitor.py` (신규)
  - `02-linux-process/README.md` (신규)
  - `README.md` (갱신)
  - `docs/ARCHITECTURE.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
  - `docs/ERROR_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_monitor.py`
  - `python3 monitor.py`
  - `lsof -nP -iTCP:8081 -sTCP:LISTEN`
- **검증 및 테스트 결과**:
  - 단위 테스트 2건 전수 통과 (`Ran 2 tests in 0.017s - OK`)
  - HTTP 서버(PID: 55016) 대상 실시간 CPU 0.9%, RSS 10960KiB 확인 및 `SIGTERM` 후 `running: false` 정상 전이 확인
- **Commit Hash**: `33665a3` (`feat(02-linux-process): 서버 프로세스 모니터 PoC 구현 및 HTTP 서버 연동 검증`)

---

## [2026-10-24 17:04] feat(01-http-server): HTTP 기초 서버 구현 및 상태 검증 기능 추가
- **작업 목적**:
  - 클라우드 아키텍처의 기본 통신 규격인 HTTP 서버 구현 및 상태 검증(200 OK, 404 Not Found)
  - 무중단 데몬 스레드 기반의 자동화 단위 테스트 구성
- **변경 파일**:
  - `01-http-server/main.py` (신규)
  - `01-http-server/test_main.py` (신규)
  - `01-http-server/README.md` (신규)
  - `docs/ERROR_LOG.md` (갱신)
  - `docs/TEST_LOG.md` (갱신)
  - `docs/DEV_LOG.md` (갱신)
- **실행 명령어**:
  - `python3 -m unittest -v test_main.py`
  - `curl -i http://127.0.0.1:8081/health`
  - `curl -i http://127.0.0.1:8081/missing`
- **검증 및 테스트 결과**:
  - 단위 테스트 2건 전수 통과 (`test_health`: OK, `test_not_found`: OK)
  - curl 헤더/본문 JSON 검증 완료
- **Commit Hash**: `f228405` (`feat(01-http-server): HTTP 기초 서버 구현 및 상태 검증 기능 추가`)

---

## [2026-10-24 16:58] chore: 프로젝트 초기 환경 및 문서 구조 설정
- **작업 목적**: 클라우드 컴퓨팅 12단계 실습을 위한 저장소 기본 환경(.gitignore, README, docs 4종) 구축
- **변경 파일**:
  - `.gitignore` (신규)
  - `README.md` (신규)
  - `docs/ARCHITECTURE.md` (신규)
  - `docs/DEV_LOG.md` (신규)
  - `docs/ERROR_LOG.md` (신규)
  - `docs/TEST_LOG.md` (신규)
- **실행 명령어**: `git status`
- **검증 결과**: 파일 생성 및 Git 작업 영역 준비 완료
- **Commit Hash**: `3c4605e`
