# app/api/user.py

from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.schemas import UserCreate, UserCreateResponse, RoleOut, LevelOut
from app.core import db_connector # Import file connector

router = APIRouter(prefix="/v1", tags=["user"])

@router.get("/roles", response_model=List[RoleOut], summary="Mendapatkan daftar semua Role (untuk Dropdown)")
def get_roles():
    """Mendapatkan daftar ID dan Nama Role dari tabel ref_role."""
    try:
        roles = db_connector.get_all_roles()
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil Roles: {str(e)}")

@router.get("/levels", response_model=List[LevelOut], summary="Mendapatkan daftar semua Level (untuk Dropdown)")
def get_levels():
    """Mendapatkan daftar ID dan Nama Level dari tabel ref_level."""
    try:
        levels = db_connector.get_all_levels()
        return levels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil Levels: {str(e)}")

@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED, summary="Mendaftarkan User Baru")
def register_user(user_data: UserCreate):
    """Mendaftarkan user baru ke tabel 'user'."""
    try:
        # Pastikan role_id dan level_id yang diinput valid (lebih dari 0)
        if user_data.role_id <= 0 or user_data.level_id <= 0:
             raise HTTPException(status_code=400, detail="ID Role atau Level tidak valid.")
             
        user_id = db_connector.create_user(
            name=user_data.name,
            ref_role_id=user_data.role_id,
            ref_level_id=user_data.level_id
        )
        return UserCreateResponse(user_id=user_id, name=user_data.name)
        
    except Exception as e:
        # Menangkap error dari db_connector (misal IntegrityError/FK error)
        raise HTTPException(status_code=400, detail=f"Gagal mendaftarkan user. Periksa ID Role/Level. Detail: {str(e)}")