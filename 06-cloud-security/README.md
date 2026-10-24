# 06단계: Cloud Security Policy Simulator (IAM · Security Group · NACL)

> **실습 목표**: 클라우드 보안 아키텍처의 3대 핵심 기둥인 **IAM(Identity and Access Management)** 최소 권한 정책 평가 엔진, 인스턴스 레벨의 **Stateful 방화벽(Security Group)**, 서브넷 경계의 **Stateless 패킷 필터(NACL)**의 판별 로직을 모델링하고 자동 테스트 8건으로 검증한다.

---

## 📌 1. 핵심 학습 개념

- **IAM 권한 평가 원칙 (Least Privilege)**:
  - 명시적 거부(`Explicit Deny`)가 항상 최우선 적용됩니다.
  - 명시적 허용(`Allow`)이 있어야 권한이 승인됩니다.
  - 일치하는 규칙이 없으면 기본적으로 차단(`Implicit Deny`)됩니다.
- **Security Group (상태 저장, Stateful)**:
  - 인바운드 규칙으로 허용된 트래픽에 대한 반환(응답) 트래픽은 아웃바운드 규칙과 무관하게 자동 통과합니다.
  - `Allow` 규칙만 정의 가능합니다 (Deny 규칙 불가).
- **Network ACL (상태 비저장, Stateless)**:
  - 인바운드와 아웃바운드 규칙을 각각 별도로 엄격히 검사합니다.
  - 나가는 응답 패킷의 경우 클라이언트의 **임시 포트(Ephemeral Port: 1024~65535)**가 아웃바운드 NACL에 허용되어 있어야 응답이 도달합니다.
  - 낮은 규칙 번호(Rule Number)가 높은 번호보다 먼저 평가됩니다.

---

## 🚀 2. 실행 방법 (Mac zsh)

### 1) 기본 정책 및 네트워크 흐름 평가
```zsh
cd 06-cloud-security
python3 security.py
```
출력 예시:
```json
{
  "iam_public": "ALLOW",
  "iam_private": "EXPLICIT_DENY",
  "network": {
    "request_allowed": true,
    "response_allowed": true
  }
}
```

### 2) 허용되지 않은 클라이언트 IP 테스트
```zsh
python3 security.py --client-ip 198.51.100.10
# SG 인바운드 규칙 미일치로 request_allowed: false
```

### 3) NACL 아웃바운드 차단 시나리오 테스트 (임시 포트 미허용)
```zsh
python3 security.py --client-port 80
# request_allowed: true, response_allowed: false (Stateless NACL 차단!)
```

---

## 🧪 3. 자동 단위 테스트 실행

```zsh
cd 06-cloud-security
python3 -m unittest -v test_security.py
```

### 검증 기준 (8건)
- `test_iam_allow`: S3 퍼블릭 객체 조회 시 ALLOW
- `test_iam_explicit_deny`: S3 프라이빗 객체 조회 시 명시적 거부 EXPLICIT_DENY
- `test_iam_implicit_deny`: 권한 없는 S3 삭제 요청 시 암시적 거부 IMPLICIT_DENY
- `test_sg_stateful`: 수립된 연결(established=True)에 대한 반환 트래픽 자동 통과 검증
- `test_sg_cidr`: 허용 CIDR 대역 통과 및 미허용 IP 차단
- `test_nacl_order`: 100(Deny)이 200(Allow)보다 먼저 평가되는 순서 규칙 검증
- `test_nacl_default_deny`: 일치 규칙 부재 시 기본 차단 검증
- `test_end_to_end`: 정상 요청, IP 차단, 임시 포트 차단 3가지 엔드투엔드 시나리오 검증
- 8건 모두 `OK`
