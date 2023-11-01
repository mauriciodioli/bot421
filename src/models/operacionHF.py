from flask import Blueprint
from utils.common import Marshmallow, db, get
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import time

ma = Marshmallow()

operacionHF = Blueprint('operacionHF',__name__) 

# mal el orden de los argunmentos, los nombres(español o ingles? se usa ingles), y  clordid ????  es imposible el restreo
class OperacionHF:
    def __init__(self, ticker, size, side, type, ws_cli_ord_id, price ):
        self.ticker = ticker
        self.size = size
        self.side = get.pyRofexInicializada.Side.BUY if side == 'comprar' else get.pyRofexInicializada.Side.SELL
        self.order_type = get.pyRofexInicializada.OrderType.LIMIT if type == 'limite' else get.pyRofexInicializada.OrderType.MARKET
        self.ws_Cliordid = ws_cli_ord_id
        self.price = price
        self.clOrdID = None  # este atributo para guardar el clOrdID

        #self.order_type = order_type
   

    def enviar_orden(self, cuenta):
            #ticker,size,side,order_type,ws_client_order_id,price
            respuesta = get.pyRofexInicializada.send_order_via_websocket(ticker=self.ticker, side=self.side, size=self.size, order_type=self.order_type, ws_client_order_id=self.ws_Cliordid, price=self.price)
            self.clOrdID = respuesta.get('clOrdID', None)  # Almacenar el ClOrdID
        
            return True
     