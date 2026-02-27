from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# ======================================================================
# 💡 SKEMA BARU UNTUK METRIK 5 ASPEK LLM (0-5)
# Ini adalah metrik yang dihasilkan LLM di generate_final_report
# ======================================================================
class FinalScoreMetricsLLM(BaseModel):
    Relevansi: int = Field(..., ge=0, le=5)
    Klaritas: int = Field(..., ge=0, le=5)
    Struktur: int = Field(..., ge=0, le=5)
    Kepercayaan_Diri: int = Field(..., ge=0, le=5)
    Ringkas: int = Field(..., ge=0, le=5)

# ======================================================================
# 💡 SKEMA BARU UNTUK DETAIL METRIK (Gabungan Rubrik Statis & Skor LLM)
# ======================================================================
class DetailedMetric(BaseModel):
    Aspek: str
    Fokus_Utama: str
    Metrik_Evaluasi_Teknis: str
    Skor: int # 0-5

# ======================================================================
# 💡 SKEMA OUTPUT AKHIR (FinalFeedbackOut)
# ======================================================================
class FinalFeedbackOut(BaseModel):
    """Output komprehensif setelah semua skor dihitung dan laporan dihasilkan."""
    # Data Identifikasi
    user_id: int
    main_question_id: int
    
    # Skor Final Berbobot (Dihitung di router)
    final_weighted_score: float = Field(..., ge=0, le=100, description="Skor total akhir setelah bobot kompetensi diaplikasikan.")
    
    # Raw Scores Per Pertanyaan (Hasil LLM S_i, 0-100)
    raw_scores_per_question: Dict[str, float] = Field(..., description="Skor mentah (0-100) yang diberikan LLM per pertanyaan (Q1, Q2, ...)")
    
    # Feedback
    feedback_narrative: str = Field(..., description="Umpan balik naratif yang disusun oleh LLM.")
    
    # Detail Rubrik dan Matriks (Hasil generate_final_report)
    score_metrics: FinalScoreMetricsLLM # 5 kriteria utama (0-5)
    detailed_metrics_list: List[DetailedMetric] # Daftar lengkap kriteria dengan deskripsi dan skor

# ======================================================================
# 💡 SKEMA INPUT API (Disesuaikan)
# ======================================================================
class FinalFeedbackRequest(BaseModel):
    user_id: int
    main_question_id: int 
    role_id: int 
    level_id: int 


# ======================================================================
# 🗑️ SKEMA LAMA (DIHAPUS atau DIPERTAHANKAN jika masih dipakai)
# Catatan: ScoreMetrics dan NlpGuardrails dipertahankan jika file lain masih menggunakannya.
# Saya akan mempertahankan ScoreMetrics dan NlpGuardrails, tetapi mengubah FinalFeedback 
# menjadi FinalFeedbackOut untuk menghindari konflik.

# --- Model untuk Matriks Penilaian (Rubrik 5 Aspek) ---
class ScoreMetrics(BaseModel):
    """Skema untuk skor numerik per aspek (0-100), digunakan untuk skor per pertanyaan (S_i)."""
    relevance: float = Field(..., ge=0, le=100, description="Kesesuaian jawaban dengan pertanyaan dan kebenaran teknis.")
    clarity: float = Field(..., ge=0, le=100, description="Kejelasan penyampaian dan minimnya kata pengisi.")
    structure: float = Field(..., ge=0, le=100, description="Keteraturan alur jawaban, logis, penerapan pola STAR.")
    confidence: float = Field(..., ge=0, le=100, description="Tingkat keyakinan dalam diksi.")
    conciseness: float = Field(..., ge=0, le=100, description="Keringkasan penyampaian.")
    
# --- Model untuk Metrik Objektif (Hasil NLP Guardrails) ---
class NlpGuardrails(BaseModel):
    """Hasil metrik objektif dari NLP processor (Dipertahankan untuk kompatibilitas)."""
    cosine_similarity: float = Field(..., ge=0, le=1, description="Kemiripan semantik jawaban user vs ground truth (0-1).")
    keyword_coverage_ratio: float = Field(..., ge=0, le=1, description="Rasio keyword yang berhasil dicakup (0-1).")
    filler_ratio: float = Field(..., ge=0, le=1, description="Rasio kata pengisi dalam jawaban (0-1).")
    is_star_detected: bool = Field(..., description="Apakah pola STAR (Situation, Task, Action, Result) terdeteksi.")