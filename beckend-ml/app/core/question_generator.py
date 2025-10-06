# app/core/questions_generator.py

from typing import List

# Fungsi fallback / default untuk pertanyaan generatif AI
def generate_followup_from_base(base_q_and_answers: List[dict], desired_count: int = 3) -> List[str]:
    """
    base_q_and_answers: [{'question': '...', 'answer': '...'}, ...]
    Returns: List pertanyaan generatif (dummy/fallback)
    """
    followup_questions = []
    for i in range(desired_count):
        followup_questions.append(
            f"Pertanyaan lanjutan {i+1} berdasarkan jawaban Q1 dan Q2"
        )
    return followup_questions
