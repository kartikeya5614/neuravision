"""
NEURAVISION — Flask Backend (PostgreSQL Edition)
Run with: python app.py
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db, release_conn
from utils.face_engine import reload_encodings
from routes.subjects   import subjects_bp
from routes.detection  import detection_bp
from routes.attendance import attendance_bp
from routes.analytics  import analytics_bp
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)

    # Load face encodings from DB on startup
    with app.app_context():
        try:
            reload_encodings()
        except Exception as e:
            logging.warning(f"Could not load encodings on startup: {e}")

    # Release DB connection after each request
    app.teardown_appcontext(release_conn)

    app.register_blueprint(subjects_bp,    url_prefix="/api/subjects")
    app.register_blueprint(detection_bp,   url_prefix="/api/detect")
    app.register_blueprint(attendance_bp,  url_prefix="/api/attendance")
    app.register_blueprint(analytics_bp,   url_prefix="/api/analytics")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "system": "NEURAVISION", "db": "PostgreSQL"}

    return app


app = create_app()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  NEURAVISION is running!")
    print("  Open: http://localhost:5000/api/health")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
