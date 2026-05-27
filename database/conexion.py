import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "biblioteca.db")


class Database:
    @staticmethod
    def get_connection():
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    @classmethod
    def initialize(cls):
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        with cls.get_connection() as conn:
            from database.migrations import run_migrations

            run_migrations(conn)
