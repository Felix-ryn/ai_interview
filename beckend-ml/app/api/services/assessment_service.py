# api/services/assessment_service.py

from typing import Optional, Dict, List
from app.core import db_connector
from helpers.ai_service import generate_followup_from_base

# ==========================
# SERVICE LAYER ASSESSMENT
# ==========================

def get_assessment_state(user_id: int) -> Dict[str, int]:
    """
    Ambil state assessment user:
    - current_question: nomor pertanyaan terakhir user
    - ml_question_count: jumlah ML question yang sudah dibuat
    """
    ml_questions = db_connector.get_all_ml_questions_for_user(user_id)
    ml_count = len(ml_questions)

    # Ambil jawaban terakhir user untuk main question
    last_answers = db_connector.get_all_answers_for_user_and_mq(user_id, main_question_id=1)
    current_q = len(last_answers)
    
    return {
        "current_question": current_q,
        "ml_question_count": ml_count
    }


def update_assessment_state(user_id: int, current_question: int, ml_question_count: int):
    """
    Update state user.
    Bisa diimplementasikan di DB atau cache, tergantung kebutuhan.
    Saat ini kosong, karena state diambil langsung dari DB.
    """
    pass


def save_user_answer(user_id: int, answer_text: str, question_type: str = "main", question_id: Optional[int] = None) -> int:
    """
    Simpan jawaban user.
    question_type: "main" atau "ml"
    question_id: ID pertanyaan (main_question_id atau ml_question_id)
    """
    if question_type == "main":
        return db_connector.insert_user_answer_main(user_id, question_id, answer_text)
    elif question_type == "ml":
        return db_connector.insert_user_answer_ml(user_id, question_id, answer_text)
    else:
        raise ValueError("question_type harus 'main' atau 'ml'")


def generate_ml_question(user_id: int, role: str = "", level: str = "", answers: List[str] = None) -> Optional[str]:
    """
    Generate pertanyaan ML (follow-up) berdasarkan jawaban sebelumnya.
    Menggunakan fungsi generate_followup_from_base.
    """
    if answers is None:
        answers = []
    result = generate_followup_from_base(user_id, role, level, answers)
    ml_questions = result.get("generated_questions", [])
    if ml_questions:
        return ml_questions[0]
    return None


def insert_ml_question(user_id: int, question_text: str) -> int:
    """
    Simpan pertanyaan ML ke DB. Jika sudah ada, kembalikan ID existing.
    """
    return db_connector.insert_ml_question(user_id, question_text)


def get_main_question(q_number: int, role_name: str = "", level_name: str = "") -> Optional[Dict]:
    """
    Ambil pertanyaan main berdasarkan nomor urut (q_number).
    Gunakan role_name dan level_name untuk filter.
    """
    questions = db_connector.get_base_questions_by_names(role_name, level_name, limit=q_number)
    if len(questions) >= q_number:
        return questions[q_number - 1]
    return None
