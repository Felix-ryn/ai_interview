# api/helpers/score_calculator.py
from ..config.scoring_matrix import get_assessment_weights

def calculate_final_score(role_id: str, level_id: str, raw_scores: dict) -> float:
    """
    Menghitung skor akhir tertimbang (Weighted Final Score).
    
    raw_scores: { 'Q1': 90, 'Q2': 75, 'Q3': 80, 'Q4': 85, 'Q5': 70 }
    """
    
    weights = get_assessment_weights(role_id, level_id)

    if not weights:
        raise ValueError(f"Bobot penilaian untuk Role ID {role_id} dan Level ID {level_id} tidak ditemukan.")

    final_score = 0.0
    
    # 1. Pembobotan (Si x Wi) dan Agregasi
    for q_key, weight in weights.items():
        score = raw_scores.get(q_key)
        
        if score is None:
            # Asumsi jika skor tidak ada, pertanyaan tersebut tidak dijawab (Skor = 0)
            score = 0
            
        # Hitung skor yang dibobotkan
        # Contoh: 90 (skor) * 0.15 (bobot) = 13.5
        weighted_score = score * weight
        final_score += weighted_score

    # Skor Akhir sudah dalam skala 0-100 (karena total bobot = 1.0)
    return round(final_score, 2)