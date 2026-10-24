# 12단계: GitOps · Argo CD · High Availability (HA)

## 1. 개요 및 학습 목표
- **학습 주제**: GitOps 패러다임, Argo CD, 지속적 배포(CD), 고가용성(High Availability, HA), 자가 치유 및 상태 동기화(Drift Detection)
- **비용**: 0원 (로컬 K8s 및 Git 기반 선언형 배포)
- **목표**:
  1. Git 저장소를 단일 진실 원천(Single Source of Truth)으로 삼아 인프라와 애플리케이션의 배포 형상을 선언적으로 관리합니다.
  2. Git의 변경 사항을 감지하여 대상 클러스터에 자동으로 동기화(Sync)하고, 수동 변경(Drift) 발생 시 원래 형상으로 자동 복구(Auto-Heal)하는 메커니즘을 학습합니다.
  3. 무중단 고가용성 아키텍처의 최종 완결을 검증합니다.
