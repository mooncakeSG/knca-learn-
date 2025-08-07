# 🚀 Quick Start Guide

Get the KCNA Learning Platform up and running in minutes!

## 📋 Prerequisites

Before you start, make sure you have the following installed:

- **Docker Desktop** - For containerization
- **kubectl** - Kubernetes command-line tool
- **Minikube** or **kind** - Local Kubernetes cluster
- **Node.js 18+** - For frontend development
- **Python 3.10+** - For backend development

## 🎯 Option 1: Local Development (Recommended for Learning)

### Step 1: Clone and Setup
```bash
git clone <your-repo-url>
cd kcna-learn
```

### Step 2: Run Setup Script
```bash
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh
```

### Step 3: Start the Applications
```bash
# Terminal 1 - Start Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start Frontend
cd frontend
npm run dev
```

### Step 4: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Option 2: Kubernetes Deployment

### Step 1: Start Local Kubernetes Cluster
```bash
# Using Minikube
minikube start --driver=docker --cpus=4 --memory=8192

# Or using Kind
kind create cluster --name kcna-learn
```

### Step 2: Install NGINX Ingress Controller
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### Step 3: Deploy the Application
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Step 4: Access the Application
```bash
# Get the external IP
kubectl get svc -n ingress-nginx

# Add to /etc/hosts (or Windows hosts file)
echo "127.0.0.1 kcna-learn.local" | sudo tee -a /etc/hosts
echo "127.0.0.1 api.kcna-learn.local" | sudo tee -a /etc/hosts

# Access the application
open http://kcna-learn.local
```

## 🧪 Testing the Application

### 1. Register a New User
- Go to http://localhost:3000/register
- Create an account with your email and password

### 2. Take a Quiz
- Navigate to the Quizzes section
- Select a Kubernetes fundamentals quiz
- Answer questions and see your score

### 3. Check Your Progress
- Visit the Progress section to see your learning journey
- Track your quiz attempts and scores

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker restart postgres-local
```

#### 3. Kubernetes Pod Issues
```bash
# Check pod status
kubectl get pods -n kcna-learn

# Check pod logs
kubectl logs -f deployment/backend -n kcna-learn
kubectl logs -f deployment/frontend -n kcna-learn

# Describe pod for more details
kubectl describe pod <pod-name> -n kcna-learn
```

#### 4. Ingress Issues
```bash
# Check ingress status
kubectl get ingress -n kcna-learn

# Check ingress controller
kubectl get pods -n ingress-nginx
```

## 📚 Learning Resources

### Kubernetes Concepts Covered
- **Pods**: Basic units of deployment
- **Deployments**: Manage stateless applications
- **StatefulSets**: Manage stateful applications (PostgreSQL)
- **Services**: Enable communication between components
- **Ingress**: External access management
- **ConfigMaps & Secrets**: Configuration management
- **PersistentVolumeClaims**: Storage management
- **HorizontalPodAutoscaler**: Auto-scaling

### Next Steps
1. **Explore the Code**: Understand how each component works
2. **Modify the Application**: Add new features or quizzes
3. **Practice Kubernetes**: Try different deployment strategies
4. **Study for KCNA**: Use this platform to prepare for the exam

## 🎓 KCNA Exam Preparation

This platform helps you learn:
- ✅ Kubernetes architecture and components
- ✅ Pod lifecycle and management
- ✅ Service discovery and networking
- ✅ Storage and persistence
- ✅ Configuration and secrets management
- ✅ Application deployment and scaling
- ✅ Monitoring and troubleshooting

## 🆘 Getting Help

- **Documentation**: Check the `/docs` folder
- **Issues**: Create an issue on GitHub
- **Community**: Join our discussion forum

---

**Happy Learning! 🎓**

Remember: The best way to learn Kubernetes is by doing. This platform gives you hands-on experience with real-world concepts! 