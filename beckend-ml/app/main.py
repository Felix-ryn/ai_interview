from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import traceback
# 💡 PERBAIKAN: Import IntegrityError DAN DatabaseError
from mysql.connector.errors import IntegrityError, DatabaseError 

from pydantic import BaseModel

from app.models.schemas import (
    BaseQuestionOut, SubmitAnswersRequest, SubmitAnswersResponse,
    # 💡 PERBAIKAN: Impor schema yang diperlukan untuk endpoint start
    SessionStartResponse, QuestionDetail 
)
from app.core.llm_service import generate_feedback, generate_followup_questions
from app.core.db_connector import (
    get_base_questions_by_names,
    get_main_question_text_by_id,
    # Tambahkan get_ml_question_text_by_id agar konteks LLM benar
    get_ml_question_text_by_id, 
    insert_user_answer_main,
    insert_ml_question,
    insert_user_answer_ml,
    check_ml_question_exists
)

# 💡 Definisikan ulang SessionStartRequest karena mungkin tidak ada di schemas.py
class SessionStartRequest(BaseModel):
    role: str
    level: str

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

# --- ENDPOINT START (TIDAK BERUBAH) ---
@app.post("/api/sessions/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest): 
    try:
        # 1. Ambil 2 pertanyaan dasar
        qs = get_base_questions_by_names(payload.role, payload.level, limit=2)
        
        # 2. Jika tidak ada, lempar 404. 
        if not qs or len(qs) < 2:
            raise HTTPException(status_code=404, detail="Tidak ada pertanyaan dasar yang cukup (minimal 2) untuk role/level ini.")

        first_q = qs[0]
        
        # 3. Logika pembuatan Session ID sederhana
        temp_session_id = f"sess_{first_q['id']}_{payload.role}_{payload.level}"
        
        # 4. Format respons sebagai List[QuestionDetail]
        formatted_questions = [
            {"id": q['id'], "question": q['question']} for q in qs
        ]

        return SessionStartResponse(
            session_id=temp_session_id,
            base_questions=formatted_questions # Mengirim array 2 pertanyaan
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print("Unexpected non-HTTP error in /api/sessions/start:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Terjadi kesalahan server tak terduga saat memulai sesi.")
# --- AKHIR ENDPOINT START ---


@app.get("/api/v1/questions/base", response_model=List[BaseQuestionOut])
def get_base_questions(role: str = Query(...), level: str = Query(...)):
    qs = get_base_questions_by_names(role, level, limit=2)
    if not qs:
        raise HTTPException(status_code=404, detail="Tidak ada pertanyaan dasar untuk role/level ini.")
    return [{"id": r["id"], "question": r["question"]} for r in qs]

@app.post("/api/v1/questions/answers", response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest):
    try:
        base_q_and_answers = []
        for ans in payload.answers:
            qtext = None
            question_id = ans.main_question_id # ID yang dikirim frontend

            try:
                # 1. Coba simpan sebagai Jawaban Pertanyaan UTAMA (Q1/Q2)
                insert_user_answer_main(
                    user_id=payload.user_id,
                    main_question_id=question_id,
                    answer_text=ans.answer_text
                )
                qtext = get_main_question_text_by_id(question_id)
                
            except IntegrityError as e:
                # 2. JIKA GAGAL (karena FK 1452), asumsikan ID tersebut dari ml_question
                if "1452" in str(e):
                    try:
                        # Coba simpan sebagai Jawaban Pertanyaan AI (Q3/Q4/Q5)
                        insert_user_answer_ml(
                            user_id=payload.user_id,
                            ml_question_id=question_id,
                            answer_text=ans.answer_text
                        )
                        # Ambil teks pertanyaan dari ml_question untuk konteks LLM
                        qtext = get_ml_question_text_by_id(question_id)
                        
                    except DatabaseError as e_db:
                        # TANGKAP ERROR TIMEOUT DI SINI (setelah rollback di db_connector.py)
                        print(f"Gagal menyimpan ke ml_question karena Database Error (Timeout/Deadlock): {e_db}")
                        traceback.print_exc()
                        raise HTTPException(status_code=500, detail="Database Error: Terjadi Lock wait timeout saat menyimpan jawaban AI. Coba lagi.")
                        
                    except Exception as e_ml:
                        print(f"Gagal menyimpan ke main_question dan ml_question: {e_ml}")
                        traceback.print_exc()
                        raise HTTPException(status_code=500, detail="Gagal menyimpan jawaban karena masalah Foreign Key yang kompleks.")
                else:
                    # Jika IntegrityError adalah jenis lain, kita lempar
                    raise
            
            except DatabaseError as e_db:
                # TANGKAP ERROR TIMEOUT DI SINI (setelah rollback di db_connector.py)
                print(f"Gagal menyimpan ke main_question karena Database Error (Timeout/Deadlock): {e_db}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail="Database Error: Terjadi Lock wait timeout saat menyimpan jawaban utama. Coba lagi.")

            # 3. Jika qtext berhasil didapat (berarti insert berhasil di 1 atau 2)
            if qtext:
                base_q_and_answers.append({'question': qtext, 'answer': ans.answer_text})


        # CASE A: generate step (Terjadi setelah Q2, Q3, atau Q4 dijawab)
        if not payload.ai_answers:
            # 💡 PERBAIKAN: Ubah desired_count=3 menjadi 1 (kita hanya butuh 1 pertanyaan berikutnya)
            try:
                generated = generate_followup_questions(
                    role=payload.role,
                    level=payload.level,
                    base_q_and_answers=base_q_and_answers,
                    desired_count=1 # Kita hanya butuh satu pertanyaan per langkah
                )
            except Exception as e:
                print("LLM generate_followup_questions error:", e)
                generated = []

            # simpan pertanyaan AI ke DB -> return id
            generated_ids = []
            for q in generated:
                # Menambahkan try/except untuk mengatasi kemungkinan timeout saat insert ml_question
                try:
                    ml_id = insert_ml_question(payload.user_id, q)
                    generated_ids.append(ml_id)
                except DatabaseError as e_db:
                    print(f"Gagal insert ml_question karena Database Error (Timeout/Deadlock): {e_db}")
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail="Database Error: Terjadi Lock wait timeout saat menyimpan pertanyaan AI. Coba lagi.")


            # generate feedback untuk jawaban yang baru disubmit
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
            
            # Memastikan check_ml_question_exists tidak gagal karena timeout/deadlock
            try:
                exists = check_ml_question_exists(ai.ml_question_id)
            except DatabaseError as e_db:
                print(f"Gagal check_ml_question_exists karena Database Error (Timeout/Deadlock): {e_db}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail="Database Error: Terjadi Lock wait timeout saat memeriksa pertanyaan AI.")
            
            if not exists:
                # Memastikan insert_ml_question tidak gagal karena timeout/deadlock
                try:
                    ai.ml_question_id = insert_ml_question(
                        payload.user_id,
                        f"Pertanyaan AI default untuk jawaban: {ai.answer_text}"
                    )
                except DatabaseError as e_db:
                    print(f"Gagal insert ml_question (default) karena Database Error (Timeout/Deadlock): {e_db}")
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail="Database Error: Terjadi Lock wait timeout saat menyimpan pertanyaan AI (default). Coba lagi.")


            # simpan jawaban AI
            try:
                insert_user_answer_ml(
                    user_id=payload.user_id,
                    ml_question_id=ai.ml_question_id,
                    answer_text=ai.answer_text
                )
            except DatabaseError as e_db:
                print(f"Gagal insert_user_answer_ml (final) karena Database Error (Timeout/Deadlock): {e_db}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail="Database Error: Terjadi Lock wait timeout saat menyimpan jawaban AI (final). Coba lagi.")
                
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

    except HTTPException:
        raise
    except Exception as e:
        print("Unexpected error in /answers:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
