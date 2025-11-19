from datetime import datetime
from typing import List, Optional, Dict

from desktop.database.db import Database


class UserRepository:
    def __init__(self, db: Database):
        self.db = db
        self._ensure_table()
        self._ensure_role_column()

    def _ensure_table(self):
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                organization TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL
            )
            """,
            commit=True
        )

    def _ensure_role_column(self):
        columns = self.db.execute("PRAGMA table_info(users)").fetchall()
        if not any(col['name'] == 'role' for col in columns):
            self.db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'", commit=True)

    def add_user(self, full_name: str, email: str, organization: str, role: str) -> int:
        cursor = self.db.execute(
            """
            INSERT INTO users (full_name, email, organization, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, organization, role, datetime.utcnow().isoformat()),
            commit=True
        )
        return cursor.lastrowid

    def list_users(self) -> List[Dict]:
        cursor = self.db.execute(
            "SELECT id, full_name, email, organization, role, created_at FROM users ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_user(self, user_id: int) -> Optional[Dict]:
        cursor = self.db.execute(
            "SELECT id, full_name, email, organization, role, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_role(self, user_id: int, role: str):
        self.db.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (role, user_id),
            commit=True
        )


