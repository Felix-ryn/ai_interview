from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import traceback
import asyncio 

# 💡 Import skema yang dibutuhkan (Pastikan FinalFeedbackOut yang baru terimpor)
from models.schemas import FinalFeedbackRequest, FinalFeedbackOut 
# 💡 Import fungsi logic dan database
from core.llm_service import generate_final_report, get_raw_score_per_question 
# 💡 Asumsi: File ini ada dan berisi fungsi calculate_final_score
from api.helpers.score_calculator import calculate_final_score 
from core.db_connector import get_all_answers_for_user_and_mq, get_user_session_details, save_final_report_to_db

# Prefix untuk endpoint ini adalah /api/v1/feedback
router = APIRouter(prefix="/v1", tags=["Feedback"])

# Catatan: Jumlah total Q&A diasumsikan 5 (2 base + 3 follow-up) untuk laporan final
REQUIRED_Q_A_COUNT = 5 

@router.post("/feedback", response_model=FinalFeedbackOut, summary="Memproses Evaluasi Akhir dan Mendapatkan Laporan Hasil Wawancara")
async def get_final_feedback(payload: FinalFeedbackRequest):
    """
    Menerima ID sesi, menghitung skor mentah (S_i), menghitung skor akhir berbobot (W_i * S_i),
    dan menghasilkan laporan naratif final.
    """
    try:
        # 1. Ambil semua Jawaban (Main & AI Follow-up) dari Database
        answers: List[Dict[str, str]] = get_all_answers_for_user_and_mq(
            payload.user_id,
            payload.main_question_id
        )
        
        # Periksa jumlah jawaban
        if not answers or len(answers) < REQUIRED_Q_A_COUNT: 
            raise HTTPException(
                status_code=400,
                detail=f"Jawaban tidak lengkap. Minimal {REQUIRED_Q_A_COUNT} Q&A diperlukan untuk laporan final ({len(answers)} ditemukan)."
            )

        # 2. Ambil detail sesi (Role Name dan Level Name)
        session_details = get_user_session_details(
            payload.role_id,
            payload.level_id
        )

        # 3. Penilaian Asinkron (Menghitung S_i untuk setiap jawaban)
        # LLM memberikan Skor Mentah (S_i) per pertanyaan (Q1, Q2, Q3, Q4, Q5)
        scoring_tasks = [
            get_raw_score_per_question(
                question=qa['question'], 
                answer=qa['answer'], 
                role=session_details['role_name'],
                level=session_details['level_name']
            ) for qa in answers
        ]
        
        raw_scores_list = await asyncio.gather(*scoring_tasks)
        
        # Konversi raw_scores_list ke format dictionary {Q1: S1, Q2: S2, ...}
        # Gunakan nama pertanyaan sebagai kunci, atau urutan Q1, Q2, ...
        raw_scores_dict: Dict[str, float] = {f'Q{i+1}': score for i, score in enumerate(raw_scores_list)}

        
        # 4. Perhitungan Skor Akhir (Mengaplikasikan Bobot W_i * S_i)
        role_id_str = str(payload.role_id)
        level_id_str = str(payload.level_id)
        
        final_weighted_score = calculate_final_score(
            role_id=role_id_str,
            level_id=level_id_str,
            raw_scores=raw_scores_dict
        )
        
        
        # 5. Panggil LLM untuk menghasilkan 5 Metrik Kualitatif dan Laporan Naratif Final
        # report_data kini berisi: score_overall, feedback_narrative, score_metrics, detailed_metrics_list
        report_data = generate_final_report(
            role=session_details['role_name'],
            level=session_details['level_name'],
            q_and_a_list=answers,
            final_weighted_score=final_weighted_score # Kirim skor berbobot ke LLM untuk konteks naratif
        )
        
        # 6. Susun Data Output Final
        final_output = {
            "user_id": payload.user_id,
            "main_question_id": payload.main_question_id,
            # FIX: Mengganti 'final_weighted_score' menjadi 'score_overall'
            "score_overall": final_weighted_score, 
            "raw_scores_per_question": raw_scores_dict,
            "feedback_narrative": report_data['feedback_narrative'],
            "score_metrics": report_data['score_metrics'],
            "detailed_metrics_list": report_data['detailed_metrics_list']
        }

        # 7. Simpan hasil laporan final ke database
        # save_final_report_to_db(final_output)

        # 8. Kembalikan respons
        return FinalFeedbackOut(**final_output)

    except HTTPException:
        # Pengecualian yang dilempar dari dalam blok try, misalnya dari validasi jumlah jawaban
        raise
    except Exception as e:
        print(f"Error in /v1/feedback: {e}")
        traceback.print_exc()
        # Jika LLM atau proses skoring gagal
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan server saat memproses feedback final: {str(e)}"
        )