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
# 💡 PERUBAHAN BARU: DEFINISI RUBRIK PENILAIAN STATIS
# Rubrik ini menyediakan deskripsi untuk kolom "Fokus Utama" dan "Metrik Teknis" 
# yang sebelumnya terisi N/A di frontend.
# ======================================================================

RUBRIC_CRITERIA = {
    "Relevansi": {
        "fokus_utama": "Kesesuaian jawaban kandidat terhadap inti dan konteks pertanyaan, khususnya persyaratan senioritas.",
        "metrik_teknis": "Mapping konsep teknis (MLOps, Interpretasi Model, Arsitektur Data) ke domain masalah yang spesifik; Hindari jawaban terlalu umum."
    },
    "Klaritas": {
        "fokus_utama": "Kejelasan artikulasi ide, alur pikir, dan penggunaan diksi yang profesional.",
        "metrik_teknis": "Penggunaan terminologi Data Science/ML yang tepat dan konsisten (misalnya, perbedaan antara Bias/Variance, Precision/Recall); Jawaban mudah dipahami."
    },
    "Struktur": {
        "fokus_utama": "Organisasi jawaban yang logis, mudah diikuti, dan komprehensif (misalnya, menggunakan pola STAR atau Pendekatan-Solusi-Hasil).",
        "metrik_teknis": "Pemisahan masalah, solusi, implementasi, dan hasil (jika relevan); Alur yang koheren untuk studi kasus teknis."
    },
    "Kepercayaan_Diri": {
        "fokus_utama": "Tingkat keyakinan dalam menyampaikan jawaban dan kemampuan mempertahankan argumen teknis.",
        "metrik_teknis": "Nada suara yang tegas dan bahasa non-verbal yang mendukung; Kepercayaan diri harus didukung oleh substansi teknis yang kuat."
    },
    "Ringkas": {
        "fokus_utama": "Efisiensi dan ketepatan dalam durasi jawaban; Menyampaikan inti tanpa bertele-tele dan fokus pada poin krusial.",
        "metrik_teknis": "Keseimbangan antara detail teknis yang cukup dan penyampaian yang singkat; Tidak mengulang poin atau mengalihkan pembicaraan."
    }
}


# ======================================================================
# 🟢 FUNGSI KOREKSI: GENERATE FINAL REPORT
# Diperbarui untuk mengintegrasikan skor LLM dengan RUBRIC_CRITERIA.
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
    # Diperbarui untuk menyertakan detailed_metrics_list yang kosong atau default
    fallback_data = {
        "score_overall": 50.0,
        "feedback_narrative": "Laporan akhir gagal dihasilkan karena masalah koneksi AI atau format data.",
        "score_metrics": {
            "Relevansi": 3, "Klaritas": 3, "Struktur": 3, "Kepercayaan_Diri": 3, "Ringkas": 3
        },
        # Fallback list untuk Matriks Penilaian Terperinci
        "detailed_metrics_list": [
            {"Aspek": k, "Fokus_Utama": v['fokus_utama'], "Metrik_Evaluasi_Teknis": v['metrik_teknis'], "Skor": 3} 
            for k, v in RUBRIC_CRITERIA.items()
        ],
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
        
        # 4. Membangun List Metrik Terperinci (Gabungan Skor LLM + Rubrik Statis)
        detailed_metrics_list = []
        # Gunakan skor dari LLM (parsed_scores) untuk mengisi Rubrik
        for metric_name, criteria in RUBRIC_CRITERIA.items():
            # Menggunakan .get() dan memastikan skor adalah integer 0-5
            score = parsed_scores.get(metric_name)
            if isinstance(score, (int, float)):
                 score_int = int(round(score)) if isinstance(score, float) else score
                 # Memastikan skor berada dalam rentang 0-5
                 score_int = max(0, min(5, score_int)) 
            else:
                 score_int = 0 # Default jika LLM gagal memberikan skor untuk aspek ini

            detailed_metrics_list.append({
                "Aspek": metric_name,
                "Fokus_Utama": criteria['fokus_utama'],
                "Metrik_Evaluasi_Teknis": criteria['metrik_teknis'],
                "Skor": score_int # Menggunakan skor dinamis
            })

        # 5. Membangun Struktur Output Final
        # Menggunakan .get() untuk keamanan jika 'score_overall' hilang
        score_overall = parsed_scores.get("score_overall", 0.0) 
        
        # Pisahkan metrik 5 aspek dari dictionary parsed_scores
        score_metrics_data = {k: v for k, v in parsed_scores.items() if k != 'score_overall'}

        report_data = {
            "score_overall": score_overall, 
            "feedback_narrative": narrative_text,
            "score_metrics": score_metrics_data, # Hanya berisi 5 metrik detil (Relevansi, dll.)
            "detailed_metrics_list": detailed_metrics_list, # <<< DATA BARU UNTUK FRONTEND
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
# (Tetap sama seperti yang Anda berikan, hanya disalin untuk kelengkapan file)
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
