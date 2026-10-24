# 05단계: VPC · Subnet · CIDR · Routing Lab (중급 05/12)

> **실습 목표**: Docker 가상 네트워크(Bridge)에서 실제 클라우드 가상 사설망(VPC, Virtual Private Cloud)으로 확장하여, IPv4 CIDR 블록 계산, Public/Private 서브넷 구획 분리, 라우팅 테이블(RT) 규칙을 Python 기반 CLI로 모델링하고 검증합니다.

---

## 📌 주요 학습 예정 내용
- **CIDR 표기법 (Classless Inter-Domain Routing)**: `/16`, `/24` 프리픽스에 따른 가용 IP 대역 계산 원리
- **Public vs Private 서브넷**: 인터넷 게이트웨이(IGW) 직접 연결 여부에 따른 인프라 격리 설계
- **라우팅 테이블 (Routing Table)**: 대상(Destination) CIDR과 타깃(Target, IGW/NAT Gateway/Local)의 매핑 구조
- **PoC 구현 예정 파일**:
  - `cidr_calculator.py`: 서브넷 계산 및 중첩 충돌 감지 CLI
  - `test_cidr.py`: 서브넷 분할 및 라우팅 규칙 자동 단위 테스트
