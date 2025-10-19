import mysql.connector
from datetime import datetime
# 💡 BARU: Import IntegrityError dan DatabaseError untuk penanganan rollback
from mysql.connector.errors import IntegrityError, DatabaseError 
from typing import List, Dict
from app.models.feedback_schema import FinalFeedback

# ====================================================================
# FUNGSI BARU UNTUK REF_ROLE DAN REF_LEVEL
# ====================================================================

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

# ====================================================================
# FUNGSI BARU UNTUK REGISTRASI USER
# ====================================================================

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
        # Periksa apakah ID role/level ada (optional, tapi baik untuk validasi)
        # Asumsikan validasi role/level ID sudah dilakukan di API atau Pydantic.
        
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
        
# ====================================================================
# FIX KONEKSI: Menggunakan konfigurasi Laragon 3307 yang sudah diverifikasi
# ====================================================================

def _get_conn():
    """Membuat koneksi ke database MySQL."""
    return mysql.connector.connect(
        user='root', 
        password='', 
        host='127.0.0.1', 
        database='tm_db', 
        port=3307, # PORT WAJIB 3307
        auth_plugin='mysql_native_password'
    )


def get_base_questions_by_names(role_name: str, level_name: str, limit: int = 2):
    """Mengambil pertanyaan dasar berdasarkan role dan level (case-insensitive)."""
    # Fix: Normalisasi input ke huruf kecil di Python
    normalized_role = role_name.lower()
    normalized_level = level_name.lower()
    
    # === DEBUG PRINT ===
    print(f"DEBUG DB: Mencari Role: '{normalized_role}', Level: '{normalized_level}'")
    
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    q = """
    SELECT mq.id, mq.question
    FROM main_question mq
    JOIN ref_role rr ON mq.ref_role_id = rr.id
    JOIN ref_level rl ON mq.ref_level_id = rl.id
    -- Fix: Menggunakan fungsi MySQL LOWER() pada kolom DB untuk case-insensitive
    WHERE LOWER(rr.role_name) = %s AND LOWER(rl.level_name) = %s 
    ORDER BY mq.id
    LIMIT %s
    """
    try:
        cursor.execute(q, (normalized_role, normalized_level, limit))
        rows = cursor.fetchall()
        print(f"DEBUG DB: Rows ditemukan: {len(rows)}") 
        return rows
    finally:
        cursor.close()
        conn.close()

def get_main_question_text_by_id(mq_id: int):
    """Mengambil teks pertanyaan utama (main_question) berdasarkan ID."""
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
    """Mengambil teks pertanyaan AI (ml_question) berdasarkan ID."""
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
    """Menyimpan jawaban user yang merujuk ke Pertanyaan Utama (Q1/Q2). MELAKUKAN ROLLBACK JIKA GAGAL."""
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
        # KRITIS: Rollback harus dipanggil jika terjadi kesalahan (FK atau Timeout)
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()

def insert_ml_question(user_id: int, question_text: str) -> int:
    """Menyimpan pertanyaan yang dihasilkan oleh AI (ML Question) dan mengembalikan ID-nya. MELAKUKAN ROLLBACK JIKA GAGAL."""
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
    """Menyimpan jawaban user yang merujuk ke Pertanyaan AI (Q3/Q4/Q5). MELAKUKAN ROLLBACK JIKA GAGAL."""
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
        # KRITIS: Rollback harus dipanggil jika terjadi kesalahan (FK atau Timeout)
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()

def check_ml_question_exists(ml_question_id: int) -> bool:
    """Memeriksa apakah ID Pertanyaan AI ada di tabel ml_question."""
    conn = _get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM ml_question WHERE id = %s", (ml_question_id,))
        row = cursor.fetchone()
        return row is not None
    finally:
        cursor.close()
        conn.close()


def get_user_answers_for_session(user_id: int, main_question_id: int) -> List[Dict]:
    """
    Mengambil semua jawaban user terkait satu sesi (dimulai dari main_question_id).
    Juga mengambil ground truth (question text) untuk pembanding NLP.
    """
    conn = _get_conn()
    cursor = conn.cursor(dictionary=True)
    
    q = """
    SELECT 
        au.answer_text, 
        COALESCE(mq.question, mlq.question_ml) AS question_text,
        -- Kita asumsikan ground_truth ada di tabel lain atau harus di-generate. 
        -- Untuk sementara, kita pakai question_text sebagai ground_truth semantik, 
        -- atau Anda harus buat kolom 'ground_truth_answer' di main_question/ml_question.
        COALESCE(mq.question, mlq.question_ml) AS ground_truth 
    FROM answer_user au
    LEFT JOIN main_question mq ON au.main_question_id = mq.id
    LEFT JOIN ml_question mlq ON au.ml_question_id = mlq.id
    WHERE au.user_id = %s AND (au.main_question_id = %s OR au.ml_question_id IN (
        SELECT id FROM ml_question WHERE user_id = %s -- Menangkap semua ml_question yang relevan
    )) 
    ORDER BY au.created_at
    """
    # Catatan: Logika pengambilan data sesi di atas perlu disesuaikan dengan skema database sesi yang pasti.
    try:
        cursor.execute(q, (user_id, main_question_id, user_id))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def save_feedback_results(report: FinalFeedback):
    """
    Menyimpan skor akhir dan naratif feedback ke dalam tabel answer_user.
    Biasanya hanya mengupdate baris yang telah selesai diwawancarai.
    """
    conn = _get_conn()
    cursor = conn.cursor()
    
    # Asumsi: Anda akan mengupdate baris 'answer_user' yang sesuai (mungkin yang terakhir/utama)
    # atau membuat tabel baru 'final_report'. Kita update saja baris yang relevan.
    q = """
    UPDATE answer_user
    SET 
        score_overall = %s,
        score_relevance = %s, 
        score_clarity = %s, 
        score_structure = %s, 
        score_confidence = %s, 
        score_conciseness = %s,
        feedback_narrative = %s -- Asumsi: Tambahkan kolom feedback_narrative di DB
    WHERE user_id = %s AND main_question_id = %s;
    """
    
    try:
        # Ambil data dari model Pydantic
        scores = report.score_metrics
        cursor.execute(q, (
            report.score_overall, scores.relevance, scores.clarity, scores.structure,
            scores.confidence, scores.conciseness, report.feedback_narrative,
            report.user_id, report.main_question_id
        ))
        conn.commit()
    except DatabaseError as e:
        conn.rollback() 
        raise e
    finally:
        cursor.close()
        conn.close()