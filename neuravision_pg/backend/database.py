"""
NEURAVISION — PostgreSQL Database Layer
Uses psycopg2 with a simple connection pool.
"""
import psycopg2
import psycopg2.pool
import psycopg2.extras
from flask import g
import logging

log = logging.getLogger(__name__)
_pool = None


def init_db(app):
    global _pool
    cfg = app.config
    _pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=cfg["DB_HOST"],
        port=cfg["DB_PORT"],
        user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"],
        dbname=cfg["DB_NAME"],
    )
    log.info("PostgreSQL connection pool initialised ✓")


def get_conn():
    if "db_conn" not in g:
        g.db_conn = _pool.getconn()
    return g.db_conn


def release_conn(e=None):
    conn = g.pop("db_conn", None)
    if conn:
        _pool.putconn(conn)


def query_one(sql, params=()):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None


def query_all(sql, params=()):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return [dict(r) for r in rows]


def execute(sql, params=(), commit=True):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql, params)
    last_id = None
    # Try to get last inserted id if it's an INSERT
    try:
        last_id = cur.fetchone()[0]
    except Exception:
        pass
    if commit:
        conn.commit()
    cur.close()
    return last_id
