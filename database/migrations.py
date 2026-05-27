from sqlite3 import Connection
import hashlib


def _table_columns(conn: Connection, table_name: str):
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    return [row["name"] for row in cursor.fetchall()]


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def run_migrations(conn: Connection):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    def ensure_table(sql: str):
        cursor.execute(sql)

    def ensure_column(table_name: str, column_name: str, column_definition: str):
        existing_columns = _table_columns(conn, table_name)
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};"
            )

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS bibliotecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            parroquia TEXT NOT NULL DEFAULT '',
            encargado TEXT NOT NULL DEFAULT '',
            tipo TEXT NOT NULL DEFAULT 'Sede Satélite'
        );
        """
    )

    ensure_column("bibliotecas", "parroquia", "TEXT NOT NULL DEFAULT ''")
    ensure_column("bibliotecas", "encargado", "TEXT NOT NULL DEFAULT ''")

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS generos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            metodo_wely_code TEXT NOT NULL
        );
        """
    )

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );
        """
    )

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_registro TEXT UNIQUE,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            codigo_dewey TEXT NOT NULL,
            isbn TEXT NOT NULL,
            dimensiones TEXT NOT NULL,
            peso INTEGER NOT NULL,
            genero_id INTEGER NOT NULL DEFAULT 1,
            cota_bibliografica TEXT,
            observaciones TEXT,
            FOREIGN KEY (genero_id) REFERENCES generos(id) ON DELETE RESTRICT ON UPDATE CASCADE
        );
        """
    )

    ensure_column("libros", "num_registro", "TEXT")
    ensure_column("libros", "genero_id", "INTEGER NOT NULL DEFAULT 1")
    ensure_column("libros", "cota_bibliografica", "TEXT")
    ensure_column("libros", "observaciones", "TEXT")
    ensure_column("libros", "codigo_dewey", "TEXT NOT NULL DEFAULT ''")

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS inventarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            biblioteca_id INTEGER NOT NULL,
            sala_id INTEGER NOT NULL,
            cantidad_total INTEGER NOT NULL DEFAULT 0,
            cantidad_disponible INTEGER NOT NULL DEFAULT 0,
            UNIQUE(libro_id, biblioteca_id, sala_id),
            FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (biblioteca_id) REFERENCES bibliotecas(id) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE RESTRICT ON UPDATE CASCADE
        );
        """
    )

    ensure_column("inventarios", "biblioteca_id", "INTEGER NOT NULL DEFAULT 1")
    ensure_column("inventarios", "sala_id", "INTEGER NOT NULL DEFAULT 1")
    ensure_column("inventarios", "cantidad_total", "INTEGER NOT NULL DEFAULT 0")
    ensure_column("inventarios", "cantidad_disponible", "INTEGER NOT NULL DEFAULT 0")

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS distribuciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_acta TEXT NOT NULL UNIQUE,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            destino_biblioteca_id INTEGER NOT NULL,
            bultos INTEGER NOT NULL,
            responsable TEXT NOT NULL,
            FOREIGN KEY (destino_biblioteca_id) REFERENCES bibliotecas(id) ON DELETE RESTRICT ON UPDATE CASCADE
        );
        """
    )

    ensure_column("distribuciones", "num_acta", "TEXT NOT NULL")
    ensure_column("distribuciones", "fecha", "TEXT DEFAULT CURRENT_TIMESTAMP")
    ensure_column("distribuciones", "destino_biblioteca_id", "INTEGER NOT NULL DEFAULT 1")
    ensure_column("distribuciones", "bultos", "INTEGER NOT NULL DEFAULT 0")
    ensure_column("distribuciones", "responsable", "TEXT NOT NULL DEFAULT ''")

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS distribucion_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distribucion_id INTEGER NOT NULL,
            libro_id INTEGER NOT NULL,
            origen_sala_id INTEGER NOT NULL,
            destino_sala_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            FOREIGN KEY (distribucion_id) REFERENCES distribuciones(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (origen_sala_id) REFERENCES salas(id) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (destino_sala_id) REFERENCES salas(id) ON DELETE RESTRICT ON UPDATE CASCADE
        );
        """
    )

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS cola_impresion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            cota TEXT NOT NULL,
            FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """
    )

    ensure_table(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            role TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO bibliotecas (id, nombre, parroquia, encargado, tipo) VALUES (?, ?, ?, ?, ?);",
        [
            (1, "Biblioteca Central Rómulo Gallegos", "Catedral", "Equipo Central", "Sede Central"),
            (2, "Sede La Sabanita", "La Sabanita", "Encargado Sabanita", "Sede Satélite"),
            (3, "Sede Vista Hermosa", "Vista Hermosa", "Encargado Vista Hermosa", "Sede Satélite"),
            (4, "Sede Agua Salada", "Agua Salada", "Encargado Agua Salada", "Sede Satélite"),
        ],
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO salas (nombre) VALUES (?);",
        [
            ("Sala General",),
            ("Sala de Referencia",),
            ("Sala de Literatura",),
        ],
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO generos (nombre, metodo_wely_code) VALUES (?, ?);",
        [
            ("Literatura", "LIT"),
            ("Ciencias Sociales", "CS"),
            ("Ciencias Naturales", "CN"),
        ],
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO usuarios (username, password_hash, nombre, role, activo) VALUES (?, ?, ?, ?, ?);",
        [
            ("admin", _hash_password("Admin2026"), "Administrador", "administrador", 1),
            ("operador", _hash_password("Operador2026"), "Operador", "operador", 1),
        ],
    )

    cursor.execute(
        "DELETE FROM usuarios WHERE username = ? AND role = ?;",
        ("administrador", "administrador"),
    )

    conn.commit()
