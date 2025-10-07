# app/routes/questions.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.databse import get_db  # perbaikan typo
from app.models import MainQuestion, MLQuestion, AnswerUser, User
from app.models.schemas import AnswerItem, AIAnswerItem, SubmitAnswersRequest, SubmitAnswersResponse, FeedbackItem
from app.core.question_generator import generate_followup_from_base

router = APIRouter(prefix="/questions", tags=["questions"])

# -------------------------
# Endpoint: Submit semua jawaban
# -------------------------
@router.post("/answers", response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest, db: Session = Depends(get_db)):
    """
    Simpan semua jawaban user ke database (pertanyaan dasar + AI)
    """
    try:
        # 🟢 Simpan jawaban main question
        for ans in payload.answers or []:
            if ans.main_question_id is not None:
                db_ans = AnswerUser(
                    user_id=payload.user_id,
                    main_question_id=int(ans.main_question_id),
                    ml_question_id=None,
                    answer_text=ans.answer_text or "",
                    score_overall=0,
                    score_relevance=0,
                    score_clarity=0,
                    score_structure=0,
                    score_confidence=0,
                    score_conciseness=0,
                )
                db.add(db_ans)

        # 🟢 Simpan jawaban AI (ml_question)
        for ai in payload.ai_answers or []:
            if ai.ml_question_id:  # hanya jika ada id
                db_ans = AnswerUser(
                    user_id=payload.user_id,
                    main_question_id=None,
                    ml_question_id=int(ai.ml_question_id),
                    answer_text=ai.answer_text or "",
                    score_overall=0,
                    score_relevance=0,
                    score_clarity=0,
                    score_structure=0,
                    score_confidence=0,
                    score_conciseness=0,
                )
                db.add(db_ans)

        db.commit()

        # 🟢 Buat feedback gabungan untuk main + AI
        feedback_list: List[FeedbackItem] = []

        for ans in payload.answers or []:
            feedback_list.append({
                "question": f"ID {ans.main_question_id}",
                "answer": ans.answer_text,
                "feedback_text": "Feedback AI sementara untuk pertanyaan dasar"
            })

        for ai in payload.ai_answers or []:
            feedback_list.append({
                "question": f"AI ID {ai.ml_question_id}",
                "answer": ai.answer_text,
                "feedback_text": "Feedback AI sementara untuk pertanyaan AI"
            })

        return SubmitAnswersResponse(
            generated_questions=[],
            generated_questions_ids=[],
            feedback=feedback_list,
            message="Jawaban berhasil disimpan"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
