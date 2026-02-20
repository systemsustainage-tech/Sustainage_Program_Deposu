import secrets
import time
from typing import Dict, List, Tuple
from backend.core.database_manager import DatabaseManager


def _ensure_table(conn) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS temp_access_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            username TEXT,
            purpose TEXT,
            created_at INTEGER,
            expires_at INTEGER,
            max_uses INTEGER,
            use_count INTEGER DEFAULT 0,
            last_used_at INTEGER,
            revoked INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()

def generate_temp_token(db_path: str, username: str, duration_minutes: int = 30, max_uses: int = 1, purpose: str | None = None, created_by_user_id: int | None = None) -> Tuple[bool, str, str]:
    db = DatabaseManager(db_path)
    with db.get_connection() as conn:
        _ensure_table(conn)
        cur = conn.cursor()
        token = secrets.token_urlsafe(48)
        now = int(time.time())
        exp = now + int(duration_minutes * 60)
        cur.execute(
            "INSERT INTO temp_access_tokens(token, username, purpose, created_at, expires_at, max_uses, use_count, revoked) VALUES(?,?,?,?,?,?,?,0)",
            (token, username, purpose or "", now, exp, int(max_uses), 0)
        )
        conn.commit()
    return True, "token oluşturuldu", token

def verify_temp_token(db_path: str, token: str) -> Tuple[bool, str, Dict | None]:
    db = DatabaseManager(db_path)
    with db.get_connection() as conn:
        _ensure_table(conn)
        cur = conn.cursor()
        cur.execute("SELECT username, purpose, created_at, expires_at, max_uses, use_count, revoked FROM temp_access_tokens WHERE token=?", (token,))
        row = cur.fetchone()
        if not row:
            return False, "bulunamadı", None
        now = int(time.time())
        if int(row[6] or 0) == 1:
            return False, "iptal", None
        if int(row[3]) < now:
            return False, "süre doldu", None
        if int(row[5]) >= int(row[4]):
            return False, "kullanım doldu", None
        cur.execute("UPDATE temp_access_tokens SET use_count=use_count+1, last_used_at=? WHERE token=?", (now, token))
        conn.commit()
        info = {
            "username": row[0],
            "purpose": row[1],
            "created_at": row[2],
            "expires_at": row[3],
            "max_uses": row[4],
            "use_count": row[5] + 1,
        }
    return True, "ok", info

def revoke_temp_token(db_path: str, token: str) -> Tuple[bool, str]:
    db = DatabaseManager(db_path)
    with db.get_connection() as conn:
        _ensure_table(conn)
        cur = conn.cursor()
        cur.execute("UPDATE temp_access_tokens SET revoked=1 WHERE token=?", (token,))
        conn.commit()
        ok = cur.rowcount > 0
    return ok, "ok" if ok else "bulunamadı"

def list_active_tokens(db_path: str, username: str | None = None) -> List[Dict]:
    db = DatabaseManager(db_path)
    with db.get_connection() as conn:
        _ensure_table(conn)
        # conn.row_factory = sqlite3.Row  # DatabaseManager might handle this or we iterate manually
        # To match previous behavior precisely:
        cur = conn.cursor()
        q = "SELECT username, purpose, created_at, last_used_at, use_count, max_uses, revoked FROM temp_access_tokens WHERE revoked=0"
        p: List = []
        if username:
            q += " AND username=?"
            p.append(username)
        cur.execute(q, p)
        # Manually map since we don't use sqlite3.Row
        rows = cur.fetchall()
        
    return [{
        "username": r[0],
        "purpose": r[1],
        "created_at": r[2],
        "last_used_at": r[3],
        "use_count": r[4],
        "max_uses": r[5],
    } for r in rows]
