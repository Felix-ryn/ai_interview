# app/models/database_models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, BigInteger, DECIMAL, SmallInteger
from sqlalchemy.orm import relationship # Tambahkan ini untuk relasi
from datetime import datetime
from app.databse import Base  # Base dari database.py

TINYINT_SQLA = SmallInteger
# === MODEL BARU DITAMBAHKAN DI SINI ===

class RefLevel(Base):
    __tablename__ = "ref_level"

    id = Column(Integer, primary_key=True)
    level_name = Column(String(50), nullable=False, unique=True)
    
class RefRole(Base):
    __tablename__ = "ref_role"

    id = Column(Integer, primary_key=True)
    role_name = Column(String(100), nullable=False, unique=True)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    # Gunakan ForeignKey untuk menghubungkan ke ref_role dan ref_level
    ref_role_id = Column(Integer, ForeignKey('ref_role.id'), nullable=False)
    ref_level_id = Column(Integer, ForeignKey('ref_level.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Definisi Relationship
    role = relationship("RefRole")
    level = relationship("RefLevel")

class MLQuestion(Base):
    __tablename__ = "ml_question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    question_ml = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<MLQuestion(id={self.id}, user_id={self.user_id}, question_ml={self.question_ml[:30]}...)>"

class MainQuestion(Base):
    __tablename__ = "main_question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_role_id = Column(Integer, ForeignKey('ref_role.id'), nullable=False)
    ref_level_id = Column(Integer, ForeignKey('ref_level.id'), nullable=False)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# --- MODEL AnswerUser (Diperbarui sesuai Struktur DB) ---
class AnswerUser(Base):
    """Model untuk menyimpan jawaban dan hasil penilaian, disesuaikan dengan skema DB."""
    __tablename__ = "answer_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    main_question_id = Column(BigInteger, ForeignKey('main_question.id'), nullable=True)
    ml_question_id = Column(BigInteger, ForeignKey('ml_question.id'), nullable=True)
    answer_text = Column(Text, nullable=False)
    
    # Kolom Skor (sesuai TINYINT di DB, diubah ke SmallInteger atau Float untuk perhitungan)
    # Kami menggunakan Float untuk skor 0-100 karena hasil kalkulasi akan menjadi desimal.
    score_overall = Column(Float, default=0.0) # score_overall: TINYINT di DB, pakai Float di SQLAlchemy untuk akurasi perhitungan.
    score_relevance = Column(Float, default=0.0)
    score_clarity = Column(Float, default=0.0)
    score_structure = Column(Float, default=0.0)
    score_confidence = Column(Float, default=0.0)
    score_conciseness = Column(Float, default=0.0)
    
    # Kolom Metrik NLP
    # nlp_star_detected: TINYINT di DB (0 atau 1)
    nlp_star_detected = Column(TINYINT_SQLA, default=0) 
    # nlp_filler_ratio: DECIMAL(5,2) di DB, pakai DECIMAL di SQLAlchemy
    nlp_filler_ratio = Column(DECIMAL(5, 2), default=0.0) 
    
    # Kolom Feedback Naratif
    feedback_narrative = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    # Definisi Relationship
    user = relationship("User")
    main_question = relationship("MainQuestion")
    ml_question = relationship("MLQuestion")