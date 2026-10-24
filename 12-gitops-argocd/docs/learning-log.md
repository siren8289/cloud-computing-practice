# GitOps & Argo CD PoC 학습 및 검증 로그

- **테스트 환경**: macOS (Apple Silicon), Docker Desktop, kind v0.31.0, Kubernetes v1.37.0
- **저장소**: https://github.com/siren8289/cloud-computing-practice.git
- **검증 일시**: 2026-10-24 21:23:00 KST

## 검증 결과 요약
1. **Manifests static tests**: PASS (3/3 통과, `tests/test_manifests.py`)
2. **Git push for Argo CD**: PASS (Commit `9826355`, GitHub `main` 브랜치에 매니페스트 배포)
3. **kind cluster create**: PASS (`kind-cloud-study` 생성 완료, 19초)
4. **Argo CD installation**: PASS (`argocd` 네임스페이스에 서버사이드 어플라이로 설치 완료)
5. **Argo CD Application creation**: PASS (`cloud-gitops-lab` Application 생성 및 Synced/Healthy 달성)
6. **Deployment rollout**: PASS (`gitops-lab/web` Deployment 2/2 Pod Running)
7. **Service internal check (`verify.sh`)**: PASS (임시 curl Pod를 통한 ClusterIP:80 호출 성공, HTTP 200 Nginx HTML 수신)
8. **Argo CD Self-Heal test (Drift 복구)**: PASS
   - `kubectl scale deployment/web --replicas=1` 수동 변경으로 드리프트 발생
   - Argo CD가 2초 내에 변경 감지 후 Git 선언 상태인 `spec.replicas: 2`로 자동 롤백 복구 성공
9. **Kubernetes Pod recovery test (HA 복구)**: PASS
   - `web-d6b9b7466-cssjg` Pod 강제 삭제
   - Kubernetes ReplicaSet 컨트롤러가 신규 Pod `web-d6b9b7466-64s2w`를 즉시 기동하여 2/2 Ready 복원 성공
10. **Cluster 정리**: PASS (`kind delete cluster --name cloud-study` 완료)

## Error logs (오류 및 해결 내역)
| Command | Error | Cause | Fix | Retest |
|---|---|---|---|---|
| `kubectl apply -n argocd -f .../install.yaml` | `CustomResourceDefinition "applicationsets.argoproj.io" is invalid: metadata.annotations: Too long: may not be more than 262144 bytes` | kubectl 클라이언트 사이드 apply 시 `last-applied-configuration` 어노테이션 크기가 256KB 한도를 초과함 | `kubectl apply --server-side --force-conflicts -n argocd -f ...` 명령어로 서버사이드 apply 적용 | PASS (모든 Argo CD CRD 및 컨트롤러 정상 등록 완료) |
