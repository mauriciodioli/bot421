# exepciones
#'Working outside of application context.\n\nThis typically means that you attempted to use functionality that needed\nthe current application. To solve this, set up an application context\nwith app.app_context(). See the documentation for more information.'

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
import strategies.datoSheet as datoSheet 
import requests
import routes.api_externa_conexion.cuenta as cuenta

from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import pprint





estrategiaSheetWS = Blueprint('estrategiaSheetWS',__name__)


class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2




@estrategiaSheetWS.route('/estrategia_sheet_WS/', methods=['POST'])
def estrategia_sheet_WS():
    
    if request.method == 'POST':
        try:
            usuario = request.form['usuario']
            get.accountLocalStorage = request.form['cuenta']
            access_token = request.form['access_token']
            correo_electronico = request.form['correo_electronico']
            
            ContenidoSheet_list = SuscripcionDeSheet()#**22
           
            get.pyRofexInicializada.order_report_subscription(account= get.accountLocalStorage , snapshot=True,handler = order_report_handler)
            pyRofexWebSocket =  get.pyRofexInicializada.init_websocket_connection (
                                    market_data_handler=market_data_handler_estrategia,
                                    order_report_handler= order_report_handler,
                                    error_handler=error_handler,
                                    exception_handler=exception_handler
                                    )
            carga_operaciones(ContenidoSheet_list[0], get.accountLocalStorage ,usuario,correo_electronico,ContenidoSheet_list[1])
            # Crear una instancia de RofexMarketDataHandler
            

            
            
    #  except:  
    #      print("_EstrategyUno_contraseña o usuario incorrecto")  
    #      flash('Loggin Incorrect')    
    #      return render_template("errorLogueo.html" ) 
    
        except jwt.ExpiredSignatureError:
                print("El token ha expirado")
                return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except:
           print("no pudo leer la base de datos")
    return render_template('/estrategiaOperando.html')
     
def SuscripcionDeSheet():
    # Trae los instrumentos para suscribirte
    ContenidoSheet = get_instrumento_para_suscripcion_ws()#**66
    ContenidoSheet_list = list(ContenidoSheet)   
   
  
    longitudLista = len(ContenidoSheet_list)
    ContenidoSheet_list_solo_symbol = cargaSymbolParaValidar(ContenidoSheet_list)
   # print("Cantidad de elementos a suscribir: ",len(ContenidoSheet_list_solo_symbol))
   # print("<<<<<---------------------Instrumentos a Suscribir --------------------------->>>>>> ")
   # for item in ContenidoSheet_list_solo_symbol:
   #     print(item)

    repuesta_listado_instrumento = get.pyRofexInicializada.get_detailed_instruments()
    
    listado_instrumentos = repuesta_listado_instrumento['instruments']   
    #print("instrumentos desde el mercado para utilizarlos en la validacion: ",listado_instrumentos)
    tickers_existentes = inst.obtener_array_tickers(listado_instrumentos) 
    instrumentos_existentes = val.validar_existencia_instrumentos(ContenidoSheet_list_solo_symbol,tickers_existentes)
      
    #### aqui define el MarketDataEntry
    entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
               get.pyRofexInicializada.MarketDataEntry.OFFERS,
               get.pyRofexInicializada.MarketDataEntry.LAST]
    
      
    #### aqui se subscribe   
    mensaje = get.pyRofexInicializada.market_data_subscription(tickers=instrumentos_existentes,entries=entries)
   
    #print("instrumento_suscriptio",mensaje)
    datos = ContenidoSheet_list
    
   
    
    return [ContenidoSheet_list,instrumentos_existentes]

def cargaSymbolParaValidar(message):
    listado_final = []
    for Symbol,tipo_de_activo,trade_en_curso,ut,senial  in message: 
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
  
def get_instrumento_para_suscripcion_ws():
      ContenidoSheet = datoSheet.leerSheet()
      datoSheet.crea_tabla_orden()  
      return ContenidoSheet
    
def market_data_handler_estrategia(message):
        ## mensaje = Ticker+','+cantidad+','+spread
    
    print(" FUN: market_data_handler_estrategia: _")
     
    print( " Marca de tpo guardada:",  get.VariableParaTiemposMDHandler)
    marca_de_tiempo = message["timestamp"]
    print( " Marca de tpo Actual  :",  marca_de_tiempo, " Diferencia:", marca_de_tiempo - get.VariableParaTiemposMDHandler)
    
    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 20000: # 20 segundos
    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 60000: # 1 minuto
    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 600000: # 10 minutos
    if  (1): # entra todo el tiempo para debug. Comentar esta linea y elejir alguna opcion de arriba
            # esto hay que hacerlo aca, solo cada x segundos
            banderaLecturaSheet = 1 #La lectura del sheet es solo cada x minutos
            print("marca_de_tiempo - get.VariableParaTiemposMDHandler :",marca_de_tiempo - get.VariableParaTiemposMDHandler)
            if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 60000:#para testear luego eliminar
             banderaLecturaSheet = 0 #La lectura del sheet es solo cada x minutos
            get.VariableParaSaldoCta=cuenta.obtenerSaldoCuenta( get.accountLocalStorage )# cada mas de 5 segundos
            #print ( "ENTROOOO ahora:",  get.VariableParaTiemposMDHandler ,' account: ' )
            get.VariableParaTiemposMDHandler = message["timestamp"]# milisegundos
    
    # Va afuera de la verificacion de periodo de tiempo, porque debe ser llamada inmediatamente
    # para cumplir con el evento de mercado market data
    
    #symbol = message["instrumentId"]["symbol"]
    #print(symbol)
    #print(get.diccionario_global_operaciones.items())
    #lista = list(get.diccionario_global_operaciones.items())
    #print(lista[0][1]['clOrdId_alta'])
   
    
      
    if message["marketData"]["BI"] != None:
        if  message["marketData"]["OF"] != None:
            if  message["marketData"]["LA"] != None:  
                estrategiaSheetNuevaWS(message,banderaLecturaSheet)
        
    
        
        
        






    # Defines the handlers that will process the Order Reports.


@estrategiaSheetWS.route('/botonPanico/', methods = ['POST']) 
def botonPanico():
    respuesta = botonPanicoRH('true')
    #get.pyRofexInicializada.close_websocket_connection()
    return render_template("utils/bottonPanic.html" ) 

def botonPanicoRH(message):
    # Llamada al método /botonPanico utilizando la referencia a wsConnection
        if message == 'true':
         get.VariableParaBotonPanico = 1
        print("esta dentro del boton de panico ",get.VariableParaBotonPanico)
        
        return get.VariableParaBotonPanico
    
def order_report_handler( order_report):
    
    # Este es el Execution Report y se envía al cliente cada vez que hay un cambio en el estado de una orden. 
    """ **11
    El campo wsClOrdId se utiliza para identificar la orden envíada.
    Este campo va a venir solamente en el primer Execution Report (con estado PENDING_NEW o REJECT).
    
    En el primer Execution Report recibido el campo wsClOrdId se debe referenciar con el campo clOrdId
        para poder seguir los diferentes estados de la orden.
    
    El campo wsClOrdId es un campo general alfanumerico de hasta 20 caracteres que nosotros elegimos
        El usuario debe asegurarse que el ID ingresado le permita identificar la orden. 
        La API no valida que el ID sea único.
        
    Para saber qué sucedió con la orden
    Verificar: ID de cuenta, el ID de ejecución y el estado de la orden. 
    
    client_order_ID (clOrdId): 
        Es el id de request al mercado de alta de una orden
        Request de cancelacion de orden tiene clOrdId distinto. Pero ambos request pueden ser sobre la
        misma orden con su Order_ID.
    orderId :  
        ID de la orden en mercado. Si la orden fue rechazada o todavía no llegó al
        mercado, este campo es null.
        
    Valores posibles de status: NEW, PENDING_NEW, PENDING_REPLACE, PENDING_CANCEL, REJECTED, PENDING_APPROVAL, CANCELLED y 
    REPLACED
    
    ordType: Tipo de orden. Valores posibles:
        ● LIMIT        ● MARKET        ● MARKET        ● STOP_LIMIT        ● STOP_LIMIT_MERVAL
    
    "clientId":"user14473450286174Cnl5"
    "proprietary":"PBCP"
    
    """   
    #orderId: ID de la orden. 
    # Si la orden fue rechazada o todavía no llegó al mercado, este campo es none.
    # verificar si es none, si lo es, recien preguntar por wsClOrdId
    # si este campo existe, wsClOrdId ya no existe !!!
    #print(order_report["orderReport"]["orderId"])
    if order_report["orderReport"]["orderId"] is None:
        print("OR: no hay orderId, chequeando wsClOrdId ... ")
    else    :
        print("OR: orderId :", order_report["orderReport"]["orderId"])
        
    
    #clOrdId: 
    # ID del request de una orden.
    print(order_report["orderReport"]["clOrdId"])
    # wsClOrdId: 
    # ID de validacion nuestra
    print(order_report["orderReport"]["wsClOrdId"])
    # status
    # En una orden, especifica el estado de la misma. Valores posibles:
    # NEW, PENDING_NEW, PENDING_REPLACE, PENDING_CANCEL, REJECTED, PENDING_APPROVAL, CANCELLED, REPLACED
    print(order_report["orderReport"]["status"])
    # text -->> refiere el motivo del estado de la orden.
    print(order_report["orderReport"]["text"])


    # proprietary:  
    # Si las órdenes se envían vía API REST/WS, el propietario de la orden puede ser “PBCP” o “ISV_PBCP”.
    print(order_report["orderReport"]["proprietary"])
    
    # id. nombre de la cuenta: REM6603
    print(order_report["orderReport"]["accountId"]["id"])
    
    print(order_report["orderReport"]["instrumentId"]["marketId"])#ROFX
    print(order_report["orderReport"]["instrumentId"]["symbol"])

    
    print(order_report["orderReport"]["price"])
    print(order_report["orderReport"]["orderQty"])
    print(order_report["orderReport"]["ordType"])
    print(order_report["orderReport"]["side"])
    print(order_report["orderReport"]["timeInForce"])
    print(order_report["orderReport"]["transactTime"])
    
    


def estrategiaSheetNuevaWS(message, banderaLecturaSheet):
    if banderaLecturaSheet == 0:
        ContenidoSheet = datoSheet.leerSheet()
        banderaLecturaSheet = 1
        ContenidoSheet_list = list(ContenidoSheet)

        for Symbol,tipo, TradeEnCurso,ut,senial in ContenidoSheet_list[2:]:
            if Symbol in get.diccionario_global_operaciones:
                print(senial)
                if senial != '':
                    if senial != get.diccionario_global_operaciones[Symbol]['senial']:
                        if get.diccionario_global_operaciones[Symbol]['status'] == "0":
                            print(get.diccionario_global_operaciones[Symbol]['senial'])
                            get.diccionario_global_operaciones[Symbol]['senial'] = senial
                            print(get.diccionario_global_operaciones[Symbol]['senial'])

            #mepAl30 = calcularMepAl30WS(message) ####Calcula dolar MEP
            mepAl30 = 460 ####Calcula dolar MEP
    Symbol = message["instrumentId"]["symbol"]
    tipo_de_activo = get.diccionario_global_operaciones[Symbol]['tipo_de_activo']
    senial = get.diccionario_global_operaciones[Symbol]['senial']
    TradeEnCurso =  get.diccionario_global_operaciones[Symbol]['tradeEnCurso']
    if Symbol in get.diccionario_global_operaciones:
       # if get.diccionario_global_operaciones[Symbol] == message["instrumentId"]["symbol"]:
            if get.diccionario_global_operaciones[Symbol]['status'] == "0":
                if get.diccionario_global_operaciones[Symbol]['ut'] !="0":                                
                    if TradeEnCurso == 'LONG_':                        
                        if senial != "":
                            if get.diccionario_global_operaciones[Symbol]['tipo_de_activo'] == 'CEDEAR':
                                mepCedear = calcularMepCedearsWS(message)
                                porcentaje_de_diferencia = -1 #se compara el mepCedear con el mepAl30                                
                                if porcentaje_de_diferencia <= 1:
                                    if senial == 'OPEN.':
                                        if message["marketData"]["OF"] != None:                                         
                                            Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]
                                        if message["marketData"]["LA"] != None:                                         
                                            Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                            

                                    if senial == 'closed.':  
                                        if message["marketData"]["BI"] != None: 
                                            Liquidez_ahora_cedear = message["marketData"]["BI"][0]["size"]
                                        if message["marketData"]["LA"] != None:
                                            Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                       
                                    if int(Liquidez_ahora_cedear) < int(get.diccionario_global_operaciones[Symbol]['ut']):
                                        if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear != 0 and message != '':
                                         datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, mepCedear, message)
                                         print("*1 FUN: estrategiaSheetNuevaWS -->> dato.")
                                        else:                                          
                                          datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], get.diccionario_global_operaciones[Symbol]['ut'], senial, mepCedear, message)
                                          print("*1 FUN: estrategiaSheetNuevaWS -->> dato.")
                            if get.diccionario_global_operaciones[Symbol]['tipo_de_activo'] == 'ARG':
                                    
                                    if senial == 'OPEN.':
                                        if message["marketData"]["OF"] != None:                                       
                                            Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]
                                        if message["marketData"]["LA"] != None: 
                                            Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                        

                                    if senial == 'closed.':  
                                        if message["marketData"]["BI"] != None: 
                                             Liquidez_ahora_cedear = message["marketData"]["BI"][0]["size"]
                                        if message["marketData"]["LA"] != None:
                                             Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                        

                                    if int(Liquidez_ahora_cedear) < int(get.diccionario_global_operaciones[Symbol]['ut']):
                                        print(Symbol," ",tipo_de_activo," ",TradeEnCurso," ",Liquidez_ahora_cedear," ",senial," ",mepCedear,message)
                                        if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear != 0 and message != '':
                                            #datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, mepCedear, message)
                                         print("*1 FUN: estrategiaSheetNuevaWS -->> dato.")
                                        else:
                                          
                                            #datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], get.diccionario_global_operaciones[Symbol]['ut'], senial, mepCedear, message)
                                          print("*1 FUN: estrategiaSheetNuevaWS -->> dato.")




##########################AQUI SE REALIZA CALCULO DE MEP CEDEARS####################
def calcularMepCedearsWS(message):
     #traer los precios del cedear
    # print("_calcularMepCedears_______ le da 380")
     resultado = instrument_by_symbol_para_CalculoMep(message) 
     #resultado2 = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs") 
     
    # ko_ci = resultado['OF'][0]['price'] #vendedora OF ko_ci punta vendedora (porque es lo que yo deberia comprar si quiero dolar mep)
    # koD_ci =resultado2['BI'][0]['price'] #compradora BI koD_ci punta compradora (el que me compra lo bonos para tener mis dolares)
    # size = resultado2['BI'][0]['size']
   #  print("__________ko_ci____________",ko_ci)
   #  print("__________koD_ci____________",koD_ci)
   #  print("__________size____________",size)
     #mep= ko_ci / koD_ci
     
     """"
     if len(resultado['OF']) > 0:
        offer_price = resultado['OF'][0]['price'] #vendedora OF
     else:
        offer_price=0
        
     if len(resultado['BI']) > 0:
        bid_price =resultado['BI'][0]['price'] #compradora BI
     else:
        bid_price=0
     """
     offer_price=0      # borrar y programar bien
     bid_price=0        # borrar y programar bien
     mep=380            # borrar y programar bien
     size=10
     dato = [mep,size,offer_price,bid_price]
     return dato
 
 
 
def calcularMepAl30WS(message):
     
     
  #  resultado = instrument_by_symbol_para_CalculoMep(message)    
  #  resultado2 = instrument_by_symbol_para_CalculoMep(message) 
    
    
    #if isinstance(message["marketData"]["OF"][0]["price"],float):
    #precio = message["marketData"]["OF"][0]["price"]
    #if isinstance(message["marketData"]["OF"][0]["size"],int):
    #Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]


    #if len( message['marketData']['OF']) == 0:
    if not isinstance(message["marketData"]["OF"][0]["size"],int):# entra si el offer esta vacio
        # entra si el offer esta vacio
        print(" FUN calcularMepAl30WS: La clave 'OF' está vacía.")
    else:

        al30_ci = message['marketData']['OF'][0]['price'] #vendedora OF
        al30D_ci =message['marketData']['BI'][0]['price'] #compradora BI
        #print("__________al30_ci____________",al30_ci)
        #print("__________al30D_ci____________",al30D_ci)
        
        # simulo compra de bono      
        #print("____simulo compra de bono ")  
        # al30ci_unitaria = al30_ci/100
        #cantidad_al30ci=int(10000/al30ci_unitaria)
        #print("__________cantidad_al30ci_________",cantidad_al30ci)
        
        # ahora simulo la venta de los bonos D
        #print("ahora simulo la venta de los bonos D")
        #al30D_ci_unitaria = al30D_ci/100
        #dolaresmep = al30D_ci_unitaria * cantidad_al30ci
        #mep = 10000 / dolaresmep
    mep = 380
    #print(" FUN calcularMepAl30WS: .")
    return mep

def instrument_by_symbol_para_CalculoMep(message):
     # print("__________entra a instrument_by_symbol____________",message) 
      try:
        
                
            objeto = message 
           # for objeto in objeto:     
            
           # print("instrumentooooooooooooooooooooooooooooo LA ",objeto['marketData']['LA'])
           # print("instrumentooooooooooooooooooooooooooooo BI ",objeto['BI'])            
           # print("instrumentooooooooooooooooooooooooooooo OF ",objeto['OF'])
            jdato = str(objeto['marketData']['LA'])
            jdato1 = str(objeto['marketData']['BI'])
            jdato2 = str(objeto['marketData']['OF'])
            if jdato.find('price')==-1:
                print("no tiene nada LA ",jdato.find('price'))
                
            elif jdato1.find('price')==-1:
                print("no tiene nada BI ",jdato1.find('price'))
                
            
            elif jdato2.find('price')==-1:
                print("no tiene nada OF",jdato2.find('price'))
           
            return objeto
        
      except:       
        flash('instrument_by_symbol_para_CalculoMep__: Symbol Incorrect')   
        return render_template("instrumentos.html" )

def carga_operaciones(ContenidoSheet_list,account,usuario,correo_electronico,message):#carg
      
     #filtrar las coincidencias entre las dos listas
     coincidencias = [elemento2 for elemento1 in message for elemento2 in ContenidoSheet_list if elemento1 == elemento2[0]]

    # print(coincidencias)
    
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
            'wsClOrdId' : random.randint(1, 100000),
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

        
        
    # Acceder al diccionario global y a los objetos Orden
     
    #     db.session.add(nueva_orden)
    #     db.session.commit() 
     #get.current_session = db.session
     #for clave, valor in get.diccionario_global_operaciones.items():
     #     print(f'Clave: {clave}, Valor: {valor}')
        
    # db.session.close()
    # print("sale de cargar operaciones")


def order_report_handler( order_report):
        # Obtener el diccionario de datos del reporte de orden
        order_data = order_report['orderReport']

        # Leer un valor específico del diccionario
        clOrdId = order_data['clOrdId']
        symbol = order_data['instrumentId']['symbol']
        status = order_data['status']      
        
    
            #orderId: ID de la orden. 
    # Si la orden fue rechazada o todavía no llegó al mercado, este campo es none.
    # verificar si es none, si lo es, recien preguntar por wsClOrdId
    # si este campo existe, wsClOrdId ya no existe !!!
    #print(order_report["orderReport"]["orderId"])
      

        _cancela_orden(order_report)
          
        if status == 'EXECUTED':
            _operada(order_report) 
        
         ###### BOTON DE PANICO        
        response = botonPanicoRH('false') 
        print("respuesta desde el boton", response)
        
        if response == 1: ### si es 1 el boton de panico fue activado
             _cancel_if_orders(symbol,clOrdId,status)
        
        
     
                    
                    

def _update_size(order):
        if order["orderReport"]["status"] in ("PARTIALLY_FILLED", "FILLED"):
            if order["orderReport"]["side"] == "BUY":
                InstrumentoEstrategiaUno.buy_size -= round(order["orderReport"]["lastQty"])
            if order["orderReport"]["side"] == "SELL":
                InstrumentoEstrategiaUno.sell_size -= round(order["orderReport"]["lastQty"])
            if InstrumentoEstrategiaUno.sell_size == InstrumentoEstrategiaUno.buy_size == 0:
                InstrumentoEstrategiaUno.sell_size = InstrumentoEstrategiaUno.buy_size = InstrumentoEstrategiaUno.initial_size

def _operada(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']
    timestamp = order_data['timestamp']

    if status not in ['CANCELLED', 'FILLED']:
        if symbol in get.diccionario_global_operaciones:
            global_order = get.diccionario_global_operaciones[symbol]
            operacion_enviada = None
            for operacion in get.diccionario_operaciones_enviadas:
                if operacion['Symbol'] == symbol and operacion['client_order_id'] == clOrdId:
                    operacion_enviada = operacion
                    break

            if operacion_enviada:
                if global_order['ut'] > 0:
                    global_order['ut'] -= operacion_enviada['ut']
                    operacion_enviada['status'] = 'OPERATED'
                    operacion_enviada['timestamp'] = timestamp
                else:
                    global_order['status'] = '1'
                    operacion_enviada['status'] = 'OPERATED'
                    operacion_enviada['timestamp'] = timestamp

    
def _cancela_orden(order_report):
    
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']
    timestamp = order_data['timestamp']
    # Recorrer los elementos del diccionario_enviados
    for valor in get.diccionario_operaciones_enviadas.items():
        if valor["Symbol"] == symbol:           
            if valor["status"] == 1:
                if  valor["_ws_client_order_id"] == order_report['wsOrderClId'] :
                    valor["_cliOrderId"] = order_report['ClOrderId']
                    valor["status"] = "2"
                break

             
            timestamp_order_report = timestamp
            tiempo_diccionario = valor["timestamp"]
            tiempo_order_report = datetime.strptime(timestamp_order_report, "%Y-%m-%d %H:%M:%S.%f")
            tiempo_diferencia = tiempo_order_report - tiempo_diccionario
           
            if tiempo_diferencia >= 5:
               _cancel_if_orders(symbol,clOrdId,status)            
    
    
     
def _cancel_if_orders(symbol,clOrdId,order_status):
    #debe sumar de la lista de orden general
    #eliminar de la ordenes enviadas luedo de confirmacion de cancelacion
    print("Orden order_status:", order_status)
     # Obtener el estado de la orden
    if order_status in ['PENDING', 'ACTIVE', 'PARTIALLY_EXECUTED', 'SENT', 'ROUTED', 'ACCEPTED']:
        get.pyConectionWebSocketInicializada.cancel_order_via_websocket(client_order_id=clOrdId) 
        print("Orden cancelada:", clOrdId)
          # Aumentar el valor de ut en get.diccionario_global_operaciones
        for clave, valor in get.diccionario_global_operaciones.items():
            if valor["Symbol"] == symbol and valor["client_order_id"] == clOrdId:
                ut_actual = int(valor["ut"])
                ut_enviada = int(get.diccionario_operaciones_enviadas[0]["ut"])
                incremento = ut_actual * (ut_enviada / ut_actual)
                valor["ut"] = str(ut_actual + incremento)
                break  
        
        # Eliminar la orden de get.diccionario_operaciones_enviadas
        for orden in get.diccionario_operaciones_enviadas:
            if orden["Symbol"] == symbol and orden["client_order_id"] == clOrdId:
                get.diccionario_operaciones_enviadas.remove(orden)
                break
    else:
        print("La orden no se puede cancelar en el estado actual:", order_status)
        
   

   

def _send_order( side, px, size):
        InstrumentoEstrategiaUno.state = States.WAITING_ORDERS
        order = get.pyRofexInicializada.send_order(
            ticker=InstrumentoEstrategiaUno.instrument,
            side=side,
            size=size,
            price=round(px, 6),
            order_type=get.pyRofexInicializada.OrderType.LIMIT,
            cancel_previous=True
        )
        InstrumentoEstrategiaUno.my_order[order["order"]["clientId"]] = None
        print("sending %s order %s@%s - id: %s" % (side, size, px, order["order"]["clientId"]))                


##########################esto es para ws#############################


def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))

#'Working outside of application context.\n\nThis typically means that you attempted to use functionality that needed\nthe current application. To solve this, set up an application context\nwith app.app_context(). See the documentation for more information.'