from flask import Blueprint, current_app
from datetime import datetime, timedelta
import time
import routes.api_externa_conexion.get_login as get
from panelControlBroker.panelControl import enviar_leer_sheet

test_ejecutarHiloPanelControl = Blueprint('test_ejecutarHiloPanelControl', __name__)

def ejecutar_en_hilo(app, pais, user_id, accountCuenta, selector, hora_inicio, hora_fin):
    """
    Función para ejecutar el proceso durante el día simulado.
    """
    dia_actual = datetime.now().weekday()

    # Verificar si el día está en la lista de días de ejecución
    if dia_actual in [get.DIAS_SEMANA[dia] for dia in get.DIAS_EJECUCION]:
        while True:
            # Forzamos la hora actual para la simulación
            now = datetime.now()

            # Simulación del inicio del día
            if now.hour >= hora_inicio and now.hour < hora_fin:
                if len(get.diccionario_global_sheet) > 0:
                    if not get.luzThred_funcionando['luz']:
                        get.luzThred_funcionando['luz'] = True
                        get.luzThred_funcionando['hora'] = now.hour
                        get.luzThred_funcionando['minuto'] = now.minute
                        get.luzThred_funcionando['segundo'] = now.second

                    # Simulación de leer los datos de la hoja si está dentro del horario
                    if (now.hour >= 9 and now.hour < 20) or (now.hour == 20 and now.minute <= 5):
                        enviar_leer_sheet(app, pais, user_id, accountCuenta, 'hilo', selector)

            # Simulación de final del día y cierre
            if now.hour == 20 and 7 >= 6 and 23 <= 59 and get.luzMDH_funcionando:
                terminaConexionParaActualizarSheet(get.CUENTA_ACTUALIZAR_SHEET)
                get.symbols_sheet_valores.clear()
                get.sheet_manager = None
                get.autenticado_sheet = False
                break  # Termina la ejecución del día simulado
            time.sleep(1)  # Evitar que se sobrecargue el bucle

    else:
        time.sleep(86400)  # Espera de 24 horas si no es un día de ejecución

def terminaConexionParaActualizarSheet(account):   
    try:
        pyRofexInicializada = get.ConexionesBroker[account]['pyRofex']
        pyRofexInicializada.close_websocket_connection(environment=account)
        del get.ConexionesBroker[account]  # Eliminar la conexión del diccionario
    except KeyError:
        pyRofexInicializada = None
        print(f"La cuenta {account} no existe en ConexionesBroker.")
        
    get.precios_data.clear()
    return True

def simular_dias(app, pais, user_id, accountCuenta, selector, dias_simulados=2, hora_inicio=9, hora_fin=20):
    """
    Función para simular la ejecución en varios días.
    """
    for dia in range(dias_simulados):
        print(f"Simulando el día {dia + 1}")
        ejecutar_en_hilo(app, pais, user_id, accountCuenta, selector, hora_inicio, hora_fin)
        print(f"Día {dia + 1} terminado.")
        time.sleep(1)  # Simular una pausa entre días

# Ruta de prueba
@test_ejecutarHiloPanelControl.route('/test_ejecutarHiloPanelControl_test')
def entradaTest3():
    print('************************************************')
    dias_simulados = 2  # Define el número de días simulados
    app = current_app._get_current_object()   
    with app.app_context():
        for dia in range(dias_simulados):
            print(f'\n--- Test Case {dia + 1} ---')
            simular_dias(app, 'argentina', '1', '44593', 'produccion', dias_simulados=dias_simulados, hora_inicio=9, hora_fin=20)  # Ajusta los parámetros según sea necesario
