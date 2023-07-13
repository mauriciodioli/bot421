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
            get.VariableParaBotonPanico = 0
            ContenidoSheet_list = SuscripcionDeSheet()#**22
            estadoOperacionAnterioCargaDiccionarioEnviadas(get.accountLocalStorage,usuario,correo_electronico)
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
    #print(message)
    time = datetime.now()
    timeuno = int(time.timestamp())*1000
    # message1 = {'type': 'Md', 'timestamp': 1684504693780, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'WTI/JUL23'}, 'marketData': {'OF': [{'price': 72.44, 'size': 100}], 'BI': [{'price': 72.4, 'size': 100}], 'LA': {'price': 72.44, 'size': 200, 'date': 1684504670967}}}
    # message2 = {'type': 'Md', 'timestamp': 1684504693780, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'ORO/JUL23'}, 'marketData': {'OF': [{'price': 72.44, 'size': 100}], 'BI': [{'price': 72.4, 'size': 100}], 'LA': {'price': 72.44, 'size': 200, 'date': 1684504670967}}}
    #message = {'type': 'Md', 'timestamp': timeuno, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'WTI/JUL23'}, 'marketData': {'OF': [{'price': 68.92, 'size': 100}], 'BI': [{'price': 68.83, 'size': 100}], 'LA': {'price': 68.82, 'size': 3, 'date': 1687786000759}}}    
        ###### BOTON DE PANICO #########        
    response = botonPanicoRH('false') 
    print("respuesta desde el boton", response)
    #puse uno para probar cuando termino de testear poner != 1        
    if response != 1: ### si es 1 el boton de panico fue activado

        print(" FUN: market_data_handler_estrategia: _")
        
        #print( " Marca de tpo guardada:",  get.VariableParaTiemposMDHandler)
        marca_de_tiempo = message["timestamp"]
        #print( " Marca de tpo Actual  :",  marca_de_tiempo, " Diferencia:", marca_de_tiempo - get.VariableParaTiemposMDHandler)
        #contador = 0
        #while contador < 100:
        #    contador +=1
        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 20000: # 20 segundos
        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 60000: # 1 minuto
        #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 600000: # 10 minutos
        banderaLecturaSheet = 1 #La lectura del sheet es solo cada x minutos
        #if  (60000): # entra todo el tiempo para debug. Comentar esta linea y elejir alguna opcion de arriba
           

           # pedir el listado de instrumentos existentes en la cta, para verificar
           # antes de hacer un close. deberia coincidir lo que quiero cerrar con lo que
           # hay efectivamente para cerrar

        if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 10000: # 10 segundos        
            get.VariableParaSaldoCta=cuenta.obtenerSaldoCuenta( get.accountLocalStorage )# cada mas de 5 segundos
            #VariableParaSaldoCta
            banderaLecturaSheet = 0 #La lectura del sheet es solo cada x minutos
            get.VariableParaTiemposMDHandler = message["timestamp"]# milisegundos
        
        # Va afuera de la verificacion de periodo de tiempo, porque debe ser llamada inmediatamente
        # para cumplir con el evento de mercado market data
        
        #symbol = message["instrumentId"]["symbol"]
        #print(symbol)
        #print(get.diccionario_global_operaciones.items())
        #lista = list(get.diccionario_global_operaciones.items())
        #print(lista[0][1]['clOrdId_alta'])

        if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
            print("FUN market_data_handler_estrategia: message[marketData][BI] es None o está vacío")
        elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
            print("FUN market_data_handler_estrategia: message[marketData][OF] es None o está vacío")
        elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:
            print("FUN market_data_handler_estrategia: message[marketData][LA] es None o está vacío")
        else:
        
            tiempoAhora = datetime.now()
            estrategiaSheetNuevaWS(message, banderaLecturaSheet)
            tiempoDespues = datetime.now()
            teimporAhoraInt = tiempoDespues - tiempoAhora
            tiempomili =  teimporAhoraInt.total_seconds() * 1000
            print("FUN_ estrategiaSheetWS tiempoTotal en microsegundos: ",teimporAhoraInt.microseconds," en milisegundo: ",tiempomili)
        
            """"
            * NEW
            * PARTIALLY_FILLED
            * FILLED
            * CANCELLED
            * REJECTED
            * EXPIRED
            * PENDING_CANCEL
            * PENDING_REPLACE
                REPLACED
                CALCULATED
                ACCEPTED_FOR_BIDDING
                * PENDING_NEW
                * PARTIALLY_FILLED_CANCELED
                * PARTIALLY_FILLED_REPLACED
                * UNKNOWN
                * ERROR
                * OK
            """ 
          #  order_report = { 'orderId' : 1686061963452333,'clOrdId' : 424621963526655,'proprietary' : "PBCP","execId" : 1685959201352046,"accountId" : {'id': 'REM6603'},"instrumentId" : {'marketId': 'ROFX', 'symbol': message['instrumentId']['symbol']},'price' : 71.67,'orderQty' : 15,'ordType' : 'LIMIT','side' : 'BUY','timeInForce' : 'DAY','transactTime' : '20230606-11:32:43.452-0300','avgPx' : 0,'lastPx' : 0,'lastQty' : 0,'cumQty' : 0,'leavesQty' : 15,
          #                  'status' : 'FILLED',
          #                  'text' : 'ME_ACCEPTED',
          #                  'originatingUsername' : 'PBCP'                        
          #                  }
           # order_report_handler( order_report)
                
            # aca iria un if del saldo, si el saldo da cero porque el sistema anda mal
            # o porque es fin de semana o fuera de horario de negociacion
            # mejor que no entre a hacer cosas que generen errores
            # ahora es domingo y me da cero el saldo    

    
    
        






    


@estrategiaSheetWS.route('/botonPanico/', methods = ['POST']) 
def botonPanico():
    respuesta = botonPanicoRH('true')
    #get.pyRofexInicializada.close_websocket_connection()
    return render_template("utils/bottonPanic.html" ) 

def botonPanicoRH(message):
    # Llamada al método /botonPanico utilizando la referencia a wsConnection
        if message == 'true':
         get.VariableParaBotonPanico = 1
        print("Se accionó el Boton de Panico ?",get.VariableParaBotonPanico)
        
        return get.VariableParaBotonPanico
    

def estrategiaSheetNuevaWS(message, banderaLecturaSheet):
    
    if banderaLecturaSheet == 0:
        ContenidoSheet = datoSheet.leerSheet()
        banderaLecturaSheet = 1
        ContenidoSheet_list = list(ContenidoSheet)

        for Symbol,tipo, TradeEnCurso,ut,senial in ContenidoSheet_list[2:]:
            if Symbol in get.diccionario_global_operaciones:
                #print("FUN estrategiaSheetNuevaWS Symbol:",Symbol," senial",senial)
                if senial != '':
                    #aqui entra en caso que tenga que cambiar la señal del stock de operaciones 
                    if senial != get.diccionario_global_operaciones[Symbol]['senial']:
                        if get.diccionario_global_operaciones[Symbol]['status'] == "0":
                            print(get.diccionario_global_operaciones[Symbol]['senial'])
                            get.diccionario_global_operaciones[Symbol]['senial'] = senial
                            print(get.diccionario_global_operaciones[Symbol]['senial'])
                if senial == 'closed.' and  message["instrumentId"]["symbol"] == Symbol:
                             cargar_operarciones_diccionario_operaciones_enviadas(Symbol)
                            
                            

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
                                        #if message["marketData"]["OF"] != None:
                                        if isinstance(message["marketData"]["OF"][0]["size"], int):#sacar
                                            Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]
                                        else:
                                            #if message["marketData"]["LA"] != None:                                         
                                            if isinstance(message["marketData"]["LA"]["size"], int):
                                                Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                       
                                        if Liquidez_ahora_cedear < int(get.diccionario_global_operaciones[Symbol]['ut']):
                                                
                                            if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear[0] != 0 and message != '':
                                                      datoSheet.OperacionWs(Symbol, tipo_de_activo,0, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, mepCedear, message)
                                                # datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'],'1', senial, mepCedear, message)
                                        else:                                          
                                            if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear[0] != 0 and message != '':
                                                      datoSheet.OperacionWs(Symbol, tipo_de_activo,0, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], get.diccionario_global_operaciones[Symbol]['ut'], senial, mepCedear, message)
                                           
                                      

                                    if senial == 'closed.':  
                                        #if message["marketData"]["BI"] != None: 
                                        if isinstance(message["marketData"]["BI"][0]["size"], int):
                                            Liquidez_ahora_cedear = message["marketData"]["BI"][0]["size"]
                                        else:
                                            #if message["marketData"]["LA"] != None:
                                            if isinstance(message["marketData"]["LA"]["size"], int):
                                                Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                                
                                        if len(get.diccionario_operaciones_enviadas) != 0:  
                                          for key, valor in get.diccionario_operaciones_enviadas.items():
                                            if valor['Symbol'] == message["instrumentId"]["symbol"]:
                                                if Liquidez_ahora_cedear < valor['_ut_']:
                                                    if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear[0] != 0 and message != '':
                                                        datoSheet.OperacionWs(valor['Symbol'] , tipo_de_activo, 0 , get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, mepCedear, message)
                                                    # datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'],'1', senial, mepCedear, message)
                                                else:                                          
                                                    if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear[0] != 0 and message != '':
                                                       datoSheet.OperacionWs(valor['Symbol'] , tipo_de_activo, 0 , get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], valor['_ut_'], senial, mepCedear, message)
                                                        # datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'],'1', senial, mepCedear, message)
                                         
                            if get.diccionario_global_operaciones[Symbol]['tipo_de_activo'] == 'ARG':
                                    mepCe = 0   
                                    if senial == 'OPEN.':
                                        #if message["marketData"]["OF"] != None:     
                                        if isinstance(message["marketData"]["OF"][0]["size"], int):                                  
                                            Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]
                                        else:
                                            #if message["marketData"]["LA"] != None: 
                                            if isinstance(message["marketData"]["LA"]["size"], int):                                  
                                                Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                        if Liquidez_ahora_cedear < int(get.diccionario_global_operaciones[Symbol]['ut']):
                                            if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != ''  and message != '':
                                                datoSheet.OperacionWs(Symbol, tipo_de_activo,0, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, mepCe, message)
                                            # datoSheet.OperacionWs(Symbol, tipo_de_activo, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'],'1', senial, mepCedear, message)
                                        else:   
                                                                              
                                            if Symbol != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != ''  and message != '':
                                                    datoSheet.OperacionWs(Symbol, tipo_de_activo,0, get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], get.diccionario_global_operaciones[Symbol]['ut'], senial, mepCe, message)
                                           

                                    if senial == 'closed.':  
                                        #if message["marketData"]["BI"] != None: 
                                        if isinstance(message["marketData"]["BI"][0]["size"], int):                                  
                                             Liquidez_ahora_cedear = message["marketData"]["BI"][0]["size"]
                                        else:
                                            #if message["marketData"]["LA"] != None:
                                            if isinstance(message["marketData"]["LA"]["size"], int):                                  
                                                Liquidez_ahora_cedear = message["marketData"]["LA"]["size"]
                                        if len(get.diccionario_operaciones_enviadas) != 0:
                                          for key, valor in get.diccionario_operaciones_enviadas.items():
                                            if valor['Symbol'] == message["instrumentId"]["symbol"]:
                                                if Liquidez_ahora_cedear < valor['_ut_']:
                                                    if valor['status'] == 'OPERAR' and valor['Symbol']  != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != ''  and message != '':
                                                        datoSheet.OperacionWs(valor['Symbol'] , tipo_de_activo, valor['_cliOrderId'], get.diccionario_global_operaciones[Symbol]['tradeEnCurso'], Liquidez_ahora_cedear, senial, 0, message)
                                                else:                                          
                                                    if valor['status'] == 'OPERAR' and valor['Symbol']  != '' and tipo_de_activo != '' and TradeEnCurso != '' and Liquidez_ahora_cedear != 0 and senial != '' and message != '':
                                                        datoSheet.OperacionWs(valor['Symbol'] , tipo_de_activo, valor['_cliOrderId'], get.diccionario_global_operaciones[Symbol]['tradeEnCurso'],valor['_ut_'], senial, 0, message)
                                        




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
      #print("__________FUN instrument_by_symbol_para_CalculoMep:____________",message) 
      #print("_FUN CalculoMep:_") 
      try:
        
                
            objeto = message 
            jdato = str(objeto['marketData']['LA'])
            jdato1 = str(objeto['marketData']['BI'])
            jdato2 = str(objeto['marketData']['OF'])
            if jdato.find('price')==-1:
                print("FUN instrument_by_symbol_para_CalculoMep: no existe LA ",jdato.find('price'))
                
            elif jdato1.find('price')==-1:
                print("FUN instrument_by_symbol_para_CalculoMep: no existe BI ",jdato1.find('price'))
                
            
            elif jdato2.find('price')==-1:
                print("FUN instrument_by_symbol_para_CalculoMep: no existe OF",jdato2.find('price'))
           
            return objeto
        
      except:       
        flash('FUN instrument_by_symbol_para_CalculoMep: Symbol Incorrecto')   
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
        #################################################
        ###### cambiar esto finalizado el test ##########
        #################################################
        #order_data = order_report
        # Leer un valor específico del diccionario
        clOrdId = order_data['clOrdId']
        symbol = order_data['instrumentId']['symbol']
        status = order_data['status']   
        # se fija que cuando venga el reporte el diccionario tenga elementos
        if len(get.diccionario_operaciones_enviadas) != 0:
            asignarClOrId(order_report)
        
            
                ###### BOTON DE PANICO #########        
            response = botonPanicoRH('false') 
            print("respuesta desde el boton", response)
                
            if response == 1: ### si es 1 el boton de panico fue activado
                
                _cancel_if_orders(symbol,clOrdId,status)
                if status != 'NEW' and status != 'PENDING_NEW' and status != 'UNKNOWN':  
                  _operada(order_report) 
            
            else:  
            
                if status != 'FILLED' and status !='CANCELLED'and  status != 'ERROR' and status != 'REJECTED' and status != 'EXPIRED' and status != 'UNKNOWN': 
                    _cancela_orden(order_report)
                    
                # if status == 'EXECUTED':
                if status != 'NEW' and status != 'PENDING_NEW' and status != 'UNKNOWN':  
                    _operada(order_report) 
             
        
            

def _operada(order_report):
    order_data = order_report['orderReport']
     #################################################
     ###### cambiar esto finalizado el test ##########
     #################################################
    #order_data = order_report
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']   
   
   
    if status in ['CANCELLED','ERROR','REJECTED','EXPIRED']:  
              if symbol in get.diccionario_global_operaciones:                  
                for key, operacion in get.diccionario_operaciones_enviadas.items():
                            if operacion['Symbol'] == symbol and operacion['_cliOrderId'] == int(clOrdId) and  operacion['status'] != 'TERMINADA' and operacion['status'] != 'CANCELLED':
                                ut_a_devolver = operacion['_ut_']                                
                                operacion['status'] = 'TERMINADA'
                                for key, operacionGlobal in get.diccionario_global_operaciones.items():
                                    if operacionGlobal['symbol'] == symbol :
                                        pprint.pprint(get.diccionario_global_operaciones)
                                        operacionGlobal['ut'] ==  int(operacionGlobal['ut']) + int(ut_a_devolver)
                                        pprint.pprint(get.diccionario_global_operaciones)
                                        if operacionGlobal['status'] != '0':
                                            operacionGlobal['status']== '0'
                            if operacion['Symbol'] == symbol and operacion['_cliOrderId'] == int(clOrdId) and operacion['status'] == 'CANCELLED':                
                                operacion['status'] = 'TERMINADA'
                                pprint.pprint(get.diccionario_global_operaciones)
                                pprint.pprint(get.diccionario_operaciones_enviadas) 

    if status == 'FILLED': 
            endingEnviadas = 'SI'
            endingGlobal = 'SI'  
              
            for operacion_enviada in get.diccionario_operaciones_enviadas.values():  
                if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId) and  operacion_enviada['status'] != 'TERMINADA':
                    operacion_enviada['status'] = 'TERMINADA'
                if  operacion_enviada['status'] != 'TERMINADA':
                    endingEnviadas = 'NO'
                 
            for key, operacionGlobal in get.diccionario_global_operaciones.items():  
                print(key," : ",operacionGlobal['ut'])
                if operacionGlobal['symbol'] == symbol and operacionGlobal['ut'] == '0':
                   operacionGlobal['status'] = '1'
                   
                if  operacionGlobal['status'] == '0':
                    endingGlobal = 'NO'
            
            endingOperacionBot (endingGlobal,endingEnviadas)                             
                               
                            
    
def _cancela_orden(order_report):
    
    order_data = order_report['orderReport']
     #################################################
     ###### cambiar esto finalizado el test ##########
     #################################################
    #order_data = order_report
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']
    timestamp_order_report = order_data['transactTime'] 
    
    
    # Recorrer los elementos del diccionario_enviados
    for key, valor in get.diccionario_operaciones_enviadas.items():       
        if valor["Symbol"] == symbol and valor['_cliOrderId'] == int(clOrdId): 
           
            tiempo_diccionario = valor["timestamp"]
            # Verificar y ajustar el formato de cadena de fecha si es necesario

            if isinstance(tiempo_diccionario, str):
                tiempo_diccionario = datetime.strptime(tiempo_diccionario, "%Y-%m-%d %H:%M:%S")
           
            # Convertir el timestamp en milisegundos a objeto datetime
            # Convertir las cadenas de texto en objetos datetime
            diferencia_segundos = tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario)   
           

            print("FUN _cancela_orden: diferencia [seg]",diferencia_segundos)
            
            
            #diferencia = fecha2_obj - tiempo_diccionario
            #print("FUN _cancela_orden: Diferencia",diferencia)

            
            
            #if diferencia >= 300:
            #if diferencia_segundos >= 300:
            
            _cancel_if_orders(symbol,clOrdId,status)            
    
    
     
def _cancel_if_orders(symbol,clOrdId,order_status):
    #debe sumar de la lista de orden general
    #eliminar de la ordenes enviadas luedo de confirmacion de cancelacion
    print("FUN _cancel_if_orders:  Orden order_status:", order_status)
     # Obtener el estado de la orden
    if order_status in ['PENDING_NEW','NEW','PENDING','REJECT','ACTIVE','PARTIALLY_EXECUTED','SENT','ROUTED','ACCEPTED','PARTIALLY_FILLED','PARTIALLY_FILLED_CANCELED','PARTIALLY_FILLED_REPLACED','PENDING_REPLACE']:
        get.pyConectionWebSocketInicializada.cancel_order_via_websocket(client_order_id=clOrdId) 
        print("FUN _cancel_if_orders:  Orden cancelada:", clOrdId)
          # Aumentar el valor de ut en get.diccionario_global_operaciones        
        for key, operacion_enviada in get.diccionario_operaciones_enviadas.items():                   
            if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId):
                if operacion_enviada["status"] != 'PENDING_CANCEL':
                    operacion_enviada["status"] = 'PENDING_CANCEL'                     
                    break  # Salir del bucle después de eliminar el elemento encontrado    
                 
            break  
    else:
        print("FUN _cancel_if_orders: La orden no se puede cancelar en el estado actual:", order_status)
        


def tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario):
     fecha2_obj = datetime.strptime(timestamp_order_report, "%Y%m%d-%H:%M:%S.%f%z")
     fecha_comun_enviada = tiempo_diccionario.strftime("%Y%m%d-%H:%M:%S")
     fecha_comun_orh = fecha2_obj.strftime("%Y%m%d-%H:%M:%S")
     print("FUN tiempoDeEsperaOperacioncalculaTiempo: fecha_enviada",fecha_comun_enviada)
     print("FUN tiempoDeEsperaOperacioncalculaTiempo: fecha_ORH",fecha_comun_orh)
     # Restar los dos objetos datetime
     fecha_obj1 = datetime.strptime(fecha_comun_enviada, "%Y%m%d-%H:%M:%S")
     fecha_obj2 = datetime.strptime(fecha_comun_orh, "%Y%m%d-%H:%M:%S")

     diferencia = fecha_obj2 - fecha_obj1
     diferencia_segundos = abs(diferencia.total_seconds())
    
     return diferencia_segundos

def asignarClOrId(order_report):
      order_data = order_report['orderReport']
        #################################################
        ###### cambiar esto finalizado el test ##########
        #################################################
      #order_data = order_report
        # Leer un valor específico del diccionario
      clOrdId = order_data['clOrdId']
      symbol = order_data['instrumentId']['symbol']
      status = order_data['status']   
       
      pprint.pprint(get.diccionario_operaciones_enviadas) 
      for key, valor in get.diccionario_operaciones_enviadas.items():  
           
        if valor["Symbol"] == symbol and valor["_cliOrderId"] == 0:                  
            if valor["status"] == '1':                
                # pasa que llegamos aca y wsOrderClId puede no existir mas
                if status in ['PENDING_NEW','REJECT']: 
                    if 'wsClOrdId' in order_report:                
                        wsClOrdId = order_data['wsClOrdId'] 
                        if  valor["ws_client_order_id"] == int(wsClOrdId):
                            valor["_cliOrderId"] = int(clOrdId)
                            valor["status"] = "2"                            
                else:
                    valor["_cliOrderId"] = int(clOrdId) 
                    
def estadoOperacionAnterioCargaDiccionarioEnviadas(accountCuenta,userCuenta,user_id):
   try:        
        repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
        
        datos = repuesta_operacion['orders']
        #print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",datos)
        diccionario = {}
        get.diccionario_operaciones_enviadas.clear()
        # Diccionario para almacenar la resta de los valores por símbolo
        # Diccionario para almacenar los símbolos con resta distinta de 0
       # Diccionario para almacenar los símbolos con resta distinta de 0
        resultado = {}

        for  dato in datos:
            
            symbol = dato['instrumentId']['symbol']
            side = dato["side"]
            orderQty = dato["orderQty"]
            
            if side == "BUY":
                resultado[symbol] = resultado.get(symbol, 0) + orderQty
            elif side == "SELL":
                resultado[symbol] = resultado.get(symbol, 0) - orderQty

        # Mostrar todos los datos de datos
        for symbol, resta in resultado.items():
            if resta != 0:
                print(f"Símbolo: {symbol}")
                for dato in datos:
                    if  dato['instrumentId']['symbol'] == symbol:
                        
                        if dato['orderId'] is not None:
                            pprint.pprint(dato)          
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
                            
                            if side != 'SELL':
                                diccionario = {
                                            "Symbol": Symbol,
                                            "_t_": 'None',
                                            "_tr_": 'operar',
                                            "_s_": 'None',
                                            "_ut_": orderQty,
                                            "precio Offer": 'None',
                                            "ws_client_order_id": 'None',
                                            "_cliOrderId": int(clOrdId),
                                            "timestamp": datetime.now(),
                                            "status": status,
                                            "user_id": user_id,
                                            "userCuenta": userCuenta,
                                            "accountCuenta": accountCuenta
                                                }
                                
                            
                                get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                                #pprint.pprint(get.diccionario_operaciones_enviadas)
        
            print("______________________estadoOperacionAnterioCargaDiccionarioEnviadas_________________")
            
            
        for key,valor in get.diccionario_operaciones_enviadas.items():
             print(key," : ",valor['_cliOrderId'])
        return 'ok'
   except:  
        print("no carga correctamente el diccionario")         
   return 'ok' 

def cargar_operarciones_diccionario_operaciones_enviadas(Symbol):
         for key,valor in get.diccionario_operaciones_enviadas.items():
            if valor['Symbol']== Symbol and valor['status'] != 'OPERAR':
                diccionario = {
                        "Symbol": Symbol,
                        "_t_": 'None',
                        "_tr_": 'None',
                        "_s_": 'None',
                        "_ut_": valor['_ut_'],
                        "precio Offer": 'None',
                        "ws_client_order_id": 'None',
                        "_cliOrderId":0,
                        "timestamp": datetime.now(),
                        "status": 'OPERAR',
                        "user_id": 'None',
                        "userCuenta": 'None',
                        "accountCuenta": 'None'
                        }
            
           
            get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
            #pprint.pprint(get.diccionario_operaciones_enviadas)                 
##########################esto es para ws#############################

def endingOperacionBot (endingGlobal,endingEnviadas):
     if endingGlobal == 'SI' and endingEnviadas == 'SI' and get.diccionario_operaciones_enviadas:
         
        get.diccionario_operaciones_enviadas.clear()
        print("###############################################") 
        print("###############################################") 
        print("###############################################")  
        print("FELICIDADES, EL BOT TERMINO DE OPERAR CON EXITO") 
        print("###############################################") 
        print("###############################################") 
        print("###############################################") 
          #      return render_template('home.html')    

def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))

