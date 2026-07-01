import sqlite3, os, json
from datetime import datetime, timezone

# On Render, use the persistent disk at /data; locally use the project folder
if os.environ.get("RENDER"):
    DB = "/data/imu_data.db"
else:
    DB = os.path.join(os.path.dirname(__file__), "imu_data.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            feature     TEXT    NOT NULL,
            started_at  TEXT    NOT NULL,
            ended_at    TEXT,
            duration_s  REAL,
            reading_count INTEGER DEFAULT 0,
            notes       TEXT
        );
        CREATE TABLE IF NOT EXISTS imu_readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL REFERENCES sessions(id),
            t           REAL    NOT NULL,
            yaw         REAL    NOT NULL,
            pitch       REAL    NOT NULL,
            roll        REAL    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS session_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL REFERENCES sessions(id),
            t           REAL    NOT NULL,
            event_type  TEXT    NOT NULL,
            payload     TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_readings_session ON imu_readings(session_id);
        CREATE INDEX IF NOT EXISTS idx_events_session   ON session_events(session_id);
    """)
    conn.commit()
    conn.close()


def session_create(feature: str, started_at: str = None) -> int:
    conn = get_db()
    ts = started_at or datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO sessions (feature, started_at) VALUES (?, ?)",
        (feature, ts)
    )
    session_id = cur.lastrowid
    conn.commit(); conn.close()
    return session_id


def session_end(session_id: int, readings: list, ended_at: str = None):
    conn = get_db()
    now = ended_at or datetime.now(timezone.utc).isoformat()
    row = conn.execute("SELECT started_at FROM sessions WHERE id=?", (session_id,)).fetchone()
    duration = None
    if row:
        from datetime import datetime as dt
        try:
            duration = (dt.fromisoformat(now) - dt.fromisoformat(row["started_at"])).total_seconds()
        except Exception:
            pass

    if readings:
        conn.executemany(
            "INSERT INTO imu_readings (session_id, t, yaw, pitch, roll) VALUES (?,?,?,?,?)",
            [(session_id, r.get("t", 0), r.get("yaw", 0), r.get("pitch", 0), r.get("roll", 0))
             for r in readings]
        )

    conn.execute(
        "UPDATE sessions SET ended_at=?, duration_s=?, reading_count=? WHERE id=?",
        (now, duration, len(readings), session_id)
    )
    conn.commit(); conn.close()


def session_add_event(session_id: int, event_type: str, payload: dict = None, t: float = None):
    if t is None:
        import time; t = time.time()
    conn = get_db()
    conn.execute(
        "INSERT INTO session_events (session_id, t, event_type, payload) VALUES (?,?,?,?)",
        (session_id, t, event_type, json.dumps(payload) if payload else None)
    )
    conn.commit(); conn.close()


def sessions_list():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY id DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def session_get(session_id: int):
    conn = get_db()
    session  = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    readings = conn.execute(
        "SELECT t, yaw, pitch, roll FROM imu_readings WHERE session_id=? ORDER BY t",
        (session_id,)
    ).fetchall()
    events   = conn.execute(
        "SELECT t, event_type, payload FROM session_events WHERE session_id=? ORDER BY t",
        (session_id,)
    ).fetchall()
    conn.close()
    if not session:
        return None
    return {
        "session":  dict(session),
        "readings": [dict(r) for r in readings],
        "events":   [dict(e) for e in events],
    }
