from typing import Dict, List
from app.models.feedback_schema import ScoreMetrics, NlpGuardrails, FinalFeedback
from app.models.competency_matrix import get_competency_data
from app.core.nlp_processor import calculate_nlp_guardrails
from app.core.llm_service import generate_llm_score, generate_feedback_narrative # Asumsi fungsi ada

# Konstanta Kalibrasi
WEIGHT_LLM = 0.7  # Bobot untuk skor subjektif LLM
WEIGHT_NLP = 0.3  # Bobot untuk metrik objektif NLP

# --- Fungsi Penilaian Ganda (Kalibrasi) ---
def calibrate_score(llm_scores: ScoreMetrics, nlp_metrics: NlpGuardrails, weights: Dict[str, float]) -> float:
    """
    Melakukan kalibrasi skor akhir.
    
    Rumus Kalibrasi Sederhana:
    Skor Akhir = (W_LLM * Skor LLM Berbobot) + (W_NLP * Skor NLP Terbobot)
    """
    
    # A. Hitung Skor LLM Berbobot (Weighted LLM Score)
    llm_weighted_score = 0
    for aspect, weight in weights.items():
        llm_score = getattr(llm_scores, aspect)
        llm_weighted_score += llm_score * weight

    # B. Hitung Skor NLP Berbobot (Weighted NLP Score)
    # Metrik NLP diubah menjadi nilai 0-100 dan dibobotkan sesuai aspek yang relevan.
    nlp_score = (
        (nlp_metrics.cosine_similarity * 100 * weights.get("relevance", 0)) + # Cosine untuk Relevance
        ((1 - nlp_metrics.filler_ratio) * 100 * weights.get("clarity", 0)) +  # Filler untuk Clarity
        (100 if nlp_metrics.is_star_detected else 0) * weights.get("structure", 0) # STAR untuk Structure
    )
    # Tambahkan metrik lain jika ada (misal: keyword coverage)
    nlp_score_final = nlp_score / (weights.get("relevance", 0) + weights.get("clarity", 0) + weights.get("structure", 0))
    
    # C. Kalibrasi Akhir
    final_score = (WEIGHT_LLM * llm_weighted_score) + (WEIGHT_NLP * nlp_score_final)
    
    return min(max(final_score, 0), 100) # Batasi skor antara 0 dan 100


# --- Fungsi Utama Evaluator ---
async def evaluate_full_session(
    user_id: int, 
    main_question_id: int, 
    answer_data: List[Dict], # {answer_text, question_text, ground_truth}
    role_id: int, 
    level_id: int
) -> FinalFeedback:
    
    # 1. Ambil Matriks Kompetensi
    weights, keywords = get_competency_data(role_id, level_id)
    
    # 2. Iterasi dan Proses Jawaban (Untuk Sederhana, kita ambil jawaban pertama)
    first_answer = answer_data[0]
    
    # 3. LLM Scoring (Penilaian Subjektif Awal)
    # Asumsi: LLM memberikan skor 5 aspek (Relevance, Clarity, dll.) dan dikembalikan sebagai ScoreMetrics
    llm_scores: ScoreMetrics = await generate_llm_score(first_answer["answer_text"], first_answer["question_text"])
    
    # 4. NLP Guardrails (Penilaian Objektif)
    nlp_metrics: NlpGuardrails = calculate_nlp_guardrails(
        first_answer["answer_text"], 
        first_answer["ground_truth"], # Memerlukan data Ground Truth dari DB
        keywords.get("Relevance", [])
    )
    
    # 5. Kalibrasi Skor
    final_score = calibrate_score(llm_scores, nlp_metrics, weights)
    
    # 6. Penyusunan Feedback Naratif (Feedback Composer)
    # LLM membuat narasi berdasarkan skor dan metrik teknis
    narrative = await generate_feedback_narrative(llm_scores, nlp_metrics, final_score)
    
    return FinalFeedback(
        user_id=user_id,
        main_question_id=main_question_id,
        session_id="SESS-" + str(main_question_id), # Contoh session ID
        score_overall=final_score,
        feedback_narrative=narrative,
        score_metrics=llm_scores,
        nlp_metrics=nlp_metrics,
        competency_weights=weights
    )