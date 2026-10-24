# 11단계: Observability & Monitoring (Prometheus · Metrics)

## 1. 개요 및 학습 목표
- **학습 주제**: 클라우드 관측 가능성(Observability), Prometheus 메트릭 수집, 카운터(Counter) 및 히스토그램(Histogram), 모니터링 대시보드
- **비용**: 0원 (로컬 Prometheus 및 메트릭 엔드포인트 기반)
- **목표**:
  1. 클라우드 마이크로서비스에서 메트릭(`GET /metrics`)을 표준 포맷으로 노출하는 원리를 이해합니다.
  2. 요청 수, HTTP 상태 코드별 응답 수, 지연 시간(Latency)을 측정하는 모니터링 시스템을 구축합니다.
  3. 서비스의 가용성과 성능 이상 징후를 실시간 메트릭으로 탐지합니다.
