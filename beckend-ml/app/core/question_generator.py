from app.core.llm_service import generate_followup_questions, generate_feedback
from app.core.db_connector import insert_ml_question, insert_user_answer_ml, get_main_question_text_by_id
from sqlalchemy.orm import Session

def generate_followup_from_base(user_id: int, role: str, level: str, answers: list, db: Session):
    """
    Generate pertanyaan AI lanjutan berdasarkan jawaban user sebelumnya.
    """
    base_q_and_answers = []
    for ans in answers:
        question_text = get_main_question_text_by_id(ans.main_question_id, db)
        base_q_and_answers.append({'question': question_text, 'answer': ans.answer_text})

    # PANGGIL LLM / AI SEBENARNYA
    generated_questions = generate_followup_questions(role, level, base_q_and_answers, desired_count=3)

    # Simpan pertanyaan AI ke DB
    generated_ids = []
    for q in generated_questions:
        ml_id = insert_ml_question(user_id, q, db)
        generated_ids.append(ml_id)

    # Generate feedback AI untuk jawaban dasar
    feedbacks = generate_feedback(role, level, base_q_and_answers)

    return {
        "generated_questions": generated_questions,
        "generated_questions_ids": generated_ids,
        "feedback": feedbacks,
        "message": "Berhasil generate pertanyaan AI dan feedback."
    }
