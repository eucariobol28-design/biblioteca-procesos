from typing import Dict, List, Optional


class Libro:
    def __init__(self, conn):
        self.conn = conn

    def crear(
        self,
        num_registro: str,
        titulo: str,
        autor: str,
        genero_id: int,
        codigo_dewey: str,
        isbn: str,
        dimensiones: str,
        peso: int,
        observaciones: str,
    ) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO libros (
                num_registro, titulo, autor, genero_id, codigo_dewey,
                isbn, dimensiones, peso, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                num_registro.strip() if num_registro else None,
                titulo.strip(),
                autor.strip(),
                genero_id,
                codigo_dewey.strip(),
                isbn.strip(),
                dimensiones.strip(),
                peso,
                observaciones.strip(),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def listar_pendientes(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.num_registro, l.titulo, l.autor, l.codigo_dewey,
                   l.isbn, l.dimensiones, l.peso, l.observaciones,
                   g.nombre AS genero, f.cota
            FROM libros l
            LEFT JOIN generos g ON l.genero_id = g.id
            LEFT JOIN fichas f ON l.id = f.libro_id
            WHERE f.aprobada IS NULL OR f.aprobada = 0
            ORDER BY l.id ASC;
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def listar_catalogados(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.num_registro, l.titulo, l.autor, l.codigo_dewey,
                   l.isbn, l.dimensiones, l.peso, l.observaciones,
                   g.nombre AS genero, f.cota
            FROM libros l
            JOIN fichas f ON l.id = f.libro_id
            LEFT JOIN generos g ON l.genero_id = g.id
            WHERE f.aprobada = 1
            ORDER BY l.id DESC;
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def listar_todos(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.num_registro, l.titulo, l.autor, l.codigo_dewey,
                   l.isbn, l.dimensiones, l.peso, l.observaciones,
                   g.nombre AS genero, l.cota_bibliografica
            FROM libros l
            LEFT JOIN generos g ON l.genero_id = g.id
            ORDER BY l.id DESC;
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def obtener(self, libro_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT l.*, g.nombre AS genero, f.cota AS ficha_cota
            FROM libros l
            LEFT JOIN generos g ON l.genero_id = g.id
            LEFT JOIN fichas f ON l.id = f.libro_id
            WHERE l.id = ?;
            """,
            (libro_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def actualizar_cota(self, libro_id: int, cota: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE libros SET cota_bibliografica = ? WHERE id = ?;",
            (cota.strip(), libro_id),
        )
        self.conn.commit()
