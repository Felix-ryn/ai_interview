# app/main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.models.schemas import (
    BaseQuestionOut, SubmitAnswersRequest, SubmitAnswersResponse
)
from app.core.llm_service import generate_followup_questions
from app.core.db_connector import (
    get_base_questions_by_names,
    get_main_question_text_by_id,
    insert_user_answer_main,
    insert_ml_question,
    insert_user_answer_ml  # <- harus ada fungsi ini
)

app = FastAPI(title="AI Interview Backend")

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ambil pertanyaan dasar
@app.get("/api/v1/questions/base", response_model=List[BaseQuestionOut])
def get_base_questions(role: str = Query(...), level: str = Query(...)):
    qs = get_base_questions_by_names(role, level, limit=2)
    if not qs:
        raise HTTPException(status_code=404, detail="Tidak ada pertanyaan dasar untuk role/level ini.")
    return [{"id": r["id"], "question": r["question"]} for r in qs]

# Submit jawaban + generate pertanyaan AI
@app.post("/api/v1/questions/answers", response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest):
    base_q_and_answers = []

    # 1️⃣ Simpan jawaban user untuk pertanyaan dasar
    for ans in payload.answers:
        insert_user_answer_main(
            user_id=payload.user_id,
            main_question_id=ans.main_question_id,
            answer_text=ans.answer_text
        )
        qtext = get_main_question_text_by_id(ans.main_question_id)
        base_q_and_answers.append({'question': qtext, 'answer': ans.answer_text})

    # 2️⃣ Generate pertanyaan AI
    try:
        generated = generate_followup_questions(
            role=payload.role,
            level=payload.level,
            base_q_and_answers=base_q_and_answers,
            desired_count=3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate pertanyaan AI: {e}")

    # 3️⃣ Simpan pertanyaan AI ke table ml_question + ambil id
    generated_ids = []
    for q in generated:
        ml_id = insert_ml_question(payload.user_id, q)  # insert -> return id
        generated_ids.append(ml_id)

    # 4️⃣ Simpan jawaban user untuk pertanyaan AI jika ada
    if payload.ai_answers:
        for ai_ans in payload.ai_answers:
            insert_user_answer_ml(
                user_id=payload.user_id,
                ml_question_id=ai_ans.ml_question_id,
                answer_text=ai_ans.answer_text
            )

    return SubmitAnswersResponse(
        generated_questions=generated,
        generated_questions_ids=generated_ids,
        message="Berhasil generate pertanyaan lanjutan."
    )
