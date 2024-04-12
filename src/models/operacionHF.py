from flask import Blueprint
from utils.common import Marshmallow, db, get
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import time

ma = Marshmallow()

operacionHF = Blueprint('operacionHF',__name__) 

# mal el orden de los argunmentos, los nombres(español o ingles? se usa ingles), y  clordid ????  es imposible el restreo
class OperacionHF:
    #send_order_via_websocket:  ticker,size,side,order_type,ws_client_order_id,price
    def __init__(self, ticker, accion, size, price, ws_client_order_id,order_type):
        self.ticker = ticker
        self.side = get.pyRofexInicializada.Side.BUY if accion == 'comprar' else get.pyRofexInicializada.Side.SELL
        self.size = size
        self.price = price
        self.order_type = order_type
        self._ws_client_order_id = ws_client_order_id


        #self.order_type = order_type
   

    def enviar_orden(self):
            #send_order_via_websocket:  ticker,size,side,order_type,ws_client_order_id,price
            #get.pyConectionWebSocketInicializada.send_order_via_websocket(ticker=Symbol,size=ut,side=get.pyRofexInicializada.Side.BUY,order_type=get.pyRofexInicializada.OrderType.LIMIT,ws_client_order_id=_ws_client_order_id,price=precio)
            #get.pyRofexInicializada.send_order_via_websocket(ticker=self.ticker, side=self.side, size=self.size, order_type=self.order_type, price=self.price)
            get.pyRofexInicializada.send_order_via_websocket(ticker=self.ticker,size=self.size,side=self.side,order_type=self.order_type,ws_client_order_id=self._ws_client_order_id,price=self.price)
            #ticker=self.ticker,size=self.size,side=self.side,order_type=self.order_type,ws_client_order_id=self._ws_client_order_id,price=self.price
            
        
            return True
     