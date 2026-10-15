#!/bin/sh
# WHY THIS FILE EXISTS:
# One-shot script to prepare a fresh EKS cluster for the app deployment.
# Run this immediately after `terraform apply` and `aws eks update-kubeconfig`.
# It installs:
#   - The gp3 StorageClass (needed for Postgres PVCs)
#   - ingress-nginx (creates the AWS Load Balancer)
#   - metrics-server (needed for HPA to work)
# Usage: bash scripts/bootstrap-cluster.sh
set -euo pipefail

NAMESPACE="project-clinq"

echo "=== Creating namespace and StorageClass ==="
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/storageclass-gp3.yaml

echo ""
echo "=== Installing ingress-nginx (creates AWS Load Balancer) ==="
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>/dev/null || true
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  -n ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer \
  --wait --timeout 5m

echo ""
echo "=== Installing metrics-server (required for HPA) ==="
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ 2>/dev/null || true
helm repo update
helm upgrade --install metrics-server metrics-server/metrics-server \
  -n kube-system \
  --set args[0]="--kubelet-insecure-tls" \
  --wait --timeout 3m

echo ""
echo "=== Waiting for ingress-nginx LoadBalancer hostname ==="
echo "(This can take 2-5 minutes while AWS provisions the ELB...)"
for i in $(seq 1 30); do
  HOSTNAME=$(kubectl get svc ingress-nginx-controller -n ingress-nginx \
    -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
  if [ -n "$HOSTNAME" ]; then
    echo ""
    echo "✓ Ingress ELB hostname: ${HOSTNAME}"
    echo "  Use this as your app URL: http://${HOSTNAME}"
    break
  fi
  printf "."
  sleep 10
done

echo ""
echo "=== Bootstrap complete! Next: deploy the app ==="
echo "  helm upgrade --install project-clinq ./helm/project-clinq \\"
echo "    -n project-clinq -f helm/project-clinq/values-eks.yaml \\"
echo "    --set backend.image.tag=<SHA> --set frontend.image.tag=<SHA> \\"
echo "    --set postgres.password=<YOUR_PASSWORD>"
