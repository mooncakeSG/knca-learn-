# Kubernetes Concepts in KCNA Learning Platform

This document explains the Kubernetes concepts and resources used in the KCNA Learning Platform project.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   PostgreSQL    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (StatefulSet) │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Ingress       │
                    │   (NGINX)       │
                    │   Port: 80/443  │
                    └─────────────────┘
```

## 📚 Kubernetes Resources Used

### 1. Namespace
**File**: `k8s/namespace.yaml`
- **Purpose**: Logical isolation of resources
- **Concept**: Namespaces provide a mechanism for isolating groups of resources within a single cluster
- **Usage**: All our application resources are deployed in the `kcna-learn` namespace

### 2. ConfigMap
**File**: `k8s/configmap.yaml`
- **Purpose**: Store non-sensitive configuration data
- **Concept**: ConfigMaps allow you to decouple configuration artifacts from image content
- **Usage**: Stores database URLs, Redis settings, and application configuration

### 3. Secret
**File**: `k8s/secret.yaml`
- **Purpose**: Store sensitive data like passwords and API keys
- **Concept**: Secrets are similar to ConfigMaps but are specifically designed to hold sensitive data
- **Usage**: Stores database credentials (base64 encoded)

### 4. PersistentVolumeClaim (PVC)
**File**: `k8s/postgres-pvc.yaml`
- **Purpose**: Request storage resources
- **Concept**: PVCs are requests for storage by users
- **Usage**: Provides persistent storage for PostgreSQL data

### 5. StatefulSet
**File**: `k8s/postgres-statefulset.yaml`
- **Purpose**: Manage stateful applications
- **Concept**: StatefulSets provide guarantees about the ordering and uniqueness of Pods
- **Usage**: Runs PostgreSQL with stable network identities and persistent storage

### 6. Deployment
**Files**: `k8s/backend-deployment.yaml`, `k8s/frontend-deployment.yaml`, `k8s/redis-deployment.yaml`
- **Purpose**: Manage stateless applications
- **Concept**: Deployments provide declarative updates for Pods and ReplicaSets
- **Usage**: Runs frontend, backend, and Redis with rolling updates

### 7. Service
**File**: `k8s/services.yaml`
- **Purpose**: Expose applications running on Pods
- **Concept**: Services define a logical set of Pods and a policy by which to access them
- **Usage**: Enables internal communication between components

### 8. Ingress
**File**: `k8s/ingress.yaml`
- **Purpose**: Manage external access to services
- **Concept**: Ingress manages external access to the services in a cluster
- **Usage**: Routes external traffic to frontend and backend services

### 9. HorizontalPodAutoscaler (HPA)
**File**: `k8s/hpa.yaml`
- **Purpose**: Automatically scale Pods based on metrics
- **Concept**: HPA automatically scales the number of Pods based on observed CPU/memory utilization
- **Usage**: Scales backend based on CPU and memory usage

## 🔧 Key Kubernetes Concepts Demonstrated

### 1. Pod Lifecycle
- **Init Containers**: Not used in this project but could be added for database migrations
- **Liveness Probes**: Check if the application is running
- **Readiness Probes**: Check if the application is ready to serve traffic

### 2. Resource Management
- **Resource Requests**: Minimum resources needed
- **Resource Limits**: Maximum resources allowed
- **Quality of Service**: Determines Pod scheduling priority

### 3. Networking
- **ClusterIP Services**: Internal communication
- **Ingress**: External access with path-based routing
- **Network Policies**: Could be added for security

### 4. Storage
- **PersistentVolumes**: Storage provisioned by administrators
- **PersistentVolumeClaims**: Storage requests by users
- **Storage Classes**: Dynamic provisioning

### 5. Security
- **Secrets**: Sensitive data management
- **Service Accounts**: Could be added for RBAC
- **Network Policies**: Could be added for network security

## 🚀 Deployment Process

1. **Namespace Creation**: Isolates our resources
2. **Secrets & ConfigMaps**: Provides configuration
3. **Storage**: PVC for database persistence
4. **Database**: StatefulSet for PostgreSQL
5. **Cache**: Deployment for Redis
6. **Applications**: Deployments for frontend/backend
7. **Services**: Enables internal communication
8. **Ingress**: Enables external access
9. **HPA**: Enables auto-scaling

## 📊 Monitoring & Observability

### Health Checks
- **Liveness Probes**: Restart Pods if unhealthy
- **Readiness Probes**: Remove from service if not ready
- **Startup Probes**: Delay liveness probe until startup

### Resource Monitoring
- **CPU/Memory Usage**: Tracked by HPA
- **Pod Status**: Monitored via kubectl
- **Service Endpoints**: Verified via kubectl

## 🔍 Troubleshooting Commands

```bash
# Check Pod status
kubectl get pods -n kcna-learn

# Check Pod logs
kubectl logs -f deployment/backend -n kcna-learn

# Check service endpoints
kubectl get endpoints -n kcna-learn

# Check ingress status
kubectl get ingress -n kcna-learn

# Check HPA status
kubectl get hpa -n kcna-learn

# Describe resources for debugging
kubectl describe pod <pod-name> -n kcna-learn
```

## 🎯 Learning Objectives

This project demonstrates:

1. **Multi-tier Architecture**: Frontend, Backend, Database
2. **Stateful Applications**: PostgreSQL with persistent storage
3. **Stateless Applications**: Frontend and Backend with scaling
4. **Service Discovery**: Internal communication via Services
5. **External Access**: Ingress with path-based routing
6. **Auto-scaling**: HPA based on resource usage
7. **Configuration Management**: ConfigMaps and Secrets
8. **Resource Management**: Requests, limits, and QoS
9. **Health Monitoring**: Probes for application health
10. **Storage Management**: PVCs for persistent data

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [KCNA Exam Guide](https://www.cncf.io/certification/kcna/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) 