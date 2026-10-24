# 🏛️ Architecture & System Design Log (아키텍처 및 시스템 설계 이력)

이 문서는 클라우드 컴퓨팅 실습의 시스템 아키텍처, 네트워크 구성, 데이터 흐름 및 설계 결정(ADR)을 기록합니다.

---

## [2026-10-24] 01단계: 클라우드 기초 및 HTTP 서버 기본 아키텍처

### 1. 설계 목적
클라우드 인프라의 모든 통신(API 호출, Health Check, 서비스 간 통신)의 근간이 되는 **HTTP 클라이언트-서버 모델**과 **네트워크 소켓 바인딩 원리**를 Mac 로컬 환경에서 직접 검증합니다.

### 2. 시스템 아키텍처 다이어그램 (Mermaid)

```mermaid
flowchart TD
    subgraph ClientArea ["Client (클라이언트 계층)"]
        Browser["웹 브라우저"]
        CurlCLI["curl CLI"]
        UnitTest["unittest 클라이언트"]
    end

    subgraph HostArea ["Mac 로컬 호스트 (127.0.0.1:8081)"]
        Socket["TCP 소켓 리스너 (:8081)"]
        HTTPServer["Python HTTPServer"]
        Handler["CloudHandler (BaseHTTPRequestHandler)"]
        Router{"경로 라우터 (self.path)"}
        Health["/health (200 OK, JSON)"]
        NotFound["기타 경로 (404 Not Found, JSON)"]
    end

    Browser -->|HTTP GET /health| Socket
    CurlCLI -->|HTTP GET /health| Socket
    UnitTest -->|HTTP GET /health| Socket
    Socket --> HTTPServer
    HTTPServer --> Handler
    Handler --> Router
    Router -->|path == '/health'| Health
    Router -->|else| NotFound
```

### 3. 데이터 및 요청/응답 흐름 시퀀스 다이어그램 (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Client as 클라이언트 (curl / test)
    participant Server as HTTP 서버 (127.0.0.1:8081)
    participant Handler as CloudHandler
    participant Response as HTTP Response Builder

    Client->>Server: TCP 연결 수립 (SYN -> SYN-ACK -> ACK)
    Client->>Server: HTTP GET /health Request 전송
    Server->>Handler: 요청 디스패치 (do_GET 호출)
    Note over Handler: self.path 검증 및 비즈니스 로직 판별
    Handler->>Response: send_response(200)
    Handler->>Response: send_header('Content-Type', 'application/json')
    Handler->>Response: send_header('Content-Length', len(body))
    Handler->>Response: end_headers()
    Handler->>Client: Response Header + JSON Body 반환 (status: ok)
    Client->>Server: 연결 종료 또는 유지
```

### 4. API 엔드포인트 명세
| Method | URI | Description | Status Code | Response Body |
| :---: | :--- | :--- | :---: | :--- |
| `GET` | `/health` | 서버 헬스체크 (상태 정상 여부 확인) | `200 OK` | `{"status": "ok", "service": "cloud-http-lab"}` |
| `GET` | `/missing` (또는 기타 모든 미등록 경로) | 존재하지 않는 리소스 요청 | `404 Not Found` | `{"error": "not_found"}` |
