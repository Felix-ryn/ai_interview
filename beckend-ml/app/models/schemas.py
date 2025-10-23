from pydantic import BaseModel, Field
from typing import List, Optional, Dict # 💡 TAMBAHKAN Dict

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

# -------------------------------------------------------
# 🟢 SKEMA BARU UNTUK FINAL FEEDBACK
# -------------------------------------------------------
class FinalFeedbackRequest(BaseModel):
    user_id: int = Field(..., description="ID dari user yang mengikuti wawancara.")
    main_question_id: int = Field(..., description="ID dari pertanyaan utama pertama (untuk identifikasi sesi).")
    role_id: int = Field(..., description="ID Role yang dipilih.")
    level_id: int = Field(..., description="ID Level yang dipilih.")

class FinalFeedbackOut(BaseModel):
    score_overall: float = Field(..., description="Skor total kumulatif (0-100).")
    feedback_narrative: str = Field(..., description="Umpan balik naratif yang panjang dan komprehensif.")
    # Gunakan Dict untuk metrics (Komunikasi, Teknis, dll.)
    score_metrics: Dict[str, float] = Field(..., description="Metrik penilaian terperinci (e.g., {'Komunikasi': 4.5, 'Teknis': 4.8, 'Relevansi': 4.0}).")