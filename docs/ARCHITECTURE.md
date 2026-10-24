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

---

## [2026-10-24] 02단계: Linux 커널 자원 관리 및 서버 프로세스 모니터링 아키텍처

### 1. 설계 목적
클라우드 가상 머신(EC2) 또는 컨테이너(Docker/K8s) 내부에서 실행되는 서버 애플리케이션의 운영체제 자원 점유 구조(PID, PPID, CPU, RSS 메모리, STAT)를 추적하고, 시스템 호출 및 시그널(SIGTERM)을 통한 정상 종료 프로세스를 검증합니다.

### 2. 프로세스 라이프사이클 및 시스템 자원 상호작용 (Mermaid)

```mermaid
flowchart TD
    subgraph OSKernel ["운영체제 커널 (macOS / Linux Kernel)"]
        Scheduler["CPU 스케줄러 (시분할 다중화)"]
        MMU["가상 메모리 관리자 (RSS 상주 메모리)"]
        SocketTable["TCP 소켓 테이블 (:8081 LISTEN)"]
        ProcTable["프로세스 테이블 (PID, PPID, STAT)"]
    end

    subgraph ServerProcess ["HTTP 서버 프로세스 (PID: 55016)"]
        MainThread["메인 실행 스레드 (CloudHandler)"]
        MemoryHeap["Python 힙 메모리 (약 10.9MB)"]
    end

    subgraph MonitorTool ["프로세스 모니터 (monitor.py)"]
        SubprocessCall["subprocess.run('ps -p PID ...')"]
        Parser["출력 문자열 6필드 파싱 엔진"]
        JSONOutput["표준 JSON 출력 (running, cpu, rss)"]
    end

    ServerProcess -->|시스템 호출 (socket, bind)| SocketTable
    ServerProcess -->|메모리 할당 요청 (malloc)| MMU
    Scheduler -->|CPU 실행 시간 배분| MainThread
    SubprocessCall -->|커널 프로세스 테이블 조회| ProcTable
    ProcTable --> Parser
    Parser --> JSONOutput
```

### 3. 프로세스 생명주기 상태 전이도 (State Diagram)

```mermaid
stateDiagram-v2
    [*] --> Ready: 프로세스 생성 (fork/execv)
    Ready --> Running: CPU 스케줄러 디스패치
    Running --> Ready: 시분할 할당 시간 만료
    Running --> Waiting: I/O 또는 네트워크 이벤트 대기
    Waiting --> Ready: I/O 완료 인터럽트 수신
    Running --> Terminated: SIGTERM/SIGINT 수신 및 자원 반환
    Terminated --> [*]
```

---

## [2026-10-24] 03단계: TCP/IP · DNS · HTTP 계층형 네트워크 진단 아키텍처

### 1. 설계 목적
클라우드 인프라의 마이크로서비스 또는 클라이언트가 원격 서버와 통신할 때 거치는 **3대 네트워크 계층(DNS 주소 해석 → TCP 3-Way Handshake 세션 수립 → HTTP 요청/응답)**을 프로그래밍 방식으로 분리하여 장애 원인(도메인 미등록 vs 포트 미오픈/방화벽 vs 경로 404)을 정확하게 판별합니다.

### 2. 계층별 네트워크 진단 아키텍처 (Mermaid)

```mermaid
flowchart TD
    subgraph DiagnosticTool ["네트워크 진단 도구 (diagnose.py)"]
        CLI["사용자 CLI 인자 (host, port, path)"]
        DnsStep["1단계: DNS 해석 (getaddrinfo)"]
        TcpStep["2단계: TCP 연결 (create_connection)"]
        HttpStep["3단계: HTTP 통신 (urlopen)"]
        Report["통합 JSON 진단 리포트"]
    end

    subgraph NetworkLayers ["인터넷 / 로컬 네트워크 계층"]
        DNS["DNS 네임서버 (도메인 -> IP 변환)"]
        Socket["TCP 계층 (SYN -> SYN-ACK -> ACK)"]
        Server["HTTP 웹 서버 (01-http-server)"]
    end

    CLI --> DnsStep
    DnsStep -->|도메인 주소 질의| DNS
    DNS -->|IP 주소 목록 반환| DnsStep
    DnsStep -->|성공 시 IP 전달| TcpStep
    TcpStep -->|TCP 3-Way Handshake 시도| Socket
    Socket -->|연결 성공| TcpStep
    TcpStep -->|소켓 연결 성공 시| HttpStep
    HttpStep -->|GET /health 요청| Server
    Server -->|200 OK / 404 Not Found| HttpStep
    HttpStep --> Report
```

### 3. 계층별 장애 판별 매트릭스 (Troubleshooting Hierarchy)

| 진단 단계 | 점검 기술 | 성공 시 결과 | 실패 시 에러 및 원인 분석 |
| :---: | :---: | :--- | :--- |
| **1단계: DNS** | `socket.getaddrinfo()` | `ok: true`, IP 목록 반환 | `gaierror`: 잘못된 도메인명, 로컬 DNS 설정 오류 |
| **2단계: TCP** | `socket.create_connection()` | `ok: true`, 포트 연결 성공 | `ConnectionRefusedError`: 서버 프로세스 미구동, 방화벽 차단<br>`TimeoutError`: 네트워크 라우팅 지연, 패킷 드롭 |
| **3단계: HTTP** | `urllib.request.urlopen()` | `ok: true`, Status 200 | `HTTP 404`: 경로는 틀렸으나 네트워크 연결은 완벽히 정상<br>`HTTP 500`: 백엔드 서버 내부 애플리케이션 버그 |

---

## [2026-10-24] 04단계: 가상화 · Docker 컨테이너 격리 및 스토리지 영속성 아키텍처

### 1. 설계 목적
운영체제 레벨 가상화 기술인 Docker를 활용하여 01단계의 HTTP 서버를 불변(Immutable) 이미지로 패키징하고, 컨테이너 프로세스가 종료·삭제되어도 사용자 데이터(`note.txt`)가 보존되도록 **Docker Named Volume 마운트 아키텍처**를 구성 및 검증합니다.

### 2. Docker 포트 매핑 및 볼륨 마운트 구조 (Mermaid)

```mermaid
flowchart TD
    subgraph HostMac ["macOS 호스트 (127.0.0.1)"]
        CurlClient["curl CLI / 웹 브라우저"]
        HostPort["호스트 바인딩 포트 (:8081)"]
        subgraph DockerStorageEngine ["Docker 스토리지 서브시스템"]
            NamedVol["Docker Named Volume (notes_data)<br>물리 경로: /var/lib/docker/volumes/..."]
        end
    end

    subgraph ContainerSpace ["Docker 격리 컨테이너 (04-docker-storage-api-1)"]
        ContainerPort["컨테이너 소켓 (:8081)"]
        PythonServer["Python HTTP Server (main.py)"]
        subgraph ImageLayers ["컨테이너 파일시스템 계층"]
            ROLayer["Image 레이어 (python:3.11-slim + code) - Read Only"]
            RWLayer["Container 레이어 (임시 쓰기 계층) - Read/Write"]
        end
        MountPoint["마운트 지점: /data/note.txt"]
    end

    CurlClient -->|http://127.0.0.1:8081/note| HostPort
    HostPort -->|Docker NAT 브리지 포워딩| ContainerPort
    ContainerPort --> PythonServer
    PythonServer -->|POST /note 파일 쓰기| MountPoint
    MountPoint -.->|볼륨 바인드 마운트 동기화| NamedVol
```

### 3. 컨테이너 삭제 및 재생성 시 데이터 영속성 라이프사이클

```mermaid
sequenceDiagram
    autonumber
    actor Admin as 사용자 (Mac Terminal)
    participant Compose as Docker Compose
    participant Container1 as 컨테이너 #1 (api-1)
    participant Volume as Named Volume (notes_data)
    participant Container2 as 컨테이너 #2 (새로운 api-1)

    Admin->>Compose: docker compose up -d --build
    Compose->>Volume: Volume 'notes_data' 생성
    Compose->>Container1: Container #1 기동 (Volume /data 마운트)
    Admin->>Container1: POST /note {"note": "persist-me"}
    Container1->>Volume: /data/note.txt 파일 기록 (영구 저장)
    
    Note over Admin,Container1: [컨테이너 파괴 단계]
    Admin->>Compose: docker compose down
    Compose->>Container1: Container #1 강제 종료 및 삭제
    Note over Volume: 볼륨 'notes_data'는 삭제되지 않고 호스트에 온전히 보존됨!

    Note over Admin,Container2: [새 컨테이너 기동 및 데이터 복원 확인]
    Admin->>Compose: docker compose up -d
    Compose->>Container2: 완전히 새로운 컨테이너 #2 생성 (동일 볼륨 마운트)
    Admin->>Container2: GET /note 요청
    Container2->>Volume: /data/note.txt 조회
    Container2-->>Admin: 200 OK {"note": "persist-me"} 반환 (영속성 검증 성공!)
```

---

## [2026-10-24] 05단계: VPC 가상 사설망 · 서브넷 구획 및 라우팅 아키텍처

### 1. 설계 목적
클라우드 인프라의 근간인 **VPC(Virtual Private Cloud)** 논리망 구축, Public/Private 서브넷 격리 분할, 주소 중복 충돌 방지, 그리고 패킷 라우팅의 최우선 규칙인 **Longest Prefix Match(최장 접두사 일치)** 알고리즘을 파이썬 표준 라이브러리(`ipaddress`)로 모델링하여 검증합니다.

### 2. VPC 및 서브넷 라우팅 구조 (Mermaid)

```mermaid
flowchart TD
    subgraph VPC ["AWS Virtual Private Cloud (10.0.0.0/16) - 총 65,536개 IP"]
        subgraph PublicSubnet ["Public Subnet (10.0.1.0/24) - 가용 251개"]
            WebServer["웹 서버 인스턴스 (10.0.1.10)"]
        end

        subgraph PrivateSubnet ["Private Subnet (10.0.2.0/24) - 가용 251개"]
            Database["DB 인스턴스 (10.0.2.15)"]
        end

        subgraph RouteTable ["서브넷 라우트 테이블 (Longest Prefix Match)"]
            R1["10.0.2.0/24 -> Target: specific (우선순위 1위: /24)"]
            R2["10.0.0.0/16 -> Target: local (우선순위 2위: /16)"]
            R3["0.0.0.0/0 -> Target: igw (기본 경로: /0)"]
        end
    end

    InternetGateway["인터넷 게이트웨이 (IGW)"]
    PublicSubnet -->|인터넷 통신 (0.0.0.0/0)| RouteTable
    RouteTable -->|외부 공인 IP (예: 8.8.8.8)| InternetGateway
    RouteTable -->|내부 VPC 통신 (예: 10.0.3.15)| R2
    RouteTable -->|특정 전용 서브넷 통신 (예: 10.0.2.15)| R1
```

### 3. Longest Prefix Match 라우팅 매칭 매트릭스

| 목적지 IP | 매칭되는 라우트 후보들 | 선택된 최장 접두사 (Winner) | 최종 타깃 (Target) | 라우팅 결정 이유 |
| :---: | :--- | :---: | :---: | :--- |
| `10.0.2.15` | `0.0.0.0/0` (/0), `10.0.0.0/16` (/16), `10.0.2.0/24` (/24) | `10.0.2.0/24` | `specific` | 일치하는 규칙 중 서브넷 마스크 비트 길이가 가장 김 (/24) |
| `10.0.3.15` | `0.0.0.0/0` (/0), `10.0.0.0/16` (/16) | `10.0.0.0/16` | `local` | /24는 불일치, /0보다 더 구체적인 /16이 우선 적용됨 |
| `8.8.8.8` | `0.0.0.0/0` (/0) | `0.0.0.0/0` | `igw` | 내부 사설 IP가 아니므로 기본 경로(Default Gateway)로 전달 |

---

## [2026-10-24] 06단계: 클라우드 보안 3대 요소 (IAM · Security Group · NACL) 아키텍처

### 1. 설계 목적
클라우드 보안 거버넌스의 3대 축인 **IAM(API 제어 권한 평가)**, **Security Group(인스턴스 레벨 Stateful 방화벽)**, **NACL(서브넷 경계 Stateless 패킷 필터)**의 동작 메커니즘을 모델링하고, 명시적 거부 최우선 원칙 및 상태 저장/비저장 트래픽 제어를 검증합니다.

### 2. 클라우드 다계층 보안 방어선 구조 (Mermaid)

```mermaid
flowchart TD
    subgraph ClientLayer ["외부 클라이언트 (IP: 203.0.113.10)"]
        UserReq["HTTP 요청 (:8081)<br>출발지 임시포트: 55000"]
        UserResp["HTTP 응답 수신 (:55000)"]
    end

    subgraph SubnetBoundary ["서브넷 경계 보안 (Stateless)"]
        NaclIn{"NACL Inbound 규칙<br>낮은 번호순 평가 (Rule 100)"}
        NaclOut{"NACL Outbound 규칙<br>임시포트(1024~65535) 검사"}
    end

    subgraph InstanceBoundary ["인스턴스 경계 보안 (Stateful)"]
        SGIn{"Security Group Inbound<br>허용 규칙 집합 (Allow Only)"}
        SGConnTracker["연결 추적기 (Connection Tracker)<br>established=True 자동 허용"]
    end

    subgraph Workload ["웹 서버 워크로드 (:8081)"]
        HttpApp["Python HTTP Web Server"]
    end

    UserReq -->|1. 패킷 도착| NaclIn
    NaclIn -->|Rule 100 Allow| SGIn
    NaclIn -.->|일치 규칙 없음/Deny| Drop1["패킷 차단 (Drop)"]

    SGIn -->|허용 CIDR 일치| HttpApp
    SGIn -.->|규칙 없음| Drop2["패킷 차단 (Drop)"]

    HttpApp -->|2. 응답 패킷 전송| SGConnTracker
    SGConnTracker -->|Stateful: 별도 아웃바운드 규칙 불필요| NaclOut
    NaclOut -->|Rule 100 Allow (1024~65535)| UserResp
    NaclOut -.->|아웃바운드 미허용 시 (예: port 80)| Drop3["응답 패킷 차단 (Drop)"]
```

### 3. IAM 권한 평가 결정 트리 (Decision Tree)

```mermaid
flowchart TD
    Request["API 작업 요청 (Action, Resource)"] --> CheckExplicitDeny{"일치하는 명시적 Deny<br>(Explicit Deny)가 있는가?"}
    CheckExplicitDeny -->|Yes| DenyResult["EXPLICIT_DENY (최종 거부)"]
    CheckExplicitDeny -->|No| CheckExplicitAllow{"일치하는 명시적 Allow<br>(Explicit Allow)가 있는가?"}
    CheckExplicitAllow -->|Yes| AllowResult["ALLOW (작업 승인)"]
    CheckExplicitAllow -->|No| ImplicitDenyResult["IMPLICIT_DENY (기본 차단)"]
```







---

## [2026-10-24] 07단계: Docker Multi-Container Networking & Service Discovery 아키텍처

### 1. 설계 목적
단일 컨테이너 실행 환경을 넘어 마이크로서비스 아키텍처의 핵심인 **컨테이너 간 격리된 사설 가상 네트워크(User-defined Bridge Network)**와 **이름 기반 주소 해석(Embedded DNS Service Discovery)**, 그리고 **선언적 헬스체크 기반 의존성(`condition: service_healthy`)**을 구성하고 통신 경로를 분리 검증합니다.

### 2. 멀티 컨테이너 네트워크 및 통신 경로 (Mermaid)

```mermaid
flowchart TD
    subgraph HostMac ["호스트 머신 (macOS)"]
        CurlCmd["curl -i http://127.0.0.1:8081/health"]
        PortProxy["포트 포워딩 프록시 (127.0.0.1:8081 -> 8081)"]
    end

    subgraph CustomBridgeNet ["Docker 가상 브리지 네트워크: lab-net (172.25.0.0/16)"]
        subgraph DockerDNS ["Docker 내장 DNS 서버 (127.0.0.11:53)"]
            DNSLookup["서비스 이름 'api' -> 가상 IP 172.25.0.2 매핑 반환"]
        end

        subgraph ClientSvc ["client 컨테이너 (진단 클라이언트)"]
            CheckScript["check.py<br>1. socket.getaddrinfo('api', 8081)<br>2. socket.create_connection()<br>3. urllib.request.urlopen()"]
        end

        subgraph ApiSvc ["api 컨테이너 (Python ThreadingHTTPServer)"]
            ApiApp["main.py<br>바인딩: 0.0.0.0:8081<br>IP: 172.25.0.2"]
            HealthcheckProbe["Healthcheck: urllib.request /health (간격: 2s)"]
        end
    end

    CurlCmd -->|호스트 루프백 요청| PortProxy
    PortProxy -->|브리지 네트워크 포워딩| ApiApp
    CheckScript -->|1. 도메인 'api' DNS 질의| DNSLookup
    DNSLookup -->|2. 가상 IP 172.25.0.2 응답| CheckScript
    CheckScript -->|3. TCP 연결 및 GET /health 요청| ApiApp
    ApiApp -->|4. HTTP 200 OK + JSON 응답| CheckScript
```

### 3. 통신 경로 및 보안 격리 비교

| 구분 | 호스트 접근 경로 | 컨테이너 내부 접근 경로 |
| :--- | :--- | :--- |
| **목적지 주소** | `http://127.0.0.1:8081/health` | `http://api:8081/health` |
| **주소 해석 방식** | 호스트 OS `/etc/hosts` 및 루프백 | Docker 내장 DNS (`127.0.0.11`) |
| **적용 보안 설정** | `ports: ["127.0.0.1:8081:8081"]` (로컬 루프백 한정) | `networks: [lab-net]` (동일 가상 브리지 내 격리) |
| **특징** | 외부 네트워크 노출 차단, 안전한 로컬 개발 | IP 변경 시에도 서비스 이름(`api`)으로 유연하게 결합 |


---

## [2026-10-24] 08단계: CI/CD Pipeline & GitHub Actions Automation 아키텍처

### 1. 설계 목적
개발자가 로컬에서 작성한 코드가 원격 저장소(`main` 브랜치)에 반영될 때마다 빌드·테스트를 수동으로 수행하지 않고, **GitHub Actions 클라우드 러너(Runner)를 통해 자동화된 품질 검증(CI)을 강제**하는 아키텍처를 수립합니다.
- **Fail-Fast 원칙**: Python 단위 테스트가 실패하면 리소스가 많이 소모되는 Docker 이미지 빌드 단계(`needs: python-tests`)로 진입하지 않고 즉시 파이프라인을 중단합니다.
- **최소 권한 원칙(Least Privilege)**: 워크플로 토큰 권한을 `permissions: contents: read`로 제한하여 잠재적인 보안 사고를 방지합니다.

### 2. CI 파이프라인 워크플로 구조 (Mermaid)

```mermaid
flowchart TD
    subgraph Trigger ["트리거 이벤트 (Triggers)"]
        PushEvent["git push origin main"]
        PREvent["Pull Request to main"]
        ManualEvent["workflow_dispatch (수동 트리거)"]
    end

    subgraph GitHubHostedRunner ["GitHub Actions 클라우드 환경 (ubuntu-latest)"]
        subgraph Job1 ["Job 1: python-tests"]
            StepCheckout1["actions/checkout@v6"]
            StepSetupPy["actions/setup-python@v6 (Python 3.11)"]
            StepTestApp["08-ci-actions/test_app.py 단위 테스트 (3건)"]
            StepTestNet["07-compose-network/test_local.py 단위 테스트 (3건)"]
        end

        subgraph Job2 ["Job 2: docker-build (needs: python-tests)"]
            StepCheckout2["actions/checkout@v6"]
            StepDockerBuild["docker build -t cloud-ci-lab:ci ./08-ci-actions"]
            StepSmokeTest["Smoke Test: 컨테이너 기동 및 헬스체크 폴링 (최대 25회)"]
            StepComposeBuild["07-compose-network compose build 검증"]
        end
    end

    PushEvent --> StepCheckout1
    PREvent --> StepCheckout1
    ManualEvent --> StepCheckout1

    StepCheckout1 --> StepSetupPy --> StepTestApp --> StepTestNet
    StepTestNet -->|성공 (Success)| StepCheckout2
    StepTestNet -.->|실패 (Fail)| Abort["파이프라인 즉시 중단 (Fail-Fast)"]

    StepCheckout2 --> StepDockerBuild --> StepSmokeTest --> StepComposeBuild
    StepComposeBuild --> PassResult["최종 CI 성공 (Green Check)"]
```

### 3. CI 파이프라인 구성 요소 비교 매트릭스

| 구성 요소 | 기술 스펙 | 핵심 역할 및 실무 의의 |
| :--- | :--- | :--- |
| **Workflow** | `cloud-ci.yml` | 전체 자동화 파이프라인의 생명주기와 실행 흐름을 선언하는 YAML 명세서 |
| **Runner** | `ubuntu-latest` | GitHub이 클라우드 상에서 일회성(Ephemeral)으로 프로비저닝하여 작업을 격리 실행하는 가상 머신 |
| **Job 1** | `python-tests` | 런타임 의존성 구성 및 단위 테스트를 수행하여 코드 로직의 결함을 1차 방어 |
| **Job 2** | `docker-build` | `needs: python-tests`로 선행 작업 통과 시에만 컨테이너 불변 이미지 패키징 및 스모크 테스트 수행 |
| **Permissions** | `contents: read` | 불필요한 쓰기/관리자 권한을 배제하여 토큰 탈취 시 저장소 변조 위협을 차단 |
