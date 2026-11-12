"""
src/db.py
─────────────────────────────────────────────────────────────────────────────
Gestión de la conexión a MySQL usando SQLAlchemy y variables de entorno.
Detecta automáticamente si MySQL no está disponible y activa el modo demo.
"""

import os
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# ─── Variables de entorno ────────────────────────────────────────────────────
_HOST    = os.getenv("MYSQL_HOST",    "localhost")
_PORT    = os.getenv("MYSQL_PORT",    "3306")
_USER    = os.getenv("MYSQL_USER",    "")
_PASS    = os.getenv("MYSQL_PASSWORD","")
_DB_DW   = os.getenv("MYSQL_DB_DW",  "qqp_dw")
_DB_OLTP = os.getenv("MYSQL_DB_OLTP","qqp_oltp")

# ─── Cadena de conexión ──────────────────────────────────────────────────────
def _url(db: str) -> str:
    return (
        f"mysql+pymysql://{_USER}:{_PASS}@{_HOST}:{_PORT}/{db}"
        "?charset=utf8mb4"
    )

@st.cache_resource(show_spinner=False)
def get_engine_dw():
    """Devuelve el motor SQLAlchemy para el esquema qqp_dw."""
    return create_engine(_url(_DB_DW), pool_pre_ping=True, pool_recycle=3600)

@st.cache_resource(show_spinner=False)
def get_engine_oltp():
    """Devuelve el motor SQLAlchemy para el esquema qqp_oltp."""
    return create_engine(_url(_DB_OLTP), pool_pre_ping=True, pool_recycle=3600)

def test_connection() -> tuple[bool, str]:
    """
    Prueba la conexión a MySQL.
    Devuelve (True, versión) si tiene éxito, (False, mensaje_error) si falla.
    """
    try:
        engine = get_engine_dw()
        with engine.connect() as conn:
            version = conn.execute(text("SELECT VERSION()")).scalar()
        return True, f"MySQL {version}"
    except Exception as e:
        return False, str(e)

def is_connected() -> bool:
    """Atajo para verificar si hay conexión activa."""
    ok, _ = test_connection()
    return ok
