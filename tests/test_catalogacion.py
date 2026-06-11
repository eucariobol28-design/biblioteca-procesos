import os
import json
import pytest
from database.conexion import Database
from controllers.biblioteca_controller import BibliotecaController

# Use in-memory DB for tests
os.environ['BIBLIOTECA_DB'] = ':memory:'

@pytest.fixture(scope='function')
def ctrl():
    Database.initialize()
    return BibliotecaController()

def test_procesar_catalogacion_experta_minimal(ctrl):
    registro = {
        'titulo': 'La prueba del tiempo',
        'autor': 'Juan Pérez',
        'editorial': 'Editorial Test',
        'ciudad': 'Caracas',
        'year': '2021',
        'paginas': 240,
        'dimensiones': '20 x 13 cm',
        'isbn': '9780000000000',
        'observaciones': 'Sin daños',
        'genero': 'Historia'
    }
    res = ctrl.procesar_catalogacion_experta(registro)
    assert 'fase_1' in res and 'fase_2' in res and 'fase_3' in res and 'fase_4' in res
    assert res['fase_2']['isbn'] == registro['isbn']
    assert isinstance(res['fase_3']['cota'], str) and len(res['fase_3']['cota']) > 0

def test_aplicar_resultado_crea_ficha_y_cola(ctrl):
    # crear libro simple
    libro_id = ctrl.guardar_libro('TST-01','Libro Test','Ana Gómez',1,'800','9780000000001',1,'21x14x2',150,1,'')
    registro = {'titulo':'Libro Test','autor':'Ana Gómez','isbn':'9780000000001','paginas':100,'dimensiones':'21 x 14 cm','year':'2020'}
    res = ctrl.procesar_catalogacion_experta(registro)
    ctrl.aplicar_resultado_experto(libro_id, res, encolar=True)
    ficha = ctrl.ficha_model.obtener_por_libro(libro_id)
    assert ficha is not None
    cotas = ctrl.ficha_model.listar_cotas()
    assert any(c['libro_id'] == libro_id for c in cotas)
