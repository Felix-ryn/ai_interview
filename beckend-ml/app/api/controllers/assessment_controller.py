# api/controllers/assessment_controller.py
from ..helpers.score_calculator import calculate_final_score
from ..services.ai_scoring_service import get_ai_scores
from ..services.assessment_service import (
    save_user_answer,
    get_assessment_state,
    update_assessment_state,
    generate_ml_question,
    insert_ml_question,
    get_main_question
)


async def submit_answer(request_data: dict):
    """
    Controller untuk menerima jawaban user, menyimpan ke DB,
    dan menentukan pertanyaan selanjutnya.
    """
    try:
        user_id = request_data.get("userId")
        answer = request_data.get("answer")

        if not user_id or answer is None:
            return {"error": "Data jawaban tidak lengkap."}, 400

        # 1. Simpan jawaban user
        save_user_answer(user_id, answer)

        # 2. Ambil status assessment user
        state = get_assessment_state(user_id)
        current_q = state.get("current_question", 0)
        ml_count = state.get("ml_question_count", 0)

        # Tentukan pertanyaan berikutnya
        next_q_number = current_q + 1

        next_question = None

        # 3. Logic ML Question hanya untuk pertanyaan ke-3,4,5
        if 3 <= next_q_number <= 5 and ml_count < 3:
            ml_question = generate_ml_question(user_id)
            insert_ml_question(user_id, ml_question)
            next_question = ml_question
            ml_count += 1
        else:
            # Ambil pertanyaan main
            next_question = get_main_question(next_q_number)

        # 4. Update state user
        update_assessment_state(user_id, next_q_number, ml_question_count=ml_count)

        return {
            "message": "Jawaban diterima.",
            "nextQuestion": next_question,
            "currentQuestionNumber": next_q_number
        }, 200

    except Exception as e:
        # Bisa ditambah logging untuk debugging
        return {"error": "Terjadi kesalahan server saat memproses jawaban."}, 500


async def submit_assessment(request_data: dict):
    """
    Controller untuk menghitung skor akhir assessment.
    """
    try:
        answers = request_data.get('answers')
        role_id = str(request_data.get('roleId'))
        level_id = str(request_data.get('levelId'))

        # Validasi
        if not answers or not role_id or not level_id:
            return {"error": "Data assessment tidak lengkap."}, 400

        # 1. Penilaian (Menghitung skor Si)
        raw_scores = await get_ai_scores(answers, role_id, level_id)

        # 2. Perhitungan skor akhir (pembobotan Wi)
        final_score = calculate_final_score(role_id, level_id, raw_scores)

        # 3. Kembalikan hasil
        return {
            "message": "Penilaian berhasil dihitung.",
            "roleId": role_id,
            "levelId": level_id,
            "rawScores": raw_scores,
            "finalScore": final_score
        }, 200

    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": "Terjadi kesalahan server saat memproses skor."}, 500
