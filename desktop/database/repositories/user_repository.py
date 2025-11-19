from datetime import datetime
from typing import List, Optional, Dict

from desktop.database.db import Database


class UserRepository:
    def __init__(self, db: Database):
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                organization TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            commit=True
        )

    def add_user(self, full_name: str, email: str, organization: str) -> int:
        cursor = self.db.execute(
            """
            INSERT INTO users (full_name, email, organization, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (full_name, email, organization, datetime.utcnow().isoformat()),
            commit=True
        )
        return cursor.lastrowid

    def list_users(self) -> List[Dict]:
        cursor = self.db.execute(
            "SELECT id, full_name, email, organization, created_at FROM users ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_user(self, user_id: int) -> Optional[Dict]:
        cursor = self.db.execute(
            "SELECT id, full_name, email, organization, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

