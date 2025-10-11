import mysql.connector
from datetime import datetime
# 💡 BARU: Import IntegrityError dan DatabaseError untuk penanganan rollback
from mysql.connector.errors import IntegrityError, DatabaseError 

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
