from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g
import routes.instrumentosGet as instrumentosGet
from utils.db import db
from models.orden import Orden
import jwt
import json
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
            cuenta = request.form['cuenta']
            access_token = request.form['access_token']
            correo_electronico = request.form['correo_electronico']
            
    
            ContenidoSheet_list = SuscripcionDeSheet()#**22
            carga_operaciones(ContenidoSheet_list[0],cuenta,usuario,correo_electronico,ContenidoSheet_list[1])
            get.pyRofexInicializada.order_report_subscription(account=cuenta, snapshot=True,handler = order_report_handler)
            pyRofexWebSocket =  get.pyRofexInicializada.init_websocket_connection (
                                    market_data_handler=market_data_handler_estrategia,
                                    order_report_handler= order_report_handler,
                                    error_handler=error_handler,
                                    exception_handler=exception_handler
                                    )
            
            
            
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
           print("contraseña o usuario incorrecto")
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
    #print(" FUN: market_data_handler_estrategia: {0}".format(message))
    print(" FUN: market_data_handler_estrategia: _")
     
    print( " Marca de tpo guardada:",  get.VariableParaTiemposMDHandler)
    marca_de_tiempo = message["timestamp"]
    print( " Marca de tpo Actual  :",  marca_de_tiempo, " Diferencia:", marca_de_tiempo - get.VariableParaTiemposMDHandler)
    
    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 20000: # 20 segundos
    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 60000: # 1 minuto
    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 600000: # 10 minutos
    if  (1): # entra todo el tiempo para debug. Comentar esta linea y elejir alguna opcion de arriba
            # esto hay que hacerlo aca, solo cada x segundos
            banderaLecturaSheet = 0 #La lectura del sheet es solo cada x minutos
            get.VariableParaSaldoCta=cuenta.obtenerSaldoCuenta("REM6603")# cada mas de 5 segundos
            #print ( "ENTROOOO ahora:",  get.VariableParaTiemposMDHandler ,' account: ' )
            get.VariableParaTiemposMDHandler = message["timestamp"]# milisegundos
    
    # Va afuera de la verificacion de periodo de tiempo, porque debe ser llamada inmediatamente
    # para cumplir con el evento de mercado market data
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
    """
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
    
    
    
        
       

"""
       ###### BOTON DE PANICO        
        response = botonPanicoRH('false') 
        print("respuesta desde el boton", response)
        if response == 1: ### si es 1 el boton de panico fue activado 
        #if order_report["orderReport"]["clOrdId"] in InstrumentoEstrategiaUno.my_order.keys():
      #      InstrumentoEstrategiaUno._update_size(order_report)
         if order_report["orderReport"]["status"] in ("NEW", "PARTIALLY_FILLED"):
               print("processing new order")
               cancel_response = get.pyRofexInicializada.cancel_order_via_websocket(order_report["orderReport"]["clOrdId"])
               if cancel_response["status"] == "OK":
                    print("La orden se canceló exitosamente.")
               else:
                    print("Error al cancelar la orden:", cancel_response["description"])
         elif order_report["orderReport"]["status"] == "FILLED":
                print("processing filled")
                cancel_response = get.pyRofexInicializada.cancel_order_via_websocket(order_report["orderReport"]["clOrdId"])
                if cancel_response["status"] == "OK":
                    print("La orden se canceló exitosamente.")
                else:
                    print("Error al cancelar la orden:", cancel_response["description"])
         elif order_report["orderReport"]["status"] == "CANCELLED":
                print("processing cancelled")
                cancel_response = get.pyRofexInicializada.cancel_order_via_websocket(order_report["orderReport"]["clOrdId"])
                if cancel_response["status"] == "OK":
                    print("La orden se canceló exitosamente.")
                else:
                    print("Error al cancelar la orden:", cancel_response["description"])
         elif order_report["orderReport"]["status"] == "PENDING_NEW":
                print("processing pending_new")
                cancel_response = get.pyRofexInicializada.cancel_order_via_websocket(order_report["orderReport"]["clOrdId"])
                print("processing pending_new: ",cancel_response)
                if cancel_response["status"] == "OK":
                    print("La orden se canceló exitosamente.")
                else:
                    print("Error al cancelar la orden:", cancel_response["description"])
        ###### FIN  BOTON DE PANICO 
"""     
        
        



def estrategiaSheetNuevaWS(message, banderaLecturaSheet):      #**11 
    
    #try:
        
        if banderaLecturaSheet == 0:#esto es para que lea el sheet solo una vez
            ContenidoSheet = datoSheet.leerSheet() 
            banderaLecturaSheet = 1  
        
            ContenidoSheet_list = list(ContenidoSheet)
            cantidadUtaOperar = datoSheet.CuentaCantidadUT(ContenidoSheet_list)# **77
        
            cont = 0 
            contadorMep=0
        
            #mepAl30 = calcularMepAl30WS(message) ####Calcula dolar MEP
            mepAl30 = 460 ####Calcula dolar MEP
            sumaUT = int(cantidadUtaOperar[0]) + int(cantidadUtaOperar[1])
            #listadoCargaDiccionario = leerSheet()
            listaSaldossinOperar = {}
            listaOperacionesEnCurso = {}
        for Symbol,cedear,trade_en_curso,ut,senial  in ContenidoSheet_list[2:]:
            listaSaldossinOperar[Symbol]=ut
            listaOperacionesEnCurso[Symbol] = 0
            contadorMep +=1
            if contadorMep < 21:
               #print("____________contador mep __________ ",contadorMep)
               #mepAl30 = calcularMepAl30WS(message) ####Calcula dolar MEP de prueba esto hay que quitar en la realidad
               mepAl30 = 460
        
       # print(listaSaldossinOperar)
        
        
        #cont = 0 
        for Symbol,tipo_de_activo,trade_en_curso,ut,senial  in ContenidoSheet_list:  
                ##### CALCULAR MARGEN DE LA CUENTA PARA VER SI SE PUEDE OPERAR #######
                #Saldo_cuenta = cuenta.obtenerSaldoCuenta("REM6603")
                #print(" __Obtener Saldo Cuenta ________:  ",Saldo_cuenta )
                
                #### CONSULTAR INSTRUMENTO DETALLADO ################  
                # message["instrumentId"]["symbol"]
                #if Symbol != 'Symbol':#aqui salta la primera fila que no contiene valores
                if Symbol == message["instrumentId"]["symbol"]:
                    if Symbol != '':
                    #if trade_en_curso == 'LONG_':
                        if senial != '':
                                    
                                    if tipo_de_activo =='CEDEAR':
                                                        #saldo = cuenta.obtenerSaldoCuenta("REM6603")  
                                                        #if saldo >= int(orderQty) * float(price):    
                                                        #print("________________contador ",cont,"__________________saldo cta:",saldo)
                                                        #print("__Operando CEDEAR____: __Symbol_:",Symbol,"__tipo_de_activo_:",tipo_de_activo,"__trade_en_curso_:",trade_en_curso,"______senial_:",senial)                                
                                                        #print("__Entramos al Calculo de mep del CEDEAR, mepAL30 es_: ",mepAl30)
                                                        mepCedear = calcularMepCedearsWS(message)####Calcula dolar MEP CEDEAR
                                                        #print("__Resultado mepCedear_: ",mepCedear) # devuelve 10 como
                                                        # si el porcentaje de diferencia es menor compra
                                                        porcentaje_de_diferencia = 1 - (mepCedear[0] / mepAl30)
                                                        porcentaje_de_diferencia = -1
                                                        #print("__Comparacion mepCedear y mepAL30__________",porcentaje_de_diferencia)# por ahora no importa
                                                        #if ese % es > al 1% no se puede compara el cedear por se muy caro el mep
                                                        if porcentaje_de_diferencia <= 1:
                                                            # Liquidez es la cantidad presente a operar 
                                                            #Liquidez_ahora_cedear = datoSheet.compruebaLiquidez(ut,mepCedear[1]) #**44
                                                            if senial=='OPEN.':
                                                                if isinstance(message["marketData"]["OF"][0]["size"],int):
                                                                    Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]
                                                                elif isinstance(message["marketData"]["LA"][0]["size"],int):
                                                                    Liquidez_ahora_cedear = message["marketData"]["LA"][0]["size"]
                                                                else:
                                                                    Liquidez_ahora_cedear = 0

                                                            if senial=='closed.':
                                                                if isinstance(message["marketData"]["BI"][0]["size"],int):
                                                                    Liquidez_ahora_cedear = message["marketData"]["BI"][0]["size"]
                                                                elif isinstance(message["marketData"]["LA"][0]["size"],int):
                                                                    Liquidez_ahora_cedear = message["marketData"]["LA"][0]["size"]
                                                                else:
                                                                    Liquidez_ahora_cedear = 0
                                                                
                                                            
                                                            # sumaUT es para que itere el while. obsoleto se saca 
                                                            sumaUT = int(cantidadUtaOperar[0]) - Liquidez_ahora_cedear
                                                            
                                                            #comparo la cantidad que necesito operar (ut) con liquidez del momento.
                                                            
                                                            print("   listaSaldossinOperar[",Symbol,"] = ",listaSaldossinOperar[Symbol])
                                                            UT_a_operar = listaSaldossinOperar[Symbol]
                                                            
                                                            
                                                            if Liquidez_ahora_cedear < int(UT_a_operar) : 
                                                            # si entro aca me falta liquidez, anoto lo que falta
                                                                # en realidad tengo que actualizar la lista si se opero bien solamente
                                                                # aca la actualizamos de prepo pero hayque cambiar esto
                                                                listaSaldossinOperar[Symbol] = int(UT_a_operar)-Liquidez_ahora_cedear #guardo el symbolo y la cantidad que se operaron
                                                                
                                                                if Symbol != '' and tipo_de_activo != '' and trade_en_curso != '' and Liquidez_ahora_cedear != 0 and senial != '' and mepCedear != 0 and message != '':
                                                                    datoSheet.OperacionWs(Symbol, tipo_de_activo, trade_en_curso, Liquidez_ahora_cedear, senial, mepCedear, message)
                                                                else:
                                                                    print("*1 FUN: estrategiaSheetNuevaWS -->> datoSheet.OperacionWs No se pudo hacer -->> un argumento llega vacio.")
                                                                
                                                            else:
                                                                listaSaldossinOperar[Symbol] = 0
                                                                
                                                                if Symbol != '' and tipo_de_activo != '' and trade_en_curso != '' and UT_a_operar != 0 and senial != '' and mepCedear != 0 and message != '':
                                                                    datoSheet.OperacionWs(Symbol,tipo_de_activo,trade_en_curso,UT_a_operar,senial,mepCedear,message)
                                                                else:
                                                                    print("*2 FUN: estrategiaSheetNuevaWS -->> datoSheet.OperacionWs No se pudo hacer -->> un argumento llega vacio.")
                                                            
                                                            
                                                            
                                                                #time.sleep(900) # Sleep for 15 minutos
                                                        #time.sleep(2) # Sleep for 15 minutos
                                                    
                                                        
                                    if tipo_de_activo =='ARG':
                                                #saldo = datoSheet.cuenta.obtenerSaldoCuenta()      
                                                #print("________________cont ",cont,"__________________saldo ARG",saldo)
                                                #comprueba la liquidez
                                                if senial=='OPEN.':
                                                    #print (type(message))
                                                    #print (message["marketData"]["OF"][0]["price"])
                                                    if isinstance(message["marketData"]["OF"][0]["size"],int):
                                                        Liquidez_ahora_arg = message["marketData"]["OF"][0]["size"]
                                                    elif isinstance(message["marketData"]["LA"][0]["size"],int):
                                                        Liquidez_ahora_arg = message["marketData"]["LA"][0]["size"]
                                                    else:
                                                        Liquidez_ahora_arg = 0
                                                    
                                                if senial=='closed.':
                                                    if isinstance(message["marketData"]["BI"][0]["size"],int):
                                                        Liquidez_ahora_arg = message["marketData"]["BI"][0]["size"]
                                                    elif isinstance(message["marketData"]["LA"][0]["size"],int):
                                                        Liquidez_ahora_arg = message["marketData"]["LA"][0]["size"]
                                                    else:
                                                        Liquidez_ahora_arg = 0

                                                sumaUT = int(cantidadUtaOperar[1]) - Liquidez_ahora_arg
                                                print("   listaSaldossinOperar[",Symbol,"] = ",listaSaldossinOperar[Symbol])
                                                UT_a_operar = listaSaldossinOperar[Symbol]
                                                #comparo la cantidad que necesito operar (ut) con liquidez del momento.
                                                if Liquidez_ahora_arg < int(UT_a_operar) : 
                                                    listaSaldossinOperar[Symbol] = int(UT_a_operar)-Liquidez_ahora_arg #guardo el symbolo y la cantidad que se operaron
                                                    
                                                    if Symbol != '' and tipo_de_activo != '' and trade_en_curso != '' and Liquidez_ahora_arg != 0 and senial != '' and message != '':
                                                        mepCedear=0
                                                        datoSheet.OperacionWs(Symbol, tipo_de_activo, trade_en_curso, Liquidez_ahora_arg, senial, mepCedear, message)
                                                    else:
                                                        print("*3 FUN: estrategiaSheetNuevaWS -->> datoSheet.OperacionWs No se pudo hacer -->> un argumento llega vacio.")

                                                else:
                                                    listaSaldossinOperar[Symbol] = 0
                                                    if Symbol != '' and tipo_de_activo != '' and trade_en_curso != '' and UT_a_operar != 0 and senial != '' and message != '':
                                                        mepCedear=0
                                                        datoSheet.OperacionWs(Symbol, tipo_de_activo, trade_en_curso, UT_a_operar, senial, mepCedear, message)
                                                    else:
                                                        print("*4 FUN: estrategiaSheetNuevaWS -->> datoSheet.OperacionWs No se pudo hacer -->> un argumento llega vacio.")
                                                    

        cont=0
        for Symbol  in listaSaldossinOperar: 
            if (Symbol != '' and  Symbol != 'Symbol'):
                cont = cont + int(listaSaldossinOperar[Symbol])
            
            
        sumaUT=cont
    
        print("________________sumaUT________________ ",sumaUT)
        #time.sleep(2)#segundos
    
        return render_template('/estrategiaOperando.html')




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

def carga_operaciones(ContenidoSheet_list,account,usuario,correo_electronico,message):
    
     #filtrar las coincidencias entre las dos listas
     coincidencias = [elemento2 for elemento1 in message for elemento2 in ContenidoSheet_list if elemento1 == elemento2[0]]

     print(coincidencias)
     for elemento  in coincidencias:  
         print(elemento[0],elemento[1],elemento[2],elemento[3],elemento[4])
         
         
    # nueva_orden = Orden(1,usuario,account,account+usuario,)
    #db.session.query(Orden).all()#query

                 
##########################esto es para ws#############################

def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))

