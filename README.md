# project-clinq

Clinic appointment booking application — DevOps capstone project.

[![CI/CD](https://github.com/sergiocipher/project-clinq/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/sergiocipher/project-clinq/actions/workflows/ci-cd.yml)

---

## What the app does

ClinQ lets clinic staff book, track, and manage patient appointments.
Staff can create appointments with a patient name, doctor, scheduled date/time,
priority (low / normal / urgent), and notes. Each appointment moves through
statuses: `scheduled → completed / cancelled`. A dashboard shows live KPI
counts, a filterable/searchable table, and a recent-activity feed.

---
| Deliverable | Location |
|---|---|
| Slide deck (PDF) | [demo/](demo/ClinQ_DevOps_Project_Report.pdf) |
| Screenshots | [evidence/](evidence/) |
---

## Architecture

```
Browser
  │
  ▼
┌─────────────────────────────────────────────────────┐
│  AWS EKS (ap-south-1)                               │
│                                                      │
│  ┌──────────────┐      ┌──────────────┐             │
│  │  Ingress     │      │  Ingress     │             │
│  │  /           │      │  /api        │             │
│  └──────┬───────┘      └──────┬───────┘             │
│         │                     │                      │
│  ┌──────▼───────┐      ┌──────▼───────┐             │
│  │  Frontend    │      │  Backend     │             │
│  │  Nginx/React │      │  FastAPI     │             │
│  │  (×2 pods)   │      │  (×2 pods,   │             │
│  └──────────────┘      │   HPA 2-4)   │             │
│                         └──────┬───────┘             │
│                                │                      │
│                         ┌──────▼───────┐             │
│                         │  Postgres    │             │
│                         │  StatefulSet │             │
│                         │  (gp3 EBS)   │             │
│                         └──────────────┘             │
│                                                      │
│  monitoring/: Prometheus + Grafana (port-forward)    │
└─────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, psycopg v3 |
| Frontend | React 18, Vite, plain CSS |
| Database | PostgreSQL 16 |
| Container runtime | Docker, docker-compose |
| CI/CD | GitHub Actions, GHCR (image registry) |
| Security scanning | Trivy (HIGH/CRITICAL gate before push) |
| Infrastructure | Terraform (AWS VPC + EKS via community modules) |
| Kubernetes packaging | Helm 3 |
| Observability | Prometheus (kube-prometheus-stack), Grafana |

---

## Run locally with Docker Compose

```bash
# 1. Clone and copy env file
git clone https://github.com/sergiocipher/project-clinq.git
cd project-clinq
cp .env.example .env           # edit passwords if you want; defaults are fine locally

# 2. Start the stack
docker compose up --build

# 3. Seed sample data
bash scripts/seed.sh http://localhost:8000

# 4. Open the app
#   Frontend:  http://localhost:3000
#   API docs:  http://localhost:8000/docs
#   Metrics:   http://localhost:8000/metrics
```

Stop with `docker compose down` (add `-v` to also wipe the database).

---

## Run tests

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -v
ruff check . && ruff format --check .
```

---

## API

Base path: `/api/appointments`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/appointments` | List appointments (params: `status`, `q`, `limit`, `offset`) |
| GET | `/api/appointments/stats` | Counts by status + upcoming count |
| GET | `/api/appointments/{id}` | Get single appointment |
| POST | `/api/appointments` | Create appointment (returns 201) |
| PUT | `/api/appointments/{id}` | Update appointment |
| DELETE | `/api/appointments/{id}` | Delete appointment (returns 204) |
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (checks DB) |
| GET | `/metrics` | Prometheus metrics |

---

## CI/CD pipeline

Every push to `main`:

1. **test** — `pytest`, `ruff`, `npm run build`
2. **build-scan-push** (matrix: backend + frontend, in parallel):
   - Build image locally
   - Scan with Trivy (fails on HIGH/CRITICAL unfixed CVEs)
   - Push to GHCR with SHA tag (never `latest`)
3. **deploy** (disabled until `DEPLOY_ENABLED=true` is set in GitHub Variables):
   - `helm upgrade --install` to EKS with `--atomic` (auto-rollback on failure)

---

## Terraform + Helm deploy

See `docs/EKS_RUNBOOK.md` for the full step-by-step EKS session.

**Quick summary:**

```bash
# 1. Init and apply (creates VPC + EKS, ~15 min, ~$0.46/hour)
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply

# 2. Bootstrap cluster
$(terraform output -raw configure_kubectl)
bash scripts/bootstrap-cluster.sh

# 3. Deploy app
helm upgrade --install project-clinq ./helm/project-clinq \
  -n project-clinq --create-namespace \
  -f helm/project-clinq/values-eks.yaml \
  --set backend.image.tag=<GIT_SHA> \
  --set frontend.image.tag=<GIT_SHA> \
  --set postgres.password=<YOUR_PASSWORD>

# 4. Tear down when done (run BEFORE terraform destroy)
bash scripts/pre-destroy.sh
cd terraform && terraform destroy
```

---

## Monitoring

```bash
# Prometheus targets
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090
# Open: http://localhost:9090/targets

# Grafana dashboard
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3001:80
# Open: http://localhost:3001  (user: admin)
```

---

## Teardown

**Always run `scripts/pre-destroy.sh` before `terraform destroy`.**
Kubernetes creates AWS Load Balancers and EBS volumes that Terraform doesn't
track. Leaving them behind blocks VPC deletion and continues billing.

---

## Screenshots

See `evidence/README.md` for the expected screenshot index.
