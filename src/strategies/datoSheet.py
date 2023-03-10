from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
import routes.instrumentosGet as instrumentosGet
from utils.db import db
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os #obtener el directorio de trabajo actual
#import drive
#drive.mount('/content/gdrive')



datoSheet = Blueprint('datoSheet',__name__)

SPREADSHEET_ID='1pyPq_2tZJncV3tqOWKaiR_3mt1hjchw12Bl_V8Leh74'#drpiBot2

class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2

def leerSheet():         
     scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    
     newPath = os.path.join(os.getcwd(), 'strategies\\pruebasheetpython.json')  
     print(newPath)
     creds = ServiceAccountCredentials.from_json_keyfile_name(newPath, scope)
     
     #creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/mDioli/Documents/ITCOR/bot421/src/strategies/pruebasheetpython.json', scope)
     client = gspread.authorize(creds)
     
     sheet = client.open_by_key(SPREADSHEET_ID).sheet1   
     symbol = sheet.col_values(1)
     trade_en_curso = sheet.col_values(19)
     ut = sheet.col_values(20)
     senial = sheet.col_values(21)
     union = zip(symbol,trade_en_curso,ut,senial)
     
     #for Symbol,trade_en_curso,ut,senial  in union:
      #print(Symbol,trade_en_curso,ut,senial)
    
     
     return union
 
@datoSheet.route('/estrategiaSheet/')
def estrategiaSheet():     
    
    try:
        listado = leerSheet()
        cont =0 
        for Symbol,trade_en_curso,ut,senial  in listado:         
           
            
            if Symbol != 'Symbol':
                #if trade_en_curso == 'LONG_':
                    if senial == 'OPEN.':
                        if Symbol != '':
                                cont +=1
                                inst = InstrumentoEstrategiaUno(Symbol, 12, 0.05) 
                                print("entra a Operar____",cont,"____",Symbol,"______________",trade_en_curso,"__________________",senial)
                               
                                
                                get.pyRofexInicializada.init_websocket_connection (market_data_handler,order_report_handler,error_handler,exception_error)
                                tickers=[inst.instrument]
                               
                                entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                                            get.pyRofexInicializada.MarketDataEntry.OFFERS
                                            ]   
                                    
                                instrumento_suscriptio = get.pyRofexInicializada.market_data_subscription(tickers,entries)
                                
                                # Subscribes to receive order report for the default account
                                get.pyRofexInicializada.order_report_subscription(snapshot=True)
                    #else

        
        return render_template('/estrategiaOperando.html')
    except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
        return render_template("errorLogueo.html" )
    
def market_data_handler( message):
    
        # mensaje = Ticker+','+cantidad+','+spread
        print("_____________________Estrategia_001:...")
        print("Processing ddddddddddddddddddMarket Data Message Received: ",message)
        
                   
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
        
        
        
##########################esto es para ws#############################
#Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}
def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic21"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

