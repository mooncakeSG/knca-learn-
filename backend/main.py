from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import redis
import json
import os
from datetime import datetime, timedelta

from .database import get_db, engine
from .models import Base, User, Quiz, Question, UserProgress, QuizAttempt
from .schemas import (
    UserCreate, UserResponse, QuizCreate, QuizResponse, 
    QuestionCreate, QuestionResponse, QuizAttemptCreate,
    QuizAttemptResponse, UserProgressResponse
)
from .auth import create_access_token, get_current_user, verify_password, get_password_hash
from .config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KCNA Learning Platform API",
    description="A comprehensive API for learning Kubernetes concepts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

security = HTTPBearer()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "KCNA Learning Platform API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Test Redis connection
        redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@app.post("/auth/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

# Quiz endpoints
@app.get("/quizzes", response_model=List[QuizResponse])
async def get_quizzes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available quizzes"""
    quizzes = db.query(Quiz).offset(skip).limit(limit).all()
    return quizzes

@app.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific quiz with its questions"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    return quiz

@app.post("/quizzes", response_model=QuizResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new quiz (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    quiz = Quiz(**quiz_data.dict())
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

# Question endpoints
@app.get("/questions", response_model=List[QuestionResponse])
async def get_questions(
    quiz_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questions, optionally filtered by quiz"""
    query = db.query(Question)
    if quiz_id:
        query = query.filter(Question.quiz_id == quiz_id)
    
    questions = query.offset(skip).limit(limit).all()
    return questions

@app.post("/questions", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new question (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    question = Question(**question_data.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

# Quiz attempt endpoints
@app.post("/quiz-attempts", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    attempt_data: QuizAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a quiz attempt and calculate score"""
    # Get the quiz
    quiz = db.query(Quiz).filter(Quiz.id == attempt_data.quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get all questions for this quiz
    questions = db.query(Question).filter(Question.quiz_id == attempt_data.quiz_id).all()
    
    # Calculate score
    correct_answers = 0
    total_questions = len(questions)
    
    for question in questions:
        if question.id in attempt_data.answers:
            user_answer = attempt_data.answers[question.id]
            if user_answer == question.correct_answer:
                correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=attempt_data.quiz_id,
        answers=attempt_data.answers,
        score=score,
        completed_at=datetime.utcnow()
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    # Update user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.quiz_id == attempt_data.quiz_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            quiz_id=attempt_data.quiz_id,
            best_score=score,
            attempts_count=1,
            last_attempt_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.attempts_count += 1
        progress.last_attempt_at = datetime.utcnow()
        if score > progress.best_score:
            progress.best_score = score
    
    db.commit()
    
    # Cache the result in Redis
    cache_key = f"quiz_attempt:{attempt.id}"
    redis_client.setex(
        cache_key,
        3600,  # 1 hour TTL
        json.dumps({
            "id": attempt.id,
            "score": score,
            "total_questions": total_questions,
            "correct_answers": correct_answers
        })
    )
    
    return attempt

@app.get("/quiz-attempts", response_model=List[QuizAttemptResponse])
async def get_user_attempts(
    quiz_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's quiz attempts"""
    query = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id)
    if quiz_id:
        query = query.filter(QuizAttempt.quiz_id == quiz_id)
    
    attempts = query.order_by(QuizAttempt.completed_at.desc()).offset(skip).limit(limit).all()
    return attempts

# Progress endpoints
@app.get("/progress", response_model=List[UserProgressResponse])
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's learning progress"""
    progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    return progress

@app.get("/progress/{quiz_id}", response_model=UserProgressResponse)
async def get_quiz_progress(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's progress for a specific quiz"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.quiz_id == quiz_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this quiz"
        )
    
    return progress

# KCNA Learning Resources
@app.get("/learning-resources")
async def get_learning_resources():
    """Get KCNA learning resources and topics"""
    return {
        "topics": [
            {
                "id": 1,
                "name": "Kubernetes Fundamentals",
                "description": "Core concepts of Kubernetes",
                "subtopics": [
                    "Pods and Containers",
                    "Services and Networking",
                    "Deployments and ReplicaSets",
                    "ConfigMaps and Secrets",
                    "Volumes and Storage"
                ]
            },
            {
                "id": 2,
                "name": "Cluster Architecture",
                "description": "Understanding Kubernetes cluster components",
                "subtopics": [
                    "Control Plane Components",
                    "Worker Node Components",
                    "etcd Database",
                    "API Server",
                    "Scheduler and Controller Manager"
                ]
            },
            {
                "id": 3,
                "name": "Application Lifecycle",
                "description": "Managing applications in Kubernetes",
                "subtopics": [
                    "Deployments",
                    "Rolling Updates",
                    "Rollbacks",
                    "Health Checks",
                    "Resource Limits"
                ]
            },
            {
                "id": 4,
                "name": "Networking",
                "description": "Kubernetes networking concepts",
                "subtopics": [
                    "Services",
                    "Ingress",
                    "Network Policies",
                    "DNS",
                    "Load Balancing"
                ]
            },
            {
                "id": 5,
                "name": "Storage",
                "description": "Persistent storage in Kubernetes",
                "subtopics": [
                    "PersistentVolumes",
                    "PersistentVolumeClaims",
                    "Storage Classes",
                    "Dynamic Provisioning",
                    "Volume Types"
                ]
            }
        ],
        "resources": [
            {
                "type": "documentation",
                "title": "Kubernetes Documentation",
                "url": "https://kubernetes.io/docs/",
                "description": "Official Kubernetes documentation"
            },
            {
                "type": "video",
                "title": "Kubernetes Crash Course",
                "url": "https://www.youtube.com/watch?v=s_o8dwV2m1Y",
                "description": "Quick overview of Kubernetes concepts"
            },
            {
                "type": "practice",
                "title": "Kubernetes Playground",
                "url": "https://labs.play-with-k8s.com/",
                "description": "Interactive Kubernetes playground"
            }
        ]
    }

@app.get("/external-learning-sources")
async def get_external_learning_sources():
    """Get external learning sources for KCNA certification"""
    try:
        # Load external learning sources from JSON file
        with open("backend/resources/learning_sources.json", "r", encoding="utf-8") as f:
            learning_sources = json.load(f)
        return learning_sources
    except FileNotFoundError:
        # Fallback to hardcoded data if file not found
        return {
            "learning_sources": [
                {
                    "id": "kube-academy",
                    "title": "KubeAcademy",
                    "url": "https://kube.academy",
                    "provider": "VMware",
                    "type": "learning_platform",
                    "difficulty": "mixed",
                    "category": "kubernetes",
                    "description": "Free Kubernetes learning platform offering courses, tutorials, and hands-on labs for all skill levels.",
                    "topics": [
                        "Kubernetes Fundamentals",
                        "Advanced Concepts",
                        "Security",
                        "Networking",
                        "Storage",
                        "Monitoring",
                        "Troubleshooting",
                        "Best Practices"
                    ],
                    "duration": "self-paced",
                    "cost": "free",
                    "rating": 4.7
                },
                {
                    "id": "freecodecamp-kcna",
                    "title": "KCNA Study Course on freeCodeCamp",
                    "url": "https://www.freecodecamp.org/news/tag/kubernetes/",
                    "provider": "freeCodeCamp",
                    "type": "course",
                    "difficulty": "beginner",
                    "category": "kubernetes",
                    "description": "Comprehensive study guide and practice materials for the Kubernetes and Cloud Native Associate (KCNA) certification exam.",
                    "topics": [
                        "Kubernetes Fundamentals",
                        "Cloud Native Concepts",
                        "Container Orchestration",
                        "Microservices Architecture",
                        "DevOps Practices",
                        "Exam Preparation",
                        "Practice Questions"
                    ],
                    "duration": "self-paced",
                    "cost": "free",
                    "rating": 4.8
                }
            ],
            "categories": {
                "kubernetes": {
                    "name": "Kubernetes",
                    "description": "Container orchestration and management"
                }
            },
            "difficulty_levels": {
                "beginner": {
                    "name": "Beginner",
                    "description": "No prior experience required"
                },
                "intermediate": {
                    "name": "Intermediate",
                    "description": "Some prior knowledge recommended"
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading learning sources: {str(e)}"
        )

@app.get("/learning-sources-markdown")
async def get_learning_sources_markdown():
    """Get learning sources in Markdown format"""
    try:
        with open("backend/resources/learning_sources.md", "r", encoding="utf-8") as f:
            markdown_content = f.read()
        return {
            "content": markdown_content,
            "format": "markdown",
            "last_updated": "2024-03-15"
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning sources markdown file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading markdown content: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 