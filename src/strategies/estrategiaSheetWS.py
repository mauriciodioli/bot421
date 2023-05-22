from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g
import routes.instrumentosGet as instrumentosGet
from utils.db import db
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
import strategies.datoSheet as datoSheet 

from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket




estrategiaSheetWS = Blueprint('estrategiaSheetWS',__name__)


class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2



@estrategiaSheetWS.route('/estrategia_sheet_WS/')
def estrategia_sheet_WS():     
    
   # try:
        
        #inst = InstrumentoEstrategiaUno("WTI/MAY23", 12, 0.05) 
        SuscripcionDeSheet()#**55
        #get.pyRofexInicializada.init_websocket_connection(order_report_handler = order_report_handler)
        get.pyRofexInicializada.order_report_subscription(account="REM6603", snapshot=True,handler = order_report_handler)
        pyRofexWebSocket =  get.pyRofexInicializada.init_websocket_connection (
                                market_data_handler=market_data_handler_estrategia,
                                order_report_handler= order_report_handler,
                                error_handler=error_handler,
                                exception_handler=exception_handler
                                )
        
        #tickers=[inst.instrument]
        #print("_estrategia_sheet_WS_",tickers)
        
      
        
        #print("_estrategia_sheet_WS inst.instrument_",inst.instrument)
        # Subscribes to receive order report for the default account
        
  
        #get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaOperando.html')
  #  except:  
  #      print("_EstrategyUno_contraseña o usuario incorrecto")  
  #      flash('Loggin Incorrect')    
  #      return render_template("errorLogueo.html" ) 
    
    
     
def SuscripcionDeSheet():
    # Trae los instrumentos para suscribirte
    ContenidoSheet = get_instrumento_para_suscripcion_ws()#**66
    ContenidoSheet_list = list(ContenidoSheet)
    
    
    longitudLista = len(ContenidoSheet_list)
    ContenidoSheet_list_solo_symbol = cargaSymbolParaValidar(ContenidoSheet_list)
    
    print(len(ContenidoSheet_list_solo_symbol),"<<<<<---------------------mis_instrumentos --------------------------->>>>>> ",ContenidoSheet_list_solo_symbol)
    repuesta_listado_instrumento = get.pyRofexInicializada.get_detailed_instruments()
    
    listado_instrumentos = repuesta_listado_instrumento['instruments']   
    #print("instrumentos desde el mercado para utilizarlos en la validacion: ",listado_instrumentos)
    tickers_existentes = inst.obtener_array_tickers(listado_instrumentos) 
    instrumentos_existentes = val.validar_existencia_instrumentos(ContenidoSheet_list_solo_symbol,tickers_existentes)
      
    ##aqui se conecta al ws
    #get.pyRofexInicializada.init_websocket_connection(market_data_handler2,order_report_handler,error_handler,exception_error)
    #print("<<<-----------pasoooo conexiooooonnnn wsocket.py--------->>>>>")
      
    #### aqui define el MarketDataEntry
    entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
               get.pyRofexInicializada.MarketDataEntry.OFFERS,
               get.pyRofexInicializada.MarketDataEntry.LAST]
    
      
    #### aqui se subscribe   
    mensaje = get.pyRofexInicializada.market_data_subscription(tickers=instrumentos_existentes,entries=entries)
   
    #print("instrumento_suscriptio",mensaje)
    datos = [get.market_data_recibida,longitudLista]
    
   
    
    return datos
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
      return ContenidoSheet
    
def market_data_handler_estrategia( message):
        ## mensaje = Ticker+','+cantidad+','+spread
        #print("Processing Market Data Message Received: {0}".format(message))
        ##print(f'El instrumento en market_data_handler {message}')
        ## Llamando al método estrategiaSheet() desde market_data_handler_estrategia
     
    print( "marca de tpo seteada:",  get.VariableParaTiemposMDHandler)
    marca_de_tiempo = message["timestamp"]
    print( "marca_de_tiempo:",  marca_de_tiempo, "dif:", marca_de_tiempo - get.VariableParaTiemposMDHandler)
    

    #if  marca_de_tiempo - get.VariableParaTiemposMDHandler >= 20000: # 60 segundos
    if  (1): # 60 segundos
            print ( "ENTROOOO ahora:",  get.VariableParaTiemposMDHandler ,' account: ' )
            get.VariableParaTiemposMDHandler = message["timestamp"]# milisegundos
            estrategiaSheetNuevaWS(message)
        
    
        
        
        






    # Defines the handlers that will process the Order Reports.


@estrategiaSheetWS.route('/botonPanico/', methods = ['POST']) 
def botonPanico():
    respuesta = botonPanicoRH('true')
    get.pyRofexInicializada.close_websocket_connection()
    return render_template("home.html" ) 

def botonPanicoRH(message):
    # Llamada al método /botonPanico utilizando la referencia a wsConnection
        print("esta dentro del boton de panico ",message)
        
        return message
    
def order_report_handler( order_report):
    
        print("Recibido reporte de orden:")#**88
        print(" - Clave: ", order_report["clOrdID"])
        print(" - Estado: ", order_report["status"])
        print(" - Descripción: ", order_report["text"])
        response = botonPanicoRH('false') 
        print("respuesta desde el boton", response)
        print("Order Report Message Received: {0}".format(order_report))
        if order_report["orderReport"]["clOrdId"] in InstrumentoEstrategiaUno.my_order.keys():
            InstrumentoEstrategiaUno._update_size(order_report)
            if order_report["orderReport"]["status"] in ("NEW", "PARTIALLY_FILLED"):
                print("processing new order")
                InstrumentoEstrategiaUno.my_order[order_report["orderReport"]["clOrdId"]] = order_report
            elif order_report["orderReport"]["status"] == "FILLED":
                print("processing filled")
                del InstrumentoEstrategiaUno.my_order[order_report["orderReport"]["clOrdId"]]
            elif order_report["orderReport"]["status"] == "CANCELLED":
                print("processing cancelled")
                del InstrumentoEstrategiaUno.my_order[order_report["orderReport"]["clOrdId"]]

            if InstrumentoEstrategiaUno.state is States.WAITING_CANCEL:
                if not InstrumentoEstrategiaUno.my_order:
                    InstrumentoEstrategiaUno.state = States.WAITING_MARKET_DATA
                    if InstrumentoEstrategiaUno.last_md:
                        InstrumentoEstrategiaUno.market_data_handler(InstrumentoEstrategiaUno.last_md)
            elif InstrumentoEstrategiaUno.state is States.WAITING_ORDERS:
                for order in InstrumentoEstrategiaUno.my_order.values():
                    if not order:
                        return
                InstrumentoEstrategiaUno.state = States.WAITING_MARKET_DATA
                if InstrumentoEstrategiaUno.last_md:
                    InstrumentoEstrategiaUno.market_data_handler(InstrumentoEstrategiaUno.last_md)


def estrategiaSheetNuevaWS(message):      #**11 
    
    #try:
        
        
        ContenidoSheet = datoSheet.leerSheet()   #**22
        
        ContenidoSheet_list = list(ContenidoSheet)
        cantidadUtaOperar = datoSheet.CuentaCantidadUT(ContenidoSheet_list)# **77
        
        cont = 0 #//**22
        contadorMep=0
        
        mepAl30 = calcularMepAl30WS(message) ####Calcula dolar MEP
        sumaUT = int(cantidadUtaOperar[0]) + int(cantidadUtaOperar[1])
        #listadoCargaDiccionario = leerSheet()
        listaSaldossinOperar = {}
        for Symbol,cedear,trade_en_curso,ut,senial  in ContenidoSheet_list[2:]:
            listaSaldossinOperar[Symbol]=ut
            contadorMep +=1
            if contadorMep < 21:
               #print("____________contador mep __________ ",contadorMep)
               mepAl30 = calcularMepAl30WS(message) ####Calcula dolar MEP de prueba esto hay que quitar en la realidad
        
       # print(listaSaldossinOperar)
        
        
        
        #sumaUT = 4 # **borrar esto se calcula pero por ahora se fija.
        #while sumaUT>0:
        #listado = leerSheet() 
        #print(" ENTRA WHILLEEEEEE cantidad UT cedears: ",cantidadUtaOperar[0]," cantidad UT ARG: ",cantidadUtaOperar[1])
        for Symbol,tipo_de_activo,trade_en_curso,ut,senial  in ContenidoSheet_list:  
                ##### CALCULAR MARGEN DE LA CUENTA PARA VER SI SE PUEDE OPERAR #######
                #Saldo_cuenta = cuenta.obtenerSaldoCuenta("REM6603")
                #print(" __Obtener Saldo Cuenta ________:  ",Saldo_cuenta )
                cont +=1
                
                
                #### CONSULTAR INSTRUMENTO DETALLADO ################  
            # if saldo >= int(ut) * float(price):
                if Symbol != 'Symbol':#aqui salta la primera fila que no contiene valores
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
                                                            Liquidez_ahora_cedear = datoSheet.compruebaLiquidez(ut,mepCedear[1]) #**44
                                                            # Liquidez_ahora_cedear = 10 #para probar **33
                                                            
                                                            # sumaUT es para que itere el while
                                                            sumaUT = int(cantidadUtaOperar[0]) - Liquidez_ahora_cedear
                                                            
                                                            #listaSaldossinOperar es un diccionario 
                                                            #comparo la cantidad que necesito operar (ut) con liquidez del momento.
                                                            
                                                            print(listaSaldossinOperar[Symbol])                                                                
                                                            UT_a_operar = listaSaldossinOperar[Symbol]
                                                            
                                                            
                                                            if Liquidez_ahora_cedear < int(UT_a_operar) : 
                                                            # si entro aca me falta liquidez, anoto lo que falta
                                                                listaSaldossinOperar[Symbol] = int(UT_a_operar)-Liquidez_ahora_cedear #guardo el symbolo y la cantidad que se operaron
                                                                
                                                                datoSheet.OperacionWs(Symbol,tipo_de_activo,trade_en_curso,Liquidez_ahora_cedear,senial,mepCedear)
                                                            else:
                                                                listaSaldossinOperar[Symbol] = 0
                                                                datoSheet.OperacionWs(Symbol,tipo_de_activo,trade_en_curso,UT_a_operar,senial,mepCedear)
                                                            
                                                            
                                                            
                                                                #time.sleep(900) # Sleep for 15 minutos
                                                        #time.sleep(2) # Sleep for 15 minutos
                                                    
                                                        
                                    if tipo_de_activo =='ARG':
                                                saldo = datoSheet.cuenta.obtenerSaldoCuenta()      
                                                #print("________________cont ",cont,"__________________saldo ARG",saldo)
                                                #comprueba la liquidez
                                                Liquidez_ahora_arg = datoSheet.compruebaLiquidez(ut,mepCedear[1])
                                                #Liquidez_ahora_arg = 10 #para probar
                                                sumaUT = int(cantidadUtaOperar[1]) - Liquidez_ahora_arg
                                                UT_a_operar = listaSaldossinOperar[Symbol]
                                                #comparo la cantidad que necesito operar (ut) con liquidez del momento.
                                                if Liquidez_ahora_arg < int(UT_a_operar) : 
                                                    listaSaldossinOperar[Symbol] = int(UT_a_operar)-Liquidez_ahora_arg #guardo el symbolo y la cantidad que se operaron
                                                    datoSheet.OperacionWs(Symbol,tipo_de_activo,trade_en_curso,Liquidez_ahora_cedear,senial,mepCedear)
                                                else:
                                                    listaSaldossinOperar[Symbol] = 0
                                                    datoSheet.OperacionWs(Symbol,tipo_de_activo,trade_en_curso,UT_a_operar,senial,mepCedear)
        banderaAOperarPrimeraVez = 0 #pone la bandera a 0 para que entre a operar los no operados
                                                    
                        #else
        cont=0
        for Symbol  in listaSaldossinOperar: 
            if (Symbol != '' and  Symbol != 'Symbol'):
                cont = cont + listaSaldossinOperar[Symbol]
            
            
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
    
    #print( message['marketData']['OF'][0]['price'])   
    if len( message['marketData']['OF']) == 0:
        print("La clave 'OF' está vacía.")
    else:
        #print("La clave 'OF' no está vacía.", message['marketData']['OF'][0]['price'])
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
    #print("____________calcularMepAl30_____________")
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



                    
##########################esto es para ws#############################
#Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}
def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic21"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))

