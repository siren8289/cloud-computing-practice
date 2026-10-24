# 01단계: Cloud HTTP Fundamentals Lab (클라우드 기초 및 HTTP 서버)

> **실습 목표**: HTTP 요청/응답 구조, 소켓 바인딩(포트/루프백), 상태 코드(Status Code), 그리고 무중단 테스트 프로세스를 체득한다.

---

## 📌 1. 핵심 학습 개념

- **IaaS vs PaaS vs SaaS**: 클라우드 서비스 모델의 책임 공유 모델(Shared Responsibility Model)
- **127.0.0.1 (Loopback Address)**: 외부 네트워크와 단절된 로컬 호스트 전용 가상 인터페이스
- **HTTP 요청/응답 라이프사이클**: 클라이언트 요청 → 소켓 수신 → Request Handler 라우팅 → Header/Body 구성 → 응답 반환
- **Health Check (/health)**: 클라우드 로드밸런서(ALB, Nginx) 및 쿠버네티스(K8s Liveness/Readiness Probe)에서 인스턴스 정상 여부를 주기적으로 검사하는 핵심 엔드포인트

---

## 🚀 2. 실행 방법 (Mac zsh)

### 서버 실행
```zsh
cd 01-http-server
python3 main.py
```
출력:
```text
Server: http://127.0.0.1:8081
```

### curl 요청 검증 (별도 터미널 창)
```zsh
# 1. 헬스체크 정상 요청 (200 OK)
curl -i http://127.0.0.1:8081/health

# 2. 존재하지 않는 경로 요청 (404 Not Found)
curl -i http://127.0.0.1:8081/missing
```

---

## 🧪 3. 자동 단위 테스트 실행

```zsh
cd 01-http-server
python3 -m unittest -v
```

### 검증 기준
- `test_health`: 상태 코드 200, `{"status": "ok", "service": "cloud-http-lab"}`
- `test_not_found`: 상태 코드 404, `{"error": "not_found"}`
- 자동 테스트 2건 모두 `ok` 통과
