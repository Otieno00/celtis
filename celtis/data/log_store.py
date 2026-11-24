import json
from datetime import datetime


class LogStore:
    def __init__(self, db):
        self.db = db

    def save(self, category, label, data):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute(
            "INSERT INTO test_log (stored_at, category, label, data_json) "
            "VALUES (?,?,?,?)",
            (ts, category, label, json.dumps(data)))
        self.db.commit()
        return ts

    def load(self, category, limit=100):
        self.db.execute(
            "SELECT id, stored_at, label, data_json FROM test_log "
            "WHERE category=? ORDER BY stored_at DESC LIMIT ?",
            (category, limit))
        return self.db.fetchall()

    def delete(self, rid):
        self.db.execute("DELETE FROM test_log WHERE id=?", (rid,))
        self.db.commit()

    def delete_all(self, category):
        self.db.execute("DELETE FROM test_log WHERE category=?", (category,))
        self.db.commit()