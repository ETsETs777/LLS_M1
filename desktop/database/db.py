import os
import sqlite3
from typing import Any, Iterable, Optional


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def execute(self, query: str, params: Iterable[Any] = (), commit: bool = False):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        if commit:
            self.connection.commit()
        return cursor

    def executemany(self, query: str, params_seq: Iterable[Iterable[Any]], commit: bool = False):
        cursor = self.connection.cursor()
        cursor.executemany(query, params_seq)
        if commit:
            self.connection.commit()
        return cursor

    def close(self):
        if self.connection:
            self.connection.close()


