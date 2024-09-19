

from utils.db import db
from flask_marshmallow import Marshmallow
from flask import Blueprint
import random
from datetime import datetime

ma = Marshmallow()

operacionEstrategia = Blueprint('operacionEstrategia',__name__) 
class OperacionEstrategia:
    def __init__(self, pyRofexInicializada, diccionario_global_operaciones, diccionario_operaciones_enviadas, Symbol, tipo_de_activo, Liquidez_ahora_cedear, senial, message):
        self.pyRofexInicializada = pyRofexInicializada
        self.diccionario_global_operaciones = diccionario_global_operaciones
        self.diccionario_operaciones_enviadas = diccionario_operaciones_enviadas
        self.Symbol = Symbol
        self.tipo_de_activo = tipo_de_activo
        self.Liquidez_ahora_cedear = Liquidez_ahora_cedear
        self.senial = senial
        self.message = message

    def obtener_precio(self, tipo):
        """Obtiene el precio de 'OF', 'BI' o 'LA'"""
        return self.message["marketData"].get(tipo, [{}])[0].get("price", 0) if tipo in ["OF", "BI"] else self.message["marketData"].get(tipo, {}).get("price", 0)
    
    def operar(self):
        try:
            print("FUN: OperacionWs__ INICIO operación")
            
            # Validar existencia del símbolo en el diccionario global
            if self.Symbol not in self.diccionario_global_operaciones:
                print(f"Error: El símbolo {self.Symbol} no se encuentra en diccionario_global_operaciones")
                return
            # Parámetros básicos
            trade_en_curso = self.diccionario_global_operaciones[self.Symbol]['tradeEnCurso']
            ut = abs(int(self.diccionario_global_operaciones[self.Symbol]['ut']))
            saldocta = self.diccionario_global_operaciones[self.Symbol]['saldo']

            # Validar parámetros
            if not trade_en_curso:
                print(f"Error: trade_en_curso es None o no existe para {self.Symbol}")
                return
            if ut <= 0:
                print(f"Error: Cantidad inválida (ut): {ut}")
                return
            if saldocta is None or saldocta <= 0:
                print(f"Error: Saldo de cuenta inválido o insuficiente: {saldocta}")
                return

            # Obtener precios
            precio_of = self.obtener_precio("OF")
            precio_bi = self.obtener_precio("BI")
            precio_la = self.obtener_precio("LA")

            if precio_of is None and precio_bi is None and precio_la is None:
                print("Error: No se pudo obtener ningún precio válido (OF, BI, LA)")
                return

            plataoperacion1 = ut * precio_of if precio_of else float('inf')
            plataoperacion2 = ut * precio_bi if precio_bi else float('inf')
            plataoperacion3 = ut * precio_la if precio_la else float('inf')

            if saldocta < plataoperacion1 and saldocta < plataoperacion2 and saldocta < plataoperacion3:
                print(f"Error: Saldo insuficiente para operar. Saldo: {saldocta}, PlataOperación: {min(plataoperacion1, plataoperacion2, plataoperacion3)}")
                return

            if saldocta > plataoperacion1 and saldocta > plataoperacion2 and saldocta > plataoperacion3:
                if self.diccionario_global_operaciones[self.Symbol]['ut'] > 0:
                    _ws_client_order_id = 1001 + random.randint(1, 100000)
                    
                    # Definir precios y sides según el tipo de señal
                    if self.senial == 'OPEN.':
                        precio = precio_of if precio_of else precio_la
                        side = self.pyRofexInicializada.Side.BUY
                    elif self.senial == 'closed.':
                        precio = precio_bi if precio_bi else precio_la
                        side = self.pyRofexInicializada.Side.SELL
                    else:
                        print(f"Señal desconocida: {self.senial}")
                        return
                    
                    
                     # Validar precio
                    if precio is None:
                        print(f"Error: No se pudo determinar un precio válido para la señal {self.senial}")
                        return
                      # Enviar orden
                    print(f"Enviando orden con los siguientes parámetros:\n"
                        f" - Ticker: {self.Symbol}\n"
                        f" - Cantidad: {ut}\n"
                        f" - Precio: {precio}\n"
                        f" - Side: {side}\n"
                        f" - Cuenta: {self.diccionario_global_operaciones[self.Symbol]['accountCuenta']}\n"
                        f" - ws_client_order_id: {_ws_client_order_id}")
                    # Enviar orden
                    self.pyRofexInicializada.send_order_via_websocket(ticker=self.Symbol,size=ut,side=side,order_type=self.pyRofexInicializada.OrderType.LIMIT,ws_client_order_id=_ws_client_order_id,price=precio,environment=self.diccionario_global_operaciones[self.Symbol]['accountCuenta'])
                     
                    ws_client_order_id = _ws_client_order_id

                    diccionario = {
                        "Symbol": self.Symbol,
                        "_t_": self.tipo_de_activo,
                        "_tr_": trade_en_curso,
                        "_s_": self.senial,
                        "_ut_": ut,
                        "precio Offer": precio,
                        "_ws_client_order_id": ws_client_order_id,
                        "_cliOrderId": 0,
                        "timestamp": datetime.now(),
                        "status": "1",
                        "statusActualBotonPanico": "",
                        "user_id": self.diccionario_global_operaciones[self.Symbol]['user_id'],
                        "userCuenta": self.diccionario_global_operaciones[self.Symbol]['userCuenta'],
                        "accountCuenta": self.diccionario_global_operaciones[self.Symbol]['accountCuenta']
                    }
                    self.diccionario_operaciones_enviadas[len(self.diccionario_operaciones_enviadas) + 1] = diccionario

                    self.diccionario_global_operaciones[self.Symbol]['ut'] -= ut
                    print(f"FUN: OperacionWs__ opero correctamente: {self.Symbol}, ut: {ut}, cuenta: {self.diccionario_global_operaciones[self.Symbol]['accountCuenta']}")
            else:
                print(f"FUN: OperacionWs__ No se puede operar Saldo Insuficiente, o no hay liquidez. El Saldo es: {saldocta}")

        except Exception as e:
            print(f"Error en estrategies/opera_estrategi.py OperacionWs: {e}")

# Ejemplo de uso en tu aplicación Flask
#    operacion = Operacion(pyRofexInicializada, diccionario_global_operaciones, diccionario_operaciones_enviadas, Symbol, tipo_de_activo, Liquidez_ahora_cedear, senial, message)
#    operacion.operar()
