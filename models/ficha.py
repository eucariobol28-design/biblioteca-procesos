from typing import List, Dict, Optional


class Ficha:
    def __init__(self, conn):
        self.conn = conn

    def crear_o_actualizar(self, libro_id: int, cota: str) -> None:
        cursor = self.conn.cursor()
        existing = cursor.execute(
            "SELECT id FROM fichas WHERE libro_id = ?;",
            (libro_id,),
        ).fetchone()
        if existing:
            cursor.execute(
                """
                UPDATE fichas
                SET cota = ?, aprobada = 1, actualizado_en = CURRENT_TIMESTAMP
                WHERE libro_id = ?;
                """,
                (cota.strip(), libro_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO fichas (libro_id, cota, aprobada)
                VALUES (?, ?, 1);
                """,
                (libro_id, cota.strip()),
            )
        self.conn.commit()

    def obtener_por_libro(self, libro_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, libro_id, cota, aprobada, creado_en, actualizado_en FROM fichas WHERE libro_id = ?;",
            (libro_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_cola_impresion(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT ci.id, ci.libro_id, ci.cota, l.titulo, l.autor, g.nombre AS genero
            FROM cola_impresion ci
            JOIN libros l ON ci.libro_id = l.id
            LEFT JOIN generos g ON l.genero_id = g.id
            ORDER BY ci.id;
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def enviar_a_cola(self, libro_id: int, cota: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO cola_impresion (libro_id, cota) VALUES (?, ?);",
            (libro_id, cota.strip()),
        )
        self.conn.commit()

    def limpiar_cola(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cola_impresion;")
        self.conn.commit()

    def listar_cotas(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, libro_id, cota, creado_en FROM cola_impresion ORDER BY creado_en;"
        )
        return [dict(row) for row in cursor.fetchall()]
