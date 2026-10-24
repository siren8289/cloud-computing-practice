# 🧪 Test & Verification Log (테스트 검증 로그)

이 문서는 실습 기능에 대한 단위·통합·수동 검증 결과, 실행 명령어, 성공/실패 여부 및 미검증 항목을 기록합니다.

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
