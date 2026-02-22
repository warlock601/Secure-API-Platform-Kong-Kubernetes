# Secure API Platform with Kong on Kubernetes

This repository implements a secure internal API platform using Kong Gateway (OSS), a FastAPI microservice, and Kubernetes (Kind).

## Architecture Overview

The system consists of:
- **Kong Gateway (OSS)**: Serving as the entry point for all API traffic.
- **User Microservice**: A FastAPI application managing user records and JWT tokens.
- **SQLite Database**: Local, file-based storage for user credentials and hashes.
- **CrowdSec**: Self-managed DDoS protection monitoring Kong logs.

### API Request Flow
`Client -> Kong Gateway (Plugins Applied) -> User Microservice (FastAPI)`

- **Authentication**: JWT-based via Kong's JWT plugin.
- **Rate Limiting**: IP-based rate limiting (10 requests/min).
- **IP Protection**: CIDR-based IP restriction.
- **Custom Logic**: Custom Lua plugin for request header injection (`X-Custom-Auth-Gateway`).

---

## Prerequisites (WSL Ubuntu)

- WSL2 (Ubuntu)
- Docker Desktop with WSL Integration
- Kind (`curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind`)
- Kubectl
- Helm
- Terraform

---

## Deployment Steps (WSL Ubuntu)

### 1. Ensure Kind Cluster is Running
```bash
# Verify the cluster exists
kind get clusters | grep dev-cluster
```

### 2. Infrastructure (Terraform)
```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### 3. Build and Load Microservice
```bash
cd ../microservice
docker build -t user-service:latest .
kind load docker-image user-service:latest --name dev-cluster
```

### 4. Deploy Kong Gateway
```bash
# Add Kong Helm repo
helm repo add kong https://charts.konghq.com
helm repo update

# Deploy with custom values and extra manifests
kubectl apply -f ../k8s/kong-extras.yaml
helm install kong kong/kong -n kong -f ../helm/kong/values.yaml
```

### 5. Deploy User Microservice
```bash
cd ../helm/user-service
helm install user-service . -n user-service
```

### 6. Deploy DDoS Protection (CrowdSec)
```bash
helm repo add crowdsec https://crowdsecurity.github.io/helm-charts
helm repo update
helm install crowdsec crowdsec/crowdsec -n kong -f ../helm/crowdsec-values.yaml
```

---

## Testing Verification

### JWT Authentication
1. **Login to get token**:
   ```bash
   curl -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}'
   ```
2. **Access protected /users**:
   ```bash
   curl -X GET http://localhost:8000/users -H "Authorization: Bearer <TOKEN>"
   ```

### Authentication Bypass
- Access /health without token:
  ```bash
  curl -X GET http://localhost:8000/health
  ```

### Rate Limiting
- Run 11+ requests within a minute:
  ```bash
  for i in {1..12}; do curl -I http://localhost:8000/health; done
  ```
  Expected: One or more requests should return `429 Too Many Requests`.

### IP Whitelisting
- Modify `kong.yaml` to restrict to a specific IP and re-apply. Traffic from other IPs should be blocked (403 Forbidden).

### DDoS Protection
- Check CrowdSec alerts:
  ```bash
  kubectl exec -it <crowdsec-lapi-pod> -n kong -- cscli alerts list
  ```
