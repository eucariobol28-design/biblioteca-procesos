from typing import List, Dict, Optional


class Genero:
    def __init__(self, conn):
        self.conn = conn

    def listar(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre, metodo_wely_code FROM generos ORDER BY nombre;")
        return [dict(row) for row in cursor.fetchall()]

    def crear(self, nombre: str, metodo_wely_code: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO generos (nombre, metodo_wely_code) VALUES (?, ?);",
            (nombre.strip(), metodo_wely_code.strip()),
        )
        self.conn.commit()
        return cursor.lastrowid

    def eliminar(self, genero_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM generos WHERE id = ?;", (genero_id,))
        self.conn.commit()

    def obtener(self, genero_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre, metodo_wely_code FROM generos WHERE id = ?;", (genero_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
