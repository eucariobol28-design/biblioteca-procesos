import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import Database
from controllers.biblioteca_controller import BibliotecaController

Database.initialize()
ctrl = BibliotecaController()

registro = {
    "num_registro": "",
    "titulo": "Cien Años de Soledad: Edición conmemorativa",
    "autor": "García Márquez, Gabriel",
    "editorial": "Editorial Sudamericana",
    "ciudad": "Bogotá",
    "year": "1967",
    "paginas": 417,
    "dimensiones": "20 x 13 cm",
    "isbn": "9780307474728",
    "cantidad": 1,
    "observaciones": "Buen estado, sin daños visibles",
    "genero": "Literatura",
}

resultado = ctrl.procesar_catalogacion_experta(registro)
import pprint, json
print('\n--- Resultado de catalogación experta (demo) ---')
pp = pprint.pformat(resultado, width=120)
print(pp)
print('\n--- JSON ---')
print(json.dumps(resultado, ensure_ascii=False, indent=2))
