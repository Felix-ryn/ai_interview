# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ===============================
# Ganti sesuai database MySQL di Laragon
# ===============================
DB_USER = "root"       # username MySQL
DB_PASSWORD = ""       # password MySQL (kosong biasanya default Laragon)
DB_HOST = "127.0.0.1"
DB_PORT = "3307"
DB_NAME = "tm_db"  # ganti sesuai nama database kamu

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Buat engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # opsional: True untuk lihat query di console
)

# Session Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarative
Base = declarative_base()

# Dependency untuk FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
