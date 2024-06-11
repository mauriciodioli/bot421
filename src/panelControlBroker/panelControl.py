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
            time.sleep(60)# 5minulos
            
           
            enviar_leer_sheet(app, pais, user_id,'hilo',selector)
        

def enviar_leer_sheet(app,pais,user_id,hilo,selector):
    
     if hilo == 'hilo':
        print("ENTRA A THREAD Y LEE EL SHEET POR HILO")
        app.logger.info('ENTRA A THREAD Y LEE EL SHEET POR HILO')       
     else: 
        print("LEE EL SHEET POR LLAMADA DE FUNCION")
        app.logger.info('LEE EL SHEET POR LLAMADA DE FUNCION')

     if pais not in ["argentina", "usa","hilo"]:
        # Si el país no es válido, retorna un código de estado HTTP 404 y un mensaje de error
        abort(404, description="País no válido")
        
     
     if selector != "simulado" or selector =='vacio':
        if pais == "argentina":
            if len(get.diccionario_global_sheet) > 0:
               if not get.conexion_existente(app):
                   modifico = datoSheet.modificar_sheet(get.SPREADSHEET_ID_PRODUCCION,'data')
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
       
