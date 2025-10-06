# app/core/llm_service.py
from google import genai
import os
import json
from dotenv import load_dotenv
from app.core.question_generator import generate_followup_from_base  # pastikan sudah ada di core

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY tidak ditemukan di environment")

client = genai.Client(api_key=API_KEY)

def generate_followup_questions(role: str, level: str, base_q_and_answers: list, desired_count: int = 3):
    """
    Menghasilkan pertanyaan lanjutan AI. 
    Jika LLM gagal atau output tidak valid, gunakan fallback dari questions_generator.py
    """
    # Bangun context prompt
    context_lines = []
    for i, qa in enumerate(base_q_and_answers, start=1):
        context_lines.append(f"Q{i}: {qa.get('question')}")
        context_lines.append(f"A{i}: {qa.get('answer')}")
    context_text = "\n".join(context_lines)

    prompt = f"""
Konteks: kamu adalah pembuat pertanyaan interview untuk posisi {role} (level: {level}).
Berikut adalah pertanyaan awal dan jawaban user:
{context_text}

Tugas: Buat {desired_count} pertanyaan lanjutan yang:
- Relevan dan menindaklanjuti jawaban user.
- Singkat, jelas, dan mendorong user memberi jawaban mendetail.
Output only: JSON array of strings. Contoh:
["Pertanyaan 3 ...?", "Pertanyaan 4 ...?", "Pertanyaan 5 ...?"]
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()

        if not text:
            print("⚠️ Response LLM kosong")
            return generate_followup_from_base(base_q_and_answers, desired_count)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed][:desired_count]
            else:
                # fallback jika LLM output bukan list
                return generate_followup_from_base(base_q_and_answers, desired_count)
        except json.JSONDecodeError:
            # fallback ekstrak baris pertanyaan dari text
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            results = [ln for ln in lines if ln.endswith("?") or len(ln) > 10]
            if results:
                return results[:desired_count]
            else:
                # fallback ultimate
                return generate_followup_from_base(base_q_and_answers, desired_count)

    except Exception as e:
        print("⚠️ Error memanggil LLM:", e)
        # fallback default jika LLM gagal
        return generate_followup_from_base(base_q_and_answers, desired_count)
