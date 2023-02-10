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


estrategiaUno = Blueprint('estrategiaUno',__name__)

       
class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2




@estrategiaUno.route('/cargaDatosEstrategyUno/', methods = ['POST'])
def cargaDatosEstrategyUno():   
    if request.method == 'POST':         
        Ticker = request.form["Ticker"]   
        cantidad = request.form["cantidad"] 
        spread = request.form["spread"] 
        mensaje = Ticker+','+cantidad+','+spread
        
        inst = InstrumentoEstrategiaUno(Ticker, cantidad, spread)
       
        get.pyRofexInicializada.init_websocket_connection (market_data_handler,order_report_handler,error_handler,exception_error)
        tickers=[inst.instrument]
        print("tickers",tickers)
        entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                    get.pyRofexInicializada.MarketDataEntry.OFFERS
                    ]   
        print("entries",entries)     
        instrumento_suscriptio = get.pyRofexInicializada.market_data_subscription(tickers,entries)
        print(instrumento_suscriptio)
        print(inst.instrument)
        # Subscribes to receive order report for the default account
        get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaUno.html')
    
    
@estrategiaUno.route('/estrategyUno/')
def estrategyUno(): 
    try:
        inst = InstrumentoEstrategiaUno("WTI/MAY22", 12, 0.05) 
         
        get.pyRofexInicializada.init_websocket_connection (market_data_handler,order_report_handler,error_handler,exception_error)
        tickers=[inst.instrument]
        print("tickers",tickers)
        entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                    get.pyRofexInicializada.MarketDataEntry.OFFERS
                    ]   
        print("entries",entries)     
        instrumento_suscriptio = get.pyRofexInicializada.market_data_subscription(tickers,entries)
        print(instrumento_suscriptio)
        print(inst.instrument)
        # Subscribes to receive order report for the default account
        get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaUno.html')
    except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
        return render_template("errorLogueo.html" ) 
    
    # Defines the handlers that will process the messages.
def market_data_handler( message):
       # mensaje = Ticker+','+cantidad+','+spread
        print("Processing Market Data Message Received: {0}".format(message))
       # clientesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #clientesocket.connect(('localhost',8089))
        #clientesocket.send(format(message).encode())
       
        if InstrumentoEstrategiaUno.state is States.WAITING_MARKET_DATA:
            print("Processing Market Data Message Received: {0}".format(message))
            last_md = None
            bid = message["marketData"]["BI"]
            offer = message["marketData"]["OF"]
            if bid and offer:
                bid_px = bid[0]["price"]
                offer_px = offer[0]["price"]
                bid_offer_spread = round(offer_px - bid_px, 6) - 0.002
                if bid_offer_spread >= InstrumentoEstrategiaUno.spread:
                    if InstrumentoEstrategiaUno.my_order:
                        for order in InstrumentoEstrategiaUno.my_order.values():
                            if order["orderReport"]["side"] == "BUY" and \
                                    order["orderReport"]["price"] < bid_px:
                                InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.BUY, bid_px + InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.buy_size)
                            elif order["orderReport"]["side"] == "SELL" and \
                                    order["orderReport"]["price"] > offer_px:
                                InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.SELL, offer_px - InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.sell_size)
                    else:
                        if InstrumentoEstrategiaUno.buy_size > 0:
                            InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.BUY, bid_px + InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.buy_size)
                        if InstrumentoEstrategiaUno.sell_size > 0:
                            InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.SELL, offer_px - InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.sell_size)
                else:  # Lower spread
                    InstrumentoEstrategiaUno._cancel_if_orders()
            else:
                InstrumentoEstrategiaUno._cancel_if_orders()
        else:
            InstrumentoEstrategiaUno.last_md = message








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


  
  


   

