# 📝 Development Work Log (개발 작업 로그)

이 문서는 작업 일자별 구현 내용, 변경 파일, 실행 명령어, 검증 결과 및 Git 커밋 내역을 기록합니다.

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
