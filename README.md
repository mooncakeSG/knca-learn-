# KCNA Learning Platform

A comprehensive multi-tier Kubernetes application designed to help you learn and practice Kubernetes concepts while building a real-world application.

## 🏗️ Architecture

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

## 🚀 Features

- **Interactive Quiz System**: Practice KCNA concepts with real-time feedback
- **Progress Tracking**: Monitor your learning progress
- **Kubernetes Native**: Built with Kubernetes best practices
- **Scalable**: Horizontal Pod Autoscaler for backend
- **Persistent Storage**: PostgreSQL with PVC
- **Monitoring**: Prometheus + Grafana integration
- **CI/CD Ready**: GitHub Actions workflow

## 🛠️ Tech Stack

### Frontend
- React 18
- Tailwind CSS
- TypeScript
- Vite

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis (caching)

### Infrastructure
- Kubernetes
- Docker
- Helm
- NGINX Ingress Controller

## 📋 Prerequisites

### Local Development Tools
```bash
# Install these tools on your development machine
- Docker Desktop
- kubectl
- Helm
- Minikube or kind
- Node.js 18+
- Python 3.10+
```

### Kubernetes Cluster
```bash
# Start local cluster
minikube start --driver=docker --cpus=4 --memory=8192

# Or use kind
kind create cluster --name kcna-learn
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd kcna-learn
```

### 2. Install Dependencies
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### 3. Deploy to Kubernetes
```bash
# Deploy all components
kubectl apply -f k8s/

# Or use Helm
helm install kcna-learn ./helm/kcna-learn
```

### 4. Access the Application
```bash
# Get the external IP
kubectl get svc -n ingress-nginx

# Access via browser
http://localhost:3000
```

## 📁 Project Structure

```
kcna-learn/
├── frontend/                 # React application
├── backend/                  # FastAPI application
├── k8s/                     # Kubernetes manifests
├── helm/                     # Helm charts
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
└── monitoring/               # Prometheus + Grafana
```

## 🔧 Development

### Local Development
```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && uvicorn main:app --reload

# Database (local)
docker run -d --name postgres -e POSTGRES_PASSWORD=password postgres:15
```

### Kubernetes Development
```bash
# Deploy to cluster
kubectl apply -f k8s/

# View logs
kubectl logs -f deployment/frontend
kubectl logs -f deployment/backend

# Port forward for local access
kubectl port-forward svc/frontend 3000:3000
kubectl port-forward svc/backend 8000:8000
```

## 📊 Monitoring

Access monitoring dashboards:
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

## 🔐 Secrets Management

Create required secrets:
```bash
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=your-secure-password
```

## 📈 Scaling

The backend automatically scales based on CPU usage:
```bash
# Check HPA status
kubectl get hpa

# Scale manually
kubectl scale deployment backend --replicas=3
```

## 🧪 Testing

```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && pytest

# E2E tests
npm run test:e2e
```

## 📚 Learning Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [KCNA Exam Guide](https://www.cncf.io/certification/kcna/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the documentation in `/docs`
- Join our community discussions

---

**Happy Learning! 🎓** 