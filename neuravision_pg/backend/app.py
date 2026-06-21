"""
NEURAVISION — Flask Backend (Hybrid Edition)
Lightweight JSON-only API. No image processing, no DeepFace, no TensorFlow.
All face AI runs client-side in the browser via face-api.js.
This keeps memory usage tiny — safe for free-tier hosting (Render free = 512MB).

Run with: python app.py
"""
from flask import Flask, request
from flask_cors import CORS
from config import Config
from database import init_db, release_conn
from routes.subjects   import subjects_bp
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

    CORS(app,
         resources={r"/*": {"origins": "*"}},
         supports_credentials=False,
         allow_headers="*",
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            from flask import Response
            resp = Response()
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Headers'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            return resp

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        return response

    init_db(app)
    app.teardown_appcontext(release_conn)

    app.register_blueprint(subjects_bp,    url_prefix="/api/subjects")
    app.register_blueprint(attendance_bp,  url_prefix="/api/attendance")
    app.register_blueprint(analytics_bp,   url_prefix="/api/analytics")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "system": "NEURAVISION", "db": "PostgreSQL", "mode": "hybrid-client-ai"}

    return app


app = create_app()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  NEURAVISION (Hybrid) is running!")
    print("  Open: http://localhost:5000/api/health")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
