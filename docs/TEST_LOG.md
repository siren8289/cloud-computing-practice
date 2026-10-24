# 🧪 Test & Verification Log (테스트 검증 로그)

이 문서는 실습 기능에 대한 단위·통합·수동 검증 결과, 실행 명령어, 성공/실패 여부 및 미검증 항목을 기록합니다.

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
