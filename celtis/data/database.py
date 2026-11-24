import sqlite3
from ..config import DB_FILENAME, SCHEMA


class Database:
    def __init__(self, filename=DB_FILENAME):
        self.filename = filename
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        for stmt in SCHEMA:
            self.cursor.execute(stmt)
        self.conn.commit()
        return self

    def execute(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

    def reopen(self):
        self.close()
        return self.connect()