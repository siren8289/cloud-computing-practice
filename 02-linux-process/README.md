# 02단계: Server Process Monitor PoC (Linux · 서버 · 운영체제)

> **실습 목표**: 운영체제 커널의 프로세스 관리 체계(PID, PPID, CPU, RSS 메모리, STAT)를 이해하고, 시스템 명령어(`ps`, `lsof`, `kill`)를 파이썬 모니터링 도구로 추상화하여 서버 프로세스의 라이프사이클을 추적·검증한다.

---

## 📌 1. 핵심 학습 개념

- **OS & Kernel**: 하드웨어 자원(CPU, 메모리, 네트워크 인터페이스)을 통제하고 프로세스에 추상화된 가상 공간을 제공
- **PID (Process ID)**: 운영체제가 생성된 프로세스마다 부여하는 고유 식별 번호
- **RSS (Resident Set Size)**: 가상 메모리가 아닌, 프로세스가 실제 물리 메모리(RAM)에 점유 중인 크기 (KiB 단위)
- **Signal & Lifecycle**: 프로세스의 Ready -> Running -> Waiting -> Terminated 전이 과정과 `kill -TERM`(SIGTERM, 정상 종료) / `kill -KILL`(SIGKILL, 강제 종료)

---

## 🚀 2. 실행 방법 (Mac zsh)

### 1) 현재 모니터 프로세스 자체 분석
```zsh
cd 02-linux-process
python3 monitor.py
```
출력 예시:
```json
{
  "pid": 56789,
  "ppid": 12345,
  "cpu_percent": 0.0,
  "rss_kib": 9820,
  "status": "R+",
  "command": "python3",
  "running": true
}
```

### 2) 01단계 HTTP 서버와 연동하여 실시간 모니터링
```zsh
# 터미널 1: 01단계 HTTP 서버 실행
cd ../01-http-server
python3 main.py

# 터미널 2: 포트 8081을 리스닝 중인 서버의 PID 확인
lsof -nP -iTCP:8081 -sTCP:LISTEN

# 터미널 2: 확인된 PID로 모니터링 실행
python3 ../02-linux-process/monitor.py <조회된_PID>
```

---

## 🧪 3. 자동 단위 테스트

```zsh
cd 02-linux-process
python3 -m unittest -v test_monitor.py
```

### 검증 기준
- `test_running_process`: 현재 실행 중인 프로세스의 PID 및 메트릭 파싱 성공 (`running: True`)
- `test_nonexistent_process`: 가상 PID(999999)에 대해 미존재 상태 정상 판별 (`running: False`)
- 2건 모두 `OK`
