import re
from typing import List, Dict
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity
from .llm_service import generate_embeddings # Asumsi: Anda menggunakan LLM Service untuk Embeddings
from app.models.feedback_schema import NlpGuardrails

# Inisialisasi NLTK (Pastikan Anda sudah 'nltk.download('punkt')' dan 'nltk.download('stopwords')')
STOP_WORDS = set(stopwords.words('indonesian'))
FILLER_WORDS = {"eh", "anu", "jadi", "gini", "maksudnya", "seperti", "kayak"} # Tambahkan kata pengisi umum

def preprocess_text(text: str) -> str:
    """Tokenisasi, penghapusan stopword dan filler word."""
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    
    # Hapus stopwords dan filler words
    clean_tokens = [
        token for token in tokens 
        if token.isalnum() and token not in STOP_WORDS and token not in FILLER_WORDS
    ]
    return " ".join(clean_tokens)

def calculate_nlp_guardrails(
    user_answer: str, 
    ground_truth_answer: str, 
    expected_keywords: List[str]
) -> NlpGuardrails:
    """Menghitung semua metrik objektif NLP (Guardrails)."""
    
    # 1. Preprocessing dan Filler Ratio
    clean_answer = preprocess_text(user_answer)
    total_words = len(user_answer.split())
    
    filler_count = sum(1 for word in user_answer.lower().split() if word in FILLER_WORDS)
    filler_ratio = filler_count / total_words if total_words > 0 else 0.0

    # 2. Cosine Similarity (memerlukan embeddings)
    # Asumsi: generate_embeddings tersedia di llm_service
    embeddings = generate_embeddings([user_answer, ground_truth_answer]) 
    
    # Hitung cosine similarity antara kedua vektor embedding
    # Pastikan kedua vektor adalah 2D array
    cos_sim = sk_cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    # 3. Keyword Coverage
    covered_keywords = [
        kw for kw in expected_keywords 
        if kw.lower() in clean_answer # Pengecekan sederhana, bisa ditingkatkan dengan semantic match
    ]
    keyword_coverage_ratio = len(covered_keywords) / len(expected_keywords) if expected_keywords else 0.0
    
    # 4. Deteksi Pola STAR (Pengecekan sederhana berdasarkan frasa kunci)
    star_pattern = re.compile(r'(situasi|task|aksi|hasil|result|action)', re.IGNORECASE)
    is_star_detected = bool(star_pattern.search(user_answer))

    return NlpGuardrails(
        cosine_similarity=float(cos_sim),
        keyword_coverage_ratio=keyword_coverage_ratio,
        filler_ratio=filler_ratio,
        is_star_detected=is_star_detected
    )