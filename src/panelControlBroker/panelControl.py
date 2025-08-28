# Creating  Routes
from pipes import Template
from unittest import result
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import and_
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify, abort,current_app
from models.instrumento import Instrumento
from utils.db_session import get_db_session 
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
import re
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.orden import Orden
from models.unidadTrader import UnidadTrader
import threading
import strategies.datoSheet as datoSheet
from strategies.caucionador.caucion import caucionar 
import time
from datetime import datetime
import tokens.token as Token
from queue import Queue


panelControl = Blueprint('panelControl',__name__)

# Crear una cola global para la comunicación
lock = threading.Lock()

def obtener_pais():
    ip = request.remote_addr
    response = requests.get(f'http://ipinfo.io/{ip}')
    data = response.json()
    pais = data.get('country')
    return f'El país de la conexión es: {pais}'


@panelControl.route('/panel_control_sin_cuenta/')
def panel_control_sin_cuenta():
        
    pais = request.args.get('country')
    layout = request.args.get('layoutOrigen')
    usuario_id = request.args.get('usuario_id')
    access_token = request.args.get('access_token')
    refresh_token = request.args.get('refresh_token')
    selector = request.args.get('selector')
    account = ''
    ####COLOCADA ESTA RESPUESTA CUANDO NO HAY DATOS PARA CARGAR DESDE SHEET####
   # return render_template('notificaciones/noPoseeDatos.html',layout=layout)
   
   
    if access_token and Token.validar_expiracion_token(access_token=access_token):
        app = current_app._get_current_object()       
        respuesta =  llenar_diccionario_cada_15_segundos_sheet(app,pais,usuario_id,account,selector)
        
        datos_desempaquetados = procesar_datos(app,pais, account,usuario_id,selector)
        if layout == 'layout_dpi':
           return render_template("/paneles/panelSheetCompletoSinCuenta.html", datos = datos_desempaquetados)
        if layout == 'layout_signal':
            return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
        if layout == 'layout': 
            return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
        if layout == 'layout' or layout == 'layoutConexBroker':        
            return render_template("/paneles/panelDeControlBroker.html", datos = datos_desempaquetados)
        return "Página no encontrada"  # Cambia el mensaje según sea necesario
    else:
        return render_template('usuarios/logOutSystem.html',layout='layout')     
  

@panelControl.route("/panel_control/")
def panel_control():
     pais = request.args.get('country')
     layout = request.args.get('layoutOrigen')
     usuario_id = request.args.get('usuario_id')
     access_token = request.args.get('access_token')
     accountCuenta = request.args.get('account')
     selector =  request.args.get('selector')
     if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
        try:  
                if access_token != 'access_dpi_token_usuario_anonimo':
                    user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                else:
                    user_id = usuario_id
                respuesta =  llenar_diccionario_cada_15_segundos_sheet(app,pais,user_id,accountCuenta,selector)
                
                datos_desempaquetados = procesar_datos(app,pais, accountCuenta,usuario_id,selector)
                
                if layout == 'layout_dpi':
                     return render_template("/paneles/panelSignalSinCuentaDpi.html", datos = datos_desempaquetados)
                if layout == 'layout_signal':
                    return render_template("/paneles/panelSignalSinCuentas.html", datos = datos_desempaquetados)
                if layout == 'layout' or layout == 'layoutConexBroker':      
                    return render_template("/paneles/panelSignalConCuentas.html", datos = datos_desempaquetados)
                return "Página no encontrada"  # Cambia el mensaje según sea necesario
        except jwt.ExpiredSignatureError:
            # El token ha expirado
            # Maneja el caso en que el token ha expirado
            pass
        except jwt.InvalidTokenError:
            # El token es inválido
            # Maneja el caso en que el token no es válido
            pass
     else:
        return render_template('usuarios/logOutSystem.html')     

@panelControl.route("/panel_control_atomatico/<pais>/<usuario_id>/<access_token>/<account>/<selector>/", methods=['GET'])
def panel_control_atomatico(pais,usuario_id,access_token,account,selector):
    
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
        if access_token != 'access_dpi_token_usuario_anonimo':
            usuario_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
          
        ContenidoSheet = procesar_datos(app,pais, account,usuario_id,selector)
        datos_desempaquetados,unidadTrader = forma_datos_para_envio_paneles(app,ContenidoSheet,usuario_id,accountCuenta=account)
        if datos_desempaquetados:
        # print(datos_desempaquetados)
            return jsonify(datos=datos_desempaquetados,unidadTrader=unidadTrader)
        else:
            # Si datos_desempaquetados está vacío, devuelve una respuesta vacía
            return jsonify(datos={})
        # Si ninguna de las condiciones anteriores se cumple, devuelve una respuesta predeterminada
    else:
        return render_template('usuarios/logOutSystem.html')     
     #return jsonify(message="No se encontraron datos disponibles")



def parse_precio(cell: str, pick: str = "last") -> float:
    s = (str(cell) if cell is not None else "").strip()
    if not s or s in {"#N/A", "N/A", "-"}:
        return 0.0
    nums = re.findall(r"-?\d+(?:[.,]\d+)?", s)  # ej: ['18.20','150','37.85']
    if not nums:
        return 0.0
    n = nums[-1] if pick == "last" else nums[0]
    n = n.replace('.', '') if ('.' in n and ',' in n) else n  # miles si hay ambos
    n = n.replace(',', '.')
    try:
        return float(n)
    except ValueError:
        return 0.0

def calcula_ut(cell, unidad_trader: float) -> int:
    precio = parse_precio(cell)
    return abs(int(unidad_trader / precio)) if precio else 0

def forma_datos_para_envio_paneles(app, ContenidoSheet, user_id, accountCuenta):
    if not ContenidoSheet:
        return False
    datos_desempaquetados = list(ContenidoSheet)[2:]
    datos_procesados = []
    with app.app_context():
        with get_db_session() as session:
            ordenes = session.query(Orden).filter_by(user_id=user_id).all()
            ut_row = session.query(UnidadTrader).filter_by(usuario_id=user_id).first()
            unidadTrader = ut_row.ut if ut_row else 0
            ordenes_por_simbolo = {o.symbol: o for o in ordenes}
            for i, tupla in enumerate(datos_desempaquetados):
                dato = list(tupla)
                symbol = dato[0]
                if symbol in ordenes_por_simbolo:
                    o = ordenes_por_simbolo[symbol]
                    if len(dato) > 9:
                        dato[8], dato[9] = o.clOrdId_alta_timestamp, o.senial
                    else:
                        dato += (o.clOrdId_alta_timestamp, o.senial)
                else:
                    if len(dato) < 11:
                        dato += (None, None)
                if dato[0] != 'Formulas G sheets':
                    ut = calcula_ut(dato[7], unidadTrader)
                    dato[3] = str(ut)
                    dato.append(i + 1)
                    datos_procesados.append(tuple(dato))
    return datos_procesados, unidadTrader





def terminaConexionParaActualizarSheet(account):   
    try:
        pyRofexInicializada = get.ConexionesBroker[account]['pyRofex']
        pyRofexInicializada.close_websocket_connection(environment=account)
        
        # Eliminar la conexión del diccionario solo si existe
        del get.ConexionesBroker[account]
    except KeyError:
        # Si la clave no existe en el diccionario, pyRofexInicializada será None
        pyRofexInicializada = None
        print(f"La cuenta {account} no existe en ConexionesBroker.")
        
    get.precios_data.clear()
    return True


def llenar_diccionario_cada_15_segundos_sheet(app, pais, user_id,accountCuenta,selector):
    if pais in get.hilo_iniciado_panel_control and get.hilo_iniciado_panel_control[pais].is_alive():
        return f"Hilo para {pais} ya está en funcionamiento"

    hilo = threading.Thread(target=ejecutar_en_hilo, args=(app, pais, user_id,accountCuenta,selector,))
    get.hilo_iniciado_panel_control[pais] = hilo
    hilo.start()


    return f"Hilo iniciado para {pais}"

def ejecutar_en_hilo(app, pais, user_id,accountCuenta,selector):
    while True:
        # Obtener el día actual de la semana
        dia_actual = datetime.now().weekday()

        # Verificar si el día actual está en la lista de días de ejecución
        if dia_actual in [get.DIAS_SEMANA[dia] for dia in get.DIAS_EJECUCION]:
            time.sleep(120)  # Espera de 2 minutos
            
            if len(get.diccionario_global_sheet) > 0:
                now = datetime.now()
                if not get.luzThred_funcionando['luz']:
                    get.luzThred_funcionando['luz'] = True
                    get.luzThred_funcionando['hora'] = now.hour
                    get.luzThred_funcionando['minuto'] = now.minute
                    get.luzThred_funcionando['segundo'] = now.second
                
               

                # Preguntar si son las 11:00 y pasar la lectura
                if (now.hour >= 11 and now.hour < 17) or (now.hour == 17 and now.minute <= 5):
                #if (now.hour >= 9 and now.hour < 20) or (now.hour == 20 and now.minute <= 5):
                    enviar_leer_sheet(app, pais, user_id,accountCuenta, 'hilo', selector)
              
                #if (now.hour == 19 and now.minute >= 40 and now.minute <= 55):
                     #caucionar(account)
              #  termina_hilo = now.minute + 2 
                # Preguntar si son las 20:00 y apagar el ws y limpiar precios_data
             #   if (now.hour == 12 and now.minute <= termina_hilo) and get.luzMDH_funcionando:
                
                if (now.hour == 17 and now.minute >= 6 and now.minute <= 59) and get.luzMDH_funcionando:
                    terminaConexionParaActualizarSheet(get.CUENTA_ACTUALIZAR_SHEET)
                    get.symbols_sheet_valores.clear()
                    get.sheet_manager = None
                    get.autenticado_sheet = False
                
              
        else:
            time.sleep(86400)  # Espera de 24 horas
                        
                    
def enviar_leer_sheet(app,pais,user_id,accountCuenta,hilo,selector):
    
     if hilo == 'hilo':
        pais = 'argentina'       
      #  app.logger.info('ENTRA A THREAD Y LEE EL SHEET POR HILO')       
     else: 
        app.logger.info('LEE EL SHEET POR LLAMADA DE FUNCION')

     if pais not in ["argentina", "usa","hilo"]:
        # Si el país no es válido, retorna un código de estado HTTP 404 y un mensaje de error
        abort(404, description="País no válido")
        
     
     if selector != "simulado" or selector =='vacio':
        if pais == "argentina":
            if len(get.diccionario_global_sheet) > 0:
                if not get.conexion_existente(app,get.CUENTA_ACTUALIZAR_SHEET,
                                                 get.CORREO_E_ACTUALIZAR_SHEET,
                                                 get.VARIABLE_ACTUALIZAR_SHEET,
                                                 get.ID_USER_ACTUALIZAR_SHEET):
                  modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores',pais)
                  #modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores',pais)
                  app.logger.info('MODIFICO EL SHEET CORRECTAMENTE')
            #ContenidoSheet=datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
            ContenidoSheet=datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
        elif pais == "usa":
            ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bUSA')    
        else:
            return "País no válido"
     else:   
        if pais == "argentina":
            ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
        elif pais == "usa":
            ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
        else:
            return "País no válido"
        
     ContenidoSheetList = list(ContenidoSheet)
     get.diccionario_global_sheet[pais] ={}
     # Adquirir el bloqueo antes de modificar las variables compartidas
     with lock:
            get.diccionario_global_sheet[pais] = ContenidoSheetList
            datos_desempaquetados,unidadTrader = forma_datos_para_envio_paneles(app, get.diccionario_global_sheet[pais], user_id,accountCuenta) 
            
            if len(datos_desempaquetados) != 0:
                get.diccionario_global_sheet_intercambio[pais] = datos_desempaquetados

     
     return  get.diccionario_global_sheet_intercambio[pais]
 
 
 
def determinar_pais(pais):
    if hasattr(get, 'diccionario_global_sheet') and isinstance(get.diccionario_global_sheet, dict):
        # Asegúrate de que 'get.diccionario_global_sheet' exista y sea un diccionario

        lista_asociada = get.diccionario_global_sheet.get(pais, None)
        if lista_asociada is not None:
           # print(f"La lista asociada a {pais} es: {lista_asociada}")
            return lista_asociada
        else:
            #print(f"No se encontró una lista asociada a {pais}")
            return None
    else:
        print(f"'get.diccionario_global_sheet' no está disponible o no es un diccionario con las listas asociadas a los países.")
        return None

def procesar_datos(app,pais, accountCuenta,user_id,selector):
    if determinar_pais(pais) is not None:
        if pais not in get.diccionario_global_sheet_intercambio:
            if len(get.diccionario_global_sheet[pais])>0:
                datos_desempaquetados,unidadTrader = forma_datos_para_envio_paneles(app,get.diccionario_global_sheet[pais], user_id)
            if len(datos_desempaquetados) != 0:
                get.diccionario_global_sheet_intercambio[pais] = datos_desempaquetados
        else:
            return get.diccionario_global_sheet_intercambio[pais]
    else:
        if len(get.diccionario_global_sheet) == 0 or pais not in get.diccionario_global_sheet:
            enviar_leer_sheet(app,pais,user_id,accountCuenta,None,selector)      
        if pais in get.diccionario_global_sheet_intercambio:
           return   get.diccionario_global_sheet_intercambio[pais]
       

def verificar_estado_triggers():
    # Recorre todos los triggers en estrategias_usuario__endingOperacionBot
    for estrategia in get.estrategias_usuario__endingOperacionBot.values():
        # Verifica si el estado es 'termino'
        if estrategia['status'] == 'termino':
            return True
    
    # Si ninguno tiene el estado 'termino', retorna False
    return False

'''
get.precios_data = {
    'MERV - XMEV - GOOGL - 24hs': {'p24hs': None, 'max24hs': 3961.1, 'min24hs': 3962.2, 'last24hs': 3963.3},
    'MERV - XMEV - VALE - 24hs': {'p24hs': None, 'max24hs': 7370.1, 'min24hs': 7370.2, 'last24hs': 7370.3},
    'MERV - XMEV - RIO - 24hs': {'p24hs': None, 'max24hs': 10913.1, 'min24hs': 10913.2, 'last24hs': 10913.3},
    'MERV - XMEV - AGRO - 24hs': {'p24hs': None, 'max24hs': 58.1, 'min24hs': 58.2, 'last24hs': 58.3},
    'MERV - XMEV - TXAR - 24hs': {'p24hs': None, 'max24hs': 944.1, 'min24hs': 944.2, 'last24hs': 944.3},
    'MERV - XMEV - VALO - 24hs': {'p24hs': None, 'max24hs': 303.1, 'min24hs': 303.2, 'last24hs': 303.3},
    'MERV - XMEV - LOMA - 24hs': {'p24hs': None, 'max24hs': 1839.1, 'min24hs': 1839.2, 'last24hs': 1839.3},
    'MERV - XMEV - GGB - 24hs': {'p24hs': None, 'max24hs': 16652.1, 'min24hs': 16652.2, 'last24hs': 16652.3},
    'MERV - XMEV - BYMA - 24hs': {'p24hs': None, 'max24hs': 321.1, 'min24hs': 321.2, 'last24hs': 321.3},
    'MERV - XMEV - BMA - 24hs': {'p24hs': None, 'max24hs': 7481.1, 'min24hs': 7481.2, 'last24hs': 7481.3},
    'MERV - XMEV - CEPU - 24hs': {'p24hs': None, 'max24hs': 1182.1, 'min24hs': 1182.2, 'last24hs': 1182.3},
    'MERV - XMEV - GGAL - 24hs': {'p24hs': None, 'max24hs': 4187.1, 'min24hs': 4187.2, 'last24hs': 4187.3},
    'MERV - XMEV - SUPV - 24hs': {'p24hs': None, 'max24hs': 1649.1, 'min24hs': 1649.2, 'last24hs': 1649.3},
    'MERV - XMEV - TECO2 - 24hs': {'p24hs': None, 'max24hs': 1875.1, 'min24hs': 1875.2, 'last24hs': 1875.3},
    'MERV - XMEV - TGT - 24hs': {'p24hs': None, 'max24hs': 7940.1, 'min24hs': 7940.2, 'last24hs': 7940.3},
    'MERV - XMEV - DGCU2 - 24hs': {'p24hs': None, 'max24hs': 1170.1, 'min24hs': 1170.2, 'last24hs': 1170.3}
}
'''
