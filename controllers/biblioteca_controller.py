from datetime import datetime
from typing import Dict, List
import hashlib

from database.conexion import Database
from models.biblioteca import Biblioteca
from models.ficha import Ficha
from models.genero import Genero
from models.inventario import Inventario
from models.libro import Libro
from models.distribucion import Distribucion
from models.sala import Sala
from models.usuario import Usuario


class BibliotecaController:
    def __init__(self):
        self.conn = Database.get_connection()
        self.libro_model = Libro(self.conn)
        self.ficha_model = Ficha(self.conn)
        self.distribucion_model = Distribucion(self.conn)
        self.usuario_model = Usuario(self.conn)
        self.biblioteca_model = Biblioteca(self.conn)
        self.genero_model = Genero(self.conn)
        self.sala_model = Sala(self.conn)
        self.inventario_model = Inventario(self.conn)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def validar_credenciales(self, username: str, password: str):
        usuario = self.usuario_model.obtener_por_username(username.strip())
        if not usuario or not usuario["activo"]:
            return None
        if usuario["password_hash"] != self._hash_password(password):
            return None
        return {
            "id": usuario["id"],
            "username": usuario["username"],
            "nombre": usuario["nombre"],
            "role": usuario["role"],
        }

    def listar_usuarios(self):
        return self.usuario_model.listar()

    def crear_usuario(self, username: str, password: str, nombre: str, role: str, activo: int):
        password_hash = self._hash_password(password)
        return self.usuario_model.crear(username, password_hash, nombre, role, activo)

    def actualizar_usuario(self, usuario_id: int, nombre: str, role: str, activo: int, password: str = None):
        self.usuario_model.actualizar(usuario_id, nombre, role, activo)
        if password:
            self.usuario_model.actualizar_password(usuario_id, self._hash_password(password))

    def eliminar_usuario(self, usuario_id: int):
        self.usuario_model.eliminar(usuario_id)

    def obtener_usuario(self, usuario_id: int):
        return self.usuario_model.obtener_por_id(usuario_id)

    def roles_disponibles(self):
        return ["administrador", "operador"]

    def listar_generos(self):
        return self.genero_model.listar()

    def listar_salas(self):
        return self.sala_model.listar()

    def listar_bibliotecas(self, include_central: bool = True):
        return self.biblioteca_model.listar_destinos(include_central=include_central)

    def crear_genero(self, nombre: str, metodo_wely_code: str):
        return self.genero_model.crear(nombre, metodo_wely_code)

    def eliminar_genero(self, genero_id: int):
        self.genero_model.eliminar(genero_id)

    def crear_sala(self, nombre: str):
        return self.sala_model.crear(nombre)

    def eliminar_sala(self, sala_id: int):
        self.sala_model.eliminar(sala_id)

    def crear_biblioteca(self, nombre: str, parroquia: str, encargado: str, tipo: str):
        return self.biblioteca_model.crear(nombre, parroquia, encargado, tipo)

    def eliminar_biblioteca(self, biblioteca_id: int):
        self.biblioteca_model.eliminar(biblioteca_id)

    def cerrar(self):
        if self.conn:
            self.conn.close()

    def guardar_libro(
        self,
        num_registro: str,
        titulo: str,
        autor: str,
        genero_id: int,
        codigo_dewey: str,
        isbn: str,
        cantidad: int,
        dimensiones: str,
        peso: int,
        sala_id: int,
        observaciones: str,
    ) -> int:
        libro_id = self.libro_model.crear(
            num_registro,
            titulo,
            autor,
            genero_id,
            codigo_dewey,
            isbn,
            dimensiones,
            peso,
            observaciones,
        )
        self.inventario_model.inicializar_stock(libro_id, 1, sala_id, cantidad)
        return libro_id

    def listar_libros_pendientes(self):
        return self.libro_model.listar_pendientes()

    def listar_libros_catalogados(self):
        return self.libro_model.listar_catalogados()

    @staticmethod
    def calcular_cota(autor: str, titulo: str, codigo_dewey: str) -> str:
        iniciales = "".join([parte[0].upper() for parte in autor.split() if parte])
        primera_letra = titulo.strip()[:1].lower() if titulo else ""
        return f"{codigo_dewey.strip()}/{iniciales}{primera_letra}"

    def aprobar_y_generar_ficha(self, libro_id: int, cota: str) -> None:
        self.ficha_model.crear_o_actualizar(libro_id, cota)
        self.ficha_model.enviar_a_cola(libro_id, cota)

    def listar_destinos(self):
        return self.distribucion_model.listar_destinos()

    def obtener_stock_central(self, libro_id: int) -> int:
        return self.inventario_model.obtener_stock_total(libro_id, 1)

    def obtener_stock_central_por_sala(self, libro_id: int, sala_id: int) -> int:
        return self.inventario_model.obtener_stock(libro_id, 1, sala_id)

    def listar_salas_central(self, libro_id: int) -> List[Dict]:
        return self.inventario_model.listar_por_biblioteca_y_sala(libro_id, 1)

    def distribuir_libro(
        self,
        libro_id: int,
        cantidad: int,
        origen_sala_id: int,
        destino_biblioteca_id: int,
        destino_sala_id: int,
    ) -> str:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        disponible = self.inventario_model.obtener_stock(libro_id, 1, origen_sala_id)
        if cantidad > disponible:
            raise ValueError("No hay stock suficiente en la sala de origen seleccionada.")

        self.conn.execute("BEGIN TRANSACTION;")
        try:
            self.inventario_model.ajustar_stock(libro_id, 1, origen_sala_id, -cantidad)
            self.inventario_model.ajustar_stock(libro_id, destino_biblioteca_id, destino_sala_id, cantidad)
            distribucion_id, acta_numero = self.distribucion_model.registrar(destino_biblioteca_id, cantidad, "Sistema")
            self.distribucion_model.registrar_detalle(
                distribucion_id,
                libro_id,
                origen_sala_id,
                destino_sala_id,
                cantidad,
            )
            self.conn.commit()
            return acta_numero
        except Exception:
            self.conn.rollback()
            raise

    def generar_documentos(self, libro: dict, cantidad: int, destino: dict, acta_numero: str) -> dict:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        objeto = {
            "acta": (
                f"ACTA DE DISTRIBUCIÓN\n"
                f"Número: {acta_numero}\n"
                f"Fecha: {fecha}\n"
                f"Libro: {libro['titulo']}\n"
                f"Autor: {libro['autor']}\n"
                f"Género: {libro['genero']}\n"
                f"Cantidad enviada: {cantidad}\n"
                f"Destino: {destino['nombre']}"
            ),
            "comprobante": (
                f"COMPROBANTE DE CAJA / DESPACHO\n"
                f"Fecha: {fecha}\n"
                f"Destino: {destino['nombre']}\n"
                f"Cantidad de bultos: {cantidad}\n"
                f"Etiqueta: {libro['titulo']} - {libro['autor']}"
            ),
            "registro": (
                f"REGISTRO HISTÓRICO DE LA CENTRAL\n"
                f"Fecha: {fecha}\n"
                f"Título: {libro['titulo']}\n"
                f"Género: {libro['genero']}\n"
                f"Destino: {destino['nombre']}\n"
                f"Cantidad: {cantidad}\n"
                f"Acta: {acta_numero}"
            ),
        }
        return objeto

    def listar_cola_impresion(self):
        return self.ficha_model.listar_cola_impresion()

    def limpiar_cola_impresion(self):
        self.ficha_model.limpiar_cola()

    def reporte_mensual(self, year_month: str):
        return self.distribucion_model.reporte_mensual(year_month)

    def obtener_libro(self, libro_id: int):
        return self.libro_model.obtener(libro_id)

    def obtener_destino(self, destino_id: int):
        return self.distribucion_model.obtener_biblioteca(destino_id)
