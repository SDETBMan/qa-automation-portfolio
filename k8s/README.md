# k8s — Kubernetes Infrastructure

Kubernetes manifests for running a containerized Selenium Grid with Healenium self-healing locators. Mirrors the Docker Compose setup in `selenium-java/` and `cucumber/` but targets a real cluster, demonstrating the Docker → K8s translation used in production QA environments.

---

## Stack

| Component | Image | Purpose |
|---|---|---|
| Selenium Hub | `selenium/hub:4.16.1` | Grid router — accepts WebDriver connections |
| Chrome Node | `selenium/node-chrome:4.16.1` | Browser worker |
| Firefox Node | `selenium/node-firefox:4.16.1` | Browser worker |
| Edge Node | `selenium/node-edge:4.16.1` | Browser worker |
| Healenium Backend | `healenium/hlm-backend:3.3.0` | AI self-healing service |
| Healenium Imitator | `healenium/hlm-selector-imitator:1.0.2` | DOM comparison service |
| PostgreSQL | `postgres:12-alpine` | Healenium locator history store |

---

## Directory Structure

```
k8s/
├── namespace.yaml                   selenium-grid namespace
├── configmap.yaml                   Healenium/Postgres config (demo values)
├── secret.yaml.example              Secret template — copy → secret.yaml, do not commit
├── selenium-grid/
│   ├── hub-deployment.yaml
│   ├── hub-service.yaml
│   ├── chrome-deployment.yaml
│   ├── firefox-deployment.yaml
│   └── edge-deployment.yaml
└── healenium/
    ├── hlm-backend-deployment.yaml
    ├── hlm-backend-service.yaml
    ├── hlm-imitator-deployment.yaml
    ├── hlm-imitator-service.yaml
    ├── postgres-deployment.yaml
    └── postgres-service.yaml
```

---

## Prerequisites

- **kubectl** configured against a running cluster, **or**
- [Kind](https://kind.sigs.k8s.io/) for local clusters (`choco install kind` / `brew install kind`)

---

## Deploy

```bash
# 1. Create a local Kind cluster (skip if you already have a cluster)
kind create cluster --name selenium-grid

# 2. Apply namespace and config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# 3. Deploy Selenium Grid
kubectl apply -f k8s/selenium-grid/

# 4. Deploy Healenium (optional — only needed for self-healing tests)
kubectl apply -f k8s/healenium/

# 5. Wait for readiness
kubectl wait deployment/selenium-hub \
  --for=condition=Available --timeout=120s -n selenium-grid

# 6. Port-forward and verify
kubectl port-forward svc/selenium-hub 4444:4444 -n selenium-grid &
curl http://localhost:4444/wd/hub/status
```

Or use the Makefile shortcuts:

```bash
make k8s-apply    # apply all manifests
make k8s-status   # show pod status
make k8s-delete   # tear everything down
```

---

## Run Tests Against the Cluster

Point either framework at the grid using Maven system properties:

```bash
# selenium-java
cd selenium-java
mvn clean test -Dtarget=grid -Dgrid_url=http://localhost:4444/wd/hub -Dheadless=true -Dgroups=smoke

# cucumber
cd cucumber
mvn clean test -Dtarget=grid -Dgrid_url=http://localhost:4444/wd/hub -Dheadless=true -Dgroups=smoke
```

---

## Tear Down

```bash
kubectl delete namespace selenium-grid
# or
make k8s-delete
```

---

## CI

The `k8s` GitHub Actions workflow (`.github/workflows/k8s.yml`) is triggered manually via **workflow_dispatch**. It:

1. Creates a Kind cluster on a GitHub-hosted Ubuntu runner
2. Applies the namespace, Hub, and Chrome node manifests
3. Uses `kubectl wait --for=condition=Available` with a 180 s timeout
4. Port-forwards the Hub and health-checks `/wd/hub/status` with `curl --retry`
5. Runs smoke tests from `selenium-java` or `cucumber` against the in-cluster grid
6. Uploads Surefire reports as artifacts (7-day retention)

---

## Credentials

`configmap.yaml` holds non-sensitive demo credentials. For production clusters, migrate these values to a Kubernetes Secret — see `secret.yaml.example` for a drop-in template.
