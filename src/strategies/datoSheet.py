from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
import routes.instrumentos as instrumentos
from utils.db import db
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import requests
import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import routes.api_externa_conexion.cuenta as cuenta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os #obtener el directorio de trabajo actual
#import drive
#drive.mount('/content/gdrive')



datoSheet = Blueprint('datoSheet',__name__)

newPath = os.path.join(os.getcwd(), 'strategies\\credentials_module.json') 
directorio_credenciales = newPath 

#SPREADSHEET_ID='1pyPq_2tZJncV3tqOWKaiR_3mt1hjchw12Bl_V8Leh74'#drpiBot2
SPREADSHEET_ID='1yQeBg8AWinDLaErqjIy6OFn2lp2UM8SRFIcVYyLH4Tg'#drpiBot3 de pruba

class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2
    
  
    
def login():
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = directorio_credenciales
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credenciales)
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth(port_numbers=[8092])
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
        
    gauth.SaveCredentialsFile(directorio_credenciales)
    credenciales = GoogleDrive(gauth)
    return credenciales
def leerSheet():   
    # gauth = GoogleAuth()
     ##gauth.LocalWebserverAuth() # Autenticación mediante un servidor local
    # drive = GoogleDrive(gauth)
     # Obtener metadatos de un archivo por su ID
    # file_id = 'drpiBot2'
    # file = drive.CreateFile({'id': file_id})
    # print('File name: %s' % file['title'])
    
    # credenciales = login()  
     scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    
     newPath = os.path.join(os.getcwd(), 'strategies\\pruebasheetpython.json')  
    # creds = ServiceAccountCredentials.from_json_keyfile_name('pruebasheetpython.json', scope)
     print(newPath)
     creds = ServiceAccountCredentials.from_json_keyfile_name(newPath, scope)
     
     #creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/mDioli/Documents/ITCOR/bot421/src/strategies/pruebasheetpython.json', scope)
     client = gspread.authorize(creds)
     
     sheet = client.open_by_key(SPREADSHEET_ID).sheet1   
     symbol = sheet.col_values(1)
     tipo_de_activo = sheet.col_values(16)
     trade_en_curso = sheet.col_values(19)
     ut = sheet.col_values(20)
     senial = sheet.col_values(21)
     union = zip(symbol,tipo_de_activo,trade_en_curso,ut,senial)
     
     #for Symbol,cedear,trade_en_curso,ut,senial  in union:
      #print(Symbol,cedear,trade_en_curso,ut,senial)
    
     
     return union
 
@datoSheet.route('/estrategiaSheet/')
def estrategiaSheet():     
    
    #try:
        
        
        ContenidoSheet = leerSheet()   #**22
        
        ContenidoSheet_list = list(ContenidoSheet)
        suscribirInstrumentosPorWS(ContenidoSheet_list)
        cantidadUtaOperar = CuentaCantidadUT(ContenidoSheet_list)# cuenta cantidad de UT a operar [0] Cedear [1] otros
        
        cont = 0 #//**22
        contadorMep=0
        
        mepAl30 = calcularMepAl30() ####Calcula dolar MEP
        sumaUT = int(cantidadUtaOperar[0]) + int(cantidadUtaOperar[1])
        #listadoCargaDiccionario = leerSheet()
        listaSaldossinOperar = {}
        for Symbol,cedear,trade_en_curso,ut,senial  in ContenidoSheet_list:
            listaSaldossinOperar[Symbol]=ut
            contadorMep +=1
            if contadorMep < 21:
               print("____________contador mep __________ ",contadorMep)
               mepAl30 = calcularMepAl30() ####Calcula dolar MEP de prueba esto hay que quitar en la realidad
        
        print(listaSaldossinOperar)
        
        
        
        #sumaUT = 4 # **borrar esto se calcula peropor ahora se fija.
        while sumaUT>0:
            #listado = leerSheet() 
            print(" ENTRA WHILLEEEEEE cantidad UT cedears: ",cantidadUtaOperar[0]," cantidad UT ARG: ",cantidadUtaOperar[1])
            for Symbol,tipo_de_activo,trade_en_curso,ut,senial  in ContenidoSheet_list:  
                    ##### CALCULAR MARGEN DE LA CUENTA PARA VER SI SE PUEDE OPERAR #######
                    #Saldo_cuenta = cuenta.obtenerSaldoCuenta("REM6603")
                    #print(" #_________ Obtener Saldo Cuenta ________:  ",Saldo_cuenta )
                    cont +=1
                    
                    
                    #### CONSULTAR INSTRUMENTO DETALLADO ################  
                # if saldo >= int(ut) * float(price):
                    if Symbol != 'Symbol':#aqui salta la primera fila que no contiene valores
                        if Symbol != '':
                        #if trade_en_curso == 'LONG_':
                            if senial != '':
                                        if tipo_de_activo =='CEDEAR':
                                                            saldo = cuenta.obtenerSaldoCuenta("REM6603")      
                                                            print("________________contador ",cont,"__________________saldo cta:",saldo)
                                                            print("__Operando CEDEAR____: __Symbol_:",Symbol,"__tipo_de_activo_:",tipo_de_activo,"__trade_en_curso_:",trade_en_curso,"______senial_:",senial)                                
                                                            print("__Entramos al Calculo de mep del CEDEAR, mepAL30 es_: ",mepAl30)
                                                            mepCedear = calcularMepCedears(Symbol)####Calcula dolar MEP CEDEAR
                                                            print("__Resultado mepCedear_: ",mepCedear) # devuelve 10 como
                                                            # si el porcentaje de diferencia es menor compra
                                                            porcentaje_de_diferencia = 1 - (mepCedear[0] / mepAl30)
                                                            porcentaje_de_diferencia = -1
                                                            print("__Comparacion mepCedear y mepAL30__________",porcentaje_de_diferencia)# por ahora no importa
                                                            #if ese % es > al 1% no se puede compara el cedear por se muy caro el mep
                                                            if porcentaje_de_diferencia <= 1:  
                                                                #comprueba la liquidez
                                                                Liquidez_ahora_cedear = compruebaLiquidez(ut,mepCedear[1])#**44
                                                               # Liquidez_ahora_cedear = 10 #para probar **33
                                                                
                                                                # sumaUT es para que itere el while
                                                                sumaUT = int(cantidadUtaOperar[0]) - int (Liquidez_ahora_cedear[1])
                                                                
                                                                #listaSaldossinOperar es un diccionario 
                                                                #comparo la cantidad que necesito operar (ut) con liquidez del momento.
                                                                if listaSaldossinOperar[Symbol]==0:
                                                                        UT_a_operar = ut
                                                                else:
                                                                        UT_a_operar = listaSaldossinOperar[Symbol]
                                                                
                                                                if int(Liquidez_ahora_cedear[1]) < int(UT_a_operar) : 
                                                                # si entro aca me falta liquidez, anoto lo que falta
                                                                    listaSaldossinOperar[Symbol] = UT_a_operar-Liquidez_ahora_cedear[1] #guardo el symbolo y la cantidad que se operaron
                                                                             #print("cantidadUtaOperar[0] ",cantidad[0]," cantidad____________________ut ",cantidad[1])
                                                                
                                                                OperacionWs(Symbol,tipo_de_activo,trade_en_curso,Liquidez_ahora_cedear[1],senial)
                                                                    #time.sleep(900) # Sleep for 15 minutos
                                                                time.sleep(3) # Sleep for 15 minutos
                                                        
                                                            
                                        if tipo_de_activo =='ARG':
                                                    saldo = cuenta.obtenerSaldoCuenta()      
                                                    print("________________cont ",cont,"__________________saldo ARG",saldo)
                                                    #comprueba la liquidez
                                                    Liquidez_ahora_arg = compruebaLiquidez(ut,mepCedear[1])
                                                    #Liquidez_ahora_arg = 10 #para probar
                                                    sumaUT = int(cantidadUtaOperar[1]) - int(Liquidez_ahora_arg[1])
                                                    #comparo la cantidad que necesito operar (ut) con liquidez del momento.
                                                    if int(Liquidez_ahora_arg[1]) < int(UT_a_operar) : 
                                                    # si entro aca me falta liquidez, anoto lo que falta
                                                        listaSaldossinOperar = [Symbol,ut-Liquidez_ahora_arg[1]]#guardo el symbolo y la cantidad que se operaron
                                                    #print("cantidadUtaOperar[0] ",cantidad[0]," cantidad____________________ut ",cantidad[1])
                                                    #print(cantidad[0]," cantidad____________________ut ",cantidad[1])
                                                            
                                                    OperacionWs(Symbol,tipo_de_activo,trade_en_curso,Liquidez_ahora_arg[1],senial)   
            banderaAOperarPrimeraVez = 0 #pone la bandera a 0 para que entre a operar los no operados
                                                      
                            #else
            sumaUT -=1
            cont =0
            print("________________sumaUT________________ ",sumaUT)
            time.sleep(10)#segundos
        
        return render_template('/estrategiaOperando.html')
   # except:  
   #     print("contraseña o usuario incorrecto")  
   #     flash('Loggin Incorrect')    
   #     return render_template("errorLogueo.html" )
################ AQUI DEFINO LA COMPRA POR WS ################
def OperacionWs(Symbol,tipo_de_activo,trade_en_curso,ut,senial):
     #cont +=1
     Symbol="ORO/MAR23"
     inst = InstrumentoEstrategiaUno(Symbol, ut, 0.05) 
     print("__Funcion OperacionWs______Symbol_",Symbol,"__tipo_de_activo__",tipo_de_activo,"___trade_en_curso__",trade_en_curso,"____senial__",senial)
                     
     if senial == 'OPEN.':                    #**66          
        get.pyRofexInicializada.init_websocket_connection (market_data_handlerCompra,order_report_handler,error_handler,exception_error)
     if senial == 'closed.':
        get.pyRofexInicializada.init_websocket_connection (market_data_handlerVenta,order_report_handler,error_handler,exception_error)
     tickers=[inst.instrument]
                                
     entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                get.pyRofexInicializada.MarketDataEntry.OFFERS]   
                                        
     get.pyRofexInicializada.market_data_subscription(tickers,entries)
                                    
     # Subscribes to receive order report for the default account
     get.pyRofexInicializada.order_report_subscription(snapshot=True)
     return Symbol
    
def market_data_handlerCompra( message):
    
        # mensaje = Ticker+','+cantidad+','+spread
        print("__market_data_handlerCompra ___:  Data Message Received____: ",message)
        
                   
        last_md = None
        bid = message["marketData"]["BI"]
        offer = message["marketData"]["OF"]
        symbol =  message["instrumentId"]["symbol"]
       
        price = message["marketData"]["BI"][0]["price"]
        orderQty = "3"
        if bid and offer:
           bid_px = bid[0]["price"]
           offer_px = offer[0]["price"]
           print("bid_px: ",bid_px," offer_px ",offer_px," symbol ",symbol," orderQty ",orderQty," price ",price)
           
           get.pyRofexInicializada.send_order_via_websocket(ticker=symbol, side=get.pyRofexInicializada.Side.BUY, size=orderQty, order_type=get.pyRofexInicializada.OrderType.LIMIT,price=price)  
         
        else:
          InstrumentoEstrategiaUno._cancel_if_orders()
       


def market_data_handlerVenta( message):
    
        # mensaje = Ticker+','+cantidad+','+spread
        
        print("__market_data_handlerVenta ___:  Data Message Received____: ",message)
        
                   
        last_md = None
        bid = message["marketData"]["BI"]
        offer = message["marketData"]["OF"]
        symbol =  message["instrumentId"]["symbol"]
       
        price = message["marketData"]["BI"][0]["price"]
        orderQty = "3"
        if bid and offer:
           bid_px = bid[0]["price"]
           offer_px = offer[0]["price"]
           print("bid_px: ",bid_px," offer_px ",offer_px," symbol ",symbol," orderQty ",orderQty," price ",price)
           
           get.pyRofexInicializada.send_order_via_websocket(ticker=symbol, side=get.pyRofexInicializada.Side.SELL, size=orderQty, order_type=get.pyRofexInicializada.OrderType.LIMIT,price=price)  
         
        else:
          InstrumentoEstrategiaUno._cancel_if_orders()




    # Defines the handlers that will process the Order Reports.
def order_report_handler( order_report):
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
                    InstrumentoEstrategiaUno.market_data_handler(self.last_md)
                    
                    
                    
                    

def _update_size(order):
        if order["orderReport"]["status"] in ("PARTIALLY_FILLED", "FILLED"):
            if order["orderReport"]["side"] == "BUY":
                InstrumentoEstrategiaUno.buy_size -= round(order["orderReport"]["lastQty"])
            if order["orderReport"]["side"] == "SELL":
                InstrumentoEstrategiaUno.sell_size -= round(order["orderReport"]["lastQty"])
            if InstrumentoEstrategiaUno.sell_size == InstrumentoEstrategiaUno.buy_size == 0:
                InstrumentoEstrategiaUno.sell_size = InstrumentoEstrategiaUno.buy_size = InstrumentoEstrategiaUno.initial_size

def _cancel_if_orders():
        if InstrumentoEstrategiaUno.my_order:
            InstrumentoEstrategiaUno.state = States.WAITING_CANCEL
            for order in InstrumentoEstrategiaUno.my_order.values():
                get.pyRofexInicializada.cancel_order(order["orderReport"]["clOrdId"])
                print("canceling order %s" % order["orderReport"]["clOrdId"])

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
        
        
        
########################## esto es para ws #############################
#Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}
def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic21"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

def calcularMepAl30():
    print("____________calcularMepAl30_____________")
    #resultado = requests.post('http://127.0.0.1:5000/instrument_by_symbol_para_CalculoMep/', data ={'symbol':symbol})
    
    #traer los precios del al30
    #print("____traer los precios del al30")
    resultado = instrument_by_symbol_para_CalculoMep("WTI/MAY23")
    resultado2 = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs")    
   
   # al30_ci = resultado['OF'][0]['price'] #vendedora OF
   # al30D_ci =resultado2['BI'][0]['price'] #compradora BI
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
    mep = 10
    print("____________calcularMepAl30_____________")
    return mep

##########################AQUI SE REALIZA CALCULO DE MEP CEDEARS####################
def calcularMepCedears(Symbol):
     #traer los precios del cedear
     print("__________entra a calcular calcularMepCedears____________")
     resultado = instrument_by_symbol_para_CalculoMep("WTI/MAY23")
     resultado2 = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs") 
     
    # ko_ci = resultado['OF'][0]['price'] #vendedora OF ko_ci punta vendedora (porque es lo que yo deberia comprar si quiero dolar mep)
    # koD_ci =resultado2['BI'][0]['price'] #compradora BI koD_ci punta compradora (el que me compra lo bonos para tener mis dolares)
    # size = resultado2['BI'][0]['size']
   #  print("__________ko_ci____________",ko_ci)
   #  print("__________koD_ci____________",koD_ci)
   #  print("__________size____________",size)
     #mep= ko_ci / koD_ci
     mep=10
     size=10
     dato = [mep,size]
     return dato

def compruebaLiquidez(ut,size):
    print(ut,"___Funcion_compruebaLiquidez____________",size) 
    liquidez = int(ut) - int(size) # 100 - 3 = 97 /////// 4 - 10 = -6 
    #print("_____________liquidez____________",liquidez)
    if liquidez >= 0:    
       cantidadAComprar = size
       vecesAOperar =int(liquidez/size)
    if liquidez < 0:
        cantidadAComprar = ut
        vecesAOperar=0
    dato = [vecesAOperar,cantidadAComprar]
    #print("_____________vecesAOperar____________",vecesAOperar)
    return dato
       
    
##########################AQUI LLAMO A UN INSTRUMENTO####################

def instrument_by_symbol_para_CalculoMep(symbol):
      print("__________entra a instrument_by_symbol____________") 
      try:
        
            entries =  [ get.pyRofexInicializada.MarketDataEntry.BIDS,
                        get.pyRofexInicializada.MarketDataEntry.OFFERS,
                        get.pyRofexInicializada.MarketDataEntry.LAST,
                        get.pyRofexInicializada.MarketDataEntry.CLOSING_PRICE,
                        get.pyRofexInicializada.MarketDataEntry.OPENING_PRICE,
                        get.pyRofexInicializada.MarketDataEntry.HIGH_PRICE,
                        get.pyRofexInicializada.MarketDataEntry.LOW_PRICE,
                        get.pyRofexInicializada.MarketDataEntry.SETTLEMENT_PRICE,
                        get.pyRofexInicializada.MarketDataEntry.NOMINAL_VOLUME,
                        get.pyRofexInicializada.MarketDataEntry.TRADE_EFFECTIVE_VOLUME,
                        get.pyRofexInicializada.MarketDataEntry.TRADE_VOLUME,
                        get.pyRofexInicializada.MarketDataEntry.OPEN_INTEREST]
            #print("symbolllllllllllllllllllllll ",symbol)
           #https://api.remarkets.primary.com.ar/rest/instruments/detail?symbol=DLR/NOV23&marketId=ROFX
            repuesta_instrumento = get.pyRofexInicializada.get_market_data(ticker=symbol, entries=entries, depth=2)
           
            
            #repuesta_instrumento = get.pyRofexInicializada.get_instrument_details(ticker=symbol)
            #for repuesta_instrumento in repuesta_instrumento:        
            objeto = repuesta_instrumento['marketData']   
           # for objeto in objeto:     
            
           # print("instrumentooooooooooooooooooooooooooooo LA ",objeto['LA'])
           # print("instrumentooooooooooooooooooooooooooooo BI ",objeto['BI'])            
           # print("instrumentooooooooooooooooooooooooooooo OF ",objeto['OF'])
            jdato = str(objeto['LA'])
            jdato1 = str(objeto['BI'])
            jdato2 = str(objeto['OF'])
            if jdato.find('price')==-1:
                print("no tiene nada LA ",jdato1.find('price'))
                
            elif jdato1.find('price')==-1:
                print("no tiene nada BI ",jdato1.find('price'))
                
            
            elif jdato2.find('price')==-1:
                print("no tiene nada OF",jdato2.find('price'))
           
            return objeto
        
      except:       
        flash('Symbol Incorrect')   
        return render_template("instrumentos.html" )
   
########################################################################
def CuentaCantidadUT(listado):
    bandera = True
    countCedear =0
    countResto =0
    print("_____________CuentaCantidadUT___________")   
    for Symbol,cedear,trade_en_curso,ut,senial  in listado: 
       
        if Symbol != 'Symbol':#aqui salta la primera fila que no contiene valores
                if Symbol != '':
                        #if trade_en_curso == 'LONG_':
                            if senial != '':
                                if senial == 'OPEN.' or senial == 'closed.':
                                    if cedear =='CEDEAR':
                                        countCedear +=1
                                        #print(countCedear,Symbol,cedear,trade_en_curso,ut,senial)
                                    if cedear =='ARG':
                                        countResto +=1
                                        #print(countCedear,Symbol,cedear,trade_en_curso,ut,senial)
                                        
      
        dato = [countCedear,countResto]
       # print("countCedear ",dato[0]," countResto ",dato[1])
       
       
       
    return dato


def suscribirInstrumentosPorWS(listadoInstrumentosSheet):
    
    return True