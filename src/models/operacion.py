from flask import Blueprint
from utils.common import Marshmallow, db, get
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


ma = Marshmallow()

operacion = Blueprint('operacion',__name__) 

class Operacion:
    def __init__(self, ticker, accion, size, price, order_type):
        self.ticker = ticker
        self.side = get.pyRofexInicializada.Side.BUY if accion == 'comprar' else get.pyRofexInicializada.Side.SELL
        self.size = size
        self.price = price
        self.order_type = order_type

    def validar_saldo(self, cuenta):
        saldo_actual = get.pyRofexInicializada.get_account_report(account=cuenta)
        costo_total = self.size * self.price

        if saldo_actual >= costo_total:
            return True
        else:
            return False

    def enviar_orden(self, cuenta):
        if self.validar_saldo(cuenta):
            get.pyRofexInicializada.order_report_subscription()
            get.pyRofexInicializada.send_order_via_websocket(ticker=self.ticker, side=self.side, size=self.size, order_type=self.order_type, price=self.price)
           
            return True
        else:
            print("No hay saldo suficiente para realizar la operación.")
            return False