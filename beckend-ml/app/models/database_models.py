# app/models/database_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.databse import Base  # Base dari database.py

class MLQuestion(Base):
    __tablename__ = "ml_question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    question_ml = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<MLQuestion(id={self.id}, user_id={self.user_id}, question_ml={self.question_ml[:30]}...)>"

# Tambahkan juga model lain seperti AnswerUser, MainQuestion jika perlu
