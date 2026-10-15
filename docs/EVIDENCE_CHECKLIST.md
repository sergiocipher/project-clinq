# Evidence Checklist

All screenshots go in the `evidence/` directory. Filenames must match exactly.

| Module | File(s) | What must be visible | Also submit |
|--------|---------|----------------------|-------------|
| M1 (10 pts) | `M1-app-ui.png` or `M1-demo.mp4` | App loaded with seeded data, all CRUD actions | repo files |
| M1 | `M1-swagger.png` | `/docs` page with all endpoints listed | |
| M1 | `M1-db-table.png` | `psql \dt` output + `SELECT COUNT(*)` showing rows | |
| M2 (10 pts) | `M2-pytest.png` | Full `pytest -v` output, every test PASSED, summary line | |
| M3 (5 pts) | `M3-commits.png` | GitHub Commits page or `git log` showing 10+ meaningful commits | repo URL |
| M4 (10 pts) | `M4-compose-up.png` | `docker compose ps` — all three services Up | |
| M4 | `M4-browser-3000.png` | App at http://localhost:3000 with data | |
| M4 | `M4-nonroot.png` | `docker compose exec backend id` → uid=10001; `exec frontend id` → uid=101 | |
| M5 (15 pts) | `M5-actions-green.png` | Whole Actions run green (test + both build-scan-push legs) | Actions run URL |
| M5 | `M5-ghcr-packages.png` | GitHub Packages page, tags = commit SHA (not latest) | |
| M6 (5 pts) | `M6-trivy-backend.png` | Expanded "Trivy scan" step — backend | `docs/TRIVY_EXPLANATION.md` |
| M6 | `M6-trivy-frontend.png` | Expanded "Trivy scan" step — frontend | |
| M7 (15 pts) | `M7-tf-init.png` | "Terraform has been successfully initialized" | |
| M7 | `M7-tf-plan.png` | Bottom of plan: "Plan: N to add, 0 to change, 0 to destroy" | |
| M7 | `M7-tf-apply.png` | "Apply complete!" line | |
| M7 | `M7-aws-vpc.png` | AWS Console VPC — 2 public + 2 private subnets | |
| M7 | `M7-aws-eks.png` | AWS Console EKS → Clusters → node group | |
| M7 | `M7-tf-destroy.png` | "Destroy complete!" | |
| M8 (15 pts) | `M8-nodes.png` | `kubectl get nodes` — all nodes Ready | |
| M8 | `M8-pods.png` | `kubectl get pods -n project-clinq` — all Running, 2 replicas each | |
| M8 | `M8-svc.png` | `kubectl get svc -n project-clinq` | |
| M8 | `M8-helm-list.png` | `helm list -n project-clinq` | |
| M8 | `M8-ingress.png` | `kubectl get ingress -n project-clinq` | |
| M8 | `M8-app-ingress.png` | App in browser at ELB URL (URL bar visible) | |
| M8 | `M8-hpa.png` | `kubectl get hpa -n project-clinq` — replicas increasing during load test | |
| M9 (10 pts) | `M9-metrics-curl.png` | `curl http://localhost:8000/metrics` output | `monitoring/` values files |
| M9 | `M9-prom-targets.png` | Prometheus /targets — app target **UP** | |
| M9 | `M9-grafana.png` | Grafana dashboard with at least one populated panel | |
| M10 (5 pts) | `M10-demo.mp4` or live demo | Full CI/CD loop: commit → pipeline → deploy → browser refresh | `README.md` |
