from typing import List, Dict, Optional


class Biblioteca:
    def __init__(self, conn):
        self.conn = conn

    def listar(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nombre, parroquia, encargado, tipo FROM bibliotecas ORDER BY id;"
        )
        return [dict(row) for row in cursor.fetchall()]

    def crear(self, nombre: str, parroquia: str, encargado: str, tipo: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO bibliotecas (nombre, parroquia, encargado, tipo) VALUES (?, ?, ?, ?);",
            (nombre.strip(), parroquia.strip(), encargado.strip(), tipo.strip()),
        )
        self.conn.commit()
        return cursor.lastrowid

    def obtener(self, biblioteca_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nombre, parroquia, encargado, tipo FROM bibliotecas WHERE id = ?;",
            (biblioteca_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_destinos(self, include_central: bool = False) -> List[Dict]:
        cursor = self.conn.cursor()
        if include_central:
            cursor.execute(
                "SELECT id, nombre, parroquia, encargado, tipo FROM bibliotecas ORDER BY id;"
            )
        else:
            cursor.execute(
                "SELECT id, nombre, parroquia, encargado, tipo FROM bibliotecas WHERE id != 1 ORDER BY id;"
            )
        return [dict(row) for row in cursor.fetchall()]

    def eliminar(self, biblioteca_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM bibliotecas WHERE id = ?;", (biblioteca_id,))
        self.conn.commit()
