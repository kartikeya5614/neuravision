"""
NEURAVISION — Configuration
Reads from environment variables (set in Render dashboard for cloud deployment)
Falls back to local defaults for local development.
"""
import os

class Config:
    # ── PostgreSQL ────────────────────────────────────────────────
    DB_HOST     = os.getenv("DB_HOST",     "localhost")
    DB_PORT     = int(os.getenv("DB_PORT", 5432))
    DB_USER     = os.getenv("DB_USER",     "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "#March271996")
    DB_NAME     = os.getenv("DB_NAME",     "neuravision")

    # ── Flask ─────────────────────────────────────────────────────
    SECRET_KEY  = os.getenv("SECRET_KEY",  "neuravision-local-secret")
    DEBUG       = os.getenv("DEBUG", "true").lower() == "true"

    # ── Face Recognition ──────────────────────────────────────────
    RECOGNITION_THRESHOLD = 0.40
    LIVENESS_THRESHOLD    = 0.55
    ATTENDANCE_COOLDOWN   = 30