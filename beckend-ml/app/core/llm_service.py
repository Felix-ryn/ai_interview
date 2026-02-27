# ===============================================================
# ✅ GOOGLE GEMINI (v2) EVALUATION ENGINE — STABLE VERSION
# ===============================================================
from google import genai
from google.genai.errors import APIError
import os, json, time
from typing import List, Dict, Any
from dotenv import load_dotenv

# ===============================================================
# 🔧 ENV CONFIGURATION
# ===============================================================
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY tidak ditemukan. Pastikan sudah diset di .env")

client = genai.Client(api_key=API_KEY)


# ===============================================================
# 🧩 HELPER: FUNGSI AMAN UNTUK MEMANGGIL GEMINI DENGAN RETRY
# ===============================================================
def safe_generate_content(model: str, contents: str, config: dict = None, retries: int = 3, delay: int = 2) -> str:
    """
    Wrapper aman untuk menangani error 503, timeout, atau APIError.
    """
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "503" in err or "UNAVAILABLE" in err or "deadline" in err.lower():
                print(f"⚠️ Gemini API error (attempt {attempt}/{retries}): {err}")
                if attempt < retries:
                    print(f"⏳ Retry dalam {delay} detik...")
                    time.sleep(delay)
                    continue
            # kalau bukan error koneksi/503, langsung raise
            print(f"❌ Error fatal Gemini: {err}")
            break
    return "⚠️ Maaf, model AI sedang tidak tersedia. Coba lagi nanti."


# ===============================================================
# 🧭 RUBRIK PENILAIAN
# ===============================================================
RUBRIC_CRITERIA = {
    "Relevansi": {"fokus_utama": "Kesesuaian jawaban terhadap konteks dan kebutuhan posisi.",
                  "metrik_teknis": "Kemampuan mengaitkan konsep teknis (MLOps, Interpretasi Model, Arsitektur Data) dengan studi kasus nyata."},
    "Klaritas": {"fokus_utama": "Kejelasan ide dan penggunaan istilah teknis yang tepat.",
                 "metrik_teknis": "Penggunaan istilah ML/DS konsisten dan mudah dipahami (Precision vs Recall, Bias vs Variance, dll)."},
    "Struktur": {"fokus_utama": "Kerapian alur berpikir dan organisasi jawaban.",
                 "metrik_teknis": "Penjelasan berurutan dari masalah → solusi → hasil."},
    "Kepercayaan_Diri": {"fokus_utama": "Keyakinan dan kejelasan dalam menyampaikan argumen teknis.",
                          "metrik_teknis": "Nada tegas, tapi berbasis pada substansi teknis kuat."},
    "Ringkas": {"fokus_utama": "Efisiensi menjawab tanpa bertele-tele.",
                "metrik_teknis": "Menjawab inti permasalahan tanpa pengulangan atau pengalihan topik."}
}


# ===============================================================
# ⚙️ 1. FUNGSI MENDAPATKAN SKOR MENTAH
# ===============================================================
async def get_raw_score_per_question(question: str, answer: str, role: str, level: str) -> float:
    json_schema = {
        "type": "object",
        "properties": {"score": {"type": "number", "description": "Skor dari 0.0 hingga 100.0"}},
        "required": ["score"]
    }

    prompt = f"""
    Anda adalah pewawancara AI untuk posisi {role} Level {level}.
    Evaluasilah jawaban berikut dan berikan skor dari 0.0 sampai 100.0 berdasarkan kedalaman teknis dan relevansi.

    Pertanyaan: "{question}"
    Jawaban: "{answer}"

    Output wajib berupa JSON sesuai skema: {{"score": <float>}}
    """

    try:
        text = safe_generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json", "response_schema": json_schema}
        )
        data = json.loads(text)
        score = float(data.get("score", 50.0))
        return max(0.0, min(100.0, score))
    except Exception as e:
        print(f"⚠️ Error saat menilai pertanyaan: {e}")
        return 50.0


# ===============================================================
# 📊 2. FUNGSI LAPORAN AKHIR
# ===============================================================
def generate_final_report(role: str, level: str, q_and_a_list: List[Dict[str, str]], final_weighted_score: float) -> Dict[str, Any]:
    context = "\n".join([f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}" for i, qa in enumerate(q_and_a_list)])
    prompt = f"""
    Anda evaluator AI profesional untuk posisi {role} level {level}.
    Kandidat memperoleh skor total {final_weighted_score:.2f}/100.

    Berdasarkan transkrip berikut, buat:
    1. JSON dengan 5 skor (Relevansi, Klaritas, Struktur, Kepercayaan_Diri, Ringkas) bernilai 0–5.
    2. Naratif evaluasi minimal 3 paragraf.

    --- TRANSKRIP ---
    {context}
    --- OUTPUT FORMAT ---
    ---JSON_START---
    {{JSON}}
    ---JSON_END---
    ---NARRATIVE_START---
    {{TEKS}}
    ---NARRATIVE_END---
    """

    fallback = {
        "score_overall": final_weighted_score,
        "feedback_narrative": "⚠️ Gagal menghasilkan laporan dari AI.",
        "score_metrics": {k: 3 for k in RUBRIC_CRITERIA},
        "detailed_metrics_list": [
            {"Aspek": k, **v, "Skor": 3} for k, v in RUBRIC_CRITERIA.items()
        ],
    }

    try:
        text = safe_generate_content("gemini-2.5-flash", prompt)
        js_start, js_end = text.find('---JSON_START---'), text.find('---JSON_END---')
        nv_start, nv_end = text.find('---NARRATIVE_START---'), text.find('---NARRATIVE_END---')

        json_text = text[js_start + 15:js_end].strip() if js_start != -1 and js_end != -1 else "{}"
        narrative = text[nv_start + 19:nv_end].strip() if nv_start != -1 and nv_end != -1 else "Tidak ada naratif."

        scores = json.loads(json_text)
        metrics, detailed = {}, []

        for key, crit in RUBRIC_CRITERIA.items():
            val = scores.get(key, 3)
            val = int(max(0, min(5, val if isinstance(val, (int, float)) else 3)))
            metrics[key] = val
            detailed.append({"Aspek": key, **crit, "Skor": val})

        return {
            "score_overall": final_weighted_score,
            "feedback_narrative": narrative,
            "score_metrics": metrics,
            "detailed_metrics_list": detailed,
        }

    except Exception as e:
        print(f"❌ Gagal membuat laporan akhir: {e}")
        return fallback


# ===============================================================
# 💬 3. FUNGSI PERTANYAAN LANJUTAN
# ===============================================================
def generate_followup_questions(role: str, level: str, base_q_and_answers: list, desired_count: int = 3):
    context = "\n".join([f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}" for i, qa in enumerate(base_q_and_answers)])
    prompt = f"""
    Anda pewawancara posisi {role} level {level}.
    Berdasarkan Q&A berikut, buat {desired_count} pertanyaan lanjutan yang relevan dalam format JSON array string.

    {context}
    """
    text = safe_generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json", "response_schema": {"type": "array", "items": {"type": "string"}}}
    )
    try:
        questions = json.loads(text)
        return questions[:desired_count] if isinstance(questions, list) else [f"Pertanyaan fallback #{i+1}" for i in range(desired_count)]
    except Exception as e:
        print("⚠️ Error parsing followup questions:", e)
        return [f"Pertanyaan fallback #{i+1}" for i in range(desired_count)]


# ===============================================================
# 🧩 4. FUNGSI FEEDBACK PER JAWABAN
# ===============================================================
def generate_feedback(role: str, level: str, q_and_a: list):
    feedback = []
    for qa in q_and_a:
        q, a = qa["question"], qa["answer"]
        prompt = f"Evaluasi jawaban berikut: '{a}' untuk pertanyaan: '{q}'. Berikan feedback singkat dan spesifik."
        text = safe_generate_content("gemini-2.5-flash", prompt)
        feedback.append({"question": q, "answer": a, "feedback_text": text})
    return feedback


# ===============================================================
# 🔢 5. FUNGSI EMBEDDING
# ===============================================================
def generate_embeddings(texts: list) -> list:
    """Menghasilkan embedding vektor teks."""
    try:
        resp = client.models.embed_content(
            model="text-embedding-004",
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return [e.embedding for e in resp.embeddings]
    except Exception as e:
        print("⚠️ Error generate_embeddings:", e)
        return []
