from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
import routes.instrumentos as instrumentos
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import requests
import time
from models.orden import Orden
import random
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#import routes.api_externa_conexion.cuenta as cuenta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
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
    
class Ordenes(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2 
    #NEW  
    #PENDING_NEW
    #TIMESTAMP_ENVIO
    
   # Crear la tabla usuarios si no existe
def crea_tabla_orden():
    orden = Orden(        
         user_id =1,
         userCuenta ="mdioli",
         accountCuenta =1,
         clOrdId_alta ="0",
         clOrdId_baja ="0",
         clientId =1,
         wsClOrdId_timestamp =datetime.now,
         clOrdId_alta_timestamp = datetime.now,
         clOrdId_baja_timestamp = datetime.now,
         proprietary = True,
         marketId = "0",
         symbol = "0",   
         tipo = "0",
         tradeEnCurso = "0",
         ut = 1,   
         senial = "0",
         status = "0"    
    )
    orden.crear_tabla()
    
    
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
    
     #credenciales = login()  
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
 

################ AQUI DEFINO LA COMPRA POR WS ################
def OperacionWs(Symbol, tipo_de_activo, trade_en_curso, ut, senial, mepCedear, message):
    saldocta = get.VariableParaSaldoCta### preguntar si existe el saldo de cuanta para recien operar
    ut = abs(int(ut))
    saldoExiste = False
    
    try:
        # La clave "price" existe en message["marketData"]["OF"][0]  ???
        if "OF" in message["marketData"]:
            if isinstance(message["marketData"]["OF"], list) and len(message["marketData"]["OF"]) > 0:
                if "price" in message["marketData"]["OF"][0]:
                    plataoperacion1=ut*message["marketData"]["OF"][0]["price"]
                else:
                    plataoperacion1=0
            else:
                plataoperacion1=0
        else:
            plataoperacion1=0
                
                
        # La clave "price" existe en message["marketData"]["BI"][0] ???
        if "BI" in message["marketData"]:
            if isinstance(message["marketData"]["BI"], list) and len(message["marketData"]["BI"]) > 0:
                if "price" in message["marketData"]["BI"][0]:
                    plataoperacion2=ut*message["marketData"]["OF"][0]["price"]
                else:
                    plataoperacion2=0
            else:
                plataoperacion2=0
        else:
            plataoperacion2=0

        # La clave "price" existe en message["marketData"]["LA"]
        if "LA" in message["marketData"]:
            if "price" in message["marketData"]["LA"]:
                    plataoperacion3=ut*message["marketData"]["LA"]["price"]
            else:
                plataoperacion3=0
        else:
            plataoperacion3=0


        
        #if saldocta > ut * message["marketData"]["OF"][0]["price"] or saldocta > ut * message["marketData"]["BI"][0]["price"] or saldocta > ut * message["marketData"]["LA"]["price"]:
        #if saldocta > plataoperacion1 or saldocta > plataoperacion2 or saldocta > plataoperacion3:
        # aca comprobamos que existan el bid, el offer y el last. si alguno no existe, no tiene 
        # liquidez el instrumento. Si los tres valores existen, comprobamos
        # que el spread sea coherente (no difieran mas del 1%), si el spread es muy amplio, 
        # no hay liquidez y podemos llegar a pagar cualquier cosa.
        if (saldocta > plataoperacion1 and  
            saldocta > plataoperacion2 and 
            saldocta > plataoperacion3):
                saldoExiste = True
            #abs(plataoperacion1 - plataoperacion2) <= 0.01 * max(plataoperacion1, plataoperacion2) and
            #abs(plataoperacion1 - plataoperacion3) <= 0.01 * max(plataoperacion1, plataoperacion3) and
            #abs(plataoperacion2 - plataoperacion3) <= 0.01 * max(plataoperacion2, plataoperacion3)            
            #):
                
        else:
            print("FUN: OperacionWs__ No se puede operar Saldo Insuficiente, o no hay liquidez. El Saldo es: ",saldocta)
            
        if saldoExiste == True: 
           
                
            if int(get.diccionario_global_operaciones[Symbol]['ut']) > 0 :
                _ws_client_order_id =  1001+random.randint(1, 100000)
            
                if senial == 'OPEN.':
                    if isinstance(message["marketData"]["OF"][0]["price"], float):
                        precio = float(message["marketData"]["OF"][0]["price"])
                        print("FUN: OperacionWs__Symbol: ",Symbol," ut:",ut," _ws_client_order_id:",_ws_client_order_id," precio:",precio," _ws_client_order_id ",_ws_client_order_id)
                        get.pyConectionWebSocketInicializada.send_order_via_websocket(ticker=Symbol,side=get.pyRofexInicializada.Side.BUY,size=ut, order_type=get.pyRofexInicializada.OrderType.LIMIT,ws_client_order_id=_ws_client_order_id,price=precio)

                        ws_client_order_id = _ws_client_order_id
                        timestamp = get.diccionario_global_operaciones[Symbol]['wsClOrdId_timestamp']
                        user_id = get.diccionario_global_operaciones[Symbol]['user_id']
                        userCuenta = get.diccionario_global_operaciones[Symbol]['userCuenta']
                        accountCuenta = get.diccionario_global_operaciones[Symbol]['accountCuenta']

                        diccionario = {
                                "Symbol": Symbol,
                                "_t_": tipo_de_activo,
                                "_tr_": trade_en_curso,
                                "_s_": senial,
                                "_ut_": ut,
                                "precio Offer": precio,
                                "ws_client_order_id": ws_client_order_id,
                                "_cliOrderId": 0,
                                "timestamp": timestamp,
                                "status": "1",
                                "user_id": user_id,
                                "userCuenta": userCuenta,
                                "accountCuenta": accountCuenta
                            }
                        get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                        #restar del diccionario global
                        #get.diccionario_global_operaciones[Symbol]['ut'] -=ut
                        pprint.pprint(get.diccionario_operaciones_enviadas)
                        get.diccionario_global_operaciones[Symbol]['ut'] = str(int(get.diccionario_global_operaciones[Symbol]['ut']) - ut)

                        
                        #pprint.pprint(get.diccionario_operaciones_enviadas)
                    
                    elif isinstance(message["marketData"]["LA"]["price"], float):
                        precio = message["marketData"]["LA"]["price"]
                        print("FUN: OperacionWs__Symbol: ",Symbol," ut:",ut," _ws_client_order_id:",_ws_client_order_id," precio:",precio)
                        #get.pyConectionWebSocketInicializada.send_order_via_websocket(
                        #    ticker=Symbol,
                        #    side=get.pyRofexInicializada.Side.BUY,
                        #    size=ut,
                        #    order_type=get.pyRofexInicializada.OrderType.LIMIT,
                        #    ws_client_order_id=client_order_id,
                        #    price=precio
                        #)
                        ws_client_order_id = _ws_client_order_id
                        client_order_id = get.diccionario_global_operaciones[Symbol]['clOrdId_alta']
                        timestamp = get.diccionario_global_operaciones[Symbol]['wsClOrdId_timestamp']
                        user_id = get.diccionario_global_operaciones[Symbol]['user_id']
                        userCuenta = get.diccionario_global_operaciones[Symbol]['userCuenta']
                        accountCuenta = get.diccionario_global_operaciones[Symbol]['accountCuenta']
                        diccionario = {
                                "Symbol": Symbol,
                                "_t_": tipo_de_activo,
                                "_tr_": trade_en_curso,
                                "_s_": senial,
                                "_ut_": ut,
                                "precio Last": precio,
                                "_ws_client_order_id": ws_client_order_id,
                                "_cliOrderId": 0,
                                "timestamp": timestamp,
                                "status": "1",
                                "user_id": user_id,
                                "userCuenta": userCuenta,
                                "accountCuenta": accountCuenta
                            }
                       # get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                        #pprint.pprint(get.diccionario_operaciones_enviadas)
                       # get.diccionario_global_operaciones[Symbol]['ut'] = str(int(get.diccionario_global_operaciones[Symbol]['ut']) - ut)
                        
                elif senial == 'closed.':
                    if isinstance(message["marketData"]["OF"][0]["price"], float):
                            precio = float(message["marketData"]["OF"][0]["price"])
                            print("FUN: OperacionWs__Symbol: ",Symbol," ut:",ut," _ws_client_order_id:",_ws_client_order_id," precio:",precio)
                           # get.pyConectionWebSocketInicializada.send_order_via_websocket(
                           #     ticker=Symbol,
                           #     side=get.pyRofexInicializada.Side.SELL,
                           #     size=ut,
                           #     order_type=get.pyRofexInicializada.OrderType.LIMIT,
                           #     ws_client_order_id=_ws_client_order_id,
                           #     price=precio
                           # )
                            ws_client_order_id = _ws_client_order_id
                            timestamp = get.diccionario_global_operaciones[Symbol]['wsClOrdId_timestamp']
                            user_id = get.diccionario_global_operaciones[Symbol]['user_id']
                            userCuenta = get.diccionario_global_operaciones[Symbol]['userCuenta']
                            accountCuenta = get.diccionario_global_operaciones[Symbol]['accountCuenta']

                            diccionario = {
                                "Symbol": Symbol,
                                "_t_": tipo_de_activo,
                                "_tr_": trade_en_curso,
                                "_s_": senial,
                                "_ut_": ut,
                                "precio Offer": precio,
                                "_ws_client_order_id": ws_client_order_id,
                                "_cliOrderId": 0,
                                "timestamp": timestamp,
                                "status": "1",
                                "user_id": user_id,
                                "userCuenta": userCuenta,
                                "accountCuenta": accountCuenta
                            }
                          #  get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                            #pprint.pprint(get.diccionario_operaciones_enviadas)
                          #  get.diccionario_global_operaciones[Symbol]['ut'] = str(int(get.diccionario_global_operaciones[Symbol]['ut']) - ut)
                    
                    elif isinstance(message["marketData"]["LA"]["price"], float):
                            precio = float(message["marketData"]["LA"]["price"])
                            client_order_id = get.diccionario_global_operaciones[Symbol]['clOrdId_alta']
                            print("FUN: OperacionWs__Symbol: ",Symbol," ut:",ut," _ws_client_order_id:",_ws_client_order_id," precio:",precio)
                            #get.pyConectionWebSocketInicializada.send_order_via_websocket(
                            #    ticker=Symbol,
                            #    side=get.pyRofexInicializada.Side.SELL,
                            #    size=ut,
                            #    order_type=get.pyRofexInicializada.OrderType.LIMIT,
                            #    ws_client_order_id=client_order_id,
                            #    price=precio
                            #)
                            ws_client_order_id = _ws_client_order_id
                            timestamp = get.diccionario_global_operaciones[Symbol]['wsClOrdId_timestamp']
                            user_id = get.diccionario_global_operaciones[Symbol]['user_id']
                            userCuenta = get.diccionario_global_operaciones[Symbol]['userCuenta']
                            accountCuenta = get.diccionario_global_operaciones[Symbol]['accountCuenta']

                            diccionario = {
                                "Symbol": Symbol,
                                "_t_": tipo_de_activo,
                                "_tr_": trade_en_curso,
                                "_s_": senial,
                                "_ut_": ut,
                                "precio Last": precio,
                                "_ws_client_order_id": ws_client_order_id,
                                "_cliOrderId": 0,
                                "timestamp": timestamp,
                                "status": "1",
                                "user_id": user_id,
                                "userCuenta": userCuenta,
                                "accountCuenta": accountCuenta
                            }
                            #get.diccionario_operaciones_enviadas[len(get.diccionario_operaciones_enviadas) + 1] = diccionario
                           # pprint.pprint(get.diccionario_operaciones_enviadas)
                            #get.diccionario_global_operaciones[Symbol]['ut'] = str(int(get.diccionario_global_operaciones[Symbol]['ut']) - ut)
                            
    except Exception as e:
            print("Error en OperacionWs:", e)

    



    




       





    # Defines the handlers that will process the Order Reports.

       
                    
     
                    
                    

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
        
        
        

def calcularMepAl30():
    print("____________calcularMepAl30_____________")
    #resultado = requests.post('http://127.0.0.1:5000/instrument_by_symbol_para_CalculoMep/', data ={'symbol':symbol})
    
    #traer los precios del al30
    #print("____traer los precios del al30")
    resultado = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs")    
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
    mep = 380
    print("____________calcularMepAl30_____________")
    return mep

##########################AQUI SE REALIZA CALCULO DE MEP CEDEARS####################
def calcularMepCedears(Symbol):
     #traer los precios del cedear
     print("_calcularMepCedears_______ le da 380")
     resultado = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs") 
     #resultado2 = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs") 
     
    # ko_ci = resultado['OF'][0]['price'] #vendedora OF ko_ci punta vendedora (porque es lo que yo deberia comprar si quiero dolar mep)
    # koD_ci =resultado2['BI'][0]['price'] #compradora BI koD_ci punta compradora (el que me compra lo bonos para tener mis dolares)
    # size = resultado2['BI'][0]['size']
   #  print("__________ko_ci____________",ko_ci)
   #  print("__________koD_ci____________",koD_ci)
   #  print("__________size____________",size)
     #mep= ko_ci / koD_ci
     if len(resultado['OF']) > 0:
        offer_price = resultado['OF'][0]['price'] #vendedora OF
     else:
        offer_price=0
        
     if len(resultado['BI']) > 0:
        bid_price =resultado['BI'][0]['price'] #compradora BI
     else:
        bid_price=0
     
     mep=380
     size=10
     dato = [mep,size,offer_price,bid_price]
     return dato

def compruebaLiquidez(ut,size):
    #print(ut,"_CompruebaLiquidez____________",size) 
    liquidez = int(ut) - int(size) # 100 - 3 = 97 /////// 4 - 10 = -6 
    #print("_____________liquidez____________",liquidez)
    if liquidez >= 0:    
       cantidadAComprar = size
       vecesAOperar =int(liquidez/size)
    if liquidez < 0:
        cantidadAComprar = ut
        vecesAOperar=0
    #dato = [vecesAOperar,cantidadAComprar]
    dato = 2
    #print("_____________vecesAOperar____________",vecesAOperar)
    return dato
       
    
##########################AQUI LLAMO A UN INSTRUMENTO####################

def instrument_by_symbol_para_CalculoMep(symbol):
      print("__________entra a instrument_by_symbol____________") 
      try:
        
            entries =  [ get.pyRofexInicializada.MarketDataEntry.OFFERS,get.pyRofexInicializada.MarketDataEntry.BIDS,get.pyRofexInicializada.MarketDataEntry.LAST ]
            
            #print("symbolllllllllllllllllllllll ",symbol)
           #https://api.remarkets.primary.com.ar/rest/instruments/detail?symbol=DLR/NOV23&marketId=ROFX
            repuesta_instrumento = get.pyConectionWebSocketInicializada.get_market_data(ticker=symbol, entries=entries, depth=2)
           
            
            #repuesta_instrumento = get.pyRofexInicializada.get_instrument_details(ticker=symbol)
            #for repuesta_instrumento in repuesta_instrumento:        
            objeto = repuesta_instrumento['marketData']   
           # for objeto in objeto:     
            
           # print("instrumentooooooooooooooooooooooooooooo LA ",objeto['LA'])
           # print("instrumentooooooooooooooooooooooooooooo BI ",objeto['BI'])            
           # print("instrumentooooooooooooooooooooooooooooo OF ",objeto['OF'])
            #jdato = str(objeto['LA'])
            #jdato1 = str(objeto['BI'])
            #jdato2 = str(objeto['OF'])
            #if jdato.find('price')==-1:
            #    print("no tiene nada LA ",jdato.find('price'))
                
            #elif jdato1.find('price')==-1:
            #    print("no tiene nada BI ",jdato1.find('price'))
                
            
            #elif jdato2.find('price')==-1:
            #    print("no tiene nada OF",jdato2.find('price'))
           
            return objeto
        
      except:       
        flash('instrument_by_symbol_para_CalculoMep__: Symbol Incorrect')   
        return render_template("instrumentos.html" )
   










