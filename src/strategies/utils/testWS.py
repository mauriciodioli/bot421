from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g

import routes.instrumentosGet as instrumentosGet
from utils.db import db
from models.orden import Orden
from models.usuario import Usuario
import jwt
import json
import random
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
import strategies.estrategiaSheetWS as shWS 
import strategies.datoSheet as datoSheet 
import requests
import routes.api_externa_conexion.cuenta as cuenta

from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import pprint
import websockets





testWS = Blueprint('testWS',__name__)



@testWS.route('/ruta_de_test_ws', methods=['POST'])
def ruta_de_test_ws():
    
    if request.method == 'POST':
        try:
            usuario = request.form['usuario1']
            get.accountLocalStorage = request.form['cuenta1']
            access_token = request.form['access_token1']
            correo_electronico = request.form['correo_electronico1']
            get.VariableParaBotonPanico = 0
            ContenidoSheet_list = shWS.SuscripcionDeSheet()  # <<-- aca se suscribe al mkt data
          
            get.pyRofexInicializada.order_report_subscription(account=get.accountLocalStorage, snapshot=True, handler=order_report_handler_test)
            
            pyRofexWebSocket = get.pyRofexInicializada.init_websocket_connection(
                market_data_handler=market_data_handler_test,
                order_report_handler=order_report_handler_test,
                error_handler=error_handler,
                exception_handler=exception_handler
            )

         
            shWS.carga_operaciones(ContenidoSheet_list[0], get.accountLocalStorage, usuario, correo_electronico, ContenidoSheet_list[1])
    
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
            return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except:
            print("no pudo leer la base de datos")
    return render_template('/estrategiaOperando.html')
     



  
def get_instrumento_para_suscripcion_ws():
      ContenidoSheet = datoSheet.leerSheet()
      datoSheet.crea_tabla_orden()  
      return ContenidoSheet
    
def market_data_handler_test(message):
   
    if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
        print("FUN market_data_handler_estrategia: message[marketData][BI] es None o está vacío")
    elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
        print("FUN market_data_handler_estrategia: message[marketData][OF] es None o está vacío")
    elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:
        print("FUN market_data_handler_estrategia: message[marketData][LA] es None o está vacío")
    else:
        print("FUN market_data_handler_estrategia: SI HAY DATOS. ")
        
        
        

    
    
def order_report_handler_test( order_report):
        # Obtener el diccionario de datos del reporte de orden
        order_data = order_report['orderReport']
        #################################################
        ###### cambiar esto finalizado el test ##########
        #################################################
        #order_data = order_report
        # Leer un valor específico del diccionario
        clOrdId = order_data['clOrdId']
        symbol = order_data['instrumentId']['symbol']
        status = order_data['status']  
        timestamp_order_report = order_data['transactTime']  
        
        print("FUN order_report_handler_test: web soket mando un reporte. ")
     
            
        
              
    
        
def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))




        