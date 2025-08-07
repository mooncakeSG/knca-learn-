from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Quiz schemas
class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    difficulty: str
    time_limit: Optional[int] = None
    passing_score: float = 70.0
    is_active: bool = True

class QuizCreate(QuizBase):
    pass

class QuizResponse(QuizBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List["QuestionResponse"] = []
    
    class Config:
        from_attributes = True

# Question schemas
class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    options: Optional[Dict[str, Any]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 1

class QuestionCreate(QuestionBase):
    quiz_id: int

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Quiz attempt schemas
class QuizAttemptBase(BaseModel):
    quiz_id: int
    answers: Dict[int, str]
    time_taken: Optional[int] = None

class QuizAttemptCreate(QuizAttemptBase):
    pass

class QuizAttemptResponse(QuizAttemptBase):
    id: int
    user_id: int
    score: float
    completed_at: datetime
    
    class Config:
        from_attributes = True

# User progress schemas
class UserProgressBase(BaseModel):
    quiz_id: int
    best_score: float
    attempts_count: int
    last_attempt_at: Optional[datetime] = None
    completed: bool = False

class UserProgressResponse(UserProgressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Update the forward references
QuizResponse.model_rebuild()
QuestionResponse.model_rebuild() 