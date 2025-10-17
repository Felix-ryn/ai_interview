# app/models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional

# Skema untuk mendaftarkan user baru (Request)
class UserCreate(BaseModel):
    name: str = Field(..., description="Nama pengguna")
    role_id: int = Field(..., description="ID Role (ref_role_id)")
    level_id: int = Field(..., description="ID Level (ref_level_id)")

# Skema data untuk dropdown Role
class RoleOut(BaseModel):
    id: int
    role_name: str
    class Config:
        orm_mode = True # Aktifkan ORM mode untuk SQLAlchemy

# Skema data untuk dropdown Level
class LevelOut(BaseModel):
    id: int
    level_name: str
    class Config:
        orm_mode = True # Aktifkan ORM mode untuk SQLAlchemy

# Skema Response setelah user berhasil dibuat
class UserCreateResponse(BaseModel):
    user_id: int
    name: str
    message: str = "User berhasil didaftarkan."

# --- Model Baru untuk Session Start Response ---
class QuestionDetail(BaseModel):
    id: int
    question: str

class SessionStartResponse(BaseModel):
    session_id: str
    # Mengganti first_question: str dan first_question_id: int
    base_questions: List[QuestionDetail] # Mengirim List dari 2 pertanyaan
# ---------------------------------------------


class AnswerItem(BaseModel):
    main_question_id: int
    answer_text: str

class AIAnswerItem(BaseModel):
    ml_question_id: int
    answer_text: str 

# 🟢 Model baru untuk feedback hasil analisis AI
class FeedbackItem(BaseModel):
    question: str
    answer: str
    feedback_text: str

class SubmitAnswersRequest(BaseModel):
    user_id: int
    role: str
    level: str
    answers: List[AnswerItem] 
    ai_answers: Optional[List[AIAnswerItem]] = []

class SubmitAnswersResponse(BaseModel):
    generated_questions: List[str]
    generated_questions_ids: Optional[List[int]] = []
    feedback: Optional[List[FeedbackItem]] = [] 
    message: str

class BaseQuestionOut(BaseModel):
    id: int
    question: str