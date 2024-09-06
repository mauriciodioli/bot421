# test_order_report_handler.py
from flask import Blueprint, render_template,session, request, redirect, url_for, flash,jsonify,g
#from utils.db import db

import random
from datetime import datetime

test_2_order_report_handler = Blueprint('test_2_order_report_handler',__name__)


# Función para simular un reporte de orden
def simulate_order_report(clOrdId, symbol, status, transactTime, text):
    return {
        'orderReport': {
            'clOrdId': clOrdId,
            'instrumentId': {'symbol': symbol},
            'status': status,
            'transactTime': transactTime,
            'text': text
        }
    }

# Función para simular operaciones enviadas
def simulate_operacion_enviada1(clOrdId, symbol, status, ut):
    return {
        'Symbol': symbol,
        '_cliOrderId': clOrdId,       
        'status': status,
        '_ut_': ut
    }
    
    
def simulate_operacion_enviada(clOrdId, symbol, status, ut, user_id, userCuenta, accountCuenta, saldo):
    return {
        'Symbol': symbol,
        '_t_': 'None',
        '_tr_': 'None',
        '_s_': 'None',
        '_ut_': ut,
        'precio Offer': 'None',
        '_ws_client_order_id': 'None',
        '_cliOrderId': clOrdId,
        'timestamp': datetime.now(),
        'status': status,
        'statusActualBotonPanico': status,
        'user_id': user_id,
        'userCuenta': userCuenta,
        'accountCuenta': accountCuenta,
        'tiempoSaldo': datetime.now(),
        'saldo': saldo
    }
 #{'Symbol': 'MERV - XMEV - BBAR - 24hs', '_cliOrderId': 1, 'status': 'TERMINADA'},
# Simulación de diccionarios globales y operaciones enviadas
diccionario_global_operaciones = {
    'AAPL': {'symbol': 'AAPL', 'ut': 0, 'status': '0'},
    #'GOOG': {'symbol': 'GOOG', 'ut': 0, 'status': '1'},
    #'MSFT': {'symbol': 'MSFT', 'ut': 3, 'status': '1'},
    #'TSLA': {'symbol': 'TSLA', 'ut': 10, 'status': '0'},
    #'AMZN': {'symbol': 'AMZN', 'ut': 0, 'status': '1'},
    #'FB': {'symbol': 'FB', 'ut': 7, 'status': '0'},
    #'NFLX': {'symbol': 'NFLX', 'ut': 2, 'status': '1'},
    #'NVDA': {'symbol': 'NVDA', 'ut': 8, 'status': '0'},
    #'BABA': {'symbol': 'BABA', 'ut': 1, 'status': '1'},
    #'ORCL': {'symbol': 'ORCL', 'ut': 3, 'status': '0'}
}




user_id = 'apipuntillo22583398'
userCuenta = 'dpuntillo@gmail.com'
accountCuenta = '10861'
saldo = 1581539.79

diccionario_operaciones_enviadas = {
    1: simulate_operacion_enviada(101, 'AAPL', '1', 1, user_id, userCuenta, accountCuenta, saldo),
    2: simulate_operacion_enviada(131, 'BBAR', 'ANTERIOR', 7, user_id, userCuenta, accountCuenta, saldo),
    3: simulate_operacion_enviada(141, 'AAPL', 'ANTERIOR', 8, user_id, userCuenta, accountCuenta, saldo),
    4: simulate_operacion_enviada(4, 'AAPL', 'ANTERIOR', 17, user_id, userCuenta, accountCuenta, saldo),
   # 5: simulate_operacion_enviada(5, 'TSLA', 'ANTERIOR', 1, user_id, userCuenta, accountCuenta, saldo),
   # 6: simulate_operacion_enviada(6, 'BMA', 'ANTERIOR', 4, user_id, userCuenta, accountCuenta, saldo),
   # 7: simulate_operacion_enviada(7, 'GFGC51973O', 'ANTERIOR', 5, user_id, userCuenta, accountCuenta, saldo),
   # 101: simulate_operacion_enviada(101, 'AAPL', '1', 3, user_id, userCuenta, accountCuenta, saldo),
   # 121: simulate_operacion_enviada(121, 'AAPL', '1', 7, user_id, userCuenta, accountCuenta, saldo), 
   # 131: simulate_operacion_enviada(131, 'AAPL', '1', 5, user_id, userCuenta, accountCuenta, saldo),
   # 102: simulate_operacion_enviada(102, 'AAPL', '1', 7, user_id, userCuenta, accountCuenta, saldo),
   # 132: simulate_operacion_enviada(132, 'AAPL', '1', 7, user_id, userCuenta, accountCuenta, saldo),    
   # 8: simulate_operacion_enviada(8, 'MIRG', 'ANTERIOR', 1, user_id, userCuenta, accountCuenta, saldo),
   # 9: simulate_operacion_enviada(9, 'AGRO', 'ANTERIOR', 13, user_id, userCuenta, accountCuenta, saldo),
   # 10: simulate_operacion_enviada(10, 'COME', 'ANTERIOR', 50, user_id, userCuenta, accountCuenta, saldo),
   # 11: simulate_operacion_enviada(11, 'LOMA', 'ANTERIOR', 1, user_id, userCuenta, accountCuenta, saldo),
   # 12: simulate_operacion_enviada(104, 'AAPL', 'REJECTED', 8, user_id, userCuenta, accountCuenta, saldo),
   # 105: simulate_operacion_enviada(105, 'AAPL', 'CANCELLED', 3, user_id, userCuenta, accountCuenta, saldo),
   # 125: simulate_operacion_enviada(125, 'AAPL', 'FILLED', 3, user_id, userCuenta, accountCuenta, saldo),
   # 201: simulate_operacion_enviada(201, 'GOOG', 'ANTERIOR', 20, user_id, userCuenta, accountCuenta, saldo),
   # 202: simulate_operacion_enviada(202, 'GOOG', 'FILLED', 15, user_id, userCuenta, accountCuenta, saldo),
   # 203: simulate_operacion_enviada(203, 'GOOG', 'NEW', 5, user_id, userCuenta, accountCuenta, saldo),
   # 301: simulate_operacion_enviada(301, 'MSFT', 'ANTERIOR', 10, user_id, userCuenta, accountCuenta, saldo),
   # 302: simulate_operacion_enviada(302, 'MSFT', 'FILLED', 8, user_id, userCuenta, accountCuenta, saldo),
   # 401: simulate_operacion_enviada(401, 'TSLA', 'ANTERIOR', 12, user_id, userCuenta, accountCuenta, saldo),
   # 402: simulate_operacion_enviada(402, 'TSLA', 'FILLED', 6, user_id, userCuenta, accountCuenta, saldo),
   # 501: simulate_operacion_enviada(501, 'AMZN', 'NEW', 3, user_id, userCuenta, accountCuenta, saldo),
    502: simulate_operacion_enviada(502, 'AMZN', 'FILLED', 7, user_id, userCuenta, accountCuenta, saldo),
}



# Escenarios de prueba
test_cases = [
    simulate_order_report(101, 'AAPL', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(502, 'AMZN', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(131, 'BBAR', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(141, 'AAPL', 'REJECTED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(102, 'AAPL', 'FILLED', '2024-07-18T12:01:00Z', 'Stock 10'),
    simulate_order_report(103, 'AAPL', 'REJECTED', '2024-07-18T12:02:00Z', 'Stock 20'),
    simulate_order_report(4, 'AAPL', 'CANCELLED', '2024-07-18T12:03:00Z', 'Stock 30'),
    simulate_order_report(125, 'AAPL', 'NEW', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(105, 'AAPL', 'PARTIALLY_FILLED', '2024-07-18T12:04:00Z', 'Stock 40'),
    simulate_order_report(106, 'AAPL', 'EXPIRED', '2024-07-18T12:05:00Z', 'Stock 50'),
    simulate_order_report(107, 'AAPL', 'DONE_FOR_DAY', '2024-07-18T12:06:00Z', 'Stock 60'),
    simulate_order_report(108, 'AAPL', 'CANCEL_REJECTED', '2024-07-18T12:07:00Z', 'Stock 70'),
    #simulate_order_report(109, 'AAPL', 'PENDING_CANCEL', '2024-07-18T12:08:00Z', 'Stock 80'),
   # simulate_order_report(201, 'GOOG', 'FILLED', '2024-07-18T12:09:00Z', 'Stock 90'),
   # simulate_order_report(301, 'MSFT', 'ANTERIOR', '2024-07-18T12:10:00Z', 'Stock 100'),
   # simulate_order_report(302, 'MSFT', 'FILLED', '2024-07-18T12:11:00Z', 'Stock 110'),
   # simulate_order_report(401, 'TSLA', 'NEW', '2024-07-18T12:12:00Z', 'Stock 120'),
   # simulate_order_report(402, 'TSLA', 'FILLED', '2024-07-18T12:13:00Z', 'Stock 130'),
   # simulate_order_report(501, 'AMZN', 'FILLED', '2024-07-18T12:14:00Z', 'Stock 140'),
   # simulate_order_report(601, 'FB', 'CANCELLED', '2024-07-18T12:15:00Z', 'Stock 150'),
   # simulate_order_report(701, 'NFLX', 'FILLED', '2024-07-18T12:16:00Z', 'Stock 160'),
   # simulate_order_report(801, 'NVDA', 'REJECTED', '2024-07-18T12:17:00Z', 'Stock 170'),
   # simulate_order_report(901, 'BABA', 'FILLED', '2024-07-18T12:18:00Z', 'Stock 180'),
   # simulate_order_report(1001, 'ORCL', 'ANTERIOR', '2024-07-18T12:19:00Z', 'Stock 190')
]

# Función para obtener el stock de la orden
def obtenerStock(text):
    return random.randint(0, 10)  # Simulación de obtener stock

# Función para asignar clOrdId (simulación)
def asignarClOrId(order_report):
    pass

# Función para verificar si un valor es numérico
def es_numero(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

# Función principal para manejar el reporte de orden
def order_report_handler(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']        
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']  
    print('___________ORH_______STATUS__ENTREGADO: ', status, 'symbol: ',symbol)
    timestamp_order_report = order_data['transactTime']  
   
    if es_numero(clOrdId):
        if len(diccionario_operaciones_enviadas) != 0:
            asignarClOrId(order_report)
            if status != 'NEW' and status != 'PENDING_NEW' and status != 'UNKNOWN':  
                
                _operada(order_report)   

def _operada(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']
    stock_para_closed = int(float(obtenerStock(order_data['text'])))

    print(f'Processing clOrdId {clOrdId} for {symbol} with status {status}')

    # Verifica si el estado está en la lista de estados relevantes
    if status in ['CANCELLED', 'ERROR', 'REJECTED', 'EXPIRED']:
        actualizar_diccionario_enviadas(order_data, symbol, status)

    # Procesa el estado final
    if status in ['FILLED', 'REJECTED','CANCELLED']:
        procesar_estado_final(symbol, clOrdId)
        
        
def actualizar_diccionario_enviadas(order_data, symbol, status):
    """Actualiza el diccionario de operaciones enviadas según el estado de la orden."""
    
    clOrdId = order_data['clOrdId']
    
    if symbol in diccionario_global_operaciones:
        for key, operacion in diccionario_operaciones_enviadas.items():
            # Si la operación corresponde al símbolo y clOrdId
            if operacion['Symbol'] == symbol and operacion['_cliOrderId'] == int(clOrdId):
                # Si la operación no está 'TERMINADA' ni 'CANCELLED'
                if operacion['status'] not in ['TERMINADA', 'CANCELLED']:
                    # Orden Rechazada ('REJECTED'): Si la orden tiene estado 'REJECTED'
                    if status == 'REJECTED':
                        ut_a_devolver = 0
                    # Otros Estados de la Orden: Si la orden tiene cualquier otro estado
                    else:
                        #se coloca este if para que no se le devuelva un valor negativo si la orden tiene estado 'CANCELLED'
                        #y se le le quita el valor de la orden
                        #se debe quitar este if si se desea que el valor de la orden sea positivo cuando la orden sea 'CANCELLED'
                        #if status == 'CANCELLED':
                        #    ut_a_devolver = 0
                        #else:
                        if status == 'CANCELLED':
                            ut_a_devolver = 0
                        else:
                            ut_a_devolver = operacion['_ut_']
                    # Marca la operación como 'TERMINADA'
                    operacion['status'] = 'TERMINADA'
                    
                    # Llamar a la función para actualizar el diccionario global
                    actualizar_diccionario_global(symbol, ut_a_devolver)
                elif operacion['status'] == 'ANTERIOR' and status == 'REJECTED':
                    operacion['status'] = 'TERMINADA'
                elif operacion['status'] == 'CANCELLED':
                    operacion['status'] = 'TERMINADA'
                            

def process_operations():
    global endingGlobal, endingEnviadas

    # Verifica si hay alguna operación global con ut distinto de 0
    endingGlobal = not any(
        operacionGlobal['ut'] != 0
        for operacionGlobal in diccionario_global_operaciones.values()
    )

    # Verifica si hay alguna operación enviada con status distinto de 'TERMINADA'
    endingEnviadas = not any(
        operacionGlobal['status'] != 'TERMINADA'
        for operacionGlobal in diccionario_operaciones_enviadas.values()
    )

    return endingGlobal and endingEnviadas



    # Verifica si el estado está en la lista de estados relevantes
    #if status in ['CANCELLED', 'ERROR', 'REJECTED', 'EXPIRED']:
     #   actualizar_diccionario_enviadas(order_data, symbol, status)

    # Procesa el estado final
   # if status in ['FILLED', 'REJECTED']:
    #    procesar_estado_final(symbol, clOrdId)



def procesar_estado_final(symbol, clOrdId):
    global endingGlobal, endingEnviadas

    endingGlobal = False
    endingEnviadas = False

    # Actualiza el estado de las operaciones enviadas
    endingEnviadas = actualizar_estado_operaciones( symbol, clOrdId)    
    # Revisa las operaciones globales
    for key, operacionGlobal in diccionario_global_operaciones.items():
        if operacionGlobal['symbol'] == symbol:
            if operacionGlobal['ut'] == 0:
                # Verifica si todas las operaciones relacionadas están terminadas
                all_enviadas_terminadas = all(
                    operacion['status'] == 'TERMINADA'
                    for operacion in diccionario_operaciones_enviadas.values()
                    if operacion["Symbol"] == symbol
                )
                if all_enviadas_terminadas:
                    operacionGlobal['status'] = '1'
                    endingGlobal = True
                else:
                    endingGlobal = False
            else:
                endingGlobal = False

    # Asegura que `endingEnviadas` siga siendo 'SI' si corresponde
    if endingGlobal == True and endingEnviadas == True:
        print(f'Final state: endingGlobal={endingGlobal}, endingEnviadas={endingEnviadas}, symbol={symbol}')
        endingOperacionBot(endingGlobal, endingEnviadas, symbol)   

# Función para actualizar el estado de las operaciones enviadas
def actualizar_estado_operaciones(symbol, clOrdId):
    todas_terminadas = True
    for operacion_enviada in diccionario_operaciones_enviadas.values():
        # Verifica si la operación actual no está terminada
        if operacion_enviada['status'] != 'TERMINADA':
            # Actualiza el estado si coincide con el símbolo y clOrdId proporcionados
            if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId):
                operacion_enviada['status'] = 'TERMINADA'
        
   # Verifica si todas las operaciones están en estado 'TERMINADA'
    for operacion_enviada in diccionario_operaciones_enviadas.values():
        if operacion_enviada['status'] != 'TERMINADA':
            todas_terminadas = False
            break  # Sale del bucle si encuentra una operación que no está terminada
    return todas_terminadas
        
def actualizar_diccionario_global(symbol, ut_a_devolver, status_terminado=False):
    """Actualiza el diccionario global de operaciones."""
    operacionGlobal = diccionario_global_operaciones.get(symbol)
    if operacionGlobal:
        if status_terminado:
            operacionGlobal['ut'] = int(ut_a_devolver)
        else:
            operacionGlobal['ut'] += int(ut_a_devolver)
        
        if operacionGlobal['status'] != '0':
            operacionGlobal['status'] = '0'
                 
              
def endingOperacionBot(endingGlobal, endingEnviadas, symbol):
    if symbol in diccionario_global_operaciones and diccionario_operaciones_enviadas:
        print('endingGlobal___ ', endingGlobal, ' endingEnviadas', endingEnviadas, 'symbol: ', symbol)
        # Clear the dictionary if all conditions are met
        diccionario_operaciones_enviadas.clear()
        print("###############################################") 
        print("###############################################") 
        print("###############################################")  
        print("FELICIDADES, EL BOT TERMINO DE OPERAR CON EXITO") 
        print("###############################################") 
        print("###############################################") 
        print("###############################################") 
        








            
# Llamada a la función order_report_handler con cada caso de prueba
@test_2_order_report_handler.route('/test_2_order_report_handler')
def entradaTest2():
    print('************************************************')
    for i, report in enumerate(test_cases):
        print(f'\n--- Test Case {i+1} ---')
        order_report_handler(report)
