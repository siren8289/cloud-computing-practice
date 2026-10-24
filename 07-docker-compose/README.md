# 07단계: Docker · Compose · 컨테이너 다중 서비스 네트워크 Lab (중급 07/12)

> **실습 목표**: 단일 컨테이너를 넘어 01~04단계의 HTTP 웹 API 서버와 03단계 네트워크 진단기를 Docker Compose의 사용자 정의 브리지 네트워크(Custom Bridge Network) 상에 독립된 멀티 컨테이너 서비스로 기동하고, **내장 DNS 기반 서비스 디스커버리(Service Discovery)**와 포트 격리 환경을 구축·검증합니다.

---

## 📌 주요 학습 예정 내용
- **Docker Compose 다중 서비스 오케스트레이션**: `api` 서비스와 `diagnostics` 서비스 정의
- **사용자 정의 브리지 네트워크 (User-Defined Bridge Network)**: 서비스 이름(`api`)을 도메인명으로 자동 해석하는 Docker 내부 DNS 동작 원리
- **포트 노출 격리**: 프라이빗 서비스는 호스트 포트 바인딩 없이 내부 네트워크 통신만 허용하는 마이크로서비스 격리 설계
- **PoC 구현 예정 파일**:
  - `compose.yaml`: 멀티 컨테이너 서비스 및 커스텀 네트워크 명세
  - `test_compose.py`: 컨테이너 간 이름 기반 통신 및 격리 자동 단위 테스트
