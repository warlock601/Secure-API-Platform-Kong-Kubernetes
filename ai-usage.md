# AI Usage Documentation

This document describes the AI tools and interactions used to design, code, and debug this project.

## AI Tools Used
- **Antigravity (Gemini-based AI Assistant)**: Primary assistant for generating implementation plans, microservice code, Kubernetes manifests, Helm charts, and documentation.
- **VS Code / IDE Integration**: For orchestration and file management.

## Prompts Interaction and History

### 1. Initialization and Planning
- **Prompt**: "Secure API Platform using Kong on Kubernetes [Detailed requirements...]"
- **Action**: The AI analyzed the requirements and proposed an implementation plan covering FastAPI, Kong, SQLite, Helm, Terraform, and DDoS protection (CrowdSec).

### 2. Microservice Implementation
- **Prompt**: "The user has approved this document." (After review of implementation plan)
- **Action**: The AI implemented the FastAPI user service (`main.py`), requirements, and Dockerfile. 

### 3. Infrastructure and Gateway Configuration
- **Prompt**: Automated execution of tasks based on approved plan.
- **Action**: The AI generated Terraform files for namespaces, Helm chart templates for the user service, and declarative Kong configuration (`kong.yaml`).

### 4. DDoS and Security Setup
- **Prompt**: Automated execution of tasks.
- **Action**: The AI configured CrowdSec Helm values and custom Kong Lua logic for header injection.

### 5. Environment Refinement
- **Prompt**: "So all this will be ruynning ina Kind cluster in WSL ubuntu , Please proceed with considering that, provide the implementation plan and everything"
- **Action**: The AI updated the implementation plan and README to align with the WSL/Kind environment, providing specific deployment commands and architecture context.

---

*Note: This file records the interaction history between the user and the AI assistant as it happened during the development process.*
