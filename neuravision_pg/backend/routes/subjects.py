"""NEURAVISION — /api/subjects (Hybrid Edition)
No image/encoding storage here — face descriptors live only in the
browser's memory (face-api.js). The server just keeps a directory
of names/IDs/departments for attendance record-keeping.
"""
from flask import Blueprint, request, jsonify
import logging
from database import query_all, query_one, execute

subjects_bp = Blueprint("subjects", __name__)
log = logging.getLogger(__name__)


@subjects_bp.route("/", methods=["GET"])
def list_subjects():
    rows = query_all(
        "SELECT id, subject_id, name, department, email, role, photo_url, registered_at, is_active "
        "FROM subjects ORDER BY registered_at DESC"
    )
    for r in rows:
        r["registered_at"] = str(r["registered_at"])
    return jsonify({"subjects": rows, "total": len(rows)})


@subjects_bp.route("/register", methods=["POST"])
def register_subject():
    """
    Lightweight registration — just metadata, no image.
    The actual face descriptor is captured and stored client-side
    by face-api.js in the browser session.

    POST JSON: { "subject_id": "STU-001", "name": "...", "department": "...", "email": "...", "role": "...", "photo_url": "..." }
    """
    data = request.get_json(force=True)
    sid  = (data.get("subject_id") or "").strip().upper()
    name = (data.get("name") or "").strip()
    photo_url = (data.get("photo_url") or "").strip() or None

    if not sid or not name:
        return jsonify({"error": "subject_id and name are required"}), 400

    existing = query_one("SELECT id FROM subjects WHERE subject_id = %s", (sid,))
    if existing:
        # Already exists — treat as success (idempotent), useful since
        # browser-side registration may re-fire across sessions.
        execute(
            "UPDATE subjects SET name = %s, department = %s, email = %s, role = %s, "
            "photo_url = COALESCE(%s, photo_url) WHERE subject_id = %s",
            (name, data.get("department",""), data.get("email",""), data.get("role","student"), photo_url, sid)
        )
        return jsonify({"message": "Subject updated", "subject_id": sid}), 200

    execute(
        """INSERT INTO subjects (subject_id, name, department, email, role, photo_url)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (sid, name, data.get("department",""), data.get("email",""), data.get("role","student"), photo_url)
    )
    log.info(f"Registered: {name} ({sid})")
    return jsonify({"message": "Subject registered successfully", "subject_id": sid}), 201


@subjects_bp.route("/<sid>", methods=["DELETE"])
def delete_subject(sid):
    if not query_one("SELECT id FROM subjects WHERE subject_id = %s", (sid,)):
        return jsonify({"error": "Not found"}), 404
    execute("DELETE FROM subjects WHERE subject_id = %s", (sid,))
    return jsonify({"message": f"{sid} deleted"})


@subjects_bp.route("/<sid>/toggle", methods=["PATCH"])
def toggle_subject(sid):
    row = query_one("SELECT is_active FROM subjects WHERE subject_id = %s", (sid,))
    if not row:
        return jsonify({"error": "Not found"}), 404
    new = not row["is_active"]
    execute("UPDATE subjects SET is_active = %s WHERE subject_id = %s", (new, sid))
    return jsonify({"subject_id": sid, "is_active": new})
