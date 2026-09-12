---
name: prod-gcp
description: Operations, diagnostics, and management runbook for GCP production infrastructure covering GKE (Kubernetes), Airflow / Cloud Composer DAGs, Cloud SQL (PostgreSQL), and Cloud Logging / Monitoring. Use when diagnosing cluster issues, checking pods/deployments, investigating Airflow DAG failures, querying Cloud SQL, or running Cloud Logging queries.
---

# GCP Production Infrastructure Runbook

Operational guide for inspecting, operating, and troubleshooting Ostorlab's Google Cloud Platform (GCP) production infrastructure.

---

## 🏛 Core Infrastructure Topology

| Component | Service | Primary Details |
| :--- | :--- | :--- |
| **GCP Project** | Cloud Resource Manager | `api-project-609180564266` |
| **Primary Region / Zone** | Compute Engine / GKE | `europe-west1-b` (Region: `europe-west1`) |
| **Kubernetes Cluster** | Google Kubernetes Engine (GKE) | `production-cluster-2` |
| **Orchestration** | Apache Airflow / Cloud Composer | Orchestrates scanning pipelines, cron jobs, and PR review agents |
| **Database** | Cloud SQL (PostgreSQL) | Managed PostgreSQL with SSL client authentication |
| **Observability** | Cloud Logging & Monitoring | Google Cloud Logging + internal Prometheus / Grafana stack |
| **LLM Gateway** | LiteLLM Proxy on GKE | High-availability LiteLLM routing on Kubernetes with Redis & Postgres |

---

## 🔑 Authentication & Cluster Access

> [!IMPORTANT]
> **Always Use `gcloud` for GCP Investigation**: When investigating GCP production infrastructure, pods, Cloud Logging, Airflow DAGs, or Cloud SQL, always use `gcloud` and `kubectl`.
> **If Authentication Fails**: If any `gcloud` or `kubectl` command fails with authentication errors (e.g. `400 invalid_grant`, `invalid_rapt`, expired auth tokens, or non-interactive password prompts), **immediately ask the user to log in** via `gcloud auth login` in their terminal before making assumptions or proceeding.

### 1. Configure GCP Project & Credentials
```bash
# Set active project
gcloud config set project api-project-609180564266

# Authenticate GKE cluster access
gcloud container clusters get-credentials production-cluster-2 \
  --zone europe-west1-b \
  --project api-project-609180564266
```

### 2. Verify Kubernetes Context
```bash
kubectl config current-context
kubectl cluster-info
```

---

## ☸️ GKE / Kubernetes Operations

### Key Production Namespaces & Services

| Namespace | Services & Roles |
| :--- | :--- |
| `default` | General production workloads, dynamic worker pods (PR reviewer, scan tasks) |
| `ogle-scanning-engine` | Core vulnerability scanning engine and persistence workers |
| `ogle-reporting-engine` | Vulnerability management, GraphQL backend, Airflow scan connectors |
| `impact` | Impact analysis service |
| `internal-docs` | Internal documentation portal & API knowledge base |
| `litellm` | LiteLLM routing proxy, litellm-redis, and litellm-postgres |
| `monitoring` | Prometheus server, Prometheus Pushgateway, Grafana dashboards |
| `timescaledb` / `memorystore` | Time-series databases and Redis caches |

### Common Kubernetes Commands

#### 1. Checking Pod Health & Status
```bash
# List all pods across all namespaces
kubectl get pods -A --sort-by='.metadata.creationTimestamp'

# Check pods in a specific namespace
kubectl get pods -n <namespace> -o wide

# Find failing, pending, or crashing pods
kubectl get pods -A --field-selector status.phase!=Running
```

#### 2. Investigating Logs & Crashes
```bash
# Stream live logs from a pod
kubectl logs -f <pod-name> -n <namespace>

# View logs from previous crashed instance
kubectl logs <pod-name> -n <namespace> --previous

# Describe pod events (image pull errors, OOMKilled, volume mount issues)
kubectl describe pod <pod-name> -n <namespace>
```

#### 3. Rolling Restarts & Deployments
```bash
# Restart a deployment
kubectl rollout restart deployment/<deployment-name> -n <namespace>

# Check rollout status
kubectl rollout status deployment/<deployment-name> -n <namespace>

# Roll back a failed deployment
kubectl rollout undo deployment/<deployment-name> -n <namespace>
```

#### 4. Managing Ingress & Google-Managed Certificates
```bash
# Check Ingress health
kubectl get ingress -A

# Check Google ManagedCertificate provisioning status
kubectl get managedcertificates -A
kubectl describe managedcertificate <cert-name> -n <namespace>
```

---

## 🌪 Airflow Orchestration & DAG Operations

Airflow coordinates long-running and scheduled workloads, including:
- Vulnerability scanning pipelines (`ogle_scanning_engine` agent groups)
- Automated PR Review Agent DAGs (`pr-reviewer-discovery`, `pr-reviewer-single`)
- Schedulestore & synchronization cron jobs

### Worker Execution Model (`GKEPodOperator`)
Airflow launches containerized tasks dynamically onto GKE (`production-cluster-2`) using `GKEPodOperator`:
- Tasks run as isolated, ephemeral pods in the `default` namespace.
- Pods pull images using Kubernetes secret `dockerhub-credential`.
- On completion or failure, Airflow captures pod logs and cleans up the pod.

### Investigating Airflow Tasks
1. **Airflow Web UI**: Inspect DAG run graph, task logs, and execution history.
2. **Finding Active Worker Pods on GKE**:
   ```bash
   # List running Airflow-dispatched pods
   kubectl get pods -n default -l airflow-worker=true
   ```
3. **Checking Worker Pod Logs**:
   ```bash
   kubectl logs <airflow-worker-pod-name> -n default
   ```

---

## 🗄 Cloud SQL (Managed PostgreSQL) Operations

### Architecture & Security
- Cloud SQL instances are strictly protected with SSL client certificate authentication.
- Secrets stored in Kubernetes:
  - `*-db-ssl-cert-secrets` (Server CA certificate)
  - `*-db-ssl-client-cert-secrets` (Client public certificate)
  - `*-db-ssl-client-key-secrets` (Client private key)

### Operational Procedures

#### 1. Listing Cloud SQL Instances
```bash
gcloud sql instances list --project=api-project-609180564266
```

#### 2. Checking Instance Health & Configuration
```bash
gcloud sql instances describe <instance-name> --project=api-project-609180564266
```

#### 3. Connecting via Cloud SQL Auth Proxy (Local Debugging)
```bash
# Start Cloud SQL Auth Proxy locally
cloud-sql-proxy api-project-609180564266:europe-west1:<instance-name> --port 5432
```

#### 4. Running Migrations on Kubernetes Pods
```bash
kubectl exec -it deployment/<app-deployment> -n <namespace> -- python manage.py migrate
```

---

## 📊 Cloud Logging & Observability

### 1. Querying Google Cloud Logging via `gcloud`
```bash
# Query recent error logs from GKE containers
gcloud logging read 'resource.type="k8s_container" AND severity>=ERROR' \
  --project=api-project-609180564266 \
  --limit=25 \
  --format="json(timestamp, resource.labels.pod_name, textPayload, jsonPayload.message)"

# Query logs for a specific pod name prefix
gcloud logging read 'resource.type="k8s_container" AND resource.labels.pod_name:"pr-reviewer"' \
  --project=api-project-609180564266 \
  --limit=50
```

### 2. Internal Monitoring Stack (Prometheus & Grafana)
- Prometheus scrapes cluster metrics and pushgateway endpoints in namespace `monitoring`.
- Grafana dashboards are deployed under namespace `monitoring` via `grafana-deployment.yaml`.

---

## 🚨 Incident Response & Troubleshooting Runbook

### Issue: Pod in `CrashLoopBackOff` or `OOMKilled`
1. Check exit code and termination reason:
   ```bash
   kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.status.containerStatuses[0].lastState.terminated}'
   ```
2. If `reason: OOMKilled`: Increase memory requests/limits in the deployment manifest in `ogle_infra/`.
3. If `reason: Error`: Check `kubectl logs <pod-name> -n <namespace> --previous` for unhandled Python exceptions or missing environment variables.

### Issue: Ingress Returning 502 / SSL Certificate Errors
1. Verify Google Managed Certificate status:
   ```bash
   kubectl describe managedcertificate <cert-name> -n <namespace>
   ```
   *Expected status: `Active`. If `Provisioning`, check DNS records pointing to the Ingress IP.*
2. Check backend service health in Ingress:
   ```bash
   kubectl describe ingress <ingress-name> -n <namespace>
   ```
3. Check application readiness probes in deployment.
