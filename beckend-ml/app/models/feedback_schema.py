from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# --- Model untuk Matriks Penilaian (Rubrik 5 Aspek) ---
class ScoreMetrics(BaseModel):
    """Skema untuk skor numerik per aspek (0-100)"""
    relevance: float = Field(..., ge=0, le=100, description="Kesesuaian jawaban dengan pertanyaan dan kebenaran teknis.")
    clarity: float = Field(..., ge=0, le=100, description="Kejelasan penyampaian dan minimnya kata pengisi.")
    structure: float = Field(..., ge=0, le=100, description="Keteraturan alur jawaban, logis, penerapan pola STAR.")
    confidence: float = Field(..., ge=0, le=100, description="Tingkat keyakinan dalam diksi.")
    conciseness: float = Field(..., ge=0, le=100, description="Keringkasan penyampaian.")
    
# --- Model untuk Metrik Objektif (Hasil NLP Guardrails) ---
class NlpGuardrails(BaseModel):
    """Hasil metrik objektif dari NLP processor"""
    cosine_similarity: float = Field(..., ge=0, le=1, description="Kemiripan semantik jawaban user vs ground truth (0-1).")
    keyword_coverage_ratio: float = Field(..., ge=0, le=1, description="Rasio keyword yang berhasil dicakup (0-1).")
    filler_ratio: float = Field(..., ge=0, le=1, description="Rasio kata pengisi dalam jawaban (0-1).")
    is_star_detected: bool = Field(..., description="Apakah pola STAR (Situation, Task, Action, Result) terdeteksi.")

# --- Model Output Akhir (Dikembalikan ke Frontend) ---
class FinalFeedback(BaseModel):
    """Output komprehensif yang dikembalikan ke frontend."""
    # Data Identifikasi
    user_id: int
    main_question_id: int
    session_id: str
    
    # Skor Final
    score_overall: float = Field(..., ge=0, le=100, description="Skor total akhir setelah kalibrasi.")
    
    # Feedback
    feedback_narrative: str = Field(..., description="Umpan balik naratif yang disusun oleh LLM.")
    
    # Detail Rubrik dan Matriks
    score_metrics: ScoreMetrics
    nlp_metrics: NlpGuardrails
    competency_weights: Dict[str, float] = Field(..., description="Bobot aspek kompetensi yang digunakan untuk kalibrasi.")

# --- Model Input API (yang akan diterima oleh /feedback endpoint) ---
class FeedbackInput(BaseModel):
    user_id: int
    main_question_id: int # Atau session_id yang lebih spesifik
    role_id: int # Diperlukan untuk mengambil Matriks Kompetensi
    level_id: int # Diperlukan untuk mengambil Matriks Kompetensi