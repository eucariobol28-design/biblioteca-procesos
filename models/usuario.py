from typing import List, Dict, Optional


class Usuario:
    def __init__(self, conn):
        self.conn = conn

    def listar(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username, nombre, role, activo FROM usuarios ORDER BY id;"
        )
        return [dict(row) for row in cursor.fetchall()]

    def obtener_por_username(self, username: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, nombre, role, activo FROM usuarios WHERE username = ?;",
            (username,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def obtener_por_id(self, usuario_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username, nombre, role, activo FROM usuarios WHERE id = ?;",
            (usuario_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def crear(self, username: str, password_hash: str, nombre: str, role: str, activo: int = 1) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, nombre, role, activo) VALUES (?, ?, ?, ?, ?);",
            (username.strip(), password_hash, nombre.strip(), role.strip(), activo),
        )
        self.conn.commit()
        return cursor.lastrowid

    def actualizar(self, usuario_id: int, nombre: str, role: str, activo: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET nombre = ?, role = ?, activo = ? WHERE id = ?;",
            (nombre.strip(), role.strip(), activo, usuario_id),
        )
        self.conn.commit()

    def actualizar_password(self, usuario_id: int, password_hash: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET password_hash = ? WHERE id = ?;",
            (password_hash, usuario_id),
        )
        self.conn.commit()

    def eliminar(self, usuario_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?;", (usuario_id,))
        self.conn.commit()
