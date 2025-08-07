#!/bin/bash

# KCNA Learning Platform Local Setup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Setting up KCNA Learning Platform Local Environment${NC}"

# Check if required tools are installed
echo -e "${YELLOW}🔍 Checking required tools...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10+ first.${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed. Please install kubectl first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All required tools are installed${NC}"

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Install backend dependencies
echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Start local Kubernetes cluster (if not running)
echo -e "${YELLOW}🚀 Starting local Kubernetes cluster...${NC}"

# Check if minikube is installed and start it
if command -v minikube &> /dev/null; then
    if ! minikube status &> /dev/null; then
        echo -e "${YELLOW}Starting minikube...${NC}"
        minikube start --driver=docker --cpus=4 --memory=8192
    else
        echo -e "${GREEN}Minikube is already running${NC}"
    fi
elif command -v kind &> /dev/null; then
    if ! kind get clusters | grep -q "kcna-learn"; then
        echo -e "${YELLOW}Creating kind cluster...${NC}"
        kind create cluster --name kcna-learn
    else
        echo -e "${GREEN}Kind cluster is already running${NC}"
    fi
else
    echo -e "${YELLOW}No local Kubernetes cluster found. Please install minikube or kind.${NC}"
fi

# Install NGINX Ingress Controller
echo -e "${YELLOW}📦 Installing NGINX Ingress Controller...${NC}"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
echo -e "${YELLOW}⏳ Waiting for NGINX Ingress Controller to be ready...${NC}"
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Create namespace
echo -e "${YELLOW}📦 Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

# Apply secrets and configmaps
echo -e "${YELLOW}🔐 Applying secrets and configmaps...${NC}"
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml

# Start local database
echo -e "${YELLOW}🗄️ Starting local PostgreSQL...${NC}"
docker run -d \
  --name postgres-local \
  -e POSTGRES_DB=kcna_learn \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# Start local Redis
echo -e "${YELLOW}🔴 Starting local Redis...${NC}"
docker run -d \
  --name redis-local \
  -p 6379:6379 \
  redis:7-alpine

# Wait for databases to be ready
echo -e "${YELLOW}⏳ Waiting for databases to be ready...${NC}"
sleep 10

# Create .env file for backend
echo -e "${YELLOW}📝 Creating backend environment file...${NC}"
cat > backend/.env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/kcna_learn
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
EOF

# Create .env file for frontend
echo -e "${YELLOW}📝 Creating frontend environment file...${NC}"
cat > frontend/.env << EOF
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
EOF

echo -e "${GREEN}✅ Local environment setup completed!${NC}"
echo -e "\n${YELLOW}📝 Next steps:${NC}"
echo -e "1. Start the backend:"
echo -e "   cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo -e "\n2. Start the frontend:"
echo -e "   cd frontend && npm run dev"
echo -e "\n3. Access the application:"
echo -e "   Frontend: http://localhost:3000"
echo -e "   Backend API: http://localhost:8000"
echo -e "   API Docs: http://localhost:8000/docs"
echo -e "\n4. To deploy to Kubernetes:"
echo -e "   ./scripts/deploy.sh"
echo -e "\n${GREEN}🎉 Happy learning!${NC}" 