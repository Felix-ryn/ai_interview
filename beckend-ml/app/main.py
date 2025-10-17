import os
import sys
from dotenv import load_dotenv
load_dotenv()

# =======================================================
# 🧠 Tambahan agar path "app/" dikenali saat run dari root
# =======================================================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import traceback

# 💡 Import error handling untuk MySQL
from mysql.connector.errors import IntegrityError, DatabaseError
from pydantic import BaseModel, Field # <<< FIELD DITAMBAHKAN UNTUK MENGHINDARI ERROR

# =======================================================
# 📦 Import schemas (Disesuaikan dan Ditambah)
# =======================================================
from models.schemas import (
    BaseQuestionOut,
    SubmitAnswersRequest,
    SubmitAnswersResponse,
    SessionStartResponse,
    QuestionDetail,
    # 🟢 SKEMA BARU DITAMBAHKAN
    UserCreate,            
    UserCreateResponse,    
    RoleOut,               
    LevelOut               
)

# =======================================================
# 📦 Import core logic (Disesuaikan dan Ditambah)
# =======================================================
from core.llm_service import generate_feedback, generate_followup_questions
from core.db_connector import (
    get_base_questions_by_names,
    get_main_question_text_by_id,
    get_ml_question_text_by_id,
    insert_user_answer_main,
    insert_ml_question,
    insert_user_answer_ml,
    check_ml_question_exists,
    # 🟢 FUNGSI BARU DITAMBAHKAN
    get_all_roles,       
    get_all_levels,      
    create_user          
)

# 💡 Definisi request untuk memulai sesi
class SessionStartRequest(BaseModel):
    role: str
    level: str


# =======================================================
# 🚀 FASTAPI APP
# =======================================================
app = FastAPI(title="AI Interview Backend")

# =======================================================
# 🔓 CORS (Frontend Vite)
# =======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# 🟢 ENDPOINT BARU: User Registration & Dropdown Data
# -------------------------------------------------------

@app.get("/api/v1/roles", response_model=List[RoleOut], summary="Mendapatkan daftar semua Role (untuk Dropdown)")
def get_roles():
    try:
        roles = get_all_roles()
        return roles
    except Exception as e:
        print(f"Gagal mengambil Roles: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil Roles: {str(e)}")

@app.get("/api/v1/levels", response_model=List[LevelOut], summary="Mendapatkan daftar semua Level (untuk Dropdown)")
def get_levels():
    try:
        levels = get_all_levels()
        return levels
    except Exception as e:
        print(f"Gagal mengambil Levels: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil Levels: {str(e)}")

@app.post("/api/v1/register", response_model=UserCreateResponse, status_code=201, summary="Mendaftarkan User Baru")
def register_user(user_data: UserCreate):
    try:
        # Pengecekan dasar ID 
        if user_data.role_id <= 0 or user_data.level_id <= 0:
             raise HTTPException(status_code=400, detail="ID Role atau Level tidak valid.")
             
        user_id = create_user(
            name=user_data.name,
            ref_role_id=user_data.role_id,
            ref_level_id=user_data.level_id
        )
        return UserCreateResponse(user_id=user_id, name=user_data.name)
        
    except IntegrityError as e:
        # Menangkap error Foreign Key jika ID Role/Level tidak ada
        raise HTTPException(status_code=400, detail=f"Gagal mendaftarkan user. Periksa ID Role/Level. Detail: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in /v1/register: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


# -------------------------------------------------------
# 🟢 ENDPOINT LAMA: Mulai Sesi Interview
# -------------------------------------------------------
@app.post("/api/sessions/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest):
    try:
        qs = get_base_questions_by_names(payload.role, payload.level, limit=2)

        if not qs or len(qs) < 2:
            raise HTTPException(
                status_code=404,
                detail="Tidak ada pertanyaan dasar yang cukup (minimal 2) untuk role/level ini."
            )

        first_q = qs[0]
        # Catatan: Session ID ini tidak menggunakan user_id yang baru dibuat
        temp_session_id = f"sess_{first_q['id']}_{payload.role}_{payload.level}" 

        formatted_questions = [
            {"id": q['id'], "question": q['question']} for q in qs
        ]

        return SessionStartResponse(
            session_id=temp_session_id,
            base_questions=formatted_questions
        )

    except HTTPException:
        raise
    except Exception as e:
        print("Unexpected non-HTTP error in /api/sessions/start:", e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan server tak terduga saat memulai sesi."
        )


# -------------------------------------------------------
# 🟢 ENDPOINT LAMA: Ambil Pertanyaan Dasar
# -------------------------------------------------------
@app.get("/api/v1/questions/base", response_model=List[BaseQuestionOut])
def get_base_questions(role: str = Query(...), level: str = Query(...)):
    qs = get_base_questions_by_names(role, level, limit=2)
    if not qs:
        raise HTTPException(
            status_code=404,
            detail="Tidak ada pertanyaan dasar untuk role/level ini."
        )
    return [{"id": r["id"], "question": r["question"]} for r in qs]


# -------------------------------------------------------
# 🟢 ENDPOINT LAMA: Submit Jawaban
# -------------------------------------------------------
@app.post("/api/v1/questions/answers", response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest):
    try:
        base_q_and_answers = []

        # =======================================================
        # 🧩 SIMPAN JAWABAN UTAMA
        # =======================================================
        for ans in payload.answers:
            qtext = None
            question_id = ans.main_question_id

            try:
                insert_user_answer_main(
                    user_id=payload.user_id,
                    main_question_id=question_id,
                    answer_text=ans.answer_text
                )
                qtext = get_main_question_text_by_id(question_id)

            except IntegrityError as e:
                if "1452" in str(e): # Coba simpan sebagai jawaban ML jika FK main_question gagal
                    try:
                        insert_user_answer_ml(
                            user_id=payload.user_id,
                            ml_question_id=question_id,
                            answer_text=ans.answer_text
                        )
                        qtext = get_ml_question_text_by_id(question_id)
                    except DatabaseError as e_db:
                        print(f"Gagal menyimpan ke ml_question: {e_db}")
                        traceback.print_exc()
                        raise HTTPException(
                            status_code=500,
                            detail="Database Error: Lock wait timeout saat menyimpan jawaban AI."
                        )
                    except Exception as e_ml:
                        print(f"Gagal simpan ke main/ml_question: {e_ml}")
                        traceback.print_exc()
                        raise HTTPException(
                            status_code=500,
                            detail="Gagal menyimpan jawaban karena masalah Foreign Key."
                        )
                else:
                    raise

            except DatabaseError as e_db:
                print(f"Gagal menyimpan ke main_question: {e_db}")
                traceback.print_exc()
                raise HTTPException(
                    status_code=500,
                    detail="Database Error: Lock wait timeout saat menyimpan jawaban utama."
                )

            if qtext:
                base_q_and_answers.append({'question': qtext, 'answer': ans.answer_text})

        # =======================================================
        # 🧠 CASE A: Generate Pertanyaan Lanjutan (Jawaban Dasar)
        # =======================================================
        if not payload.ai_answers:
            try:
                generated = generate_followup_questions(
                    role=payload.role,
                    level=payload.level,
                    base_q_and_answers=base_q_and_answers,
                    desired_count=1
                )
            except Exception as e:
                print("LLM generate_followup_questions error:", e)
                generated = []

            generated_ids = []
            for q in generated:
                try:
                    ml_id = insert_ml_question(payload.user_id, q)
                    generated_ids.append(ml_id)
                except DatabaseError as e_db:
                    print(f"Gagal insert ml_question: {e_db}")
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500,
                        detail="Database Error: Lock wait timeout saat menyimpan pertanyaan AI."
                    )

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

        # =======================================================
        # 🧩 CASE B: Final Submit (Jawaban Lanjutan AI)
        # =======================================================
        all_q_and_a = base_q_and_answers.copy()
        for ai in payload.ai_answers:
            try:
                exists = check_ml_question_exists(ai.ml_question_id)
            except DatabaseError as e_db:
                print(f"Gagal check_ml_question_exists: {e_db}")
                traceback.print_exc()
                raise HTTPException(
                    status_code=500,
                    detail="Database Error: Lock wait timeout saat memeriksa pertanyaan AI."
                )

            if not exists:
                # Fallback: Jika ID ml_question tidak valid, buat pertanyaan default
                try:
                    ai.ml_question_id = insert_ml_question(
                        payload.user_id,
                        f"Pertanyaan AI default untuk jawaban: {ai.answer_text}"
                    )
                except DatabaseError as e_db:
                    print(f"Gagal insert ml_question (default): {e_db}")
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500,
                        detail="Database Error: Lock wait timeout saat menyimpan pertanyaan AI (default)."
                    )

            try:
                insert_user_answer_ml(
                    user_id=payload.user_id,
                    ml_question_id=ai.ml_question_id,
                    answer_text=ai.answer_text
                )
            except DatabaseError as e_db:
                print(f"Gagal insert_user_answer_ml (final): {e_db}")
                traceback.print_exc()
                raise HTTPException(
                    status_code=500,
                    detail="Database Error: Lock wait timeout saat menyimpan jawaban AI (final)."
                )

            all_q_and_a.append({
                "question": f"Pertanyaan AI ID {ai.ml_question_id}",
                "answer": ai.answer_text
            })

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


# -------------------------------------------------------
# 🧾 ENDPOINT LAMA: Report Sesi Interview
# -------------------------------------------------------
@app.get("/api/sessions/{session_id}/report")
def get_session_report(session_id: str):
    """
    Endpoint laporan hasil sesi interview berdasarkan session_id.
    Versi awal ini dummy agar tidak 404, bisa diganti query database nanti.
    """
    try:
        mock_report = {
            "session_id": session_id,
            "summary": "Sesi wawancara selesai. Berikut hasil umpan balik Anda.",
            "feedback": [
                {
                    "question": "Apa yang kamu ketahui tentang data cleaning?",
                    "answer": "Saya menggunakan pandas dan numpy untuk data preprocessing.",
                    "feedback": "Jawaban bagus. Sebutkan juga metode handling missing values untuk konteks lanjutan."
                },
                {
                    "question": "Bagaimana kamu menangani outlier?",
                    "answer": "Saya gunakan IQR dan boxplot untuk mendeteksi outlier.",
                    "feedback": "Pendekatan tepat. Jelaskan juga metode z-score."
                }
            ]
        }
        return JSONResponse(content=mock_report, status_code=200)
    except Exception as e:
        print("Error generating session report:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Terjadi kesalahan saat memuat laporan sesi.")