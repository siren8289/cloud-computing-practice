# Kubernetes PoC log
- Local Python tests: Success (3/3 passed in 0.532s - test_health, test_version, test_404)
- Docker image build: Success (cloud-api:v1 & cloud-api:v2 build complete)
- kind cluster create: Success (cloud-study cluster created in 17s with kindest/node:v1.37.0)
- Deployment rollout: Success (cloud-api deployment rolled out with 2/2 ready replicas)
- ClusterIP Service DNS response: Success (internal-check busybox -> http://cloud-api:8081/health returned {"status": "ok", "version": "v1"})
- Pod deletion recovery: Success (Pod cloud-api-7d4cd7d87d-g49qn deleted -> New Pod created and restored 2 ready replicas)
- v1 -> v2 rolling update: Success (RollingUpdate maxSurge: 1, maxUnavailable: 0 -> version-check returned {"service": "cloud-api", "version": "v2"})
- **Git commit hash**: `94e7c2c`
- **Git push 결과**: `origin/main` 전송 완료

## Error logs
| Command | Error | Cause | Fix | Retest |
|---|---|---|---|---|
| 없음 | - | - | - | 100% 로컬 kind 클러스터 상에서 전수 검증 통과 |
