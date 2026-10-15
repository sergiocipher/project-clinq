#!/bin/sh
# WHY THIS FILE EXISTS:
# Generates sustained HTTP load against the backend to push CPU above the HPA
# target (50%) so you can watch the HPA scale up replicas in real time.
# Runs N temporary in-cluster busybox pods that loop wget requests.
# Usage: bash scripts/load-test.sh [BACKEND_URL] [NUM_PODS]
set -euo pipefail

BACKEND_URL="${1:-http://project-clinq-backend.project-clinq.svc.cluster.local:8000}"
NUM_PODS="${2:-3}"
NAMESPACE="project-clinq"

echo "Starting ${NUM_PODS} load-test pods against ${BACKEND_URL}..."
echo "Watch HPA in another terminal: kubectl get hpa -n ${NAMESPACE} -w"
echo ""

i=0
while [ "$i" -lt "$NUM_PODS" ]; do
  i=$((i + 1))
  kubectl run "load-test-${i}" -n "${NAMESPACE}" \
    --image=busybox:1.36 \
    --restart=Never \
    -- sh -c "while true; do wget -q -O- ${BACKEND_URL}/api/appointments > /dev/null 2>&1; done" \
    2>/dev/null || echo "  Pod load-test-${i} already exists, skipping"
  echo "  Started load-test-${i}"
done

echo ""
echo "Load test running. To stop and clean up:"
echo "  kubectl delete pod -n ${NAMESPACE} -l run=load-test || \\"
for j in $(seq 1 "$NUM_PODS"); do printf "  kubectl delete pod load-test-%s -n %s\n" "$j" "${NAMESPACE}"; done
