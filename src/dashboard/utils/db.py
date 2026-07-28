import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "nifty100.db"


class Database:
    def __init__(self):
        self.db_path = DB_PATH

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_dataframe(self, query, params=None):
        conn = self.connect()
        try:
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def execute(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()


db = Database()