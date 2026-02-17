# Secure-API-Platform-Kong-Kubernetes


## Secure API Platform with Kong on Kubernetes

This repository contains a complete implementation of a secure API platform using Kong Gateway (DB-less mode) and a Python microservice, designed to run on Kubernetes.

## Architecture Overview

The system consists of two main components running in Kubernetes:
1.  **Kong Gateway**: Acts as the single entry point (Ingress). It handles Authentication (JWT), Traffic Control (Rate Limiting, IP Whitelisting), and Routing.
2.  **User Microservice**: A Python Flask application using SQLite. It processes business logic and data persistence.

### API Request Flow

`Client -> Kong Gateway -> [Auth & Plugins] -> User Microservice`

1.  **Client** makes a request to Kong (e.g., `POST /login`).
2.  **Kong** matches the route.
3.  **Kong** executes configured plugins:
    *   **IP Restriction**: Checks if the client IP is allowed.
    *   **Rate Limiting**: Checks if the client has exceeded the limit (10 req/min).
    *   **JWT Auth**: Verifies the token (if the route is protected).
    *   **Custom Lua**: Injects headers or logs the request.
4.  If all checks pass, **Kong** proxies the request to the upstream `user-service`.
5.  **Microservice** handles the request and returns a response.
6.  **Kong** forwards the response back to the client.

## Authentication Strategy

*   **JWT Authentication**: Used for protected endpoints.
*   **Bypass**: Public endpoints are configured in `kong/kong.yml` to NOT use the JWT plugin.

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/health` | GET | NO | Health check |
| `/verify` | GET | NO | Verify token (Manual check) |
| `/login` | POST | NO (Rate Limited) | Get JWT |
| `/users` | GET | YES | List users |

## DDoS Protection & Security

We implement a multi-layered defense strategy:
1.  **Network Layer**: **IP Whitelisting** (Kong `ip-restriction` plugin) blocks all traffic not originating from trusted CIDRs (e.g. `10.0.0.0/8`, `127.0.0.1`).
2.  **Application Layer**: **Rate Limiting** (Kong `rate-limiting` plugin) limits clients to 10 requests per minute to prevent abuse.
3.  **Custom Logic**: A custom Lua plugin monitors traffic and provides custom logging/header injection to track processing time and origin.

## Deployment Instructions

### Prerequisites
*   Kubernetes Cluster (or Minikube/Kind)
*   Helm 3
*   Kubectl

### Steps

1.  **Build Microservice**:
    ```bash
    cd microservice
    docker build -t user-service:latest .
    # If using Minikube/Kind, load image: kind load docker-image user-service:latest
    ```

2.  **Deploy User Service**:
    ```bash
    helm install user-service ./helm/user-service
    ```

3.  **Deploy Kong (DB-less)**:
    We use the official Kong chart with our custom config.
    First, create the ConfigMap for the declarative config and plugins:
    ```bash
    kubectl create configmap kong-dbless-config --from-file=kong.yml=./kong/kong.yml
    kubectl create configmap kong-custom-plugins --from-file=./kong/plugins
    ```

    Then install Kong:
    ```bash
    helm repo add kong https://charts.konghq.com
    helm repo update
    helm install kong kong/kong -f ./helm/kong/values.yaml
    ```

## Verification & Testing

1.  **Health Check (Public)**:
    ```bash
    curl -v http://<KONG_IP>/health
    # Expected: 200 OK, {"status": "healthy"}
    ```

2.  **Login (Get Token)**:
    ```bash
    curl -X POST http://<KONG_IP>/login -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}'
    # Expected: 200 OK, Returns {"token": "..."}
    ```

3.  **Access Protected Resource (With Token)**:
    ```bash
    TOKEN="<paste_token_here>"
    curl -H "Authorization: Bearer $TOKEN" http://<KONG_IP>/users
    # Expected: 200 OK, List of users
    ```

4.  **Access Protected Resource (No Token)**:
    ```bash
    curl -v http://<KONG_IP>/users
    # Expected: 401 Unauthorized
    ```

5.  **Test Rate Limiting**:
    Run the login command 11 times in rapid succession.
    # Expected: On the 11th try, 429 Too Many Requests.

6.  **Test IP Whitelisting**:
    Modify `kong/kong.yml` to exclude your IP, apply changes (update ConfigMap & restart Kong), and request again.
    # Expected: 403 Forbidden.
