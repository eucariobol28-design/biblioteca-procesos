from typing import List, Dict, Optional


class Sala:
    def __init__(self, conn):
        self.conn = conn

    def listar(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre FROM salas ORDER BY id;")
        return [dict(row) for row in cursor.fetchall()]

    def crear(self, nombre: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO salas (nombre) VALUES (?);", (nombre.strip(),))
        self.conn.commit()
        return cursor.lastrowid

    def eliminar(self, sala_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM salas WHERE id = ?;", (sala_id,))
        self.conn.commit()

    def obtener(self, sala_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre FROM salas WHERE id = ?;", (sala_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
