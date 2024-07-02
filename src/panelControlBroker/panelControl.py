# Creating  Routes
from pipes import Template
from unittest import result
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import and_
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify, abort,current_app
from models.instrumento import Instrumento

from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.orden import Orden
import threading
import strategies.datoSheet as datoSheet
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


@panelControl.route('/panel_control_sin_cuenta')
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
        respuesta =  llenar_diccionario_cada_15_segundos_sheet(app,pais,account,selector)
        
        datos_desempaquetados = procesar_datos(app,pais, account,usuario_id,selector)
        
        if layout == 'layout_signal':
            return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
        if layout == 'layout': 
            return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
        if layout == 'layout' or layout == 'layoutConexBroker':        
            return render_template("/paneles/panelDeControlBroker.html", datos = datos_desempaquetados)
        return "Página no encontrada"  # Cambia el mensaje según sea necesario
    else:
        return render_template('usuarios/logOutSystem.html',layout='layout')     
  

@panelControl.route("/panel_control")
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
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            
                respuesta =  llenar_diccionario_cada_15_segundos_sheet(app,pais,accountCuenta,selector)
                
                datos_desempaquetados = procesar_datos(app,pais, accountCuenta,usuario_id,selector)
                
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
        ContenidoSheet = procesar_datos(app,pais, account,usuario_id,selector)
        datos_desempaquetados = forma_datos_para_envio_paneles(app,ContenidoSheet,usuario_id)
        if datos_desempaquetados:
        # print(datos_desempaquetados)
            return jsonify(datos=datos_desempaquetados)
        else:
            # Si datos_desempaquetados está vacío, devuelve una respuesta vacía
            return jsonify(datos={})
        # Si ninguna de las condiciones anteriores se cumple, devuelve una respuesta predeterminada
    else:
        return render_template('usuarios/logOutSystem.html')     
     #return jsonify(message="No se encontraron datos disponibles")

def forma_datos_para_envio_paneles(app, ContenidoSheet, user_id):
    if not ContenidoSheet:
        return False

    datos_desempaquetados = list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
    datos_procesados = []

    with app.app_context():
        # Consultar todas las órdenes de la cuenta
       
        ordenes_cuenta = db.session.query(Orden).filter_by(user_id=user_id).all()

        # Crear un diccionario para mapear los símbolos de las órdenes a las órdenes
        ordenes_por_simbolo = {orden.symbol: orden for orden in ordenes_cuenta}

        for i, tupla_exterior in enumerate(datos_desempaquetados):
            dato = list(tupla_exterior)  # Convierte la tupla interior a una lista
            symbol = dato[0]

            # Comprobar si hay una orden para este símbolo en las órdenes de la cuenta
            if symbol in ordenes_por_simbolo:
                orden_existente = ordenes_por_simbolo[symbol]

                # Si se encuentra una orden, agregar datos adicionales al dato
                dato_extra = (orden_existente.clOrdId_alta_timestamp, orden_existente.senial)
                if len(dato) > 9:
                    dato[8] = orden_existente.clOrdId_alta_timestamp
                    dato[9] = orden_existente.senial
                else:
                    dato +=dato_extra                
            else:
                if len(dato)<11:
                # Si no se encuentra una orden, agregar None como datos adicionales
                    dato_extra = (None, None)
                    dato += dato_extra

           
            dato.append(i + 1)
            datos_procesados.append(tuple(dato))

    return datos_procesados


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


def llenar_diccionario_cada_15_segundos_sheet(app, pais, user_id,selector):
    if pais in get.hilo_iniciado_panel_control and get.hilo_iniciado_panel_control[pais].is_alive():
        return f"Hilo para {pais} ya está en funcionamiento"

    hilo = threading.Thread(target=ejecutar_en_hilo, args=(app, pais, user_id,selector,))
    get.hilo_iniciado_panel_control[pais] = hilo
    hilo.start()


    return f"Hilo iniciado para {pais}"

def ejecutar_en_hilo(app,pais,user_id,selector):
          while True:
            #time.sleep(420)# 420 son 7 minutos
           
            time.sleep(120)# 4minulos
            
            if len(get.diccionario_global_sheet) > 0:
                if  get.luzThred_funcionando == False:
                   get.luzThred_funcionando = True
                ################################# preguntar si son las 11 ##################
                ################################# pasar la lectura #########################                
                if datetime.now().hour >= 14 and datetime.now().hour < 20:
                    enviar_leer_sheet(app, pais, user_id,'hilo',selector)               
                ################################# pregutar si son las 17 hs #################
                ################## apagar el ws y limpia precios_data #######################
                now = datetime.now()
                if (now.hour == 20 and now.minute >= 0 and now.minute <= 59) and get.luzMDH_funcionando:
                    terminaConexionParaActualizarSheet(get.CUENTA_ACTUALIZAR_SHEET)
                    get.symbols_sheet_valores.clear()
                    get.sheet_manager = None
                    get.autenticado_sheet = False
                    
                    
def enviar_leer_sheet(app,pais,user_id,hilo,selector):
    
     if hilo == 'hilo':
        pais = 'argentina'
        app.logger.info('ENTRA A THREAD Y LEE EL SHEET POR HILO')       
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
                  #modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores',pais)
                  modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores',pais)
                  print(' PANELCONTROL.PY ESTA COMENTADA LA LINEA DESCOMENTAR ANTES DE SUBIR A GIT ACTION') 
                  app.logger.info('MODIFICO EL SHEET CORRECTAMENTE')
            ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
        elif pais == "usa":
            ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'drpibotUSA')    
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
            datos_desempaquetados = forma_datos_para_envio_paneles(app, get.diccionario_global_sheet[pais], user_id) 
            
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
            datos_desempaquetados = forma_datos_para_envio_paneles(app,get.diccionario_global_sheet[pais], user_id)
            if len(datos_desempaquetados) != 0:
                get.diccionario_global_sheet_intercambio[pais] = datos_desempaquetados
        else:
            return get.diccionario_global_sheet_intercambio[pais]
    else:
        if len(get.diccionario_global_sheet) == 0 or pais not in get.diccionario_global_sheet:
            enviar_leer_sheet(app,pais,accountCuenta,None,selector)      
        if pais in get.diccionario_global_sheet_intercambio:
           return   get.diccionario_global_sheet_intercambio[pais]
       



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
