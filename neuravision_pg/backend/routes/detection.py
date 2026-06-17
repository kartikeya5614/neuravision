"""NEURAVISION — /api/detect"""
from flask import Blueprint, request, jsonify
import base64, time, logging
from database import execute, query_one
from utils.face_engine import recognise_faces
from utils.liveness import compute_liveness_score
from config import Config
from datetime import date, datetime

detection_bp = Blueprint("detection", __name__)
log = logging.getLogger(__name__)
_cooldown = {}


@detection_bp.route("/frame", methods=["POST"])
def process_frame():
    t0   = time.time()
    data = request.get_json(force=True)
    if not data.get("frame_b64"):
        return jsonify({"error": "No frame"}), 400

    cam_id = data.get("cam_id", "CAM-01")
    try:
        img_bytes = base64.b64decode(data["frame_b64"])
    except Exception:
        return jsonify({"error": "Invalid base64"}), 400

    faces   = recognise_faces(img_bytes)
    results = []

    for face in faces:
        sid        = face.get("subject_id", "UNKNOWN")
        confidence = face.get("confidence", 0.0)
        liveness   = compute_liveness_score(face)

        execute(
            """INSERT INTO detection_log
               (subject_id, confidence, liveness, cam_id)
               VALUES (%s, %s, %s, %s)""",
            (sid, confidence, liveness, cam_id)
        )

        logged = False
        if sid != "UNKNOWN" and liveness >= Config.LIVENESS_THRESHOLD:
            now  = time.time()
            last = _cooldown.get(sid, 0)
            if now - last > Config.ATTENDANCE_COOLDOWN:
                _cooldown[sid] = now
                _mark_attendance(sid, confidence)
                logged = True

        results.append({
            "subject_id": sid,
            "name":       face.get("name", "Unknown"),
            "confidence": round(confidence, 4),
            "box":        face.get("box", []),
            "liveness":   round(liveness, 4),
            "logged":     logged,
        })

    ms = round((time.time()-t0)*1000)
    return jsonify({"faces": results, "face_count": len(results), "processing_ms": ms})


def _mark_attendance(sid, confidence):
    today = date.today().isoformat()
    now   = datetime.now()
    existing = query_one(
        "SELECT id FROM attendance WHERE subject_id=%s AND date=%s", (sid, today)
    )
    if existing:
        execute(
            "UPDATE attendance SET last_seen=%s, scan_count=scan_count+1 WHERE id=%s",
            (now, existing["id"])
        )
    else:
        execute(
            """INSERT INTO attendance (subject_id, date, first_seen, last_seen, confidence, status)
               VALUES (%s,%s,%s,%s,%s,'present')""",
            (sid, today, now, now, confidence)
        )
    log.info(f"Attendance marked: {sid}")
