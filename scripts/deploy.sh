#!/bin/bash

# KCNA Learning Platform Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="kcna-learn"
BACKEND_IMAGE="kcna-learn-backend:latest"
FRONTEND_IMAGE="kcna-learn-frontend:latest"

echo -e "${GREEN}🚀 Starting KCNA Learning Platform Deployment${NC}"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed. Please install kubectl first.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if namespace exists, create if not
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}📦 Creating namespace: $NAMESPACE${NC}"
    kubectl apply -f k8s/namespace.yaml
fi

# Build and push Docker images
echo -e "${YELLOW}🔨 Building Docker images...${NC}"

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build -t $BACKEND_IMAGE ./backend

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
docker build -t $FRONTEND_IMAGE ./frontend

# Apply Kubernetes manifests
echo -e "${YELLOW}📋 Applying Kubernetes manifests...${NC}"

# Apply secrets and configmaps
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml

# Apply storage
kubectl apply -f k8s/postgres-pvc.yaml

# Apply database
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Apply backend
kubectl apply -f k8s/backend-deployment.yaml

# Apply frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Apply services
kubectl apply -f k8s/services.yaml

# Apply ingress
kubectl apply -f k8s/ingress.yaml

# Apply HPA
kubectl apply -f k8s/hpa.yaml

# Wait for deployments to be ready
echo -e "${YELLOW}⏳ Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available deployment/backend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=available deployment/frontend -n $NAMESPACE --timeout=300s

# Get service URLs
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Application Status:${NC}"
kubectl get pods -n $NAMESPACE
echo -e "\n${GREEN}🌐 Services:${NC}"
kubectl get svc -n $NAMESPACE
echo -e "\n${GREEN}🔗 Ingress:${NC}"
kubectl get ingress -n $NAMESPACE

# Get external IP (if available)
echo -e "\n${YELLOW}📝 To access the application:${NC}"
echo -e "1. Add to your /etc/hosts file:"
echo -e "   127.0.0.1 kcna-learn.local"
echo -e "   127.0.0.1 api.kcna-learn.local"
echo -e "\n2. Access the application at:"
echo -e "   Frontend: http://kcna-learn.local"
echo -e "   API: http://api.kcna-learn.local"
echo -e "\n3. For local development, use port forwarding:"
echo -e "   kubectl port-forward svc/frontend 3000:3000 -n $NAMESPACE"
echo -e "   kubectl port-forward svc/backend 8000:8000 -n $NAMESPACE"

echo -e "\n${GREEN}🎉 KCNA Learning Platform is now deployed!${NC}" 