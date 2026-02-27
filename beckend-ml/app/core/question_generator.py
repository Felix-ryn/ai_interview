from typing import List, Dict
from sqlalchemy.orm import Session

from app.core.llm_service import (
    generate_followup_questions,
    generate_feedback
)

from app.core.db_connector import (
    insert_ml_question,
    insert_user_answer_ml,
    get_main_question_text_by_id,
    get_ml_question_text_by_id,
    get_all_ml_questions_for_user
)


def _normalize_text(s: str) -> str:
    """Normalisasi sederhana untuk compare (trim + collapse spaces)."""
    if s is None:
        return ""
    return " ".join(s.strip().split())


def generate_followup_from_base(user_id: int, role: str, level: str, answers: list, db: Session = None):
    """
    Generate maksimal 3 pertanyaan AI (pertanyaan ke-3, ke-4, ke-5).
    - Jika user sudah punya >=3 pertanyaan ML di DB -> jangan generate ulang, langsung kembalikan yang ada.
    - Jika user punya <3 -> generate hanya sisa yang diperlukan.
    - Basis untuk generate:
        * Jika ada jawaban ML (ml_question_id != None) -> gunakan jawaban ML sebagai konteks.
        * Jika belum ada jawaban ML -> gunakan jawaban main_question (jawaban awal) sebagai konteks.
    """

    # ------------- 0) Ambil existing ML questions untuk user -------------
    existing_ml_rows = get_all_ml_questions_for_user(user_id) or []
    # pastikan urut berdasarkan id asc (paling awal terlahir pertama)
    existing_count = len(existing_ml_rows)

    # Jika sudah ada 3 atau lebih ML questions, kembalikan tiga pertama (tidak generate ulang)
    if existing_count >= 3:
        existing_three = existing_ml_rows[:3]
        return {
            "generated_questions": [r["question_ml"] for r in existing_three],
            "generated_questions_ids": [r["id"] for r in existing_three],
            "feedback": [],
            "message": "Pertanyaan AI sudah tersedia (tidak digenerate ulang)."
        }

    # ------------- 1) Filter jawaban ML dari parameter answers -------------
    ml_answers = [a for a in answers if getattr(a, "ml_question_id", None) is not None]

    base_q_and_answers: List[Dict[str, str]] = []

    # ------------- 2) Tentukan konteks dasar untuk generate -------------
    if ml_answers:
        # Gunakan jawaban dari pertanyaan ML yang sudah ada sebagai konteks
        for ans in ml_answers:
            # Ambil teks pertanyaan ML dari DB (jawaban biasanya hanya menyimpan ml_question_id)
            qtext = get_ml_question_text_by_id(int(ans.ml_question_id))
            if qtext:
                base_q_and_answers.append({
                    "question": qtext,
                    "answer": ans.answer_text
                })
    else:
        # Belum ada ML answers -> gunakan jawaban main_question sebagai konteks
        for ans in answers:
            if getattr(ans, "main_question_id", None) is None:
                continue
            qtext = get_main_question_text_by_id(int(ans.main_question_id))
            if qtext:
                base_q_and_answers.append({
                    "question": qtext,
                    "answer": ans.answer_text
                })

    # ------------- 3) Hitung berapa yang perlu digenerate -------------
    to_generate = 3 - existing_count
    generated_questions: List[str] = []
    generated_ids: List[int] = []

    if to_generate <= 0:
        # seharusnya tidak masuk sini karena ditangani di atas
        existing_three = existing_ml_rows[:3]
        generated_questions = [r["question_ml"] for r in existing_three]
        generated_ids = [r["id"] for r in existing_three]
    else:
        # Panggil LLM untuk generate sisa pertanyaan
        try:
            raw = generate_followup_questions(
                role=role,
                level=level,
                base_q_and_answers=base_q_and_answers,
                desired_count=to_generate
            )
        except Exception as e:
            # fallback: log dan kosongkan
            print("LLM generate_followup_questions error:", e)
            raw = []

        # Pastikan list
        if not isinstance(raw, list):
            raw = list(raw) if raw else []

        # Normalisasi & deduplikasi (hindari pertanyaan yang sama antar generated dan existing)
        existing_texts = {_normalize_text(r["question_ml"]): r["id"] for r in existing_ml_rows}
        cleaned_generated = []
        for item in raw:
            t = _normalize_text(item)
            if not t:
                continue
            if t in existing_texts:
                # sudah ada, jangan tambahkan duplicate teks
                continue
            if t in {_normalize_text(x) for x in cleaned_generated}:
                # duplicate di hasil LLM itu sendiri
                continue
            cleaned_generated.append(item)

        # Hanya ambil sebanyak to_generate (sudah memastikan tidak sama dg existing)
        cleaned_generated = cleaned_generated[:to_generate]

        # Simpan ke DB dan kumpulkan ID (dengan cek exist di insert_ml_question)
        for q in cleaned_generated:
            try:
                ml_id = insert_ml_question(user_id, q)
            except Exception as e:
                print("insert_ml_question failed:", e)
                # skip jika gagal, lanjutkan yang lain
                continue
            if ml_id:
                generated_ids.append(ml_id)
                generated_questions.append(q)

        # Jika ada existing, gabungkan existing (urut) dengan newly generated - tapi batasi total 3
        if existing_count > 0:
            existing_questions = [r["question_ml"] for r in existing_ml_rows]
            existing_ids = [r["id"] for r in existing_ml_rows]
            # Gabungkan, jaga urutan: existing (awal) kemudian newly generated
            all_qs = existing_questions + generated_questions
            all_ids = existing_ids + generated_ids
            # ambil maksimum 3 pertama
            generated_questions = all_qs[:3]
            generated_ids = all_ids[:3]
        else:
            # Tidak ada existing, hanya hasil generated (maks 3 karena slice di atas)
            generated_questions = generated_questions[:3]
            generated_ids = generated_ids[:3]

    # ------------- 4) Generate feedback untuk konteks (opsional) -------------
    feedbacks = []
    if callable(generate_feedback):
        try:
            # generate_feedback expects q_and_a param name perhaps; be tolerant
            feedbacks = generate_feedback(role=role, level=level, q_and_a=base_q_and_answers)
        except TypeError:
            try:
                feedbacks = generate_feedback(role, level, base_q_and_answers)
            except Exception as e:
                print("generate_feedback failed:", e)
                feedbacks = []
        except Exception as e:
            print("generate_feedback failed:", e)
            feedbacks = []

    return {
        "generated_questions": generated_questions,
        "generated_questions_ids": generated_ids,
        "feedback": feedbacks,
        "message": "Berhasil generate pertanyaan AI (maks 3) dan menyimpan yang diperlukan."
    }
