import mysql.connector
from datetime import datetime
from mysql.connector.errors import IntegrityError, DatabaseError 
from typing import List, Dict, Any 

# === Ganti _get_conn dengan yang sesuai dengan konfigurasi Anda ===
def _get_conn():
    """Membuat koneksi ke database MySQL."""
    # Pastikan kredensial ini sudah benar
    return mysql.connector.connect(
        user='root', 
        password='', 
        host='127.0.0.1', 
        database='tm_db', 
        port=3307, 
        auth_plugin='mysql_native_password'
    )
# ===================================================================

def get_all_roles():
    """Mengambil semua data role dari ref_role."""
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    q = "SELECT id, role_name FROM ref_role ORDER BY role_name"
    try:
        cursor.execute(q)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_all_levels():
    """Mengambil semua data level dari ref_level."""
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    q = "SELECT id, level_name FROM ref_level ORDER BY id"
    try:
        cursor.execute(q)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def create_user(name: str, ref_role_id: int, ref_level_id: int) -> int:
    """Menyimpan user baru ke tabel user dan mengembalikan ID-nya."""
    conn = _get_conn()
    cursor = conn.cursor()
    last_id = None
    q = """
    INSERT INTO user (name, ref_role_id, ref_level_id, created_at) 
    VALUES (%s, %s, %s, %s)
    """
    now = datetime.now()
    try:
        cursor.execute(q, (name, ref_role_id, ref_level_id, now))
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except (IntegrityError, DatabaseError) as e:
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()
        
def get_base_questions_by_names(role_name: str, level_name: str, limit: int = 2):
    """Mengambil pertanyaan dasar berdasarkan role dan level."""
    normalized_role = role_name.lower()
    normalized_level = level_name.lower()
    
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    q = """
    SELECT mq.id, mq.question
    FROM main_question mq
    JOIN ref_role rr ON mq.ref_role_id = rr.id
    JOIN ref_level rl ON mq.ref_level_id = rl.id
    WHERE LOWER(rr.role_name) = %s AND LOWER(rl.level_name) = %s 
    ORDER BY mq.id
    LIMIT %s
    """
    try:
        cursor.execute(q, (normalized_role, normalized_level, limit))
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()

def get_main_question_text_by_id(mq_id: int):
    """Mengambil teks pertanyaan utama berdasarkan ID."""
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT question FROM main_question WHERE id = %s", (mq_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        conn.close()

def get_ml_question_text_by_id(ml_id: int):
    """Mengambil teks pertanyaan ML (follow-up) berdasarkan ID."""
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT question_ml FROM ml_question WHERE id = %s", (ml_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        conn.close()


def insert_user_answer_main(user_id: int, main_question_id: int, answer_text: str) -> int:
    """Menyimpan jawaban user untuk pertanyaan utama."""
    conn = _get_conn()
    cursor = conn.cursor()
    last_id = None
    q = """
    INSERT INTO answer_user (
        user_id, main_question_id, ml_question_id, answer_text,
        score_overall, score_relevance, score_clarity, score_structure,
        score_confidence, score_conciseness, created_at
    ) VALUES (%s, %s, NULL, %s, 0,0,0,0,0,0, %s)
    """
    now = datetime.now()
    try:
        cursor.execute(q, (user_id, main_question_id, answer_text, now))
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except (IntegrityError, DatabaseError) as e:
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()

def insert_ml_question(user_id: int, question_text: str) -> int:
    """Menyimpan pertanyaan ML (follow-up) baru ke tabel."""
    conn = _get_conn()
    cursor = conn.cursor()
    last_id = None
    query = "INSERT INTO ml_question (user_id, question_ml, created_at) VALUES (%s, %s, %s)"
    now = datetime.now()
    try:
        cursor.execute(query, (user_id, question_text, now))
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except DatabaseError as e:
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()


def insert_user_answer_ml(user_id: int, ml_question_id: int, answer_text: str) -> int:
    """Menyimpan jawaban user untuk pertanyaan ML (follow-up)."""
    conn = _get_conn()
    cursor = conn.cursor()
    last_id = None
    q = """
    INSERT INTO answer_user (
        user_id, main_question_id, ml_question_id, answer_text,
        score_overall, score_relevance, score_clarity, score_structure,
        score_confidence, score_conciseness, created_at
    ) VALUES (%s, NULL, %s, %s, 0,0,0,0,0,0, %s)
    """
    now = datetime.now()
    try:
        cursor.execute(q, (user_id, ml_question_id, answer_text, now))
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except (IntegrityError, DatabaseError) as e:
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()

def check_ml_question_exists(ml_question_id: int) -> bool:
    """Memeriksa apakah ID pertanyaan ML (follow-up) ada."""
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM ml_question WHERE id = %s", (ml_question_id,))
        row = cursor.fetchone()
        return row is not None
    finally:
        cursor.close()
        conn.close()
        
# ====================================================================
# FUNGSI UNTUK FINAL FEEDBACK (Disediakan user, dipertahankan)
# ====================================================================

def get_user_session_details(role_id: int, level_id: int) -> Dict[str, str]:
    """
    Mengambil nama Role dan Level dari ID-nya.
    """
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        r.role_name, 
        l.level_name 
    FROM ref_role r, ref_level l 
    WHERE r.id = %s AND l.id = %s;
    """
    cursor.execute(query, (role_id, level_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return {'role_name': result['role_name'], 'level_name': result['level_name']}
    else:
        return {'role_name': 'Unknown', 'level_name': 'Unknown'}


def get_all_answers_for_user_and_mq(user_id: int, main_question_id: int) -> List[Dict[str, str]]:
    """
    Mengambil semua Pertanyaan dan Jawaban untuk sesi wawancara, diurutkan berdasarkan waktu dibuat.
    """
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    
    q = """
    SELECT 
        COALESCE(mq.question, mlq.question_ml) AS question, 
        au.answer_text AS answer
    FROM answer_user au
    LEFT JOIN main_question mq ON au.main_question_id = mq.id
    LEFT JOIN ml_question mlq ON au.ml_question_id = mlq.id
    WHERE au.user_id = %s 
    AND (
        au.main_question_id IS NOT NULL AND au.main_question_id >= %s OR 
        au.ml_question_id IS NOT NULL AND mlq.user_id = %s
    )
    ORDER BY au.created_at ASC;
    """
    try:
        cursor.execute(q, (user_id, main_question_id, user_id))
        all_answers = cursor.fetchall()
        return all_answers
    finally:
        cursor.close()
        conn.close()


def save_final_report_to_db(report_data: Dict[str, Any]):
    """
    Menyimpan skor akhir dan naratif feedback ke dalam tabel answer_user 
    (baris jawaban utama pertama) untuk record sesi.
    
    💡 KOREKSI: Konversi skor metrik (0.0-5.0 dari LLM) ke INTEGER (TINYINT di DB).
    """
    conn = _get_conn()
    cursor = conn.cursor()
    
    q = """
    UPDATE answer_user
    SET 
        score_overall = %s,
        score_relevance = %s, 
        score_clarity = %s, 
        score_structure = %s, 
        score_confidence = %s, 
        score_conciseness = %s,
        feedback_narrative = %s 
    WHERE user_id = %s AND main_question_id = %s
    ORDER BY created_at ASC
    LIMIT 1;
    """
    
    try:
        # Ambil data dari Dictionary (dari LLM)
        scores = report_data.get('score_metrics', {})
        user_id = report_data['user_id']
        main_question_id = report_data['main_question_id']
        
        # --- 💡 PERBAIKAN KRITIS: Konversi Skor Metrik (0.0-5.0) ke INT (0-5) ---
        # Gunakan round() untuk pembulatan terdekat, lalu int() untuk casting ke integer
        score_relevance_int = int(round(scores.get('Relevansi', 0.0)))
        score_clarity_int = int(round(scores.get('Klaritas', 0.0)))
        score_structure_int = int(round(scores.get('Struktur', 0.0)))
        score_confidence_int = int(round(scores.get('Kepercayaan_Diri', 0.0)))
        score_conciseness_int = int(round(scores.get('Ringkas', 0.0)))

        # Mapping skor metrik ke kolom database yang sesuai
        cursor.execute(q, (
            report_data['score_overall'], 
            score_relevance_int,         
            score_clarity_int,           
            score_structure_int,         
            score_confidence_int,        
            score_conciseness_int,       
            report_data['feedback_narrative'],
            user_id, 
            main_question_id
        ))
        conn.commit()
    except DatabaseError as e:
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()