# 🐞 Error & Troubleshooting Log (오류 해결 및 트러블슈팅 로그)

이 문서는 실습 중 발생한 오류의 현상, 에러 로그, 근본 원인 분석, 해결 조치 및 재검증 결과를 체계적으로 기록합니다.

---

## [2026-10-24] Docker 컨테이너 구동 직후 스모크 테스트 시 RemoteDisconnected 발생 및 해결
- **발생 상황 / 실행 명령어**: `docker run -d ... && python3 -c "urllib.request.urlopen(...)"`
- **오류 로그**:
  ```text
  http.client.RemoteDisconnected: Remote end closed connection without response
  ```
- **원인 분석**:
  - `docker run -d` 명령어는 백그라운드 컨테이너 생성이 완료되는 즉시 셸로 제어를 반환하지만, 컨테이너 내부의 Python 프로세스가 실행되고 소켓 포트(`0.0.0.0:8081`)를 `listen()` 상태로 전환하기까지 약간의 부팅 지연(Cold Start, 수백 밀리초)이 존재합니다.
  - 이 짧은 시간차 동안 클라이언트가 즉시 HTTP 요청을 보내면 소켓 연결이 비정상 종료(RemoteDisconnected)됩니다.
- **해결 방법**:
  - CI 워크플로 스크립트(`.github/workflows/cloud-ci.yml`)와 동일하게 재시도 및 백오프 폴링 로직(`for i in range(25): try ... time.sleep(0.5)`)을 적용하여 컨테이너가 요청을 수신할 준비가 될 때까지 안전하게 대기하도록 구성.
- **재검증 결과**:
  - 컨테이너 구동 후 `curl -i http://127.0.0.1:18081/health` 실행 시 `HTTP/1.0 200 OK` 정상 수신 확인
- **관련 커밋**: `feat(08-ci): GitHub Actions 자동 테스트 및 Docker 빌드`

---

## [2026-10-24] ps 명령어 실행 시 zsh: operation not permitted 차단 및 조치
- **발생 상황 / 실행 명령어**: `ps -p $$ -o pid=,ppid=,%cpu=,rss=,stat=,comm=`
- **오류 로그**:
  ```text
  zsh:1: operation not permitted: ps
  ```
- **원인 분석**: 
  - macOS 샌드박스 보안 환경에서는 시스템 프로세스 정보 테이블을 직접 읽어오는 `ps` 바이너리의 실행이 격리 제한됨.
- **해결 방법**: 
  - 호스트 권한(BypassSandbox: true)으로 커널 프로세스 테이블 접근 권한을 확보하여 실행.
- **재검증 결과**:
  - `python3 -m unittest -v test_monitor.py` 2건 전수 통과 (`OK`)
  - `python3 monitor.py` 정상 JSON 출력 확인
- **관련 커밋**: `feat(02-linux-process): 서버 프로세스 모니터 PoC 구현 및 HTTP 서버 연동 검증`

---

## [2026-10-24] 단위 테스트 실행 시 PermissionError (Operation not permitted) 발생 및 해결
- **발생 상황 / 실행 명령어**: `python3 -m unittest -v test_main.py`
- **오류 로그**:
  ```text
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/socket.py", line 836, in create_connection
      sock.connect(sa)
  PermissionError: [Errno 1] Operation not permitted
  urllib.error.URLError: <urlopen error [Errno 1] Operation not permitted>
  ```
- **원인 분석**: 
  - macOS 보안 샌드박스 격리 환경에서는 가상 루프백 네트워크(`127.0.0.1`)라 하더라도 프로세스 간 소켓 연결(`connect`) 권한이 기본 차단됨.
- **해결 방법**: 
  - 개발자 터미널 및 호스트 권한(BypassSandbox 모드)으로 명령어를 승인하여 로컬 루프백 소켓 통신을 정상 허용하도록 조치.
- **재검증 결과**:
  - `python3 -m unittest -v test_main.py` 실행 결과: 2건의 테스트 모두 통과 (`OK`, 소요시간 0.699초)
  - `curl -i http://127.0.0.1:8081/health` 정상 수신 확인
- **관련 커밋**: `feat(01-http-server): HTTP 기초 서버 구현 및 상태 검증 기능 추가`
