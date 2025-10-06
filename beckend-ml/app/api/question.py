from fastapi import APIRouter
from app.core.llm_service import generate_followup_questions
from app.models.schemas import SubmitAnswersRequest, SubmitAnswersResponse

router = APIRouter()

@router.post("/answers", response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest):
    # Ambil jawaban user
    base_q_and_answers = [
        {"question": a["main_question_id"], "answer": a["answer_text"]}
        for a in payload.answers
    ]

    # Panggil LLM / fallback
    followup = generate_followup_questions(payload.role, payload.level, base_q_and_answers, desired_count=3)

    # Kembalikan dict dengan key 'generated_questions'
    return {
        "generated_questions": followup,
        "message": "Berhasil"
    }
