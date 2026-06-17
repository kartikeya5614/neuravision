"""NEURAVISION — /api/attendance"""
from flask import Blueprint, request, jsonify
from database import query_all, query_one, execute
from datetime import date

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/today", methods=["GET"])
def today():
    d = date.today().isoformat()
    rows = query_all(
        """SELECT a.subject_id, s.name, s.department,
                  a.first_seen, a.last_seen, a.scan_count, a.confidence, a.status
           FROM attendance a JOIN subjects s ON s.subject_id=a.subject_id
           WHERE a.date=%s ORDER BY a.first_seen""", (d,))
    for r in rows:
        r["first_seen"]=str(r["first_seen"]); r["last_seen"]=str(r["last_seen"])
    return jsonify({"date": d, "records": rows, "present": len(rows)})

@attendance_bp.route("/date/<date_str>", methods=["GET"])
def by_date(date_str):
    rows = query_all(
        """SELECT a.subject_id, s.name, a.first_seen, a.last_seen, a.scan_count, a.status
           FROM attendance a JOIN subjects s ON s.subject_id=a.subject_id
           WHERE a.date=%s ORDER BY a.first_seen""", (date_str,))
    for r in rows:
        r["first_seen"]=str(r["first_seen"]); r["last_seen"]=str(r["last_seen"])
    return jsonify({"date": date_str, "records": rows, "present": len(rows)})

@attendance_bp.route("/subject/<sid>", methods=["GET"])
def by_subject(sid):
    rows = query_all(
        "SELECT date,first_seen,last_seen,scan_count,status FROM attendance "
        "WHERE subject_id=%s ORDER BY date DESC LIMIT 60", (sid,))
    for r in rows:
        r["date"]=str(r["date"]); r["first_seen"]=str(r["first_seen"]); r["last_seen"]=str(r["last_seen"])
    return jsonify({"subject_id": sid, "records": rows})
