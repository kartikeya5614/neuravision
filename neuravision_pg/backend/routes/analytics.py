"""NEURAVISION — /api/analytics (Hybrid Edition)"""
from flask import Blueprint, jsonify
from database import query_all, query_one
from datetime import date, timedelta

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/summary", methods=["GET"])
def summary():
    today = date.today().isoformat()
    total   = query_one("SELECT COUNT(*) AS c FROM subjects WHERE is_active=TRUE")["c"]
    present = query_one("SELECT COUNT(*) AS c FROM attendance WHERE date=%s", (today,))["c"]
    return jsonify({
        "total_registered": total,
        "present_today":    present,
        "absent_today":     max(0, total-present),
        "attendance_pct":   round(present/max(total,1)*100, 1),
    })

@analytics_bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    rows = query_all(
        """SELECT a.subject_id, s.name, s.department, COUNT(*) AS days_present
           FROM attendance a JOIN subjects s ON s.subject_id=a.subject_id
           WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
           GROUP BY a.subject_id, s.name, s.department
           ORDER BY days_present DESC LIMIT 20""")
    return jsonify({"leaderboard": rows})
