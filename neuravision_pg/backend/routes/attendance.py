"""NEURAVISION — /api/attendance (Hybrid Edition)
Lightweight JSON-only endpoints. No image processing happens here —
all face AI runs in the browser. This keeps memory usage minimal,
safe for free-tier hosting (Render free = 512MB RAM).
"""
from flask import Blueprint, request, jsonify
from database import query_all, query_one, execute
from datetime import date, datetime

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/mark", methods=["POST"])
def mark_attendance():
    """
    Lightweight attendance marking — called by the browser after
    face-api.js recognises someone locally. No image is sent here,
    only the matched subject's id and name.

    POST JSON: { "subject_id": "STU-001", "name": "Kartikeya" }
    """
    data = request.get_json(force=True)
    sid  = (data.get("subject_id") or "").strip().upper()
    name = (data.get("name") or "").strip()

    if not sid or not name:
        return jsonify({"error": "subject_id and name are required"}), 400

    # Ensure subject exists (auto-create a minimal record if not already registered)
    existing = query_one("SELECT subject_id FROM subjects WHERE subject_id = %s", (sid,))
    if not existing:
        execute(
            "INSERT INTO subjects (subject_id, name) VALUES (%s, %s) "
            "ON CONFLICT (subject_id) DO NOTHING",
            (sid, name)
        )

    today = date.today().isoformat()
    now   = datetime.now()

    row = query_one(
        "SELECT id FROM attendance WHERE subject_id = %s AND date = %s",
        (sid, today)
    )
    if row:
        execute(
            "UPDATE attendance SET last_seen = %s, scan_count = scan_count + 1 WHERE id = %s",
            (now, row["id"])
        )
        status = "updated"
    else:
        execute(
            """INSERT INTO attendance (subject_id, date, first_seen, last_seen, status)
               VALUES (%s, %s, %s, %s, 'present')""",
            (sid, today, now, now)
        )
        status = "created"

    return jsonify({"message": "Attendance recorded", "subject_id": sid, "status": status})


@attendance_bp.route("/today", methods=["GET"])
def today():
    d = date.today().isoformat()
    rows = query_all(
        """SELECT a.subject_id, s.name, s.department,
                  a.first_seen, a.last_seen, a.scan_count, a.status
           FROM attendance a JOIN subjects s ON s.subject_id = a.subject_id
           WHERE a.date = %s ORDER BY a.first_seen""", (d,))
    for r in rows:
        r["first_seen"] = str(r["first_seen"])
        r["last_seen"]  = str(r["last_seen"])
    return jsonify({"date": d, "records": rows, "present": len(rows)})


@attendance_bp.route("/date/<date_str>", methods=["GET"])
def by_date(date_str):
    rows = query_all(
        """SELECT a.subject_id, s.name, a.first_seen, a.last_seen, a.scan_count, a.status
           FROM attendance a JOIN subjects s ON s.subject_id = a.subject_id
           WHERE a.date = %s ORDER BY a.first_seen""", (date_str,))
    for r in rows:
        r["first_seen"] = str(r["first_seen"])
        r["last_seen"]  = str(r["last_seen"])
    return jsonify({"date": date_str, "records": rows, "present": len(rows)})


@attendance_bp.route("/subject/<sid>", methods=["GET"])
def by_subject(sid):
    rows = query_all(
        "SELECT date, first_seen, last_seen, scan_count, status FROM attendance "
        "WHERE subject_id = %s ORDER BY date DESC LIMIT 60", (sid,))
    for r in rows:
        r["date"]       = str(r["date"])
        r["first_seen"] = str(r["first_seen"])
        r["last_seen"]  = str(r["last_seen"])
    return jsonify({"subject_id": sid, "records": rows})
