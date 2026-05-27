from models.distribucion import Distribucion


class ImpresionController:
    def __init__(self, conn):
        self.conn = conn
        self.distribucion_model = Distribucion(conn)

    def listar_cola(self):
        return self.distribucion_model.listar_cola()

    def generar_planilla(self):
        items = self.distribucion_model.listar_cola()
        if not items:
            return []
        self.distribucion_model.limpiar_cola()
        return items
