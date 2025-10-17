# app/models/database_models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship # Tambahkan ini untuk relasi
from datetime import datetime
from app.databse import Base  # Base dari database.py

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

# Tambahkan juga model lain seperti AnswerUser, MainQuestion jika perlu
