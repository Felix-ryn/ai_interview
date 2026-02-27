# api/services/ai_scoring_service.py
import random
from ..config.scoring_matrix import get_assessment_rubric

# Anda akan menggunakan library seperti 'google-genai' atau 'requests' di sini
# Contoh ini menggunakan simulasi hasil.

async def get_ai_scores(answers: dict, role_id: str, level_id: str) -> dict:
    """
    Memanggil model AI untuk menilai setiap jawaban dan mengembalikan skor mentah (Si).
    
    answers: { 'Q1': 'Jawaban user Q1', ... }
    """
    rubric = get_assessment_rubric(role_id, level_id)
    
    if not rubric:
        raise ValueError(f"Rubrik penilaian untuk Role ID {role_id} dan Level ID {level_id} tidak ditemukan.")

    # --- Di sini Anda akan membuat Prompt untuk AI ---
    # Prompt harus mencakup:
    # 1. Jawaban user
    # 2. Pertanyaan yang relevan (Ambil dari database/CSV)
    # 3. Kriteria Penilaian (rubric['description'] dan rubric['keywords'])

    # --- SIMULASI PANGGILAN AI (HARUS DIGANTI DENGAN LOGIKA NYATA) ---
    
    print(f"Menggunakan rubrik: {rubric['description']}")
    
    # Asumsikan AI mengembalikan skor acak yang disimulasikan
    raw_scores = {}
    for q_key in answers.keys():
        # Simulasi skor 0-100. AI Anda harus mengembalikan nilai nyata!
        raw_scores[q_key] = random.randint(50, 100)
    
    # Contoh untuk memastikan 5 pertanyaan selalu ada skornya
    if len(raw_scores) < 5:
        # Tambahkan skor untuk pertanyaan AI (Q3, Q4, Q5) jika belum ada
        pass 
        
    # Asumsi 5 jawaban selalu dikirim dan dinilai
    return raw_scores