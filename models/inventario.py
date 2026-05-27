from typing import Dict, List, Optional


class Inventario:
    def __init__(self, conn):
        self.conn = conn

    def inicializar_stock(self, libro_id: int, biblioteca_id: int, sala_id: int, cantidad: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO inventarios (libro_id, biblioteca_id, sala_id, cantidad_total, cantidad_disponible) VALUES (?, ?, ?, ?, ?);",
            (libro_id, biblioteca_id, sala_id, cantidad, cantidad),
        )
        self.conn.commit()

    def ajustar_stock(self, libro_id: int, biblioteca_id: int, sala_id: int, cantidad_delta: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT cantidad_total, cantidad_disponible FROM inventarios WHERE libro_id = ? AND biblioteca_id = ? AND sala_id = ?;",
            (libro_id, biblioteca_id, sala_id),
        )
        row = cursor.fetchone()
        total = row[0] if row else 0
        disponible = row[1] if row else 0
        nuevo = disponible + cantidad_delta
        if nuevo < 0:
            raise ValueError("Stock insuficiente en inventario")
        total_nuevo = total + cantidad_delta if row else cantidad_delta
        cursor.execute(
            "INSERT OR REPLACE INTO inventarios (libro_id, biblioteca_id, sala_id, cantidad_total, cantidad_disponible) VALUES (?, ?, ?, ?, ?);",
            (libro_id, biblioteca_id, sala_id, total_nuevo, nuevo),
        )
        self.conn.commit()

    def obtener_stock(self, libro_id: int, biblioteca_id: int, sala_id: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT cantidad_disponible FROM inventarios WHERE libro_id = ? AND biblioteca_id = ? AND sala_id = ?;",
            (libro_id, biblioteca_id, sala_id),
        )
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    def obtener_stock_total(self, libro_id: int, biblioteca_id: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT SUM(cantidad_disponible) FROM inventarios WHERE libro_id = ? AND biblioteca_id = ?;",
            (libro_id, biblioteca_id),
        )
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0

    def listar_por_biblioteca_y_sala(self, libro_id: int, biblioteca_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT i.libro_id, i.biblioteca_id, i.sala_id, i.cantidad_total, i.cantidad_disponible,
                   s.nombre AS sala
            FROM inventarios i
            JOIN salas s ON i.sala_id = s.id
            WHERE i.libro_id = ? AND i.biblioteca_id = ?
            ORDER BY s.nombre;
            """,
            (libro_id, biblioteca_id),
        )
        return [dict(row) for row in cursor.fetchall()]
