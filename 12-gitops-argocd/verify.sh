#!/usr/bin/env bash
set -euo pipefail
CTX="kind-cloud-study"
NS="gitops-lab"

# Argo CD Application 확인
kubectl --context "$CTX" \
  -n argocd get application cloud-gitops-lab

# Deployment 배포 완료 대기
kubectl --context "$CTX" \
  -n "$NS" rollout status deploy/web \
  --timeout=180s

# Ready Pod 2개 검증
READY=$(kubectl --context "$CTX" \
  -n "$NS" get deploy web \
  -o jsonpath='{.status.readyReplicas}')
[[ "$READY" == "2" ]] || {
  echo "Expected 2 ready pods, got ${READY:-0}"
  exit 1
}

# 클러스터 내부 Service 접근
kubectl --context "$CTX" \
  -n "$NS" run web-check \
  --rm -i --restart=Never \
  --image=busybox:1.36 -- \
  wget -qO- http://web/

echo "Deployment replica and HTTP check: PASS"
