from models.libro import Libro
from models.distribucion import Distribucion


class CatalogacionController:
    def __init__(self, conn):
        self.conn = conn
        self.libro_model = Libro(conn)
        self.distribucion_model = Distribucion(conn)

    def listar_libros(self):
        return self.libro_model.listar()

    @staticmethod
    def calcular_cota(autor: str, titulo: str, codigo_dewey: str) -> str:
        iniciales = ''.join([parte[0].upper() for parte in autor.split() if parte])
        primera_letra = titulo.strip()[:1].lower() if titulo else ''
        return f"{iniciales}{primera_letra}.{codigo_dewey.strip()}"

    def guardar_cota(self, libro_id: int, cota: str):
        self.libro_model.actualizar_cota(libro_id, cota)
        self.distribucion_model.insertar_cola_impresion(libro_id, cota)
