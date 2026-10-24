# 10단계: Kubernetes Architecture & Pod · Deployment · Service Lab

## 1. 개요 및 학습 목표
- **학습 주제**: Kubernetes(K8s) 기초, Pod, Deployment, Service, 자가 치유(Self-Healing), 롤링 업데이트
- **비용**: 0원 (로컬 Minikube / Kind / Docker Desktop K8s 중심 PoC)
- **목표**:
  1. 단일 노드 또는 로컬 클러스터에서 컨테이너화된 마이크로서비스를 배포하고 관리하는 오케스트레이션 원리를 학습합니다.
  2. Deployment를 통해 복제본(Replicas) 유지 및 장애 Pod 자동 재생성 메커니즘을 검증합니다.
  3. Service(ClusterIP/NodePort)를 통한 내부 로드 밸런싱과 내장 DNS 탐색을 확인합니다.
