#!/bin/sh
# WHY THIS FILE EXISTS:
# MUST be run before `terraform destroy`. Kubernetes creates AWS resources
# (Load Balancers via ingress-nginx, EBS volumes via PVCs) that Terraform
# does not know about. If these are left behind, `terraform destroy` will
# hang trying to delete the VPC while the LB/ENIs are still attached.
# This script removes all Kubernetes-managed AWS resources first.
#
# Usage: bash scripts/pre-destroy.sh
set -euo pipefail

echo "=== Uninstalling app Helm release ==="
helm uninstall project-clinq -n project-clinq 2>/dev/null && echo "Done" || echo "Not installed, skipping"

echo ""
echo "=== Uninstalling kube-prometheus-stack ==="
helm uninstall kube-prometheus-stack -n monitoring 2>/dev/null && echo "Done" || echo "Not installed, skipping"

echo ""
echo "=== Uninstalling ingress-nginx (removes the AWS Load Balancer) ==="
helm uninstall ingress-nginx -n ingress-nginx 2>/dev/null && echo "Done" || echo "Not installed, skipping"

echo ""
echo "=== Deleting all PVCs (releases EBS volumes) ==="
kubectl delete pvc --all -A 2>/dev/null || true

echo ""
echo "=== Waiting for LoadBalancer Services to be removed (up to 3 min) ==="
for i in $(seq 1 18); do
  LB_COUNT=$(kubectl get svc -A --field-selector spec.type=LoadBalancer \
    -o jsonpath='{.items}' 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
  if [ "$LB_COUNT" = "0" ]; then
    echo "✓ No LoadBalancer Services remaining"
    break
  fi
  echo "  Waiting for ${LB_COUNT} LoadBalancer(s) to be deleted... (${i}/18)"
  sleep 10
done

echo ""
echo "=== Pre-destroy complete. Now run: ==="
echo "  cd terraform && terraform destroy"
echo ""
echo "After destroy, verify in AWS Console:"
echo "  - EKS clusters: empty"
echo "  - EC2 > Load Balancers: none"
echo "  - EC2 > Volumes: none"
echo "  - VPC > Elastic IPs: none"
echo ""
echo "Then delete your AWS access keys and the GitHub AWS secrets."
