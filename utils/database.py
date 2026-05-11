import sqlite3
import os
import threading
from datetime import datetime

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "mint_bot.db")


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._conn_lock = threading.Lock()
        os.makedirs(DATA_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.setup()

    def setup(self):
        with self._conn_lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    money INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    gems INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    last_daily TEXT DEFAULT NULL
                )
            """)
            self.conn.commit()

    def get_user(self, user_id):
        with self._conn_lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_user(self, user_id, data):
        with self._conn_lock:
            cursor = self.conn.cursor()
            fields = []
            values = []
            for key, value in data.items():
                if key in ("xp", "level", "money", "bank", "gems", "total_messages", "last_daily"):
                    fields.append(f"{key} = ?")
                    values.append(value)
            if not fields:
                return
            values.append(user_id)
            cursor.execute(f"""
                INSERT INTO users (user_id, {', '.join(f'{k}' for k in data.keys())})
                VALUES ({', '.join('?' for _ in data.keys())})
                ON CONFLICT(user_id) DO UPDATE SET
                    {', '.join(f'{k} = excluded.{k}' for k in data.keys())}
            """, (user_id, *data.values()))
            self.conn.commit()

    def get_leaderboard_by_xp(self, limit=10):
        with self._conn_lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT user_id, xp, level FROM users
                ORDER BY level DESC, xp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_economy_leaderboard(self, limit=10):
        with self._conn_lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT user_id, money, bank, (money + bank) AS total
                FROM users
                ORDER BY total DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
