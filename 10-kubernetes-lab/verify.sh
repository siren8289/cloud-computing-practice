#!/usr/bin/env bash
set -euo pipefail
CTX=kind-cloud-study

kubectl --context "$CTX" rollout status deployment/cloud-api --timeout=120s
READY=$(kubectl --context "$CTX" get deployment cloud-api -o jsonpath='{.status.readyReplicas}')
[[ "$READY" == "2" ]] || {
  echo "Expected 2 ready replicas; got $READY"
  exit 1
}

kubectl --context "$CTX" run internal-check \
  --rm -i --restart=Never \
  --image=busybox:1.36 -- \
  wget -qO- http://cloud-api:8081/health

kubectl --context "$CTX" get endpointslices -l kubernetes.io/service-name=cloud-api
