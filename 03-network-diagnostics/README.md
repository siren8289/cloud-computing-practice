# 03단계: Network Diagnostics CLI PoC (TCP/IP · DNS · HTTP · 네트워크 진단)

> **실습 목표**: 도메인 해석(DNS)부터 전송 계층(TCP 3-Way Handshake), 그리고 응용 계층(HTTP Request/Response)까지의 네트워크 통신 3단계를 직접 진단하고, 장애 발생 원인(DNS 해석 실패 vs 포트 리스너 부재 vs HTTP 404 경로 오류)을 명확히 구분하는 진단 CLI를 구축한다.

---

## 📌 1. 핵심 학습 개념

- **DNS (Domain Name System)**: 호스트명(도메인)을 실제 IP 주소로 매핑하는 전화번호부 (`socket.getaddrinfo`)
- **TCP 3-Way Handshake**: 데이터 전송 전 신뢰성 있는 세션을 수립하는 연결 과정 (`SYN` -> `SYN-ACK` -> `ACK`)
- **장애 원인 계층별 분리 (Troubleshooting Hierarchy)**:
  - 1단계: DNS 실패 (호스트명 조회 불가, `gaierror`)
  - 2단계: TCP 실패 (포트 미개방, 방화벽 차단, `ConnectionRefusedError`, `TimeoutError`)
  - 3단계: HTTP 실패 (서버는 떴으나 엔드포인트 없음, `404 Not Found` 등)

---

## 🚀 2. 실행 방법 (Mac zsh)

### 1) 01단계 HTTP 서버를 대상으로 로컬 진단
```zsh
# 터미널 1: 01단계 HTTP 서버 실행
cd ../01-http-server
python3 main.py

# 터미널 2: 정상 헬스체크 경로 진단 (DNS -> TCP:8081 -> HTTP /health)
cd ../03-network-diagnostics
python3 diagnose.py 127.0.0.1 --port 8081 --path /health

# 터미널 2: 존재하지 않는 경로 진단 (HTTP 404 감지)
python3 diagnose.py 127.0.0.1 --port 8081 --path /missing

# 터미널 2: 닫혀있는 포트 진단 (TCP Connection Refused 감지)
python3 diagnose.py 127.0.0.1 --port 9999
```

### 2) 외부 실제 도메인 진단 (선택 사항)
```zsh
python3 diagnose.py example.com --port 80 --path /
```

---

## 🧪 3. 자동 단위 테스트 실행

```zsh
cd 03-network-diagnostics
python3 -m unittest -v test_diagnose.py
```

### 검증 기준
- `test_dns`: `localhost` 호스트명을 `127.0.0.1`로 정상 해석
- `test_tcp`: 테스트 서버 포트로 TCP 소켓 3-Way Handshake 수립
- `test_http_200`: `/health` 요청에 대한 HTTP 200 및 JSON 파싱
- `test_http_404`: `/missing` 요청에 대한 HTTP 404 및 에러 객체 파싱
- `test_end_to_end`: `diagnose()` 통합 함수에서 3단계 전체 성공 검증
- 5건 모두 `OK`
