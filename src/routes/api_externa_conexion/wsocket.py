from flask import Blueprint, render_template, session,request, redirect, url_for, flash,jsonify
from utils.common import Marshmallow, db, get
import routes.instrumentosGet as instrumentosGet
import routes.api_externa_conexion.validaInstrumentos as val

import strategies.datoSheet as datoSheet
import routes.instrumentos as inst
from panelControlBroker.panelControl import enviar_leer_sheet

from datetime import datetime

import pandas as pd
import pyRofex #lo utilizo para test
import time    #lo utilizo para test
import asyncio
import websockets
import websocket
from flask_paginate import Pagination, get_page_parameter

import json
import os
import copy

wsocket = Blueprint('wsocket',__name__)



reporte_de_instrumentos = []


def websocketConexionShedule(app,pyRofexInicializada=None,Cuenta=None,account=None,idUser=None,correo_electronico=None,selector=None):
  
     
      cuenta = db.session.query(Cuenta).filter_by(user_id=idUser, accountCuenta=account).first()
      passwordCuenta = cuenta.passwordCuenta
      passwordCuenta = passwordCuenta.decode('utf-8')
      endPoint = get.inicializar_variables(cuenta.accountCuenta)
      #app.logger.info(endPoint)
      api_url = endPoint[0]
      ws_url = endPoint[1]
      if (len(get.ConexionesBroker) > 0 and  account in get.ConexionesBroker):
          
              #if  ConexionesBroker[accountCuenta].get('identificador') == True:
                  pyRofexInicializada = get.ConexionesBroker.get(account)['pyRofex']
                  repuesta_operacion = pyRofexInicializada.get_account_report(account=account, environment=account)
                  if repuesta_operacion:
                      pass
      else:   
        
              sobreEscituraPyRofex = True
              if sobreEscituraPyRofex == True:
                  ambiente = copy.deepcopy(get.envNuevo)
                  pyRofexInicializada = pyRofex
                  pyRofexInicializada._add_environment_config(enumCuenta=account,env=ambiente)
                  environments = account
              else:    
                  if selector == 'simulado':
                      environments = pyRofexInicializada.Environment.REMARKET
                  else:                                    
                      environments = pyRofexInicializada.Environment.LIVE
              
              pyRofexInicializada._set_environment_parameter("url", api_url, environments)                          
              pyRofexInicializada._set_environment_parameter("ws", ws_url, environments)                            
              pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments)    
              pyRofexInicializada.initialize(user=cuenta.userCuenta, password=passwordCuenta, account=account, environment=environments)                       
              
              get.ConexionesBroker[account] = {'pyRofex': pyRofexInicializada, 'cuenta': account,'identificador': True}
                
              wsocketConexion(app,pyRofexInicializada,cuenta.accountCuenta,idUser,selector)
              return True
      return True

def wsocketConexion(app,pyRofexInicializada,accountCuenta, user_id,selector):
   
   # get.pyRofexInicializada.order_report_subscription()
  # get.pyRofexInicializada.add_websocket_market_data_handler(market_data_handler_arbitraje_001)
   
   pyRofexInicializada.init_websocket_connection(market_data_handler=market_data_handler_0,order_report_handler=order_report_handler_0,error_handler=error_handler,exception_handler=exception_handler,environment=accountCuenta)
   
   if not get.ContenidoSheet_list:
      get.ContenidoSheet_list = SuscripcionDeSheet(app,pyRofexInicializada,accountCuenta,user_id,selector)  # <<-- aca se suscribe al mkt data
 
   pyRofexInicializada.remove_websocket_market_data_handler(market_data_handler_0,environment=accountCuenta)
   pyRofexInicializada.remove_websocket_order_report_handler(order_report_handler_0,environment=accountCuenta)
 

def market_data_handler_0(message):
    print(message)

def order_report_handler_0(message):
  print(message)



@wsocket.route('/detenerWSSuscripcionInstrumentos/')   
def detenerWSSuscripcionInstrumentos():
     get.pyRofexInicializada.close_websocket_connection()
     return render_template("home.html" )
   


@wsocket.route('/suscriptos/', methods = ['POST'])
def suscriptos():
      try:
        if request.method == "POST":     
     
          Ticker = request.form["symbol"]                 
          Ticker = Ticker.replace("*", " ")
          account = request.form["websocketCuenta"] 
          access_token = request.form["websocketToken"] 
          #traigo los instrumentos para suscribirme
          mis_instrumentos = instrumentosGet.get_instrumento_para_suscripcion_ws(account)
          longitudLista = len(mis_instrumentos)
          pyRofexInicializada = get.ConexionesBroker.get(account)['pyRofex']  
          repuesta_listado_instrumento = pyRofexInicializada.get_detailed_instruments(environment=account)
        # print("repuesta_listado_instrumento repuesta_listado_instrumento ",repuesta_listado_instrumento)
          listado_instrumentos = repuesta_listado_instrumento['instruments']   
          tickers_existentes = inst.obtener_array_tickers(listado_instrumentos) 
          instrumentos_existentes = val.validar_existencia_instrumentos(mis_instrumentos,tickers_existentes)
        
        ##aqui se conecta al ws
          
          pyRofexInicializada.init_websocket_connection(market_data_handler,order_report_handler,error_handler,exception_error)
          print("<<<-----------pasoooo conexiooooonnnn wsocket.py--------->>>>>")
        
          #### aqui define el MarketDataEntry
          entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                      get.pyRofexInicializada.MarketDataEntry.OFFERS,
                      get.pyRofexInicializada.MarketDataEntry.LAST]
        # while True: 

            ###asi puedo llamar otra funcion para manejar los datos del ws#####      
            #get.pyRofexInicializada.add_websocket_market_data_handler(mostrar)
            #### aqui se subscribe   
          print("<<<-----------entries instrumento_suscriptio--------->>>>> ",entries)              
          print("<<<-----------instrumentos_existentes a suscribir en wsocket.py--------->>>>>",instrumentos_existentes)       
          mensaje =pyRofexInicializada.market_data_subscription(tickers=instrumentos_existentes,entries=entries)
          
          print("instrumento_suscriptio",mensaje)
            # Subscribes to an Invalid Instrument (Error Message Handler should be call)
          # get.pyRofexInicializada.market_data_subscription(tickers=["InvalidInstrument"],entries=entries)
        
          #print("report encontrado ",report) 
        # time.sleep(100)
        # time.sleep(1)  
      # except KeyboardInterrupt:
        #  pass
        # get.pyRofexInicializad ºa.close_websocket_connection()
        
        
          return render_template('suscripcion.html', datos =  [get.market_data_recibida,longitudLista])
      except:  
           print("contraseña o usuario incorrecto")  
           flash('Loggin Incorrect')    
           return render_template("errorLogueo.html" ) 

@wsocket.route('/SuscripcionWs/', methods=['POST'])
def SuscripcionWs():
    if request.method == "POST":
        # Obtener los valores enviados desde el formulario
        Ticker = request.form.get('symbol')  # Obtener el valor del campo "symbol"
        account = request.form.get('websocketSuscricionCuenta')  # Obtener el valor del campo "websocketSuscricionCuenta"
        token = request.form.get('websocketSuscricionToken')  # Obtener el valor del campo "websocketSuscricionToken"
        
       # print("websoooooooooooooooooketttt en wsocket.py ",Ticker)
        #almaceno los symbol a suscribirme
        instrumentosGet.guarda_instrumento_para_suscripcion_ws(Ticker)
        #traigo los instrumentos para suscribirme
      
        diccionario ={}
        #actualizarTablaMD()
        #diccionario.update(get.market_data_recibida)
        pyRofexInicializada = get.ConexionesBroker.get(account)['pyRofex']       
      
        if pyRofexInicializada:        
            repuesta_listado_instrumento = pyRofexInicializada.get_detailed_instruments(environment=account)
            listado_instrumentos = repuesta_listado_instrumento['instruments']

            # Configurar paginación
            
            per_page = 10
            offset = (1 - 1) * per_page
            datos_paginated = listado_instrumentos[offset:offset + per_page]

            pagination = Pagination(page=1, total=len(listado_instrumentos), per_page=per_page, css_framework='bootstrap4')

            return render_template("instrumentos/instrumentos.html", datos=datos_paginated, pagination=pagination)
        #return render_template('suscripcion.html', datos =  [get.market_data_recibida,longitudLista])



def SuscripcionDeSheet(app,pyRofexInicializada,accountCuenta,user_id,selector):
    # Trae los instrumentos para suscribirte
   
    ContenidoJsonDb = get_instrumento_para_suscripcion_json() 
    
    ContenidoJsonDb_list_db = list(ContenidoJsonDb.values())
    #COMENTO LA PARTE DE CONSULTAR AL SHEET POR EXPIRACION DE TOKEN
    if len(get.diccionario_global_sheet) == 0 or 'argentina' not in get.diccionario_global_sheet:
       ContenidoSheet = get_instrumento_para_suscripcion_ws(app,user_id,selector)# **44
       ContenidoSheet_list = list(ContenidoSheet)
    ContenidoSheet_list = get.diccionario_global_sheet['argentina']

    
    ContenidoSheetDb = get_instrumento_para_suscripcion_db(app)
    ContenidoSheet_list_db = list(ContenidoSheetDb)
    
    
    
  
    longitudLista = len(ContenidoSheet_list)
    ContenidoSheet_list_solo_symbol = cargaSymbolParaValidar(ContenidoSheet_list)
    ContenidoSheet_list_solo_symbol_db = cargaSymbolParaValidarDb(ContenidoSheet_list_db)
    
   
   # print("Cantidad de elementos a suscribir: ",len(ContenidoSheet_list_solo_symbol))
   # print("<<<<<---------------------Instrumentos a Suscribir --------------------------->>>>>> ")
   # for item in ContenidoSheet_list_solo_symbol:
   #     print(item)

  # Convertir listas a conjuntos para eliminar duplicados
    set_contenido_ws = set(ContenidoSheet_list_solo_symbol) #comentado parte de sheet
    set_contenido_db = set(ContenidoSheet_list_solo_symbol_db)
    set_contenido_json = set(ContenidoJsonDb_list_db)

    # Combinar conjuntos y eliminar duplicados
    resultado_set = set_contenido_db.union(set_contenido_json,set_contenido_ws)
    
    # Convertir conjunto resultante en una lista
    resultado_lista = list(resultado_set)
    
    # Ahora 'resultado_lista' contiene todos los instrumentos sin duplicados

   
    #for elemento in resultado_lista:
    #    print(elemento)
    for elemento in get.ConexionesBroker:
        account = get.ConexionesBroker[elemento]['cuenta']
        if account == accountCuenta:  
            
            repuesta_listado_instrumento = pyRofexInicializada.get_detailed_instruments(environment=account)
    
    
            listado_instrumentos = repuesta_listado_instrumento['instruments']   
            #print("instrumentos desde el mercado para utilizarlos en la validacion: ",listado_instrumentos)
        
            tickers_existentes = inst.obtener_array_tickers(listado_instrumentos) 
            
            # Validamos existencia
            instrumentos_existentes = val.validar_existencia_instrumentos(resultado_lista,tickers_existentes)
            
            #instruments = ["DLR/OCT24", "DLR/OCT24"]
            
            #### aqui define el MarketDataEntry
            entries = [pyRofexInicializada.MarketDataEntry.BIDS,
                        pyRofexInicializada.MarketDataEntry.OFFERS,
                        pyRofexInicializada.MarketDataEntry.LAST]
            merdado_id = pyRofexInicializada.Market.ROFEX
            pyRofexInicializada.market_data_subscription(
                                        tickers=instrumentos_existentes,
                                        entries=entries,                                       
                                        depth=3,
                                        handler=None, 
                                        environment=account
                                    )
        
           
            datos = ContenidoSheet_list #COMENTADO POR SHEET
            
        
    #return instrumentos_existentes
    return [ContenidoSheet_list,instrumentos_existentes]
  

def cargaSymbolParaValidarDb(message):
    listado_final = []
    for instrumento  in message: 
        listado_final.append(instrumento.symbol)
        print("FUN_ cargaSymbolParaValidarDb en estrategiaSheetWS 178")
        
    return listado_final



def cargaSymbolParaValidar(message):
    listado_final = []
    for Symbol,tipo_de_activo,trade_en_curso,ut,senial,gan_tot, dias_operado, precioUt in message: 
        if Symbol != 'Symbol':#aqui salta la primera fila que no contiene valores
                                if Symbol != '':
                                #if trade_en_curso == 'LONG_':
                                    if senial != '':
                                            
                                                if tipo_de_activo =='CEDEAR':
                                                # print(f'El instrumento {Symbol} existe en el mercado')
                                                 listado_final.append(Symbol)
                                                if tipo_de_activo =='ARG':
                                                 listado_final.append(Symbol)
                                                # print(f'El instrumento {Symbol} existe en el mercado')
 
    return listado_final
  
def get_instrumento_para_suscripcion_ws(app,user_id,selector):#   **77
     ContenidoSheet =  enviar_leer_sheet(app,'argentina',user_id,None,selector) 
     return ContenidoSheet

def get_instrumento_para_suscripcion_db(app):
    ContenidoDb = datoSheet.leerDb(app)
    return ContenidoDb    

def get_instrumento_para_suscripcion_json():
   try:
        src_directory = os.getcwd() # Busca directorio raíz src o app 
        ruta_archivo_json = os.path.join(src_directory, 'strategies/listadoInstrumentos/instrumentos_001.json')
       # ruta_archivo_json = 'strategies/listadoInstrumentos/instrumentos_001.json'    
        with open(ruta_archivo_json , 'r') as archivo:
            contenido = archivo.read()
            datos = json.loads(contenido)
            
            # Acceder a los datos
           
            return datos
   except FileNotFoundError:
        print("El archivo no se encuentra.")
   except json.JSONDecodeError:
        print("Error al decodificar el JSON.")
##########################esto es para ws#############################
#Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}

def error_handler(message):
  print("Mensaje de error: {0}".format(message))

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic23"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

def order_report_handler(message):
  
  
  #print("Mensaje de OrderRouting: {0}".format(message))
  get.reporte_de_ordenes.append(message)
  
 # 2-Defines the handlers that will process the messages and exceptions.
def order_report_handler_cancel(message):
    print("Order Report Message Received: {0}".format(message))
    # 6-Handler will validate if the order is in the correct state (pending_new)
    if message["orderReport"]["status"] == "NEW":
        # 6.1-We cancel the order using the websocket connection
        print("Send to Cancel Order with clOrdID: {0}".format(message["orderReport"]["clOrdId"]))
        pyRofex.cancel_order_via_websocket(message["orderReport"]["clOrdId"])

    # 7-Handler will receive an Order Report indicating that the order is cancelled (will print it)
    if message["orderReport"]["status"] == "CANCELLED":
        print("Order with ClOrdID '{0}' is Cancelled.".format(message["orderReport"]["clOrdId"])) 
   
  ###########tabla de market data
  #Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}

def market_data_handler(message):
  
  
 # print("message",message)
  ticker = message["instrumentId"]["symbol"]
  bid = message["marketData"]["BI"] if len(message["marketData"]["BI"]) != 0 else [{'price': "-", 'size': "-"}]
  offer = message["marketData"]["OF"] if len(message["marketData"]["OF"]) != 0 else [{'price': "-", 'size': "-"}]
  last = message["marketData"]["LA"]["price"] if message["marketData"]["LA"] != None else 0
  dateLA = message['marketData']['LA']['date'] if message["marketData"]["LA"] != None else 0

  timestamp = message['timestamp']
  objeto_md = {'symbol':ticker,'bid':bid,'offer':offer,'last':last,'dateLA':dateLA,'timestamp':timestamp}
  get.market_data_recibida.append(objeto_md)
 
  #print("Mensaje de MarketData en market_data_handler: {0}".format(message))
  
  
  #{"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic21"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}
def order_report_handler(message):
  #print("Mensaje de OrderRouting: {0}".format(message))
  get.reporte_de_ordenes.append(message)