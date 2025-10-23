from google import genai
from google.genai.errors import APIError 
import os, json
from typing import List, Dict, Any

# Pastikan Pydantic models diimpor untuk type-hinting
from app.models.feedback_schema import ScoreMetrics, NlpGuardrails 
from dotenv import load_dotenv

load_dotenv()

# Gunakan os.getenv untuk mendapatkan API Key
API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY tidak ditemukan") 

client = genai.Client(api_key=API_KEY)

# ======================================================================
# 🟢 FUNGSI KOREKSI: GENERATE FINAL REPORT
# Tone diubah menjadi "konstruktif" dan metrik skor (0-5) diubah menjadi INTEGER 
# untuk memastikan kompatibilitas dengan kolom TINYINT di DB.
# ======================================================================

def generate_final_report(
    role: str, 
    level: str, 
    q_and_a_list: List[Dict[str, str]], 
    user_id: int, 
    main_question_id: int
) -> Dict[str, Any]:
    """
    Memproses semua Q&A sesi dan menghasilkan laporan akhir serta metrik penilaian menggunakan Gemini.
    """
    
    # 1. Siapkan Konteks Q&A
    context_lines = []
    for i, qa in enumerate(q_and_a_list, start=1):
        context_lines.append(f"Q{i}: {qa.get('question')}")
        context_lines.append(f"A{i}: {qa.get('answer')}")
    context_text = "\n".join(context_lines)

    # 2. Prompting untuk Laporan Akhir (Tone Konstruktif)
    prompt = f"""
    Anda adalah penilai wawancara AI yang **ahli, profesional, dan konstruktif** untuk peran {role} Level {level}. 
    Tugas Anda adalah mengevaluasi kinerja kandidat secara **objektif dan memberikan umpan balik yang seimbang**.
    Berikut adalah transkrip lengkap Pertanyaan (Q) dan Jawaban (A):

    --- TRANSKRIP Q&A ---
    {context_text}
    --- END TRANSKRIP ---

    Tugas Anda adalah memberikan penilaian menyeluruh.
    
    LANGKAH 1: Berikan Skor Akhir dan Matriks Detil.
    Berikan skor (0.0 - 100.0) untuk 'score_overall' dan 5 metrik detil (0-5) dalam format JSON murni. 
    Skor metrik harus menggunakan kunci bahasa Indonesia yang tepat: 'Relevansi', 'Klaritas', 'Struktur', 'Kepercayaan_Diri', 'Ringkas'.
    Catatan: Gunakan seluruh rentang skor (0 hingga 5), jangan hanya 0 atau 5, untuk mencerminkan nuansa kinerja.

    JSON SCHEMA WAJIB:
    {{
        "score_overall": <float 0.0-100.0>,
        "Relevansi": <integer 0-5>,
        "Klaritas": <integer 0-5>,
        "Struktur": <integer 0-5>,
        "Kepercayaan_Diri": <integer 0-5>,
        "Ringkas": <integer 0-5>
    }}
    
    LANGKAH 2: Buat Naratif Feedback.
    Tulis laporan naratif komprehensif, minimal 3 paragraf.
    - Paragraf 1: Ringkasan skor keseluruhan.
    - Paragraf 2: Analisis Kekuatan Utama DAN Area Peningkatan (gabungkan keduanya untuk narasi yang seimbang).
    - Paragraf 3: Kesimpulan dan Saran Spesifik untuk langkah selanjutnya.

    Output Anda HARUS dalam format:
    ---JSON_START---
    {{JSON DARI LANGKAH 1}}
    ---JSON_END---

    ---NARRATIVE_START---
    {{NARATIF DARI LANGKAH 2}}
    ---NARRATIVE_END---
    """

    # Struktur Fallback Data (untuk kasus error API atau parsing)
    fallback_data = {
        "score_overall": 50.0,
        "feedback_narrative": "Laporan akhir gagal dihasilkan karena masalah koneksi AI atau format data.",
        # Menggunakan integer 3 sebagai fallback untuk skor 0-5
        "score_metrics": {
            "Relevansi": 3, "Klaritas": 3, "Struktur": 3, "Kepercayaan_Diri": 3, "Ringkas": 3
        },
        "user_id": user_id, 
        "main_question_id": main_question_id 
    }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        
        # 3. Parsing Output (JSON dan Naratif)
        
        # Ekstraksi JSON (Skor)
        json_start = text.find('---JSON_START---') + len('---JSON_START---')
        json_end = text.find('---JSON_END---')
        json_text = text[json_start:json_end].strip()
        
        # Ekstraksi Naratif
        narrative_start = text.find('---NARRATIVE_START---') + len('---NARRATIVE_START---')
        narrative_end = text.find('---NARRATIVE_END---')
        narrative_text = text[narrative_start:narrative_end].strip()
        
        parsed_scores = json.loads(json_text)

        # 4. Membangun Struktur Output Final
        report_data = {
            # pop digunakan untuk memisahkan score_overall dari metrik 5 aspek
            "score_overall": parsed_scores.pop("score_overall"), 
            "feedback_narrative": narrative_text,
            "score_metrics": parsed_scores, # Hanya berisi 5 metrik detil (Relevansi, dll.)
            "user_id": user_id, 
            "main_question_id": main_question_id 
        }
        
        # Validasi kunci
        expected_keys = ["Relevansi", "Klaritas", "Struktur", "Kepercayaan_Diri", "Ringkas"]
        if not all(k in report_data['score_metrics'] for k in expected_keys):
             print("JSON metrik LLM tidak memiliki semua kunci yang diharapkan. Menggunakan fallback.")
             return fallback_data

        return report_data
        
    except (APIError, json.JSONDecodeError, ValueError, Exception) as e:
        print(f"FATAL Error generating or parsing final report from Gemini: {e}")
        return fallback_data


# ======================================================================
# FUNGSI-FUNGSI LLM LAIN
# ======================================================================

def generate_followup_questions(role: str, level: str, base_q_and_answers: list, desired_count: int = 3):
    """
    Generate pertanyaan lanjutan AI menggunakan Gemini.
    """
    context_lines = []
    for i, qa in enumerate(base_q_and_answers, start=1):
        context_lines.append(f"Q{i}: {qa.get('question')}")
        context_lines.append(f"A{i}: {qa.get('answer')}")
    context_text = "\n".join(context_lines)

    prompt = f"""
Konteks: kamu adalah pewawancara untuk posisi {role} (level {level}).
Berikut jawaban user:
{context_text}

Buat {desired_count} pertanyaan lanjutan yang relevan dan jelas.
Output: JSON array of strings.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()

        # Coba bersihkan karakter sebelum dan sesudah JSON
        start = text.find('[')
        end = text.rfind(']') + 1
        if start == -1 or end == -1:
            raise ValueError("JSON tidak ditemukan di response")

        json_text = text[start:end]
        parsed = json.loads(json_text)

        # Pastikan list dan potong sesuai desired_count
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed][:desired_count]
        else:
            raise ValueError("Response tidak berupa list")

    except Exception as e:
        print("Error generate_followup_questions:", e)
        # fallback masih ada tapi hanya jika API gagal
        return [f"Pertanyaan fallback AI #{i+1}" for i in range(desired_count)]

def generate_feedback(role: str, level: str, q_and_a: list):
    """
    Generate feedback AI untuk jawaban user.
    """
    feedback_list = []
    for item in q_and_a:
        question = item.get("question")
        answer = item.get("answer")
        prompt = f"Evaluasi jawaban berikut: {answer} untuk pertanyaan: {question}. Berikan feedback singkat, jelas, dan relevan."

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            fb_text = response.text.strip()
        except Exception as e:
            print("Error generate_feedback:", e)
            fb_text = "Feedback tidak tersedia"

        feedback_list.append({
            "question": question,
            "answer": answer,
            "feedback_text": fb_text
        })

    return feedback_list

def generate_embeddings(texts: list) -> list:
    """Menghasilkan embedding (vektor) untuk satu atau beberapa teks."""
    # Gunakan model embedding Gemini
    response = client.models.embed_content(
        model="text-embedding-004", # Model embedding yang kuat
        content=texts,
        task_type="RETRIEVAL_DOCUMENT"
    )
    # response.embedding adalah list of lists, kita hanya perlu list of vectors
    return [e.embedding for e in response.embeddings]


async def generate_llm_score(user_answer: str, question: str) -> ScoreMetrics:
    """
    Menghasilkan skor matriks 5 aspek awal dari LLM.
    LLM diprompt untuk menghasilkan JSON yang sesuai dengan ScoreMetrics.
    """
    prompt = f"""
    Anda adalah penilai ahli. Evaluasi jawaban user berikut untuk pertanyaan: '{question}'.
    Jawaban User: "{user_answer}"
    
    Berikan skor (0-100) untuk 5 aspek: 
    1. relevance (Kesesuaian dengan pertanyaan)
    2. clarity (Kejelasan penyampaian)
    3. structure (Struktur jawaban, misal STAR)
    4. confidence (Tingkat keyakinan)
    5. conciseness (Keringkasan)
    
    Output: JSON objek murni yang memetakan aspek ke skor (integer 0-100).
    Contoh: {{"relevance": 85, "clarity": 70, "structure": 90, "confidence": 75, "conciseness": 80}}
    """
    
    # Gunakan model yang mampu JSON output
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    try:
        json_text = response.text.strip()
        parsed_data = json.loads(json_text)
        return ScoreMetrics(**parsed_data)
    except Exception as e:
        print(f"Error parsing LLM Score JSON: {e}")
        # Fallback ke skor default (misal 50) jika parsing gagal
        return ScoreMetrics(relevance=50, clarity=50, structure=50, confidence=50, conciseness=50)

async def generate_feedback_narrative(
    llm_scores: ScoreMetrics, 
    nlp_metrics: NlpGuardrails, 
    final_score: float, 
    role: str
) -> str:
    """
    Menyusun feedback naratif yang kaya, menggabungkan skor subjektif dan metrik NLP objektif.
    """
    
    # Gunakan metrik terstruktur sebagai konteks dalam prompt
    context = f"""
    Skor LLM (0-100): {llm_scores.model_dump_json()}
    Metrik Objektif NLP: Cosine Sim. {nlp_metrics.cosine_similarity:.2f}, Filler Ratio {nlp_metrics.filler_ratio:.2f}, STAR Detected: {nlp_metrics.is_star_detected}
    Skor Final Terkalibrasi: {final_score:.2f}/100
    """

    prompt = f"""
    Berdasarkan konteks dan metrik penilaian berikut, susun feedback naratif profesional untuk kandidat {role}.
    
    1. Mulai dengan rangkuman skor final.
    2. Sorot area kekuatan utama.
    3. Berikan saran spesifik untuk perbaikan, fokus pada aspek yang nilainya rendah (misalnya, jika clarity rendah, sebutkan perlunya mengurangi filler words).
    
    Konteks:
    {context}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()
