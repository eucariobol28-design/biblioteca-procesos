#!/usr/bin/env python3
"""
Script de migración no destructiva (con backup) para normalizar esquema y manejar columnas legacy.
Uso seguro: hace una copia de respaldo del archivo DB antes de hacer cambios destructivos.
Por defecto exige confirmación `--yes` para ejecutar.

Ejemplo:
  python3 scripts/migrate_normalize_schema.py --db path/to/biblioteca.db --yes
  BIBLIOTECA_DB can be used instead of --db

Nota: revisar y probar en staging antes de ejecutar en producción.
"""

import argparse
import shutil
import os
import sqlite3
import time


def backup_db(db_path: str) -> str:
    ts = time.strftime('%Y%m%d%H%M%S')
    backup_path = f"{db_path}.backup.{ts}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def run_sql(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()


def ensure_column(conn, table, column, definition):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r[1] for r in cur.fetchall()]
    if column not in cols:
        print(f"Adding column {table}.{column} -> {definition}")
        run_sql(conn, f"ALTER TABLE {table} ADD COLUMN {column} {definition};")
    else:
        print(f"Column {table}.{column} already exists")


def normalize(db_path: str, yes: bool):
    if not os.path.exists(db_path):
        raise FileNotFoundError(db_path)

    print("Creating backup...")
    backup = backup_db(db_path)
    print("Backup created at:", backup)

    if not yes:
        confirm = input("Proceed to alter schema? (type YES to continue): ")
        if confirm.strip() != "YES":
            print("Aborting")
            return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # Ensure libros has canonical columns
        ensure_column(conn, 'libros', 'origen_id', 'INTEGER NOT NULL DEFAULT 1')
        ensure_column(conn, 'libros', 'genero_id', 'INTEGER NOT NULL DEFAULT 1')
        ensure_column(conn, 'libros', 'cota_bibliografica', 'TEXT')

        # Ensure inventarios has sede_id legacy column (so models can write safely)
        ensure_column(conn, 'inventarios', 'sede_id', 'INTEGER NOT NULL DEFAULT 1')

        # Ensure distribuciones has legacy-safe columns
        ensure_column(conn, 'distribuciones', 'libro_id', 'INTEGER DEFAULT 0')
        ensure_column(conn, 'distribuciones', 'sede_origen_id', 'INTEGER DEFAULT 1')
        ensure_column(conn, 'distribuciones', 'sede_destino_id', 'INTEGER DEFAULT 1')
        ensure_column(conn, 'distribuciones', 'cantidad', 'INTEGER DEFAULT 0')
        ensure_column(conn, 'distribuciones', 'acta_numero', "TEXT DEFAULT ''")

        print("Schema normalization completed. Please review and run application tests.")
    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', help='Path to database file (overrides BIBLIOTECA_DB env)', default=os.environ.get('BIBLIOTECA_DB'))
    parser.add_argument('--yes', action='store_true', help='Confirm running migration non-interactively')
    args = parser.parse_args()

    dbp = args.db or os.environ.get('BIBLIOTECA_DB') or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'biblioteca.db')
    print('DB path:', dbp)
    normalize(dbp, args.yes)
