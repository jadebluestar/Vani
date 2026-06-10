import sqlite3
import uuid
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger


# ─── In-memory cache (replaces Redis) ────────────────────────────────────────

class SimpleCache:
    """Simple in-memory cache (replaces Redis for prototyping)"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    async def get(self, key: str) -> Optional[str]:
        self._cleanup()
        return self._data.get(key)

    async def setex(self, key: str, seconds: int, value: str):
        self._data[key] = value
        self._expiry[key] = time.time() + seconds

    async def set(self, key: str, value: str):
        self._data[key] = value

    async def incr(self, key: str):
        val = int(self._data.get(key, 0))
        self._data[key] = str(val + 1)
        return val + 1

    async def expire(self, key: str, seconds: int):
        self._expiry[key] = time.time() + seconds

    async def delete(self, key: str):
        self._data.pop(key, None)
        self._expiry.pop(key, None)

    async def ping(self):
        return True

    def _cleanup(self):
        now = time.time()
        for key, exp in list(self._expiry.items()):
            if exp < now:
                self._data.pop(key, None)
                self._expiry.pop(key, None)


cache = SimpleCache()
redis_client = cache  # alias used by some routers


async def get_cache():
    return cache


async def init_cache():
    logger.info("Using in-memory cache (Redis not required)")


async def close_cache():
    logger.info("Cache closed")


# ─── SQLite local database (Supabase-compatible interface) ────────────────────

_SQLITE_DB_PATH = "vani_local.db"

_INIT_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    preferred_language TEXT DEFAULT 'kn',
    district TEXT,
    is_tutor INTEGER DEFAULT 0,
    tutor_verified INTEGER DEFAULT 0,
    coins_balance INTEGER DEFAULT 0,
    subscription_tier TEXT DEFAULT 'free',
    profile_picture TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    last_active TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    language TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    feedback TEXT,
    fluency_score REAL,
    pronunciation_score REAL,
    grammar_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS interviews (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    ai_feedback TEXT,
    question_category TEXT,
    difficulty_level INTEGER DEFAULT 1,
    score REAL,
    strengths TEXT,
    improvements TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tutors (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    languages TEXT NOT NULL,
    hourly_rate INTEGER NOT NULL,
    rating REAL DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    verified INTEGER DEFAULT 0,
    bio TEXT,
    availability TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tutor_sessions (
    id TEXT PRIMARY KEY,
    tutor_id TEXT,
    learner_id TEXT,
    status TEXT DEFAULT 'scheduled',
    scheduled_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    duration_minutes INTEGER,
    amount_paid INTEGER,
    feedback TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS progress (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    skill TEXT NOT NULL,
    score REAL DEFAULT 0,
    trend REAL DEFAULT 0,
    history TEXT DEFAULT '[]',
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS credentials (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    certificate_id TEXT UNIQUE NOT NULL,
    blockchain_tx_hash TEXT,
    level TEXT,
    skills TEXT,
    overall_score REAL DEFAULT 0,
    issued_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    verified INTEGER DEFAULT 0
);
"""

# Fields that should be parsed from JSON strings back to Python objects
_JSON_FIELDS = {
    "feedback", "ai_feedback", "strengths", "improvements",
    "history", "availability", "skills", "languages"
}


class QueryResult:
    """Mimics supabase-py's APIResponse."""

    def __init__(self, data: List[dict] = None, count: Optional[int] = None):
        self.data = data or []
        self.count = count


class SQLiteQueryBuilder:
    """Fluent query builder that replicates supabase-py's interface."""

    def __init__(self, db_path: str, table: str):
        self._db_path = db_path
        self._table = table
        self._conditions: List[tuple] = []
        self._order_col: Optional[str] = None
        self._order_desc: bool = False
        self._limit_val: Optional[int] = None
        self._offset_val: Optional[int] = None
        self._count_mode: bool = False
        self._operation: str = "select"
        self._payload: Optional[dict] = None

    # ── Filters ──────────────────────────────────────────────────────────────

    def select(self, columns: str = "*", count: Optional[str] = None):
        self._operation = "select"
        self._count_mode = count == "exact"
        return self

    def eq(self, column: str, value):
        self._conditions.append(("=", column, value))
        return self

    def neq(self, column: str, value):
        self._conditions.append(("!=", column, value))
        return self

    def gte(self, column: str, value):
        self._conditions.append((">=", column, value))
        return self

    def lte(self, column: str, value):
        self._conditions.append(("<=", column, value))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_col = column
        self._order_desc = desc
        return self

    def range(self, start: int, end: int):
        self._limit_val = end - start + 1
        self._offset_val = start
        return self

    def limit(self, n: int):
        self._limit_val = n
        return self

    # ── Mutations ─────────────────────────────────────────────────────────────

    def insert(self, data: dict):
        self._operation = "insert"
        self._payload = data
        return self

    def update(self, data: dict):
        self._operation = "update"
        self._payload = data
        return self

    def delete(self):
        self._operation = "delete"
        return self

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build_where(self):
        if not self._conditions:
            return "", []
        parts = []
        params = []
        for op, col, val in self._conditions:
            parts.append(f'"{col}" {op} ?')
            params.append(val)
        return "WHERE " + " AND ".join(parts), params

    def _serialize(self, data: dict) -> dict:
        result = {}
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                result[k] = json.dumps(v)
            elif isinstance(v, bool):
                result[k] = int(v)
            else:
                result[k] = v
        return result

    def _deserialize(self, row: dict) -> dict:
        result = {}
        for k, v in row.items():
            if k in _JSON_FIELDS and isinstance(v, str) and v:
                try:
                    result[k] = json.loads(v)
                except Exception:
                    result[k] = v
            elif k in ("is_tutor", "tutor_verified", "verified") and v is not None:
                result[k] = bool(v)
            else:
                result[k] = v
        return result

    def _connect(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Execute ───────────────────────────────────────────────────────────────

    def execute(self) -> QueryResult:
        conn = self._connect()
        cur = conn.cursor()
        try:
            if self._operation == "select":
                return self._do_select(cur)
            elif self._operation == "insert":
                return self._do_insert(cur, conn)
            elif self._operation == "update":
                return self._do_update(cur, conn)
            elif self._operation == "delete":
                return self._do_delete(cur, conn)
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Database constraint error: {e}")
        except Exception as e:
            conn.rollback()
            logger.error(f"SQLite [{self._table}.{self._operation}] error: {e}")
            raise
        finally:
            conn.close()

    def _do_select(self, cur) -> QueryResult:
        where, params = self._build_where()
        query = f'SELECT * FROM "{self._table}" {where}'
        if self._order_col:
            direction = "DESC" if self._order_desc else "ASC"
            query += f' ORDER BY "{self._order_col}" {direction}'
        if self._limit_val is not None:
            query += f' LIMIT {int(self._limit_val)}'
        if self._offset_val is not None:
            query += f' OFFSET {int(self._offset_val)}'
        cur.execute(query, params)
        rows = [self._deserialize(dict(r)) for r in cur.fetchall()]
        count = None
        if self._count_mode:
            count_q = f'SELECT COUNT(*) FROM "{self._table}" {where}'
            cur.execute(count_q, params)
            count = cur.fetchone()[0]
        return QueryResult(data=rows, count=count)

    def _do_insert(self, cur, conn) -> QueryResult:
        data = self._serialize(dict(self._payload))
        if "id" not in data or not data["id"]:
            data["id"] = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        if "created_at" not in data:
            data["created_at"] = now
        if self._table == "users" and "last_active" not in data:
            data["last_active"] = now
        if self._table == "progress" and "updated_at" not in data:
            data["updated_at"] = now

        cols = list(data.keys())
        placeholders = ",".join("?" for _ in cols)
        col_str = ",".join(f'"{c}"' for c in cols)
        vals = [data[c] for c in cols]
        cur.execute(
            f'INSERT INTO "{self._table}" ({col_str}) VALUES ({placeholders})',
            vals
        )
        conn.commit()
        cur.execute(f'SELECT * FROM "{self._table}" WHERE id = ?', [data["id"]])
        row = cur.fetchone()
        result_row = self._deserialize(dict(row)) if row else data
        return QueryResult(data=[result_row])

    def _do_update(self, cur, conn) -> QueryResult:
        data = self._serialize(dict(self._payload))
        where, params = self._build_where()
        set_parts = [f'"{k}" = ?' for k in data.keys()]
        vals = list(data.values()) + params
        cur.execute(
            f'UPDATE "{self._table}" SET {", ".join(set_parts)} {where}',
            vals
        )
        conn.commit()
        cur.execute(f'SELECT * FROM "{self._table}" {where}', params)
        rows = [self._deserialize(dict(r)) for r in cur.fetchall()]
        return QueryResult(data=rows)

    def _do_delete(self, cur, conn) -> QueryResult:
        where, params = self._build_where()
        cur.execute(f'DELETE FROM "{self._table}" {where}', params)
        conn.commit()
        return QueryResult(data=[])


class LocalDB:
    """SQLite-backed database with a supabase-py compatible interface."""

    def __init__(self, db_path: str = _SQLITE_DB_PATH):
        self._db_path = db_path
        self._init()

    def _init(self):
        conn = sqlite3.connect(self._db_path)
        try:
            conn.executescript(_INIT_SQL)
            conn.commit()
            logger.info(f"Local SQLite database ready: {self._db_path}")
        finally:
            conn.close()

    def table(self, name: str) -> SQLiteQueryBuilder:
        return SQLiteQueryBuilder(self._db_path, name)


# ─── Database selection: Supabase if reachable, else local SQLite ─────────────

def _try_supabase():
    try:
        from app.config import settings
        from supabase import create_client
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        client.table("users").select("id").limit(1).execute()
        logger.info("Connected to Supabase")
        return client
    except Exception as e:
        logger.warning(f"Supabase unreachable ({type(e).__name__}), falling back to local SQLite")
        return None


_sb = _try_supabase()
supabase = _sb if _sb is not None else LocalDB()


def get_supabase():
    return supabase
