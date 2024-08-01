from flask import Blueprint
from utils.common import Marshmallow, db, get
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import time

ma = Marshmallow()

operacion = Blueprint('operacion',__name__) 

class Operacion:
    def __init__(self, ticker, accion, size, price, order_type,environment):
        self.ticker = ticker
        self.side = get.pyRofexInicializada.Side.BUY if accion == 'comprar' else get.pyRofexInicializada.Side.SELL
        self.size = size
        self.price = price
        self.order_type = order_type
        self.environment=environment

    def validar_saldo(self, cuenta=None,pyRofexInicializada=None):
     

        # Obtener el tiempo actual
        tiempo_actual = time.time()

        # Calcular la diferencia de tiempo
        diferencia_tiempo = tiempo_actual - get.ultima_entrada

        # Si han pasado al menos 60 segundos desde la última entrada
        if diferencia_tiempo >= 30:
            # Actualizar el tiempo de la última entrada
            get.ultima_entrada = tiempo_actual

            # Realizar las operaciones que deseas hacer después de 60 segundos
            resumenCuenta = pyRofexInicializada.get_account_report(account=cuenta,environment=cuenta)
            saldo = resumenCuenta["accountData"]["availableToCollateral"]
            # Resto de las operaciones...

            # Verificar el saldo
            costo_total = self.size * self.price
            if saldo >= costo_total:
                return True
            else:
                return False

        else:
            # Si no han pasado 60 segundos, no hacemos nada
            return False

    def enviar_orden(self, cuenta=None,pyRofexInicializada=None):
        if self.validar_saldo(cuenta=cuenta,pyRofexInicializada=pyRofexInicializada):
            #pass
            pyRofexInicializada.send_order_via_websocket(ticker=self.ticker, side=self.side, size=self.size, order_type=self.order_type, price=self.price,environment=self.environment)
           
            return True
        else:
            print("No hay saldo suficiente para realizar la operación.")
            return False
    def enviar_orden_sin_validar_saldo(self, cuenta=None,pyRofexInicializada=None):
             #pass
        pyRofexInicializada.send_order_via_websocket(ticker=self.ticker, 
                                                     side=self.side, 
                                                     size=self.size, 
                                                     order_type=self.order_type, 
                                                     price=self.price,environment=self.environment)
       
        return True
    
    def enviar_orden_rest_sin_validar_saldo(self, cuenta=None,pyRofexInicializada=None,order_type=None):
             #pass
        order = pyRofexInicializada.send_order(ticker=self.ticker,
                           side=self.side,
                           size=self.size,
                           price=self.price,
                           order_type=order_type,
                           environment=self.environment)
        return True
       