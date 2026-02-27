# app/helpers/ai_service.py

from typing import List, Dict

def generate_followup_from_base(user_id: int, role: str, level: str, answers: List[str]) -> Dict[str, List[str]]:
    """
    Generate pertanyaan ML (follow-up) berdasarkan jawaban sebelumnya.
    Dummy function ini bisa diganti dengan integrasi AI / LLM di kemudian hari.

    Args:
        user_id (int): ID user
        role (str): Nama role user
        level (str): Nama level user
        answers (List[str]): List jawaban sebelumnya

    Returns:
        Dict[str, List[str]]: Dictionary dengan key 'generated_questions' berisi list pertanyaan ML
    """

    # Contoh logika sederhana: buat 3 pertanyaan ML berdasarkan jawaban sebelumnya
    # Bisa dikembangkan lebih lanjut, misal menggunakan NLP atau AI
    generated_questions = []

    if answers:
        for i, ans in enumerate(answers[-3:], 1):  # ambil 3 jawaban terakhir
            generated_questions.append(f"Pertanyaan ML {i} berdasarkan jawaban: {ans}")
    else:
        # Jika belum ada jawaban, buat pertanyaan default
        generated_questions = [
            "Pertanyaan ML 1: Ceritakan pengalaman Anda terkait topik ini.",
            "Pertanyaan ML 2: Bagaimana pendekatan Anda dalam menghadapi situasi tersebut?",
            "Pertanyaan ML 3: Apa kendala yang biasanya Anda temui?"
        ]

    return {"generated_questions": generated_questions}
