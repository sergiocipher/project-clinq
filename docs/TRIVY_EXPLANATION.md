# Trivy Scan Explanation

## What Trivy scanned

Trivy scanned the final Docker images for both the backend and frontend services.
It checked OS packages (Debian/Alpine base image libraries) and language-level
dependencies (Python packages from `requirements.txt`, Node modules from
`package-lock.json`) against a continuously-updated CVE database.

## What the result means

<!-- Student: fill in after your first successful Actions run.
     Example: "Both images passed with no HIGH or CRITICAL findings.
     The base images python:3.12-slim and nginxinc/nginx-unprivileged:1.27-alpine
     had no known unfixed vulnerabilities at the time of this scan." -->

_TODO: paste your result here after the first green pipeline run._

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
