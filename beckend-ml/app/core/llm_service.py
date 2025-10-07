from google import genai
import os, json
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
