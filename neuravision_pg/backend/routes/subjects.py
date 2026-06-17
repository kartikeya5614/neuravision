"""NEURAVISION — /api/subjects"""
from flask import Blueprint, request, jsonify
import base64, logging, pickle
from database import query_all, query_one, execute
from utils.face_engine import encode_face_from_bytes, reload_encodings

subjects_bp = Blueprint("subjects", __name__)
log = logging.getLogger(__name__)


@subjects_bp.route("/", methods=["GET"])
def list_subjects():
    rows = query_all(
        "SELECT id, subject_id, name, department, email, role, registered_at, is_active "
        "FROM subjects ORDER BY registered_at DESC"
    )
    for r in rows:
        r["registered_at"] = str(r["registered_at"])
    return jsonify({"subjects": rows, "total": len(rows)})


@subjects_bp.route("/register", methods=["POST"])
def register_subject():
    data = request.get_json(force=True)
    for f in ["subject_id", "name", "image_b64"]:
        if not data.get(f):
            return jsonify({"error": f"Missing: {f}"}), 400

    sid  = data["subject_id"].strip().upper()
    name = data["name"].strip()

    if query_one("SELECT id FROM subjects WHERE subject_id = %s", (sid,)):
        return jsonify({"error": f"'{sid}' already registered"}), 409

    try:
        img_bytes = base64.b64decode(data["image_b64"])
    except Exception:
        return jsonify({"error": "Invalid image"}), 400

    encoding = encode_face_from_bytes(img_bytes)
    if encoding is None:
        return jsonify({"error": "No face detected in image"}), 422

    encoding_blob = pickle.dumps(encoding)

    execute(
        """INSERT INTO subjects (subject_id, name, department, email, role, encoding)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (sid, name, data.get("department",""), data.get("email",""),
         data.get("role","student"), encoding_blob)
    )
    reload_encodings()
    log.info(f"Registered: {name} ({sid})")
    return jsonify({"message": "Registered successfully", "subject_id": sid}), 201


@subjects_bp.route("/<sid>", methods=["DELETE"])
def delete_subject(sid):
    if not query_one("SELECT id FROM subjects WHERE subject_id=%s", (sid,)):
        return jsonify({"error": "Not found"}), 404
    execute("DELETE FROM subjects WHERE subject_id=%s", (sid,))
    reload_encodings()
    return jsonify({"message": f"{sid} deleted"})


@subjects_bp.route("/<sid>/toggle", methods=["PATCH"])
def toggle_subject(sid):
    row = query_one("SELECT is_active FROM subjects WHERE subject_id=%s", (sid,))
    if not row:
        return jsonify({"error": "Not found"}), 404
    new = not row["is_active"]
    execute("UPDATE subjects SET is_active=%s WHERE subject_id=%s", (new, sid))
    reload_encodings()
    return jsonify({"subject_id": sid, "is_active": new})
