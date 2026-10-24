# 🧪 Test & Verification Log (테스트 검증 로그)

이 문서는 실습 기능에 대한 단위·통합·수동 검증 결과, 실행 명령어, 성공/실패 여부 및 미검증 항목을 기록합니다.

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
