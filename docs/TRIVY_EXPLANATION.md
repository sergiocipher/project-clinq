# Trivy Scan Explanation

## What Trivy scanned

Trivy scanned the final Docker images for both the backend and frontend services.
It checked OS packages (Debian/Alpine base image libraries) and language-level
dependencies (Python packages from `requirements.txt`, Node modules from
`package-lock.json`) against a continuously-updated CVE database.

## What the result means

Both images passed with 0 HIGH or CRITICAL findings after fixes were applied.

The **backend image** (python:3.12-slim / Debian) initially failed with 3 HIGH
CVEs in `starlette==0.38.6` (CVE-2024-47874, CVE-2026-48818, CVE-2026-54283 —
DoS and SSRF vulnerabilities). These were fixed by upgrading to
`fastapi==0.143.2` and pinning `starlette==1.3.1`, which contains all patches.

The **frontend image** initially used `nginxinc/nginx-unprivileged:1.27-alpine`
(Alpine 3.21.3) which had 41 HIGH/CRITICAL CVEs across OS packages including
`openssl`, `musl`, `libxml2`, `libexpat`, `libpng`, `c-ares`, and `zlib`.
The root cause was a stale base image. Bumping to `1.30.1-alpine3.23` (Alpine 3.23)
and adding `apk upgrade --no-cache` cleared all 41 findings.

## Why scan before push?

The CI pipeline builds the image locally, scans it with Trivy, and only pushes
to GHCR if the scan passes. This means a vulnerable image never reaches the
registry. If we pushed first and scanned second, a vulnerable image would exist
in the registry even if we deleted it shortly after.

## What Trivy does NOT cover

- **SAST (static application security testing):** Trivy does not analyse your
  Python or JavaScript source code for logic bugs, injection flaws, or insecure
  coding patterns.
- **Secrets scanning:** Trivy does not detect AWS keys or passwords committed
  to Git. Use `git grep` or a dedicated tool like `gitleaks` for that.
- **Runtime threats:** Trivy scans the image at build time. It cannot detect
  threats that appear at runtime (e.g. a compromised dependency loaded
  dynamically, or an attacker who gains access after deployment).

## Gate policy

The pipeline is configured with `exit-code: "1"` and `severity: HIGH,CRITICAL`.
This means a HIGH or CRITICAL unfixed CVE fails the build. This gate must never
be weakened by setting `exit-code: 0` or removing the severity filter.

If a finding appears:
1. Update the base image or dependency to a patched version.
2. If no fix is available, add a `.trivyignore` entry with a written justification
   explaining why the CVE is acceptable in this context and when it will be revisited.
