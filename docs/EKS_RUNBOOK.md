# EKS Session Runbook

**Before you start:** all earlier evidence done, S7 rehearsal passed (optional
but recommended), GHCR packages set to Public, a screen recorder ready, ~3 hours free.
**Billing starts at Step 2.**

---

| # | Step | Commands | Capture |
|---|------|----------|---------|
| 1 | Identity check | `aws sts get-caller-identity` | — |
| 2 | Create infra (15-20 min) | `cd terraform && terraform apply` | `evidence/M7-tf-apply.png` ("Apply complete!") |
| 3 | Console proof | AWS Console, region **Mumbai (ap-south-1)** → VPC (2 public + 2 private subnets) and EKS → Clusters → node group | `evidence/M7-aws-vpc.png`, `evidence/M7-aws-eks.png` |
| 4 | Connect kubectl | `$(terraform output -raw configure_kubectl)` then `kubectl get nodes` | `evidence/M8-nodes.png` |
| 5 | Bootstrap | `bash scripts/bootstrap-cluster.sh` | — |
| 6 | Deploy app | `helm upgrade --install project-clinq ./helm/project-clinq -n project-clinq --create-namespace -f helm/project-clinq/values-eks.yaml --set backend.image.tag=<SHA> --set frontend.image.tag=<SHA> --set postgres.password=<PASSWORD>` | — |
| 7 | Verify M8 | `kubectl get pods -n project-clinq` · `kubectl get svc -n project-clinq` · `helm list -n project-clinq` · `kubectl get ingress -n project-clinq` | `evidence/M8-pods.png`, `evidence/M8-svc.png`, `evidence/M8-helm-list.png`, `evidence/M8-ingress.png` |
| 8 | Open the app | `kubectl get svc -n ingress-nginx` → copy ELB hostname → `http://<ELB-hostname>` (DNS 2-5 min) · `bash scripts/seed.sh http://<ELB-hostname>` | `evidence/M8-app-ingress.png` |
| 9 | Install monitoring | `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update` · `helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace -f monitoring/kube-prometheus-stack-values.yaml --set grafana.adminPassword=$GRAFANA_PASSWORD` · re-run app helm upgrade (to register ServiceMonitor) · `kubectl -n monitoring create configmap project-clinq-dashboard --from-file=monitoring/grafana-dashboard.json && kubectl -n monitoring label configmap project-clinq-dashboard grafana_dashboard=1` | — |
| 10 | Metrics proof | `kubectl -n project-clinq port-forward svc/project-clinq-backend 8000:8000` then `curl http://localhost:8000/metrics` | `evidence/M9-metrics-curl.png` |
| 11 | Prometheus | `kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090` → http://localhost:9090/targets | `evidence/M9-prom-targets.png` (app target **UP**) |
| 12 | Grafana | `kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3001:80` → http://localhost:3001 (user `admin`). Click the app UI first to generate traffic | `evidence/M9-grafana.png` (panel with data) |
| 13 | HPA demo | `kubectl get hpa -n project-clinq -w` in one terminal · `bash scripts/load-test.sh` in another | `evidence/M8-hpa.png` |
| 14 | Troubleshooting lab | `kubectl apply -f troubleshooting/broken-image.yaml`, diagnose + fix; same for `broken-service.yaml` | `evidence/TS-broken-image.png`, `evidence/TS-broken-service.png` |
| 15 | Live demo (M10) | GitHub Settings → Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DB_PASSWORD`; Variables: `DEPLOY_ENABLED=true`, `AWS_REGION=ap-south-1`, `EKS_CLUSTER_NAME=project-clinq`. Follow `docs/DEMO_SCRIPT.md` while recording | `evidence/M10-demo.mp4` |
| 16 | Tear down | `bash scripts/pre-destroy.sh` → wait ~3 min → `cd terraform && terraform destroy` | `evidence/M7-tf-destroy.png` ("Destroy complete!") |
| 17 | Verify zero cost | Console: EKS empty, VPC gone, EC2 → Load Balancers and Volumes empty, VPC → Elastic IPs empty. Delete AWS access keys and GitHub AWS secrets. | — |

---

## Known pitfalls

| Symptom | Likely cause → fix |
|---------|-------------------|
| Postgres pod `Pending`, PVC `Pending` | StorageClass missing or EBS CSI driver not working → `kubectl apply -f k8s/storageclass-gp3.yaml`; check `kubectl get pods -n kube-system \| grep ebs` |
| `ImagePullBackOff` on our images | GHCR package is private → Package settings → Change visibility → Public |
| Backend `CrashLoopBackOff` | DB not ready (start.sh retries 30×), wrong `DATABASE_URL`, wrong password on reused PVC → `kubectl logs -n project-clinq -l app.kubernetes.io/component=backend` |
| Frontend `host not found in upstream` | `BACKEND_URL` not set to the backend Service name → check the frontend Deployment env |
| Ingress 404 | `ingressClassName` mismatch, or host rule set when using raw ELB hostname → use `values-eks.yaml` with empty host |
| HPA shows `<unknown>` | metrics-server not installed → `bash scripts/bootstrap-cluster.sh` includes it |
| Prometheus target missing | ServiceMonitor label / `serviceMonitorSelectorNilUsesHelmValues` / port name mismatch |
| `kubectl` Unauthorized | Wrong AWS profile → `aws sts get-caller-identity` |
| `terraform destroy` hangs on VPC | Leftover ELB or EBS volumes → run `scripts/pre-destroy.sh`, wait, retry |
| `start.sh: not found` on Windows | CRLF line endings → `.gitattributes` already handles this; re-checkout the file |
| Trivy fails HIGH/CRITICAL | Update base image or dep; add `.trivyignore` with justification comment; never lower the gate |
