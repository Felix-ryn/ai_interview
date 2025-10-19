from google import genai
import os, json
from app.models.feedback_schema import ScoreMetrics
from app.models.feedback_schema import NlpGuardrails
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY tidak ditemukan")

client = genai.Client(api_key=API_KEY)

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
        # Panggil fungsi pembersihan JSON jika perlu, lalu parse
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