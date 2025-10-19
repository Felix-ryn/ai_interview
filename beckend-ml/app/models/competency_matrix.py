from typing import Dict, List, Tuple
from .feedback_schema import ScoreMetrics

# Asumsi: Data ini berasal dari tabel ref_role dan ref_level
# Untuk tujuan simulasi, kita gunakan struktur hardcoded.

# --- Matriks Keyword untuk NLP Guardrails ---
# Kata kunci (keywords) yang diharapkan dari jawaban per Role dan Level.
# Ini harusnya lebih kompleks dan terhubung dengan 'main_question' di DB.
COMPETENCY_KEYWORDS: Dict[Tuple[int, int], Dict[str, List[str]]] = {
    # Key: (role_id, level_id)
    (5, 3): { # Frontend Developer, Senior (role_id:5, level_id:3)
        "Relevance": ["state management", "performance optimization", "micro-frontend", "SSR", "hydration"],
        "Structure": ["systematic approach", "problem statement", "solution", "result"]
    },
    (3, 1): { # Data Analyst, Junior (role_id:3, level_id:1)
        "Relevance": ["data cleaning", "SQL join", "visualization tool", "pivot table"],
        "Structure": ["step-by-step", "process", "outcome"]
    }
}


# --- Matriks Pembobotan untuk Kalibrasi Skor ---
# Bobot per aspek (Relevance, Clarity, Structure, Confidence, Conciseness)
# Total bobot harus 1.0 (100%).
COMPETENCY_WEIGHTS: Dict[Tuple[int, int], Dict[str, float]] = {
    # Key: (role_id, level_id)
    (5, 3): { # Frontend Developer, Senior
        "relevance": 0.35,  # Teknis sangat penting
        "clarity": 0.20,
        "structure": 0.25,  # Sistematisasi dalam menjelaskan arsitektur penting
        "confidence": 0.10,
        "conciseness": 0.10
    },
    (3, 1): { # Data Analyst, Junior
        "relevance": 0.25,
        "clarity": 0.30,  # Kejelasan komunikasi data lebih ditekankan
        "structure": 0.20,
        "confidence": 0.15,
        "conciseness": 0.10
    }
}

def get_competency_data(role_id: int, level_id: int) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """Mengambil bobot dan keyword berdasarkan role dan level."""
    key = (role_id, level_id)
    weights = COMPETENCY_WEIGHTS.get(key, COMPETENCY_WEIGHTS.get((3, 1))) # Fallback ke DA Junior
    keywords = COMPETENCY_KEYWORDS.get(key, COMPETENCY_KEYWORDS.get((3, 1)))
    return weights, keywords