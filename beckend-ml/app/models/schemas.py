# app/models/schemas.py

from pydantic import BaseModel
from typing import List, Optional

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