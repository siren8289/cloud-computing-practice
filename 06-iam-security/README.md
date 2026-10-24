# 06단계: IAM · Security Group · NACL Lab (중급 06/12)

> **실습 목표**: 클라우드 보안의 핵심 3대 요소인 **IAM 최소 권한 정책(Least Privilege Policy)**, 인스턴스 레벨의 상태 저장(Stateful) 방화벽인 **Security Group(보안 그룹)**, 그리고 서브넷 경계의 상태 비저장(Stateless) 패킷 필터인 **NACL(Network Access Control List)**의 규칙 판별 엔진을 모델링하고 검증합니다.

---

## 📌 주요 학습 예정 내용
- **IAM (Identity and Access Management)**: 주체(Principal), 행동(Action), 리소스(Resource), 효과(Effect: Allow/Deny) 기반의 JSON 정책 해석
- **Security Group (상태 저장 방화벽)**: 인바운드 허용 시 아웃바운드 자동 허용, 화이트리스트 기반 트래픽 제어
- **NACL (상태 비저장 서브넷 필터)**: 규칙 번호(Rule Number) 순서에 따른 우선 처리, 명시적 인바운드/아웃바운드 분리
- **PoC 구현 예정 파일**:
  - `security_evaluator.py`: IAM 및 SG/NACL 규칙 평가 CLI
  - `test_security.py`: 트래픽 허용/차단 자동 단위 테스트
