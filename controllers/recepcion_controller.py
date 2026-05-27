from models.libro import Libro
from models.inventario import Inventario
from models.biblioteca import Biblioteca


class RecepcionController:
    def __init__(self, conn):
        self.conn = conn
        self.libro_model = Libro(conn)
        self.inventario_model = Inventario(conn)
        self.biblioteca_model = Biblioteca(conn)

    def cargar_origenes(self):
        return self.biblioteca_model.obtener_origenes()

    def guardar_libro(self, titulo: str, autor: str, codigo_dewey: str, isbn: str, origen_id: int, cantidad: int):
        libro_id = self.libro_model.crear(titulo, autor, codigo_dewey, isbn, origen_id)
        self.inventario_model.inicializar_stock(libro_id, 1, cantidad)
        return libro_id
