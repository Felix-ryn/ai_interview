from pydantic import BaseModel
from typing import List, Optional

class AnswerItem(BaseModel):
    main_question_id: int
    answer_text: str

class AIAnswerItem(BaseModel):
    ml_question_id: int
    answer_text: str

class SubmitAnswersRequest(BaseModel):
    user_id: int
    role: str
    level: str
    answers: List[AnswerItem]
    ai_answers: Optional[List[AIAnswerItem]] = []

class SubmitAnswersResponse(BaseModel):
    generated_questions: List[str]
    generated_questions_ids: Optional[List[int]] = []
    message: str

class BaseQuestionOut(BaseModel):
    id: int
    question: str
