# Live Demo Script (M10)

**Goal:** show the full CI/CD loop — commit → pipeline → EKS deployment → browser.
**Total time:** ~8 minutes (plus pipeline run time ~4 minutes).
**Prerequisite:** EKS cluster running, `DEPLOY_ENABLED=true` set in GitHub Variables.

---

## Step 1 — Make a visible UI change (1 min)

Edit `frontend/src/App.jsx` — change the sidebar brand heading from "ClinQ" to
something slightly different (e.g. add the current date or a version suffix):

```jsx
<h1>ClinQ v2</h1>
```

Commit and push:
```bash
git add frontend/src/App.jsx
git commit -m "feat(frontend): update brand heading for live demo"
git push origin main
```

---

## Step 2 — Show the pipeline running (2 min)

1. Open GitHub → Actions → the latest run.
2. Walk through each job:
   - **test**: pytest, ruff, frontend build
   - **build-scan-push (backend)**: build → Trivy scan → push to GHCR
   - **build-scan-push (frontend)**: build → Trivy scan → push to GHCR
   - **deploy**: `helm upgrade` to EKS

Point out:
- The commit SHA as the image tag (never `latest`)
- Trivy scan step — explain that the image is scanned *before* it is pushed
- The `--atomic` flag on `helm upgrade` — rolls back automatically if pods fail

---

## Step 3 — Show rolling update on the cluster (2 min)

While the deploy job runs (or after it completes):

```bash
kubectl rollout status deployment/project-clinq-frontend -n project-clinq
kubectl get pods -n project-clinq -w
```

Point out:
- Old pods terminate only after new pods are Ready (rolling update strategy)
- No downtime — traffic continues to the old pods during the rollout

---

## Step 4 — Refresh the browser (1 min)

Open `http://<ELB-hostname>` and show:
- The sidebar now says "ClinQ v2" (or your change)
- The build badge in the footer shows the first 7 chars of the new commit SHA

---

## Step 5 — Fallback if the pipeline is slow

If the pipeline is still running during the live session, switch to a pre-recorded
screencast (`evidence/M10-demo.mp4`) showing the same steps, then show the
already-updated live cluster.

---

## Things to be ready to explain

- Why we scan before push (not after)
- What `--atomic` does in `helm upgrade`
- Why the build badge shows a 7-char SHA and not a version number
- How `DEPLOY_ENABLED=true` gates the deploy job
- What would happen if a test failed (pipeline stops, deploy never runs)
