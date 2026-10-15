# Troubleshooting Lab

Practice diagnosing common Kubernetes issues in an isolated namespace.
**None of these manifests affect the `project-clinq` namespace.**

---

## Lab 1 — ImagePullBackOff

### Apply
```bash
kubectl apply -f troubleshooting/broken-image.yaml
```

### Symptom
```
kubectl get pods -n troubleshooting-lab
NAME             READY   STATUS             RESTARTS   AGE
broken-image-*   0/1     ImagePullBackOff   0          30s
```

### Investigate
```bash
# 1. Which pod, which error?
kubectl get pods -n troubleshooting-lab

# 2. Detailed event stream — "Failed to pull image" tells you the tag/repo
kubectl describe pod -n troubleshooting-lab -l app=broken-image

# 3. Recent cluster events sorted by time
kubectl get events -n troubleshooting-lab --sort-by=.lastTimestamp
```

### Root cause
The image tag `nginx:this-tag-does-not-exist-99999` does not exist in Docker Hub.
Kubernetes cannot pull the image so the pod stays in `ImagePullBackOff`.

### Fix
Edit the Deployment to use a real tag:
```bash
kubectl set image deployment/broken-image app=nginx:1.27-alpine -n troubleshooting-lab
kubectl rollout status deployment/broken-image -n troubleshooting-lab
```

---

## Lab 2 — Service with no endpoints

### Apply
```bash
kubectl apply -f troubleshooting/broken-service.yaml
```

### Symptom
The pod runs fine, but no traffic reaches it via the Service:
```bash
curl http://<service-ip>/   # hangs or connection refused
```

### Investigate
```bash
# 1. Is the pod running?
kubectl get pods -n troubleshooting-lab -l app=broken-service-app

# 2. Does the Service have any endpoints?
kubectl get endpoints broken-service -n troubleshooting-lab
# NAME             ENDPOINTS   AGE
# broken-service   <none>      1m   <-- no endpoints = selector mismatch

# 3. What labels does the pod actually have?
kubectl get pods -n troubleshooting-lab --show-labels

# 4. What selector does the Service use?
kubectl describe svc broken-service -n troubleshooting-lab
```

### Root cause
The Service selector `app: wrong-label` does not match the pod label
`app: broken-service-app`. Kubernetes uses label selectors to route traffic —
when no pod matches, the Service has zero endpoints and drops all requests.

### Fix
Patch the Service selector to match the pod:
```bash
kubectl patch svc broken-service -n troubleshooting-lab \
  -p '{"spec":{"selector":{"app":"broken-service-app"}}}'
kubectl get endpoints broken-service -n troubleshooting-lab
# Should now show a pod IP
```

---

## Cleanup
```bash
kubectl delete ns troubleshooting-lab
```
