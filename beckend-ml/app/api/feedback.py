from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import traceback

# 💡 Import skema yang dibutuhkan
from models.schemas import FinalFeedbackRequest, FinalFeedbackOut 
# 💡 Import fungsi logic dan database
from core.llm_service import generate_final_report 
from core.db_connector import get_all_answers_for_user_and_mq, get_user_session_details, save_final_report_to_db

# Prefix untuk endpoint ini adalah /api/v1/feedback
router = APIRouter(prefix="/v1", tags=["Feedback"])

@router.post("/feedback", response_model=FinalFeedbackOut, summary="Memproses Evaluasi Akhir dan Mendapatkan Laporan Hasil Wawancara")
async def get_final_feedback(payload: FinalFeedbackRequest):
    """
    Menerima ID sesi (user, mq, role, level) dan memicu proses LLM
    untuk menghasilkan laporan akhir dan penilaian rubrik.
    """
    try:
        # 1. Ambil semua Jawaban (Main & AI Follow-up) dari Database
        answers = get_all_answers_for_user_and_mq(
            payload.user_id,
            payload.main_question_id
        )
        
        if not answers or len(answers) < 2: 
            raise HTTPException(
                status_code=400,
                detail=f"Tidak ada jawaban yang cukup ({len(answers)} ditemukan) untuk menghasilkan laporan final. Minimal 2 Q&A diperlukan."
            )

        # 2. Ambil detail sesi (Role Name dan Level Name)
        session_details = get_user_session_details(
            payload.role_id,
            payload.level_id
        )

        # 3. Panggil LLM untuk menghasilkan laporan final
        # report_data akan berupa Dict yang sesuai dengan FinalFeedbackOut
        report_data = generate_final_report(
            role=session_details['role_name'],
            level=session_details['level_name'],
            q_and_a_list=answers,
            user_id=payload.user_id,
            main_question_id=payload.main_question_id 
        )
        
        # 4. Simpan hasil laporan final ke database
        save_final_report_to_db(report_data)

        # 5. Kembalikan respons
        return FinalFeedbackOut(**report_data)

    except HTTPException:
        # Pengecualian yang dilempar dari dalam blok try, misalnya dari validasi jumlah jawaban
        raise
    except Exception as e:
        print(f"Error in /v1/feedback: {e}")
        traceback.print_exc()
        # Jika LLM gagal atau response tidak valid
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan server saat memproses feedback final: {str(e)}"
        )