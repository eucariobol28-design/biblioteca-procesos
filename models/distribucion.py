from datetime import datetime
from typing import Dict, List, Optional


def generar_acta_numero(numero_secuencia: int) -> str:
    year = datetime.now().year
    return f"ACTA-{year}-{numero_secuencia:03d}"


class Distribucion:
    def __init__(self, conn):
        self.conn = conn

    def listar_destinos(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre FROM bibliotecas WHERE id != 1 ORDER BY id;")
        return [dict(row) for row in cursor.fetchall()]

    def obtener_biblioteca(self, biblioteca_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nombre, parroquia, encargado, tipo FROM bibliotecas WHERE id = ?;",
            (biblioteca_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def contar_actas(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM distribuciones;")
        return int(cursor.fetchone()[0] or 0)

    def registrar(self, destino_biblioteca_id: int, bultos: int, responsable: str):
        cursor = self.conn.cursor()
        num_acta = generar_acta_numero(self.contar_actas() + 1)
        try:
            cursor.execute(
                "INSERT INTO distribuciones (num_acta, destino_biblioteca_id, bultos, responsable) VALUES (?, ?, ?, ?);",
                (num_acta, destino_biblioteca_id, bultos, responsable.strip()),
            )
            return cursor.lastrowid, num_acta
        except Exception:
            # Tabla antigua con columnas legacy (ej. libro_id, sede_origen_id, sede_destino_id, cantidad)
            # Intentar insertar proporcionando columnas legacy con valores por defecto seguros.
            cursor.execute(
                "INSERT INTO distribuciones (libro_id, sede_origen_id, sede_destino_id, cantidad, acta_numero, num_acta, destino_biblioteca_id, bultos, responsable) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (0, 1, destino_biblioteca_id, bultos, num_acta, num_acta, destino_biblioteca_id, bultos, responsable.strip()),
            )
            return cursor.lastrowid, num_acta

    def registrar_detalle(
        self,
        distribucion_id: int,
        libro_id: int,
        origen_sala_id: int,
        destino_sala_id: int,
        cantidad: int,
    ) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO distribucion_detalles (
                distribucion_id, libro_id, origen_sala_id, destino_sala_id, cantidad
            ) VALUES (?, ?, ?, ?, ?);
            """,
            (distribucion_id, libro_id, origen_sala_id, destino_sala_id, cantidad),
        )
        return cursor.lastrowid

    def reporte_balance(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT b.nombre AS biblioteca, s.nombre AS sala,
                   SUM(i.cantidad_total) AS total_libros,
                   SUM(i.cantidad_disponible) AS disponibles
            FROM inventarios i
            JOIN bibliotecas b ON i.biblioteca_id = b.id
            JOIN salas s ON i.sala_id = s.id
            GROUP BY b.nombre, s.nombre
            ORDER BY b.id, s.nombre;
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def reporte_mensual(self, year_month: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT b.nombre AS destino, s.nombre AS sala, g.nombre AS genero,
                   COUNT(DISTINCT l.id) AS titulos_enviados,
                   SUM(dd.cantidad) AS volumen_total
            FROM distribucion_detalles dd
            JOIN distribuciones d ON dd.distribucion_id = d.id
            JOIN libros l ON dd.libro_id = l.id
            LEFT JOIN generos g ON l.genero_id = g.id
            JOIN bibliotecas b ON d.destino_biblioteca_id = b.id
            JOIN salas s ON dd.destino_sala_id = s.id
            WHERE strftime('%Y-%m', d.fecha) = ?
            GROUP BY b.nombre, s.nombre, g.nombre
            ORDER BY b.nombre, s.nombre, g.nombre;
            """,
            (year_month,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def obtener_acta(self, distribucion_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, num_acta, fecha, destino_biblioteca_id, bultos, responsable FROM distribuciones WHERE id = ?;",
            (distribucion_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_detalles(self, distribucion_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT dd.id, dd.libro_id, dd.origen_sala_id, dd.destino_sala_id, dd.cantidad,
                   l.titulo, l.autor, l.cota_bibliografica
            FROM distribucion_detalles dd
            JOIN libros l ON dd.libro_id = l.id
            WHERE dd.distribucion_id = ?;
            """,
            (distribucion_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
