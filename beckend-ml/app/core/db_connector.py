# app/core/db_connector.py
import mysql.connector
from datetime import datetime
import os

DB_CONFIG = {
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get("DB_PASSWORD"),
    'host': os.environ.get("DB_HOST"),
    'database': os.environ.get("DB_NAME"),
    'port': int(os.environ.get("DB_PORT", 3306)),
    'auth_plugin': 'mysql_native_password'
}

def _get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def get_base_questions_by_names(role_name: str, level_name: str, limit: int = 2):
    """
    Ambil 2 pertanyaan dasar (main_question) berdasarkan nama role dan level.
    Return list of dicts: [{'id': ..., 'question': ...}, ...]
    """
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    q = """
    SELECT mq.id, mq.question
    FROM main_question mq
    JOIN ref_role rr ON mq.ref_role_id = rr.id
    JOIN ref_level rl ON mq.ref_level_id = rl.id
    WHERE rr.role_name = %s AND rl.level_name = %s
    ORDER BY mq.id
    LIMIT %s
    """
    cursor.execute(q, (role_name, level_name, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_main_question_text_by_id(mq_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM main_question WHERE id = %s", (mq_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def insert_user_answer_main(user_id: int, main_question_id: int, answer_text: str,
                            score_overall: int = 0, score_relevance: int = 0, score_clarity: int = 0,
                            score_structure: int = 0, score_confidence: int = 0, score_conciseness: int = 0,
                            nlp_star_detected: int = 0, nlp_filler_ratio: float = 0.0,
                            feedback_narrative: str = None) -> int:
    """
    Simpan jawaban user untuk main_question (kolom main_question_id terisi).
    Karena schema mengharuskan skor non-null, isi default 0 (kamu bisa update kemudian).
    """
    conn = _get_conn()
    cursor = conn.cursor()
    q = """
    INSERT INTO answer_user (
        user_id, main_question_id, ml_question_id, answer_text,
        score_overall, score_relevance, score_clarity, score_structure,
        score_confidence, score_conciseness, nlp_star_detected, nlp_filler_ratio,
        feedback_narrative, created_at
    ) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    now = datetime.now()
    params = (
        user_id, main_question_id, answer_text,
        score_overall, score_relevance, score_clarity, score_structure,
        score_confidence, score_conciseness, nlp_star_detected, nlp_filler_ratio,
        feedback_narrative, now
    )
    cursor.execute(q, params)
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def insert_ml_question(user_id: int, question_text: str) -> int:
    """
    Simpan pertanyaan yang dihasilkan AI ke tabel ml_question.
    """
    conn = _get_conn()
    cursor = conn.cursor()
    query = """
    INSERT INTO ml_question (user_id, question_ml, created_at)
    VALUES (%s, %s, %s)
    """
    now = datetime.now()
    cursor.execute(query, (user_id, question_text, now))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def insert_user_answer_ml(user_id: int, ml_question_id: int, answer_text: str,
                          score_overall: int = 0, score_relevance: int = 0, score_clarity: int = 0,
                          score_structure: int = 0, score_confidence: int = 0, score_conciseness: int = 0,
                          nlp_star_detected: int = 0, nlp_filler_ratio: float = 0.0,
                          feedback_narrative: str = None) -> int:
    """
    Simpan jawaban untuk pertanyaan ML (ml_question_id terisi).
    """
    conn = _get_conn()
    cursor = conn.cursor()
    q = """
    INSERT INTO answer_user (
        user_id, main_question_id, ml_question_id, answer_text,
        score_overall, score_relevance, score_clarity, score_structure,
        score_confidence, score_conciseness, nlp_star_detected, nlp_filler_ratio,
        feedback_narrative, created_at
    ) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    now = datetime.now()
    params = (
        user_id, ml_question_id, answer_text,
        score_overall, score_relevance, score_clarity, score_structure,
        score_confidence, score_conciseness, nlp_star_detected, nlp_filler_ratio,
        feedback_narrative, now
    )
    cursor.execute(q, params)
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id
