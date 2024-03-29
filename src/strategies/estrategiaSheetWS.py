from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g
import routes.instrumentosGet as instrumentosGet
from utils.db import db
from models.orden import Orden
from models.usuario import Usuario
import re
import jwt
import csv
import json
import random
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
import strategies.datoSheet as datoSheet 
import requests
import routes.api_externa_conexion.cuenta as cuenta
import routes.api_externa_conexion.operaciones as operaciones


from datetime import datetime,timedelta, timezone
from pytz import timezone as pytz_timezone
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import pprint
instrumentos_existentes_arbitrador1=[]
import sys




estrategiaSheetWS = Blueprint('estrategiaSheetWS',__name__)


class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2




@estrategiaSheetWS.route('/estrategia-001', methods=['POST'])
def estrategia_001():
    print('00000000000000000000000estrategia-00100000000000000000000000000')
    if request.method == 'POST':
        try:
            
            
            data = request.get_json()

            # Accede a los datos individualmente
            
            usuario = data['userCuenta']
            #usuario = "apipuntillo22583398"
            
            idTrigger = data['idTrigger']
            access_token = data['access_token']
            idUser = data['idUser']
            correo_electronico = data['correo_electronico']
            
            get.accountLocalStorage = data['cuenta']
            #get.accountLocalStorage = "20225833983"
            
            tiempoInicio = data['tiempoInicio']
            tiempoFin = data['tiempoFin']
            automatico = data['automatico']
            nombre = data['nombre']
            get.VariableParaBotonPanico = 0
           
           
            CargOperacionAnterioDiccionarioEnviadas(get.accountLocalStorage,usuario,correo_electronico)
            carga_operaciones(get.ContenidoSheet_list[0], get.accountLocalStorage ,usuario,correo_electronico,get.ContenidoSheet_list[1])
            get.pyRofexInicializada.order_report_subscription(account= get.accountLocalStorage , snapshot=True,handler = order_report_handler)
            get.pyRofexInicializada.add_websocket_market_data_handler(market_data_handler_estrategia)
            get.pyRofexInicializada.add_websocket_order_report_handler(order_report_handler)
         
       #     pyRofexWebSocket =  get.pyRofexInicializada.init_websocket_connection (
       #                             market_data_handler=market_data_handler_estrategia,
       #                             order_report_handler=order_report_handler,
       #                             error_handler=error_handler,
       #                             exception_handler=exception_handler
       #                             )
            #get.pyRofexInicializada.run_websocket()
           # carga_operaciones(get.ContenidoSheet_list[0], get.accountLocalStorage ,usuario,correo_electronico,get.ContenidoSheet_list[1])
            # Crear una instancia de RofexMarketDataHandler
            

            
            
        
    
        except jwt.ExpiredSignatureError:
                print("El token ha expirado")
                return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except:
           print("no pudo conectar el websocket en estrategiaSheetWS.py ")
    return render_template('notificaciones/estrategiaOperando.html')
     
def SuscripcionDeSheet(app):
    # Trae los instrumentos para suscribirte
   
    ContenidoJsonDb = get_instrumento_para_suscripcion_json() 
    
    ContenidoJsonDb_list_db = list(ContenidoJsonDb.values())
    #COMENTO LA PARTE DE CONSULTAR AL SHEET POR EXPIRACION DE TOKEN
    ContenidoSheet = get_instrumento_para_suscripcion_ws()# **44
    ContenidoSheet_list = list(ContenidoSheet)

    
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

    repuesta_listado_instrumento = get.pyRofexInicializada.get_detailed_instruments()
    
    listado_instrumentos = repuesta_listado_instrumento['instruments']   
    #print("instrumentos desde el mercado para utilizarlos en la validacion: ",listado_instrumentos)
   
    tickers_existentes = inst.obtener_array_tickers(listado_instrumentos) 
    
    # Validamos existencia
    instrumentos_existentes = val.validar_existencia_instrumentos(resultado_lista,tickers_existentes)
    
    
    
    #### aqui define el MarketDataEntry
    entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
               get.pyRofexInicializada.MarketDataEntry.OFFERS,
               get.pyRofexInicializada.MarketDataEntry.LAST]
    
      
    #### aqui se subscribe   **55
    mensaje = get.pyRofexInicializada.market_data_subscription(tickers=instrumentos_existentes,entries=entries,depth=3)
   
    #print("instrumento_suscriptio",mensaje)
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
    for Symbol,tipo_de_activo,trade_en_curso,ut,senial,gan_tot, dias_operado  in message: 
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
  
def get_instrumento_para_suscripcion_ws():#   **77
      ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
    
      return ContenidoSheet

def get_instrumento_para_suscripcion_db(app):
    ContenidoDb = datoSheet.leerDb(app)
    return ContenidoDb    

def get_instrumento_para_suscripcion_json():
   try:
        ruta_archivo_json = 'strategies/listadoInstrumentos/instrumentos_001.json'    
        with open(ruta_archivo_json , 'r') as archivo:
            contenido = archivo.read()
            datos = json.loads(contenido)
            
            # Acceder a los datos
           
            return datos
   except FileNotFoundError:
        print("El archivo no se encuentra.")
   except json.JSONDecodeError:
        print("Error al decodificar el JSON.")
       
def market_data_handler_estrategia(message):
    
    
    #Arbitrador001(message)
    
    ## mensaje = Ticker+','+cantidad+','+spread
    #print(message)
    time = datetime.now()
    timeuno = int(time.timestamp())*1000
    # message1 = {'type': 'Md', 'timestamp': 1684504693780, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'WTI/JUL23'}, 'marketData': {'OF': [{'price': 72.44, 'size': 100}], 'BI': [{'price': 72.4, 'size': 100}], 'LA': {'price': 72.44, 'size': 200, 'date': 1684504670967}}}
    # message2 = {'type': 'Md', 'timestamp': timeuno, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'ORO/JUL23'}, 'marketData': {'OF': [{'price': 1960, 'size': 100}], 'BI': [{'price': 1955, 'size': 100}], 'LA': {'price': 1956, 'size': 200, 'date': 1684504670967}}}
    # message = {'type': 'Md', 'timestamp': timeuno, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'WTI/JUL23'}, 'marketData': {'OF': [{'price': 76, 'size': 100}], 'BI': [{'price': 75, 'size': 100}], 'LA': {'price': 75.5, 'size': 3, 'date': 1687786000759}}}    
        ###### BOTON DE PANICO #########        
    response = botonPanicoRH('None') 
   # print("MDH respuesta desde el boton de panico", response)
   
    
    if response != 1: ### si es 1 el boton de panico fue activado
       # _cancela_orden(300)
        _cancela_orden(300)
      #  print(" FUN: market_data_handler_estrategia: _")
        
        #print( " Marca de tpo guardada:",  get.VariableParaTiemposMDHandler)
        marca_de_tiempo = message["timestamp"]
        #print( " Marca de tpo Actual  :",  marca_de_tiempo, " Diferencia:", marca_de_tiempo - get.VariableParaTiemposMDHandler)

        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 20000: # 20 segundos
        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 60000: # 1 minuto
        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 300000: # 5 minutos
        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 600000: # 10 minutos
        banderaLecturaSheet = 1 #La lectura del sheet es solo cada x minutos
        if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 300000: # 5 minutos
            # esto hay que hacerlo aca, solo cada x segundos
            banderaLecturaSheet = 0 #La lectura del sheet es solo cada x minutos


        if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 10000: # 10 segundos
            get.VariableParaSaldoCta=cuenta.obtenerSaldoCuenta( get.accountLocalStorage )# cada mas de 5 segundos
            get.VariableParaTiemposMDHandler = message["timestamp"]# milisegundos
        
        # Va afuera de la verificacion de periodo de tiempo, porque debe ser llamada inmediatamente
        # para cumplir con el evento de mercado market data



        if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
            pass
            #print("FUN market_data_handler_estrategia: message[marketData][BI] es None o está vacío")
        elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
            pass
            #print("FUN market_data_handler_estrategia: message[marketData][OF] es None o está vacío")
        elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:            
            pass
            #print("FUN market_data_handler_estrategia: message[marketData][LA] es None o está vacío")
        else:
            
            #tiempoAhora = datetime.now()
            pass
           # estrategiaSheetNuevaWS(message, banderaLecturaSheet)
            
            #tiempoDespues = datetime.now()
            #teimporAhoraInt = tiempoDespues - tiempoAhora
            #tiempomili =  teimporAhoraInt.total_seconds() * 1000
          #  print("FUN_ estrategiaSheetWS tiempoTotal en microsegundos: ",teimporAhoraInt.microseconds," en milisegundo: ",tiempomili)
 
@estrategiaSheetWS.route('/botonPanicoPortfolio/', methods = ['POST']) 
def boton_panico_portfolio():
     if request.method == 'POST':
        try:
            usuario = request.form['usuario_portfolio']
            get.accountLocalStorage = request.form['account']
            access_token = request.form['access_token_portfolio']
            correo_electronico = request.form['correo_electronico_portfolio']
            respuesta = botonPanicoRH('true')
            estadoOperacionAnterioCargaDiccionarioEnviadas(get.accountLocalStorage,usuario,correo_electronico)
            #get.pyRofexInicializada.close_websocket_connection()
            respuesta = botonPanicoRH('true')
            _cancela_orden(0)
            respuesta = botonPanicoRH('false')
            return  operaciones.estadoOperacion()
        except:
           print("no pudo leer los datos de local storage")
     return operaciones.estadoOperacion()
   
@estrategiaSheetWS.route('/botonPanico/', methods = ['POST']) 
def botonPanico():
    respuesta = botonPanicoRH('true')
    _cancela_orden(9)
    respuesta = botonPanicoRH('false')
    #get.pyRofexInicializada.close_websocket_connection()
    return render_template("utils/bottonPanic.html" ) 

def botonPanicoRH(message):
    # Llamada al método /botonPanico utilizando la referencia a wsConnection
        if message == 'true':
         get.VariableParaBotonPanico = 1
        #print("Se accionó el Boton de Panico ?",get.VariableParaBotonPanico)
        elif message == 'false':
            get.VariableParaBotonPanico = 0
       
        return get.VariableParaBotonPanico
    
def estrategiaSheetNuevaWS(message, banderaLecturaSheet):# **11
    
    if banderaLecturaSheet == 0:
        print('entra en estrategiaSheetNuevaWS punto de control sheeeet')
        ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
        banderaLecturaSheet = 1
        ContenidoSheet_list = list(ContenidoSheet)
        
        for Symbol,tipo, TradeEnCurso,ut,senial,gan_tot, dias_operado in ContenidoSheet_list[2:]:
            if Symbol in get.diccionario_global_operaciones:
                if senial != '':
                    #aqui entra en caso que tenga que cambiar la señal de trading
                    if senial != get.diccionario_global_operaciones[Symbol]['senial']:
                        if get.diccionario_global_operaciones[Symbol]['status'] == "0":
                            get.diccionario_global_operaciones[Symbol]['senial'] = senial


            mepAl30 = 460 ####Calcula dolar MEP
     # Verificar si el diccionario de operaciones está vacío
    #if not get.diccionario_global_operaciones:
    #    print("El diccionario de operaciones está vacío.")
    #else:
        # Iterar sobre las claves y valores del diccionario
    #    for clave, valor in get.diccionario_global_operaciones.items():
            # Imprimir cada clave y su correspondiente valor
   #         print("El diccionario de operaciones contiene esto")
   #         print(clave)
   #         print(valor)
    
    Symbol = message['instrumentId']['symbol']
    
    if Symbol in get.diccionario_global_operaciones:
        #print('___________________________________________________________')    
       # print(message['instrumentId']['symbol']) 
        #rutaMDH = 'C:\\Users\\mDioli\\Documents\\tmp\\operacionesMDH_01.csv'
        
        #append_order_report_to_csv(Symbol, rutaMDH)
        tipo_de_activo = get.diccionario_global_operaciones[Symbol]['tipo_de_activo']
        senial = get.diccionario_global_operaciones[Symbol]['senial']
        TradeEnCurso =  get.diccionario_global_operaciones[Symbol]['tradeEnCurso']
        
       # if get.diccionario_global_operaciones[Symbol] == message["instrumentId"]["symbol"]:
        if get.diccionario_global_operaciones[Symbol]['status'] == "0":
               
                if get.diccionario_global_operaciones[Symbol]['ut'] !="0": 
                                                 
                    if senial != "":
                        
                       if TradeEnCurso == 'LONG_': 
                           
                                    if senial == 'OPEN.':
                                        #if message["marketData"]["OF"] != None:     
                                        if isinstance(message["marketData"]["OF"][0]["size"], int):                                  
                                            Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]
                                        else:
                                            #if message["marketData"]["LA"] != None: 
                                            if isinstance(message["marketData"]["LA"]["size"], int):                                  
                                                Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                        

                                  
                                    
                                    if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != ''  and message != '':
                                        if int(Liquidez_ahora_cedear) < int(get.diccionario_global_operaciones[Symbol]['ut']):
                                                #print('operacionews')
                                                datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, 0, message)
                                        else:                                          
                                               
                                                datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], get.diccionario_global_operaciones[Symbol]['ut'], senial, 0, message)
                       else:
                            
                              if senial == 'closed.':  
                                        #if message["marketData"]["BI"] != None: 
                                 if isinstance(message["marketData"]["BI"][0]["size"], int):                                  
                                       Liquidez_ahora_cedear = message["marketData"]["BI"][0]["size"]
                                       Liquidez_ahora_cedear = Liquidez_ahora_cedear
                                 else:
                                       #if message["marketData"]["LA"] != None:
                                       if isinstance(message["marketData"]["LA"]["size"], int):                                  
                                          Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                          Liquidez_ahora_cedear = Liquidez_ahora_cedear
                               
                                 if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != ''  and message != '':
                                        if int(Liquidez_ahora_cedear) < int(get.diccionario_global_operaciones[Symbol]['ut']):
                                                #print('Symbol ',Symbol)
                                                datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, 0, message)
                                        else:                                          
                                                #print('Symbol ',Symbol)       
                                                datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], get.diccionario_global_operaciones[Symbol]['ut'], senial, 0, message)    
                                    
   # else:  
        #print(message['instrumentId']['symbol'])  
    #    print('______________________________________________________')                                   



def carga_operaciones(ContenidoSheet_list,account,usuario,correo_electronico,message):#carg
     coincidencias = []
     contador_1=0
     símbolos_vistos = set()

     #filtrar las coincidencias entre las dos listas
     for elemento1 in ContenidoSheet_list:
        if contador_1 >= 2:
          if elemento1[4] == 'closed.':   
            for key, elemento2 in get.diccionario_operaciones_enviadas.items():
               #print('elemento1 ', elemento1[0] ,' elemento2 ',elemento2['Symbol'])      
               if elemento1[0] == elemento2['Symbol']:
                    if elemento2['Symbol'] not in símbolos_vistos: 
                        print(' elemento1[0] **********************', elemento1 )
                        coincidencias.append(elemento1)
                        símbolos_vistos.add(elemento2['Symbol'])    
        contador_1 += 1                           
     #coincidencias = [elemento2 for elemento1 in message for elemento2 in ContenidoSheet_list if elemento1 == elemento2[0]]
    
     contador = 0
     for elemento1 in ContenidoSheet_list:
        if contador >= 2:
            #print('elemento1 ', elemento1)        
            for elemento2 in message:
              #if elemento1[0] == 'MERV - XMEV - COME - 48hs':
               # print(' elemento1[0] ', elemento1 ,' elemento2 ',elemento2)
                if elemento1[2] == 'LONG_':
                     if elemento1[3] != '0':
                         # if elemento1[4] == 'OPEN.':
                          if elemento1[4] == 'OPEN.':
                            if elemento1[0] == elemento2:
                                coincidencias.append(elemento1)
                               # print(' elemento1[] ', elemento1[0])
                               # print(coincidencias)
        contador += 1  
          
    
     usuariodb = db.session.query(Usuario).filter(Usuario.correo_electronico == correo_electronico).first()
     
     for elemento  in coincidencias:  
       #  print("FUN carga_operaciones_ print(elem[0]",elemento[0],"elem[1]",elemento[1],",elem[2]",elemento[2],",elem[3]",elemento[3],",elem[4])",elemento[4])
         #print(elemento[0],elemento[1],elemento[2],elemento[3],elemento[4])
         nueva_orden = Orden(
                                user_id=usuariodb.id,
                                userCuenta=usuario,
                                accountCuenta=account,
                                clOrdId_alta=random.randint(1,100000),
                                clOrdId_baja='',
                                clientId='',
                                wsClOrdId_timestamp=datetime.now(),
                                clOrdId_alta_timestamp=None,
                                clOrdId_baja_timestamp=None,  # Campo vacío
                                proprietary=True,
                                marketId='',  # Campo vacío
                                symbol=elemento[0],
                                tipo=elemento[1],
                                tradeEnCurso=elemento[2],
                                ut=elemento[3],
                                senial=elemento[4],
                                status='0'
                            )
         # Cargar los valores del objeto en el diccionario global
         nueva_orden_para_dic = {
            'user_id': usuariodb.id,
            'userCuenta': usuario,
            'accountCuenta': account,           
            'clOrdId_alta': '',
            'clOrdId_baja': '',
            'orderId': '',
            'wsClOrdId_timestamp': datetime.now(),
            'clOrdId_alta_timestamp': None,
            'clOrdId_baja_timestamp': None,
            'proprietary': True,
            'marketId': '',           
            'symbol': elemento[0],
            'tipo_de_activo': elemento[1],
            'tradeEnCurso': elemento[2],
            'ut': elemento[3],
            'senial': elemento[4],
            'status': '0'
        }
    # Cargar cada objeto Orden en el diccionario global con una clave única
         get.diccionario_global_operaciones[elemento[0]] = nueva_orden_para_dic
       
         if elemento[0] in get.diccionario_global_operaciones:
            contenido = get.diccionario_global_operaciones[elemento[0]]
            print('cargó la operacion de ',elemento[0],' ut ',elemento[3],' correctmente en diccionario global de operaciones')
         else:
            print("La clave", elemento[0], "no existe en el diccionario.")

        
    # Acceder al diccionario global y a los objetos Orden
     
    #     db.session.add(nueva_orden)
    #     db.session.commit() 
     #get.current_session = db.session
     #for clave, valor in get.diccionario_global_operaciones.items():
     #     print(f'Clave: {clave}, Valor: {valor}')
        
    # db.session.close()
    # print("sale de cargar operaciones")

def es_numero(numero):
    try:
          int(numero)
          return True
    except:
        return False
  
def order_report_handler( order_report):
        # Obtener el diccionario de datos del reporte de orden
        
        order_data = order_report['orderReport']
        clOrdId = order_data['clOrdId']        
        symbol = order_data['instrumentId']['symbol']
        status = order_data['status']  
        #print('___________order_report_handler_______OPERADA__ ',status)
        timestamp_order_report = order_data['transactTime']  
        
        rutaORH = 'C:\\Users\\mDioli\\Documents\\tmp\\operacionesORH_01.csv'
        print('status ',status)
        append_order_report_to_csv(order_report, rutaORH)
        # se fija que cuando venga el reporte el diccionario tenga elementos
        if es_numero(clOrdId):#esto se pone por que el clOrdId puede traer basura
            if len(get.diccionario_operaciones_enviadas) != 0:
                asignarClOrId(order_report)#__
                    
                    # if status == 'EXECUTED':
                if status != 'NEW' and status != 'PENDING_NEW' and status != 'UNKNOWN':  
                    _operada(order_report)   
                       
        
def _operada(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']   
    #print(symbol,' _______************  OPERADA ****************_____________ ',order_data['text'])
    
    stock_para_closed = obtenerStock(order_data['text']) 
    stock_para_closed = int(float(stock_para_closed))
    #print('stock_para_closed ',stock_para_closed)
    if status in ['CANCELLED','ERROR','REJECTED','EXPIRED']:  
              if symbol in get.diccionario_global_operaciones:                  
                for key, operacion in get.diccionario_operaciones_enviadas.items():#11111
                            if operacion['Symbol'] == symbol and operacion['_cliOrderId'] == int(clOrdId) and  operacion['status'] != 'TERMINADA' and operacion['status'] != 'CANCELLED':
                                ut_a_devolver = operacion['_ut_']   
                                if status == 'REJECTED' :
                                    ut_a_devolver = operacion['_ut_'] + stock_para_closed 
                                    print('ut_a_devolver ',ut_a_devolver) 
                                    
                                    if ut_a_devolver <= 0:
                                       print('ut_a_devolver  == 0',ut_a_devolver)
                                       operacion['status'] = 'TERMINADA'
                                    else: 
                                       operacion['status'] = '0'
                                else:                            
                                    operacion['status'] = 'TERMINADA'
                                for key, operacionGlobal in get.diccionario_global_operaciones.items():
                                    if operacionGlobal['symbol'] == symbol :
                                        operacionGlobal['ut'] = int(operacionGlobal['ut']) + int(ut_a_devolver)
                                        #datoSheet.modificar_columna_ut(operacionGlobal['symbol'],operacionGlobal['ut'])
                                        #pprint.pprint(get.diccionario_global_operaciones)
                                        if operacionGlobal['status'] != '0':
                                            operacionGlobal['status']== '0'
                             # aqui termina las ordenes canceladas que se cargaron inicalmente               
                            if operacion['Symbol'] == symbol and operacion['_cliOrderId'] == int(clOrdId) and operacion['status'] == 'CANCELLED':                
                                operacion['status'] = 'TERMINADA'
                               # pprint.pprint(g et.diccionario_global_operaciones_)
                               # pprint.pprint(g et.diccionario_operaciones_enviadas) 
                          
                

    if status == 'FILLED': 
            endingGlobal = 'SI'  # Suponiendo inicialmente que todas las operaciones son 'si'
            endingEnviadas = 'SI'
            for operacion_enviada in get.diccionario_operaciones_enviadas.values():  
                print('operacion_enviada symbol ',symbol," endingEnviadas ",endingEnviadas,'  operacion_enviada[status] ', operacion_enviada['status'])
                if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId) and  operacion_enviada['status'] != 'TERMINADA' :
                    operacion_enviada['status'] = 'TERMINADA'                     
                    print('operacion_enviada symbol ',symbol," endingEnviadas ",endingEnviadas)
         

            for key, operacionGlobal in get.diccionario_global_operaciones.items():  
                if operacionGlobal['symbol'] == symbol and operacionGlobal['ut'] == '0':                    
                    operacionGlobal['status'] = '1'
                    print(key," : ",operacionGlobal['status']," :",operacionGlobal['ut'])
                else:  # Si alguna operación no es 'si'
                    endingGlobal = 'NO'
               
            
            endingOperacionBot (endingGlobal,endingEnviadas)                             
                               
def convert_datetime(original_datetime_str, desired_timezone_str):
    # Convertir la cadena a un objeto datetime
    original_datetime = datetime.strptime(original_datetime_str, "%Y%m%d-%H:%M:%S.%f")

    # Definir la zona horaria deseada
    desired_timezone = pytz_timezone(desired_timezone_str)

    # Convertir el objeto datetime a la zona horaria deseada
    desired_datetime = original_datetime.astimezone(desired_timezone)

    # Convertir el objeto datetime a una cadena en el formato deseado
    desired_datetime_str = desired_datetime.strftime("%Y%m%d-%H:%M:%S.%f")[:-3] + desired_datetime.strftime("%z")

    return desired_datetime_str

def _cancela_orden(delay):
    
   # clOrdId = order_data['clOrdId']
   # symbol = order_data['instrumentId']['symbol']
   # status = order_data['status']
    
    time = datetime.now()
    timestamp_order_report = time.strftime("%Y%m%d-%H:%M:%S.%f%z")
   # example_datetime_str = "20230724-13:23:12.071198"
    example_timezone_str = 'Etc/GMT+3'
    timestamp_order_report = convert_datetime(timestamp_order_report, example_timezone_str)
     
    timestamp_order_report = str(timestamp_order_report)
    
    # Recorrer los elementos del diccionario_enviados
    
    for key, valor in get.diccionario_operaciones_enviadas.items():    
           
            tiempo_diccionario = valor["timestamp"]
            # Verificar y ajustar el formato de cadena de fecha si es necesario

            if isinstance(tiempo_diccionario, str):
                tiempo_diccionario = datetime.strptime(tiempo_diccionario, "%Y-%m-%d %H:%M:%S")
           
            # Convertir el timestamp en milisegundos a objeto datetime
            # Convertir las cadenas de texto en objetos datetime
            diferencia_segundos = tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario)
           

          #  print("FUN _cancela_orden: diferencia [seg]",diferencia_segundos)
            
            
            #diferencia = fecha2_obj - tiempo_diccionario
            #print("FUN _c ancela_orden: Diferencia",diferencia)

            
            
            #if diferencia >= 300:
            if diferencia_segundos >= delay:
              # print('diferencia_segundos ',diferencia_segundos,' delay ',delay)
               _cancel_if_orders(valor["Symbol"],valor['_cliOrderId'],valor['statusActualBotonPanico'])       
      
def _cancel_if_orders(symbol,clOrdId,order_status):
    #debe sumar de la lista de orden general
    #eliminar de la ordenes enviadas luedo de confirmacion de cancelacion
    try:
        # Obtener el estado de la orden
        if order_status in ['PENDING_NEW','NEW','PENDING','REJECT','ACTIVE','PARTIALLY_EXECUTED','SENT','ROUTED','ACCEPTED','PARTIALLY_FILLED','PARTIALLY_FILLED_CANCELED','PARTIALLY_FILLED_REPLACED','PENDING_REPLACE']:
            print("FUN _cancel_if_orders: ENVIA Orden DE CANCELAR: order_status:", order_status," symbol: ",symbol," clOrdId: ",clOrdId)
            get.pyConectionWebSocketInicializada.cancel_order_via_websocket(client_order_id=clOrdId) 
        
            # Aumentar el valor de ut en get.diccionario_global_operaciones        
            for key, operacion_enviada in get.diccionario_operaciones_enviadas.items(): 
                if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId):
                    if operacion_enviada["status"] != 'PENDING_CANCEL':
                        operacion_enviada["status"] = 'PENDING_CANCEL'  
                        operacion_enviada['statusActualBotonPanico'] = 'PENDING_CANCEL' 
                        print("FUN _cancel_if_orders:  Orden :", clOrdId," symbol ",symbol, " operacion_enviada[statusActualBotonPanico] ",operacion_enviada['statusActualBotonPanico'])      
                        break  # Salir del bucle después de eliminar el elemento encontrado    
               
        else:
            pass
            #print('No se puede cancelar la Orden order_status no corresponde') 
            #print("FUN _cancel_if_orders:  Orden order_status:", order_status," symbol ",symbol," clOrdId ",clOrdId) 
    except Exception as e:
        print("Error en Envio de Cancelacion de orden:", e)
    #    print("FUN _cancel_if_orders: La orden no se puede cancelar en el estado actual:", order_status)
        
def tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario):
     fecha2_obj = datetime.strptime(timestamp_order_report, "%Y%m%d-%H:%M:%S.%f%z")
     fecha_comun_enviada = tiempo_diccionario.strftime("%Y%m%d-%H:%M:%S")
     fecha_comun_orh = fecha2_obj.strftime("%Y%m%d-%H:%M:%S")
     #print("FUN tiempoDeEsperaOperacioncalculaTiempo: fecha_enviada",fecha_comun_enviada)
     #print("FUN tiempoDeEsperaOperacioncalculaTiempo: fecha_ORH",fecha_comun_orh)
     # Restar los dos objetos datetime
     fecha_obj1 = datetime.strptime(fecha_comun_enviada, "%Y%m%d-%H:%M:%S")
     fecha_obj2 = datetime.strptime(fecha_comun_orh, "%Y%m%d-%H:%M:%S")

     diferencia = fecha_obj2 - fecha_obj1
     diferencia_segundos = abs(diferencia.total_seconds())
    
     return diferencia_segundos

def asignarClOrId(order_report):
      order_data = order_report['orderReport']
      clOrdId = order_data['clOrdId']
      symbol = order_data['instrumentId']['symbol']
      status = order_data['status']   
      timestamp_order_report = order_data['transactTime'] 
      
    #  print("FUNC_asignarClOrId  symbol ",symbol, " clOrdId ",clOrdId, " status ",status," timestamp_order_report ",timestamp_order_report)
      #pprint.pprint(g et.diccionario_operaciones_enviadas) 
      for key, valor in get.diccionario_operaciones_enviadas.items():  
        tiempo_diccionario = valor["timestamp"]  
        if valor["Symbol"] == symbol and valor["_cliOrderId"] == 0:                  
            if valor["status"] == '1':                
                # pasa que llegamos aca y wsOrderClId puede no existir mas
                if status in ['PENDING_NEW','REJECT']: 
                    if 'wsClOrdId' in order_report:                
                        wsClOrdId = order_data['wsClOrdId'] 
                        if  valor["_ws_client_order_id"] == int(wsClOrdId):
                            valor["_cliOrderId"] = int(clOrdId)
                            valor["status"] = "2"  
                            valor["statusActualBotonPanico"] = status                          
                else:
                    valor["_cliOrderId"] = int(clOrdId)

      
      
        cargar_estado_para_B_panico(valor,clOrdId,timestamp_order_report,symbol,status,tiempo_diccionario)
        
def cargar_estado_para_B_panico(valor,clOrdId,timestamp_order_report,symbol,status,tiempo_diccionario): 
        #carga el estado para el boton te panico           
        if valor["Symbol"] == symbol and valor["_cliOrderId"] ==  int(clOrdId):               
            if valor['statusActualBotonPanico'] != 'PENDING_CANCEL': 
                if isinstance(tiempo_diccionario, str):
                   tiempo_diccionario = datetime.strptime(tiempo_diccionario, "%Y-%m-%d %H:%M:%S")         
                diferencia_segundos = tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario)   
                print("FUN _asignarClOrId: diferencia [seg]",diferencia_segundos)
                #if diferencia_segundos >= 3:       
                valor["statusActualBotonPanico"] = status
                print("FUN_cargar_estado_para_B_panico status ",status, " clOrdId ",clOrdId)
                   
def CargOperacionAnterioDiccionarioEnviadas(accountCuenta,userCuenta,user_id):
   try:        
        repuesta_operacion = get.pyRofexInicializada.get_account_position()
     
        reporte = repuesta_operacion['positions']
        
# Crear un conjunto para almacenar los símbolos ya vistos
        símbolos_vistos = set()

        for item in reporte:
                símbolo = item['symbol']
            # Verificar si el símbolo ya ha sido visto antes
           # if símbolo not in símbolos_vistos:
                # Si es la primera vez que se ve el símbolo, mostrar los detalles
                print("Símbolo:", símbolo)
                print("Cantidad de stock buySize:", item['buySize'])
                print("Cantidad de stock sellSize:", item['sellSize'])
                print()
                # Agregar el símbolo al conjunto de símbolos vistos
                símbolos_vistos.add(símbolo)
       
        #print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",reporte)
        diccionario = {}
        get.diccionario_operaciones_enviadas.clear()
        for posicion in reporte:
            # Accedemos al símbolo de cada posición y lo almacenamos en el diccionario
                symbol = posicion['symbol']
           # if símbolo not in símbolos_vistos:
             #   print('**************************** ',symbol)
            
                diccionario = {
                                "Symbol": symbol,
                                "_t_": 'None',
                                "_tr_": 'None',
                                "_s_": 'None',
                                "_ut_": 'orderQty',
                                "precio Offer": 'None',
                                "_ws_client_order_id": 'None',
                                "_cliOrderId": 0,
                                "timestamp": datetime.now(),
                                "status": 'ANTERIOR',
                                "statusActualBotonPanico":'ANTERIOR',
                                "user_id": user_id,
                                "userCuenta": userCuenta,
                                "accountCuenta": accountCuenta
                                    }
                get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                #pprint.pprint( get.diccionario_operaciones_enviadas)
                #for key, valor in g et.diccionario_operaciones_enviadas.items():
                #    print(key," : ",valor['_cliOrderId'])
                símbolos_vistos.add(símbolo)
        return 'ok'
   except Exception as e:       
        print("error de carga de diccionario de enviados", e)  
        flash(' error de carga de diccionario de enviados')    
   return 'ok'                   
def estadoOperacionAnterioCargaDiccionarioEnviadas(accountCuenta,userCuenta,user_id):
   try:        
        repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
        
        datos = repuesta_operacion['orders']
        #print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",datos)
        diccionario = {}
        get.diccionario_operaciones_enviadas.clear()        
        for dato in datos:
          if dato['orderId'] is not None:
            if es_numero(dato['clOrdId']):  
                orderId = dato['orderId']
                clOrdId = dato['clOrdId']
                proprietary = dato['proprietary']
                execId = dato['execId']
                accountId = dato['accountId']
                Symbol = dato['instrumentId']['symbol']
                price = dato['price']
                orderQty = dato['orderQty']
                ordType = dato['ordType']
                side = dato['side']
                timeInForce = dato['timeInForce']
                transactTime = dato['transactTime']
                avgPx = dato['avgPx']
                #lastPx = dato['lastPx']
                #lastQty = dato['lastQty']
                cumQty = dato['cumQty']
                leavesQty = dato['leavesQty']
                status = dato['status']
                text = dato['text']
                originatingUsername = dato['originatingUsername']

                
                diccionario = {
                            "Symbol": Symbol,
                            "_t_": 'None',
                            "_tr_": 'None',
                            "_s_": 'None',
                            "_ut_": orderQty,
                            "precio Offer": 'None',
                            "_ws_client_order_id": 'None',
                            "_cliOrderId": int(clOrdId),
                            "timestamp": datetime.now(),
                            "status": status,
                            "statusActualBotonPanico":status,
                            "user_id": user_id,
                            "userCuenta": userCuenta,
                            "accountCuenta": accountCuenta
                                }
                get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                #pprint.pprint( g et.diccionario_operaciones_enviadas)
            #for key, valor in g et.diccionario_operaciones_enviadas.items():
            #    print(key," : ",valor['_cliOrderId'])
        return 'ok'
   except Exception as e:       
        print("error de carga de diccionario de enviados", e)  
        flash(' error de carga de diccionario de enviados')    
   return 'ok'                   

def obtenerStock(cadena):
# Verificar si la cadena contiene la frase "Stock insuficiente"
    if "Stock insuficiente" in cadena:
        # Buscar el índice del signo "="
        index = cadena.find("=")
        # Extraer el valor después del signo "=" y eliminar los espacios en blanco al principio y al final
        valor_despues_de_igual = cadena[index:].strip()
        
        #print('valor_despues_de_igual ' ,valor_despues_de_igual)
       
        # Buscar el número después del signo "=" utilizando una expresión regular
        match = re.search(r'(?<== )-?\d+\.\d+', valor_despues_de_igual)
       # print('match ' ,match)
        # Verificar si se encontró una coincidencia
        if match:
            valor_despues_de_igual = match.group()
           # print("El primer número después del signo '=' es:", valor_despues_de_igual)
            valor = int(float(valor_despues_de_igual))
           # print(valor)
        
            return valor_despues_de_igual
        else:
           return '0'
    else:
       return '0' 


def endingOperacionBot (endingGlobal,endingEnviadas):
     print('endingGlobal___ ',endingGlobal,' endingEnviadas',endingEnviadas)
     if endingGlobal == 'SI' and endingEnviadas == 'SI' and get.diccionario_operaciones_enviadas:
         
        get.diccionario_operaciones_enviadas.clear()
        print("###############################################") 
        print("###############################################") 
        print("###############################################")  
        print("FELICIDADES, EL BOT TERMINO DE OPERAR CON EXITO") 
        print("###############################################") 
        print("###############################################") 
        print("###############################################") 
        get.pyRofexInicializada.remove_websocket_market_data_handler(market_data_handler_estrategia)
          #      return render_template('home.html')    



def error_handler(message):
  print("error_handler Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))






def append_order_report_to_csv(report, rutaORH):
    with open(rutaORH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Comprobar si el archivo está vacío para escribir las cabeceras
        file.seek(0)
        if file.tell() == 0:
            headers = []
            for key, value in report.items():
                if isinstance(value, dict):
                    for sub_key in value.keys():
                        headers.append(f"{key}_{sub_key}")
                else:
                    headers.append(key)
            writer.writerow(headers)
        
        # Escribir los valores
        values = []
        for key, value in report.items():
            if isinstance(value, dict):
                for sub_value in value.values():
                    values.append(sub_value)
            else:
                values.append(value)
        writer.writerow(values)