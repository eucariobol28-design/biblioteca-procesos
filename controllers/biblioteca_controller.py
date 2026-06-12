from datetime import datetime
from typing import Dict, List
import hashlib
import re
import time

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

    def crear_o_actualizar_biblioteca(self, nombre: str, parroquia: str = "", encargado: str = "", tipo: str = "Sede Satélite") -> int:
        """Crea una nueva biblioteca o actualiza la existente por nombre. Devuelve el id."""
        existing = self.biblioteca_model.obtener_por_nombre(nombre)
        if existing:
            self.biblioteca_model.actualizar(existing["id"], nombre, parroquia or existing.get("parroquia", ""), encargado or existing.get("encargado", ""), tipo or existing.get("tipo", "Sede Satélite"))
            return existing["id"]
        else:
            return self.biblioteca_model.crear(nombre, parroquia or "", encargado or "", tipo or "Sede Satélite")

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

    def procesar_catalogacion_experta(self, registro: Dict) -> Dict:
        """Procesa un registro de recepción y devuelve las fases de catalogación.

        `registro` puede contener claves: num_registro, titulo, autor, editorial,
        ciudad, year, paginas, dimensiones, isbn, cantidad, observaciones, genero
        """
        # --- Fase 1: Análisis Técnico y Registro ---
        num_registro = registro.get("num_registro") or f"ACQ-{int(time.time())}"
        sello_paginas = ["Portada", "Página 17"]
        observ = (registro.get("observaciones") or "").lower()
        problemas = [k for k in ["dañado", "rasgado", "moho", "humedad", "rotura", "manchado"] if k in observ]
        dictamen = "Estado óptimo" if not problemas else f"Requiere atención técnica: {', '.join(problemas)}"

        fase1 = {
            "num_adquisicion": num_registro,
            "sellado_en": sello_paginas,
            "dictamen_examen_tecnico": dictamen,
        }

        # --- Fase 2: Catalogación Descriptiva ---
        titulo_raw = (registro.get("titulo") or "").strip()
        # separar titulo y subtitulo
        subtitle = None
        for sep in [":", " - ", " / "]:
            if sep in titulo_raw:
                main_title, subtitle = [p.strip() for p in titulo_raw.split(sep, 1)]
                break
        else:
            main_title = titulo_raw

        autor_raw = (registro.get("autor") or "").strip()
        def formatear_autor(a: str) -> str:
            if "," in a:
                return " ".join([p.strip() for p in a.split(",")]) if a else a
            parts = a.split()
            if len(parts) == 0:
                return ""
            if len(parts) == 1:
                return parts[0]
            surname = parts[-1]
            given = " ".join(parts[:-1])
            return f"{surname}, {given}"

        autor_form = formatear_autor(autor_raw)

        # Pie de imprenta: intentar extraer año y editorial
        editorial = registro.get("editorial") or registro.get("editor") or ""
        ciudad = registro.get("ciudad") or ""
        year = registro.get("year") or registro.get("anio") or None
        if not year:
            m = re.search(r"(19|20)\d{2}", registro.get("editorial", "") + " " + (registro.get("observaciones") or ""))
            year = m.group(0) if m else None

        paginas = registro.get("paginas") or registro.get("numero_paginas") or None
        if paginas and isinstance(paginas, (int, float)):
            paginas_str = f"{int(paginas)} p."
        else:
            paginas_str = f"{paginas} p." if paginas else "n.p."

        dimensiones = registro.get("dimensiones") or "21 x 14 cm"
        isbn = registro.get("isbn") or ""

        fase2 = {
            "autor": autor_form,
            "titulo_principal": main_title,
            "subtitulo": subtitle,
            "pie_de_imprenta": {
                "ciudad": ciudad,
                "editorial": editorial,
                "ano": year,
            },
            "descripcion_fisica": {
                "paginas": paginas_str,
                "dimensiones": dimensiones,
            },
            "isbn": isbn,
        }

        # --- Fase 3: Catalogación Analítica y Clasificación ---
        texto_para_materias = f"{main_title} {autor_raw} {registro.get('genero','') or ''}".lower()
        stopwords = set(["el","la","los","las","de","y","en","a","del","para","con","por","un","una","su","se"])
        words = [re.sub(r"[^\w]", "", w).lower() for w in main_title.split()]
        keywords = [w for w in words if w and w not in stopwords][:3]
        materias = [w.capitalize() for w in keywords]

        dewey = "000"
        if any(k in texto_para_materias for k in ["literatur", "novel", "poe", "poema"]):
            dewey = "800"
        elif any(k in texto_para_materias for k in ["ciencia", "naturale", "biolog", "quim"]):
            dewey = "500"
        elif any(k in texto_para_materias for k in ["historia", "histór", "pasado"]):
            dewey = "900"
        elif any(k in texto_para_materias for k in ["inform", "comput", "program"]):
            dewey = "004"

        # apellido para cota
        surname = autor_form.split(",")[0] if "," in autor_form else (autor_form.split()[-1] if autor_form else "XXX")
        year_for_cota = year or (str(datetime.now().year))
        cota = f"{dewey}/{surname[:3].upper()}/{year_for_cota}"

        fase3 = {
            "materias": materias,
            "dewey": dewey,
            "cota": cota,
        }

        # --- Fase 4: Procesamiento Físico y Salida ---
        spine_label = f"{cota}\n{surname.upper()}\n{year_for_cota}"
        opac = {"cargado": True, "mensaje": "Ingreso simulado en OPAC (local)"}

        fase4 = {
            "etiqueta_lomo": spine_label,
            "opac": opac,
        }

        resultado = {
            "fase_1": fase1,
            "fase_2": fase2,
            "fase_3": fase3,
            "fase_4": fase4,
        }

        return resultado

    def aplicar_resultado_experto(self, libro_id: int, resultado: Dict, encolar: bool = True) -> None:
        """Aplica el resultado de catalogación experta: guarda la cota en libros y crea/actualiza ficha.

        Si `encolar` es True, envía la cota a la cola de impresión.
        """
        cota = resultado.get("fase_3", {}).get("cota")
        if not cota:
            raise ValueError("Resultado experto no contiene una cota válida.")
        # actualizar cota en libros
        self.libro_model.actualizar_cota(libro_id, cota)
        # crear o actualizar ficha y marcar aprobada
        self.ficha_model.crear_o_actualizar(libro_id, cota)
        if encolar:
            self.ficha_model.enviar_a_cola(libro_id, cota)
