"""
NEURAVISION — Configuration
Edit the values below to match your PostgreSQL setup.
"""
import os

class Config:
    # ── PostgreSQL ────────────────────────────────────────────────
    DB_HOST     = os.getenv("DB_HOST",     "localhost")
    DB_PORT     = int(os.getenv("DB_PORT", 5432))
    DB_USER     = os.getenv("DB_USER",     "postgres")      # your postgres username
    DB_PASSWORD = os.getenv("DB_PASSWORD", "#March271996")  # your postgres password
    DB_NAME     = os.getenv("DB_NAME",     "neuravision")

    # ── Flask ─────────────────────────────────────────────────────
    SECRET_KEY  = os.getenv("SECRET_KEY",  "neuravision-local-secret")
    DEBUG       = True

    # ── Face Recognition ──────────────────────────────────────────
    RECOGNITION_THRESHOLD = 0.55   # lower = stricter match
    LIVENESS_THRESHOLD    = 0.55   # minimum liveness score
    ATTENDANCE_COOLDOWN   = 30     # seconds before re-logging same person
