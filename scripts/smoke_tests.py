import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.conexion import Database
from controllers.biblioteca_controller import BibliotecaController

print('Inicializando BD...')
Database.initialize()
ctrl = BibliotecaController()

print('1) Crear usuario de prueba...')
try:
    uid = ctrl.crear_usuario('testuser', 'TestPass123', 'Usuario Test', 'operador', 1)
    print('-> creado usuario id:', uid)
except Exception as e:
    print('-> error creando usuario (posible duplicado):', e)

print('2) Validar credenciales...')
print('-> valid:', ctrl.validar_credenciales('testuser', 'TestPass123'))

print('3) Crear genero y sala temporal...')
gid = ctrl.crear_genero('Ensayo', 'ENS')
sid = ctrl.crear_sala('Sala Test')
print('-> genero id, sala id:', gid, sid)

print('4) Registrar libro (recepción)...')
lib_id = ctrl.guardar_libro('SM-001', 'Manual de Pruebas', 'Alvarez Lopez', gid, '300', '9780000000002', 2, '21x14x3', 200, sid, 'estado: bueno')
print('-> libro id:', lib_id)

print('5) Ejecutar catalogación experta y aplicar...')
registro = {'titulo':'Manual de Pruebas', 'autor':'Alvarez Lopez', 'editorial':'Editorial X', 'ciudad':'Caracas', 'year':'2020', 'paginas':200, 'dimensiones':'21 x 14 cm', 'isbn':'9780000000002', 'observaciones':'Buen estado', 'genero':'Ensayo'}
res = ctrl.procesar_catalogacion_experta(registro)
print('-> cota sugerida:', res['fase_3']['cota'])
ctrl.aplicar_resultado_experto(lib_id, res, encolar=True)
print('-> ficha guardada:', ctrl.ficha_model.obtener_por_libro(lib_id))

print('6) Listar cola de impresión (últimos 5):')
cola = ctrl.ficha_model.listar_cotas()
print(cola[-5:])

print('7) Probar distribución (si hay stock suficiente)...')
# Aumentar stock en central si es necesario
stock = ctrl.obtener_stock_central(lib_id)
print('-> stock central actual:', stock)
try:
    if stock < 1:
        # ajustar inventario manualmente
        ctrl.inventario_model.inicializar_stock(lib_id, 1, sid, 5)
        print('-> stock inicializado a 5 en central/sala test')
    acta = ctrl.distribuir_libro(lib_id, 1, sid, 2, sid)
    print('-> distribucion acta:', acta)
except Exception as e:
    print('-> error distribuyendo (posible stock/ids):', e)

print('8) Reporte mensual (YYYY-MM)')
print(ctrl.reporte_mensual('2026-06'))

print('\nSmoke tests finalizados.')
