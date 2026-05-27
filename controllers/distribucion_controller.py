from models.biblioteca import Biblioteca
from models.libro import Libro
from models.inventario import Inventario
from models.distribucion import Distribucion


class DistribucionController:
    def __init__(self, conn):
        self.conn = conn
        self.biblioteca_model = Biblioteca(conn)
        self.libro_model = Libro(conn)
        self.inventario_model = Inventario(conn)
        self.distribucion_model = Distribucion(conn)

    def listar_libros(self):
        return self.libro_model.listar()

    def listar_destinos(self):
        return self.biblioteca_model.obtener_sedes(include_central=False)

    def obtener_stock_central(self, libro_id: int) -> int:
        return self.inventario_model.obtener_stock(libro_id, 1)

    def enviar_a_sede(self, libro_id: int, cantidad: int, sede_destino_id: int) -> str:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        acta_numero = self.distribucion_model.registrar_distribucion(
            libro_id,
            cantidad,
            sede_origen_id=1,
            sede_destino_id=sede_destino_id,
            inventario_model=self.inventario_model,
        )
        return acta_numero
