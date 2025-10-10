from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import traceback

from pydantic import BaseModel
# --- Model yang dibutuhkan oleh endpoint baru: /api/sessions/start ---
class SessionStartRequest(BaseModel):
    role: str
    level: str

class SessionStartResponse(BaseModel):
    session_id: str
    first_question: str
    first_question_id: int
# -----------------------------------------------------------------

from app.models.schemas import (
    BaseQuestionOut, SubmitAnswersRequest, SubmitAnswersResponse
)
from app.core.llm_service import generate_feedback, generate_followup_questions
from app.core.db_connector import (
    get_base_questions_by_names,
    get_main_question_text_by_id,
    insert_user_answer_main,
    insert_ml_question,
    insert_user_answer_ml,
    check_ml_question_exists
)

app = FastAPI(title="AI Interview Backend")

# --- PERBAIKAN CORS ---
app.add_middleware(
    CORSMiddleware,
    # Mengizinkan port 5173 (Vite Frontend)
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- AKHIR PERBAIKAN CORS ---

# --- ENDPOINT BARU: /api/sessions/start (Penyebab 404 Anda) ---
@app.post("/api/sessions/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest): 
    try:
        # 1. Ambil 1 pertanyaan dasar (Menggunakan fungsi db_connector yang sudah diperbaiki)
        qs = get_base_questions_by_names(payload.role, payload.level, limit=1)
        
        # 2. Jika tidak ada, lempar 404. 
        if not qs:
            # Jika DB mengembalikan kosong, ini yang membuat 404 Not Found
            raise HTTPException(status_code=404, detail="Tidak ada pertanyaan dasar untuk role/level ini.")

        first_q = qs[0]
        
        # 3. Logika pembuatan Session ID sederhana
        temp_session_id = f"sess_{first_q['id']}_{payload.role}_{payload.level}"

        return SessionStartResponse(
            session_id=temp_session_id,
            first_question=first_q['question'],
            first_question_id=first_q['id']
        )
        
    except HTTPException:
        # Jika error adalah 404 kita sendiri
        raise
    except Exception as e:
        # Jika ada error koneksi DB, ia akan masuk ke sini dan mencetak error (500)
        print("Unexpected non-HTTP error in /api/sessions/start:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Terjadi kesalahan server tak terduga saat memulai sesi.")
# --- AKHIR ENDPOINT BARU ---


@app.get("/api/v1/questions/base", response_model=List[BaseQuestionOut])
def get_base_questions(role: str = Query(...), level: str = Query(...)):
    qs = get_base_questions_by_names(role, level, limit=2)
    if not qs:
        raise HTTPException(status_code=404, detail="Tidak ada pertanyaan dasar untuk role/level ini.")
    return [{"id": r["id"], "question": r["question"]} for r in qs]

@app.post("/api/v1/questions/answers", response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest):
    try:
        # 1) Simpan jawaban user untuk pertanyaan dasar
        base_q_and_answers = []
        for ans in payload.answers:
            insert_user_answer_main(
                user_id=payload.user_id,
                main_question_id=ans.main_question_id,
                answer_text=ans.answer_text
            )
            qtext = get_main_question_text_by_id(ans.main_question_id)
            base_q_and_answers.append({'question': qtext, 'answer': ans.answer_text})

        # CASE A: generate step (belum ada ai_answers)
        if not payload.ai_answers:
            try:
                generated = generate_followup_questions(
                    role=payload.role,
                    level=payload.level,
                    base_q_and_answers=base_q_and_answers,
                    desired_count=3
                )
            except Exception as e:
                print("LLM generate_followup_questions error:", e)
                generated = []

            # simpan pertanyaan AI ke DB -> return id
            generated_ids = []
            for q in generated:
                ml_id = insert_ml_question(payload.user_id, q)
                generated_ids.append(ml_id)

            # generate feedback untuk jawaban dasar
            try:
                feedbacks = generate_feedback(payload.role, payload.level, base_q_and_answers)
            except Exception as e:
                print("generate_feedback (for base answers) failed:", e)
                traceback.print_exc()
                feedbacks = []

            return SubmitAnswersResponse(
                generated_questions=generated,
                generated_questions_ids=generated_ids,
                feedback=feedbacks,
                message="Berhasil generate pertanyaan lanjutan dan feedback untuk jawaban dasar."
            )

        # CASE B: final submit (ada ai_answers)
        all_q_and_a = base_q_and_answers.copy()
        for ai in payload.ai_answers:
            # ✅ cek apakah pertanyaan AI sudah ada di DB
            if not check_ml_question_exists(ai.ml_question_id):
                # auto-insert pertanyaan AI jika belum ada
                ai.ml_question_id = insert_ml_question(
                    payload.user_id,
                    f"Pertanyaan AI default untuk jawaban: {ai.answer_text}"
                )

            # simpan jawaban AI
            insert_user_answer_ml(
                user_id=payload.user_id,
                ml_question_id=ai.ml_question_id,
                answer_text=ai.answer_text
            )
            all_q_and_a.append({
                "question": f"Pertanyaan AI ID {ai.ml_question_id}",
                "answer": ai.answer_text
            })

        # generate feedback untuk semua jawaban
        try:
            feedbacks = generate_feedback(payload.role, payload.level, all_q_and_a)
        except Exception as e:
            print("generate_feedback (final) failed:", e)
            traceback.print_exc()
            feedbacks = []

        return SubmitAnswersResponse(
            generated_questions=[],
            generated_questions_ids=[],
            feedback=feedbacks,
            message="Berhasil simpan jawaban AI dan generate feedback."
        )

    except Exception as e:
        print("Unexpected error in /answers:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")