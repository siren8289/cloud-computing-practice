# 🧪 Test & Verification Log (테스트 검증 로그)

이 문서는 실습 기능에 대한 단위·통합·수동 검증 결과, 실행 명령어, 성공/실패 여부 및 미검증 항목을 기록합니다.

---

## [2026-10-24 21:10] 11단계: Cloud Observability & Prometheus · Grafana 모니터링 통합 검증
- **작업 목적**: Python API 메트릭 계측(Counter, Histogram), Prometheus 5초 Scrape 및 TSDB 쿼리, Grafana 대시보드 자동 프로비저닝 전수 검증
- **테스트 환경**: macOS (darwin_arm64), Docker Desktop, Prometheus v3.5.0, Grafana 12.1.1
- **테스트 대상**: `11-observability-lab/app/`, `11-observability-lab/compose.yaml`, `prometheus/`, `grafana/`
- **테스트 명령어**:
  ```zsh
  cd 11-observability-lab
  python3 -m unittest discover -s tests -p 'test_*.py' -v
  docker compose up -d --build
  docker compose ps
  curl -i http://127.0.0.1:8081/health
  curl -i http://127.0.0.1:8081/work
  curl -i http://127.0.0.1:8081/error
  curl -s http://127.0.0.1:8081/metrics
  # 부하 트래픽 생성
  for i in $(seq 1 60); do curl -s -o /dev/null http://127.0.0.1:8081/work; done
  for i in $(seq 1 5); do curl -s -o /dev/null http://127.0.0.1:8081/error; done
  curl -s http://127.0.0.1:9090/api/v1/targets
  curl -s http://127.0.0.1:3000/api/health
  curl -s 'http://127.0.0.1:9090/api/v1/query?query=sum(http_requests_total)'
  docker compose down -v
  ```
- **테스트 및 검증 결과**:
  - [PASS] Python 단위 테스트: 4건 전수 통과 (`Ran 4 tests in 0.595s - OK`)
    - `test_health`: 200 OK 및 `{"status": "ok"}` 확인
    - `test_metrics_counter`: `/work` 호출 후 `http_requests_total` 증가 확인
    - `test_error_metric`: `/error` 호출 시 500 반환 및 `status="500"` 레이블 확인
    - `test_histogram`: `http_request_duration_seconds_bucket` 버킷 관측 확인
  - [PASS] Docker Compose 기동: `api`, `prometheus`, `grafana` 3대 컨테이너 정상 기동
  - [PASS] Prometheus Target 상태: `"health":"up"` 확인 (5s 주기 정상 스크랩)
  - [PASS] TSDB 메트릭 쿼리: `sum(http_requests_total) = 68` 정확 일치 확인
  - [PASS] Grafana 헬스체크: `{"database": "ok", "version": "12.1.1"}` 확인
  - [PASS] 리소스 정리: `docker compose down -v` 완료
- **미검증 항목**: 없음 (로컬 Docker Compose 환경에서 메트릭 수집 및 TSDB 쿼리 100% 실행 검증 완료)
- **Commit Hash**: `35acf39` (`feat(11-observability): Prometheus Grafana 모니터링 PoC`)

---

## [2026-10-24 20:45] 10단계: Kubernetes Deployment · Service · Self-Healing · RollingUpdate 통합 검증
- **작업 목적**: kind 로컬 클러스터 기반 Python HTTP 서버 배포, ClusterIP 내부 라우팅, Pod 장애 복구(Self-Healing), 롤링 업데이트 전수 검증
- **테스트 환경**: macOS (darwin_arm64), Docker Desktop, kind v0.33.0, kubectl v1.37.1
- **테스트 대상**: `10-kubernetes-lab/app/`, `10-kubernetes-lab/k8s/`, `10-kubernetes-lab/verify.sh`
- **테스트 명령어**:
  ```zsh
  cd 10-kubernetes-lab
  python3 -m unittest discover -s tests -p "test_*.py" -v
  docker build -t cloud-api:v1 ./app
  kind create cluster --name cloud-study --wait 120s
  kind load docker-image cloud-api:v1 --name cloud-study
  kubectl --context kind-cloud-study apply -f k8s/
  kubectl --context kind-cloud-study rollout status deployment/cloud-api --timeout=120s
  bash verify.sh
  # 자가 치유 검증
  POD=$(kubectl --context kind-cloud-study get pods -l app=cloud-api -o jsonpath='{.items[0].metadata.name}')
  kubectl --context kind-cloud-study delete pod "$POD"
  kubectl --context kind-cloud-study wait --for=jsonpath='{.status.readyReplicas}'=2 deployment/cloud-api --timeout=120s
  # 롤링 업데이트 검증
  docker build -t cloud-api:v2 ./app
  kind load docker-image cloud-api:v2 --name cloud-study
  kubectl --context kind-cloud-study set image deployment/cloud-api api=cloud-api:v2
  kubectl --context kind-cloud-study set env deployment/cloud-api APP_VERSION=v2
  kubectl --context kind-cloud-study rollout status deployment/cloud-api --timeout=120s
  kubectl --context kind-cloud-study run version-check --rm -i --restart=Never --image=busybox:1.36 -- wget -qO- http://cloud-api:8081/
  kind delete cluster --name cloud-study
  ```
- **테스트 및 검증 결과**:
  - [PASS] Python 단위 테스트: 3건 전수 통과 (`Ran 3 tests in 0.532s - OK`)
  - [PASS] kind 클러스터 프로비저닝: 17초 완료 (`Ready after 17s`)
  - [PASS] Deployment 배포: 2/2 Ready Pod 기동 확인
  - [PASS] Service DNS 및 헬스체크: 내부 busybox에서 `http://cloud-api:8081/health` 호출 시 `{"status": "ok", "version": "v1"}` 수신
  - [PASS] Self-Healing: Pod 1개 강제 삭제 시 즉시 새 Pod 기동되어 2/2 Replicas 정상 복구 확인
  - [PASS] Rolling Update: 구버전 Pod 순차 종료 및 신규 v2 Pod 기동 확인, `GET /` 응답 `{"service": "cloud-api", "version": "v2"}` 수신
  - [PASS] 리소스 정리: `kind delete cluster` 정상 종료
- **미검증 항목**: 없음 (로컬 kind 클러스터 환경에서 전체 오케스트레이션 라이프사이클 100% 실행 검증 완료)
- **Commit Hash**: `94e7c2c` (`feat(10-k8s): Pod Deployment Service 및 장애 복구 PoC`)

---

## [2026-10-24 20:30] 09단계: Terraform IaC State 및 네트워크 설계 생명주기 검증
- **작업 목적**: Terraform HCL 코드 구문 분석, 3대 단위 테스트(`tftest.hcl`), 리소스 State 생성(`apply`), 멱등성 검증, 리소스 완전 파괴(`destroy`) 전수 검증
- **테스트 환경**: macOS (darwin_arm64), Terraform v1.17.0
- **테스트 대상**: `09-terraform-iac/main.tf`, `variables.tf`, `outputs.tf`, `tests/network.tftest.hcl`
- **테스트 명령어**:
  ```zsh
  cd 09-terraform-iac
  terraform init
  terraform fmt -check -recursive
  terraform validate
  terraform test
  terraform plan -out=study.tfplan
  terraform apply study.tfplan
  terraform state list
  terraform output -json network_plan
  terraform plan
  terraform plan -var='environment=stage'
  terraform destroy -auto-approve
  terraform state list
  ```
- **Terraform 테스트 결과**: 총 3건 중 3건 성공 (`Success! 3 passed, 0 failed.`)
  - [PASS] `subnet_cidrs`: public(`10.0.1.0/24`), private(`10.0.2.0/24`) 서브넷 CIDR 정확성 확인
  - [PASS] `resource_dependency`: 서브넷의 `parent_vpc`가 `dev-study-vpc`를 정상 참조 확인
  - [PASS] `production_label`: `environment=prod` 변수 주입 시 `prod-study-vpc` 반영 확인
- **라이프사이클 및 멱등성 검증 결과**:
  - `terraform apply`: `Resources: 3 added, 0 changed, 0 destroyed.` 확인
  - `terraform output -json network_plan`: JSON 출력 정상 확인
  - 멱등성 검증(`terraform plan`): `No changes. Your infrastructure matches the configuration.` 확인
  - 환경 변경 계획(`-var='environment=stage'`): `Plan: 0 to add, 3 to change, 0 to destroy.` 확인
  - `terraform destroy`: `Destroy complete! Resources: 3 destroyed.`, State 리소스 0개 확인
- **미검증 항목**: 없음 (로컬 CLI 환경에서 전체 수명주기 100% 실행 검증 완료)
- **Commit Hash**: `f545c96` (`feat(09-terraform): IaC State 및 네트워크 설계 PoC`)

---

## [2026-10-24 20:21] 08단계: CI/CD Pipeline & GitHub Actions 자동 테스트 및 빌드 검증
- **작업 목적**: GitHub Actions 워크플로의 파이프라인(단위 테스트, 의존성 제어, Docker 이미지 빌드, 컨테이너 스모크 테스트) 로컬 및 원격 검증
- **테스트 대상**: `.github/workflows/cloud-ci.yml`, `08-ci-actions/app.py`, `08-ci-actions/test_app.py`, `08-ci-actions/Dockerfile`
- **테스트 명령어**:
  ```zsh
  # 1. 08단계 단위 테스트
  python3 -m unittest discover -s 08-ci-actions -p 'test_*.py' -v

  # 2. 07단계 단위 테스트 (CI 워크플로 포함 항목)
  python3 -m unittest discover -s 07-compose-network -p 'test_local.py' -v

  # 3. Docker 이미지 빌드
  docker build -t cloud-ci-lab:local ./08-ci-actions

  # 4. 컨테이너 스모크 테스트 및 정리
  docker run -d --name cloud-ci-test -p 127.0.0.1:18081:8081 cloud-ci-lab:local
  curl -i http://127.0.0.1:18081/health
  docker rm -f cloud-ci-test
  ```
- **단위 테스트 결과**:
  - `08-ci-actions/test_app.py`: 총 3건 중 3건 성공 (`Ran 3 tests in 0.530s - OK`)
    - [PASS] `test_health_status`: `/health` HTTP 200 반환 확인
    - [PASS] `test_health_json`: JSON 본문 `status: ok`, `service: cloud-ci-lab` 확인
    - [PASS] `test_unknown_route`: 미등록 경로(`/missing`) 요청 시 HTTP 404 및 `{"error": "not_found"}` 확인
  - `07-compose-network/test_local.py`: 총 3건 중 3건 성공 (`Ran 3 tests in 0.526s - OK`)
- **Docker 이미지 빌드 및 스모크 테스트 결과**:
  - `docker build`: `cloud-ci-lab:local` 이미지 태깅 및 빌드 완료
  - `curl -i http://127.0.0.1:18081/health`: HTTP 200 OK 및 `{"status": "ok", "service": "cloud-ci-lab"}` 정상 수신
- **원격 GitHub Actions 검증 항목**:
  - [x] 워크플로 YAML 구문 검증 완료
  - [x] 로컬 단위 테스트 및 스모크 테스트 전수 통과
  - [ ] GitHub Actions 원격 러너 실행 결과 (Git Push 후 원격 실행 상태 확인 예정)
- **Commit Hash**: `c726181` (`feat(08-ci): GitHub Actions 자동 테스트 및 Docker 빌드`)

---

## [2026-10-24 20:10] 07단계: Docker Multi-Container Networking 및 DNS·HTTP 통합 검증
- **작업 목적**: Docker Compose 환경에서 브리지 네트워크 격리, 내장 DNS(`127.0.0.11`)를 통한 서비스 탐색, 헬스체크 및 호스트 포트 포워딩 검증
- **테스트 대상**: `07-compose-network/api/main.py`, `07-compose-network/client/check.py`, `07-compose-network/compose.yaml`
- **테스트 코드**: `07-compose-network/test_local.py`
- **테스트 명령어**:
  ```zsh
  # 1. 로컬 단위 테스트
  cd 07-compose-network
  python3 -m unittest -v test_local.py

  # 2. Docker Compose 빌드 및 백그라운드 기동
  docker compose up -d --build api
  docker compose ps

  # 3. 호스트에서 curl 검증
  curl -i http://127.0.0.1:8081/health

  # 4. 클라이언트 컨테이너를 통한 내부 서비스 DNS 및 HTTP 검증
  docker compose run --rm client

  # 5. 리소스 정리
  docker compose down
  ```
- **단위 테스트 결과**: 총 3건 중 3건 성공 (`Ran 3 tests in 0.544s - OK`)
  - [PASS] `test_dns_tcp_http`: DNS 해석, TCP 3-Way Handshake, HTTP 200 응답 수신 검증
  - [PASS] `test_response_json`: API 서버의 JSON 본문 응답 규격(`status: ok`, `service: api`) 검증
  - [PASS] `test_unknown_route_404`: 미등록 경로(`/missing`) 요청 시 HTTP 404 Not Found 반환 검증
- **Docker Compose 통합 검증 결과**:
  - `docker compose ps`: `07-compose-network-api-1` 상태 `Up About a minute (healthy)`, 포트 `127.0.0.1:8081->8081/tcp` 정상 바인딩 확인
  - `curl -i http://127.0.0.1:8081/health`: `HTTP/1.0 200 OK`, 본문 `{"status": "ok", "service": "api"}` 정상 수신
  - `docker compose run --rm client`:
    - DNS 질의(`api`): 가상 IP `["172.25.0.2"]` 수신 확인
    - TCP 연결: `tcp: true` 확인
    - HTTP 요청: `http_status: 200`, `body: {"status": "ok", "service": "api"}` 수신 확인
- **미검증 항목**: 없음 (로컬 단위 테스트 및 Docker Desktop 환경 실제 컨테이너 구동/진단 전수 검증 완료)
- **Commit Hash**: `1fee1c7` (`feat(07-compose): 서비스 DNS 및 컨테이너 네트워크 PoC 구현`)

---

## [2026-10-24 19:59] 06단계: IAM · Security Group · NACL 보안 단위·통합 검증
- **작업 목적**: IAM 최소 권한 정책 평가, Stateful 연결 추적(SG), Stateless 규칙 번호 우선순위 및 임시 포트(NACL) 검증
- **테스트 대상**: `06-cloud-security/security.py`
- **테스트 코드**: `06-cloud-security/test_security.py`
- **테스트 명령어**:
  ```zsh
  cd 06-cloud-security
  python3 -m unittest -v test_security.py
  ```
- **단위 테스트 결과**: 총 8건 중 8건 성공 (Ran 8 tests in 0.001s - OK)
  - [PASS] `test_iam_allow`: S3 일반 객체 접근 시 ALLOW 확인
  - [PASS] `test_iam_explicit_deny`: S3 private 경로 접근 시 명시적 거부(EXPLICIT_DENY) 확인
  - [PASS] `test_iam_implicit_deny`: 권한 없는 S3 삭제 요청 시 암시적 거부(IMPLICIT_DENY) 확인
  - [PASS] `test_sg_stateful`: Security Group 상태 저장(established=True) 시 아웃바운드 자동 허용 확인
  - [PASS] `test_sg_cidr`: 허용된 203.0.113.0/24 IP만 통과 확인
  - [PASS] `test_nacl_order`: 100번 규칙(Deny)이 200번 규칙(Allow)보다 낮은 번호이므로 우선 적용 확인
  - [PASS] `test_nacl_default_deny`: 일치 규칙 부재 시 기본 차단 확인
  - [PASS] `test_end_to_end`: 정상 요청, 미허용 IP, 임시 포트 차단 3가지 흐름 검증 확인
- **CLI 시뮬레이션 결과**:
  - `python3 security.py`: IAM 정상/거부 및 네트워크 인바운드/아웃바운드 모두 true 확인
  - `python3 security.py --client-ip 198.51.100.10`: SG 인바운드 차단(`request_allowed: false`) 확인
  - `python3 security.py --client-port 80`: NACL Stateless 특성에 따른 응답 차단(`response_allowed: false`) 확인
- **Commit Hash**: `499238f` (`feat(06-security): IAM SG NACL 정책 검증 PoC 구현`)

---

## [2026-10-24 19:18] 05단계: VPC Network Planner 단위 테스트 및 라우팅 시뮬레이션 검증
- **작업 목적**: CIDR 파싱, 서브넷 용량 산출(AWS 가용 -5개), 주소 중복/범위 이탈 예외 및 Longest Prefix Match 라우팅 검증
- **테스트 대상**: `05-vpc-network-planner/planner.py`
- **테스트 코드**: `05-vpc-network-planner/test_planner.py`
- **테스트 명령어**:
  ```zsh
  cd 05-vpc-network-planner
  python3 -m unittest -v test_planner.py
  ```
- **단위 테스트 결과**: 총 6건 중 6건 성공 (Ran 6 tests in 0.000s - OK)
  - [PASS] `test_valid_plan`: 10.0.1.0/24 기준 total 256개, AWS 가용 251개 정상 산출 확인
  - [PASS] `test_overlap_rejected`: 10.0.1.0/24와 10.0.1.128/25 중복 시 `ValueError("overlaps")` 정상 발생
  - [PASS] `test_outside_vpc_rejected`: 10.0.0.0/16 외 10.1.0.0/24 지정 시 `ValueError("outside")` 정상 발생
  - [PASS] `test_longest_prefix`: /24, /16, /0 다중 매칭 시 최장 접두사 정상 선택 확인
  - [PASS] `test_no_matching_route`: 매칭 규칙 부재 시 None 반환 확인
  - [PASS] `test_invalid_network`: 비트 오류 호스트 주소(10.0.1.7/24) 표기 차단 확인
- **CLI 라우팅 시뮬레이션 결과**:
  - `python3 planner.py` (`10.0.2.15`): `10.0.2.0/24` -> `specific` 매칭 확인
  - `python3 planner.py --destination 10.0.3.15`: `10.0.0.0/16` -> `local` 매칭 확인
  - `python3 planner.py --destination 8.8.8.8`: `0.0.0.0/0` -> `igw` 매칭 확인
- **Commit Hash**: `c7a945e` (`feat(05-network): CIDR subnet routing PoC 구현`)

---

## [2026-10-24 17:45] 04단계: Docker 컨테이너 및 볼륨 영속성 단위·통합 검증
- **작업 목적**: Dockerfile 기반 이미지 빌드, 컨테이너 포트 바인딩, Named Volume 파일 영속성 및 단위 테스트 검증
- **테스트 대상**: `04-docker-storage/main.py`, `Dockerfile`, `compose.yaml`
- **테스트 코드**: `04-docker-storage/test_main.py`
- **테스트 명령어**:
  ```zsh
  cd 04-docker-storage
  python3 -m unittest -v test_main.py
  ```
- **단위 테스트 결과**: 총 3건 중 3건 성공 (Ran 3 tests in 0.585s - OK)
  - [PASS] `test_health`: GET `/health` 호출 시 200 OK 및 서비스명(`cloud-docker-lab`) 확인
  - [PASS] `test_note_roundtrip`: POST `/note` (201 Created) 저장 후 GET `/note` (200 OK) 일치 확인
  - [PASS] `test_bad_note`: 필드 누락 페이로드 전송 시 400 Bad Request 확인
- **Docker 컨테이너 및 볼륨 실환경 검증 결과**:
  - `docker compose up -d --build`: 이미지 빌드 및 컨테이너(`04-docker-storage-api-1`), 볼륨(`notes_data`) 정상 생성
  - 검증 A: `curl -i http://127.0.0.1:8081/health` -> HTTP 200 OK 수신
  - 검증 B: `curl -i -X POST .../note -d '{"note":"persist-me"}'` -> HTTP 201 Created 수신
  - 검증 C-1: `docker compose down` -> 컨테이너 및 네트워크 완전 삭제
  - 검증 C-2: `docker compose up -d` -> 새 컨테이너 기동
  - 검증 C-3: `curl -i http://127.0.0.1:8081/note` -> `HTTP 200 OK`, `{"note": "persist-me"}` 데이터 복원 완벽 확인
- **Commit Hash**: `1f36e8b` (`feat(04-docker): 가상화 · Docker 컨테이너 격리 및 볼륨 영속성 PoC 구현`)

---

## [2026-10-24 17:28] 03단계: DNS·TCP·HTTP 네트워크 진단 단위 테스트 및 통합 검증
- **작업 목적**: 호스트명 해석(DNS), 포트 연결(TCP), 애플리케이션 응답(HTTP)의 계층별 진단 정확도 검증
- **테스트 대상**: `03-network-diagnostics/diagnose.py`
- **테스트 코드**: `03-network-diagnostics/test_diagnose.py`
- **테스트 명령어**:
  ```zsh
  cd 03-network-diagnostics
  python3 -m unittest -v test_diagnose.py
  ```
- **단위 테스트 결과**: 총 5건 중 5건 성공 (Ran 5 tests in 0.199s - OK)
  - [PASS] `test_dns`: `localhost` 호스트명을 `127.0.0.1`로 정상 해석
  - [PASS] `test_tcp`: 테스트 서버 소켓 포트로 TCP 3-Way Handshake 수립 성공
  - [PASS] `test_http_200`: 정상 헬스체크 경로(`/health`) 요청 시 200 OK 및 JSON 바디 수신
  - [PASS] `test_http_404`: 미등록 경로(`/missing`) 요청 시 404 Not Found 및 에러 객체 파싱
  - [PASS] `test_end_to_end`: `diagnose()` 통합 함수에서 3단계 전체 성공 검증
- **실환경 연동 검증 결과**:
  - `python3 diagnose.py 127.0.0.1 --port 8081 --path /health`: 3단계 전체 성공
  - `python3 diagnose.py 127.0.0.1 --port 8081 --path /missing`: TCP 성공, HTTP 404 정상 분기
  - `python3 diagnose.py 127.0.0.1 --port 9999`: TCP 연결 거부(`[Errno 61] Connection refused`) 정확 감지
  - `python3 diagnose.py example.com --port 80 --path /`: 외부 공인 DNS 주소 해석(104.20.23.154 등) 및 HTTP 200 성공
- **Commit Hash**: `835c480` (`feat(03-network-diagnostics): DNS·TCP·HTTP 네트워크 진단 CLI 및 검증 PoC 구현`)

---

## [2026-10-24 17:15] 02단계: 서버 프로세스 모니터 단위 테스트 및 HTTP 서버 연동 검증
- **작업 목적**: 프로세스 모니터(`monitor.py`)의 정상 PID 파싱 및 종료 상태 판별 정확도 검증
- **테스트 대상**: `02-linux-process/monitor.py`
- **테스트 코드**: `02-linux-process/test_monitor.py`
- **테스트 명령어**:
  ```zsh
  cd 02-linux-process
  python3 -m unittest -v test_monitor.py
  ```
- **단위 테스트 결과**: 총 2건 중 2건 성공 (Ran 2 tests in 0.017s - OK)
  - [PASS] `test_running_process`: 현재 실행 중인 프로세스의 PID, PPID, CPU, RSS, 상태 파싱 성공
  - [PASS] `test_nonexistent_process`: 가상 PID(999999)에 대해 `running: False` 반환 성공
- **연동 검증 결과**:
  - `01-http-server/main.py` 구동 후 `lsof -nP -iTCP:8081 -sTCP:LISTEN`으로 PID(55016) 감지 확인
  - `python3 monitor.py 55016` 실행 시 CPU(0.9%), RSS(10960KiB), status("SN+") 정상 수집 확인
  - `kill -TERM 55016` 종료 후 재조회 시 `running: false` 정상 전이 확인
- **미검증 항목**:
  - 다중 스레드/자식 프로세스 트리 전체의 합산 메모리 모니터링은 차후 컨테이너 모니터링(04/07단계)에서 확장 예정
- **Commit Hash**: `33665a3` (`feat(02-linux-process): 서버 프로세스 모니터 PoC 구현 및 HTTP 서버 연동 검증`)

---

## [2026-10-24 17:04] 01단계: HTTP 기초 서버 단위 및 통합 테스트 검증
- **작업 목적**: HTTP 서버의 정상 헬스체크 응답(200 OK) 및 비정상 경로 응답(404 Not Found) 검증
- **테스트 대상**: `01-http-server/main.py`
- **테스트 코드**: `01-http-server/test_main.py`
- **테스트 명령어**:
  ```zsh
  cd 01-http-server
  python3 -m unittest -v test_main.py
  ```
- **테스트 결과**: 총 2건 중 2건 성공 (Ran 2 tests in 0.699s - OK)
  - [PASS] `test_health`: `/health` 요청 시 상태 코드 `200 OK`, JSON 본문 `{"status": "ok", "service": "cloud-http-lab"}` 확인
  - [PASS] `test_not_found`: `/missing` 요청 시 상태 코드 `404 Not Found`, JSON 본문 `{"error": "not_found"}` 확인
- **수동 검증 (curl) 결과**:
  ```zsh
  curl -i http://127.0.0.1:8081/health
  # HTTP/1.0 200 OK
  # Content-Type: application/json
  # {"status": "ok", "service": "cloud-http-lab"}

  curl -i http://127.0.0.1:8081/missing
  # HTTP/1.0 404 Not Found
  # Content-Type: application/json
  # {"error": "not_found"}
  ```
- **미검증 항목**:
  - 다중 클라이언트 동시 요청 시 병목 현상(멀티스레딩/비동기 처리)은 02단계(Linux 프로세스/자원 모니터링)에서 심화 검증 예정
- **Commit Hash**: `f228405` (`feat(01-http-server): HTTP 기초 서버 구현 및 상태 검증 기능 추가`)
