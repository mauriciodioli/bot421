# test_order_report_handler.py
from flask import Blueprint, render_template,session, request, redirect, url_for, flash,jsonify,g
#from utils.db import db

import random


import random


test_order_report_handler = Blueprint('test_order_report_handler',_name_)


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
def simulate_operacion_enviada(clOrdId, symbol, status, ut):
    return {
        '_cliOrderId': clOrdId,
        'Symbol': symbol,
        'status': status,
        'ut': ut
    }

# Simulación de diccionarios globales y operaciones enviadas
diccionario_global_operaciones = {
    'AAPL': {'symbol': 'AAPL', 'ut': 15, 'status': '0'},
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

diccionario_operaciones_enviadas = {
    '101': simulate_operacion_enviada(101, 'AAPL', 'FILLED', 3),
    '121': simulate_operacion_enviada(121, 'AAPL', 'FILLED', 7),   
    '131': simulate_operacion_enviada(131, 'AAPL', 'FILLED', 5),
    #'102': simulate_operacion_enviada(102, 'AAPL', 'FILLED', 7),
    '132': simulate_operacion_enviada(132, 'AAPL', 'NEW', 3),
    #'104': simulate_operacion_enviada(104, 'AAPL', 'REJECTED', 8),
    #'105': simulate_operacion_enviada(105, 'AAPL', 'CANCELLED', 3),
    #'125': simulate_operacion_enviada(125, 'AAPL', 'FILLED', 3),
    #'201': simulate_operacion_enviada(201, 'GOOG', 'ANTERIOR', 20),
    #'202': simulate_operacion_enviada(202, 'GOOG', 'FILLED', 15),
    #'203': simulate_operacion_enviada(203, 'GOOG', 'NEW', 5),
    #'301': simulate_operacion_enviada(301, 'MSFT', 'ANTERIOR', 10),
    #'302': simulate_operacion_enviada(302, 'MSFT', 'FILLED', 8),
    #'401': simulate_operacion_enviada(401, 'TSLA', 'ANTERIOR', 12),
    #'402': simulate_operacion_enviada(402, 'TSLA', 'FILLED', 6),
    #'501': simulate_operacion_enviada(501, 'AMZN', 'NEW', 3),
    #'502': simulate_operacion_enviada(502, 'AMZN', 'FILLED', 7),
    #'601': simulate_operacion_enviada(601, 'FB', 'CANCELLED', 4),
    #'602': simulate_operacion_enviada(602, 'FB', 'REJECTED', 5),
    #'701': simulate_operacion_enviada(701, 'NFLX', 'ANTERIOR', 2),
    #'702': simulate_operacion_enviada(702, 'NFLX', 'FILLED', 9),
    #'801': simulate_operacion_enviada(801, 'NVDA', 'NEW', 11),
    #'802': simulate_operacion_enviada(802, 'NVDA', 'REJECTED', 6),
    #'901': simulate_operacion_enviada(901, 'BABA', 'FILLED', 4),
    #'902': simulate_operacion_enviada(902, 'BABA', 'CANCELLED', 5),
    #'1001': simulate_operacion_enviada(1001, 'ORCL', 'ANTERIOR', 38),
    #'1002': simulate_operacion_enviada(1002, 'ORCL', 'FILLED', 2)
}
# Escenarios de prueba
test_cases = [
    simulate_order_report(101, 'AAPL', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(121, 'AAPL', 'REJECTED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(131, 'AAPL', 'CANCELLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(141, 'AAPL', 'REJECTED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(102, 'AAPL', 'FILLED', '2024-07-18T12:01:00Z', 'Stock 10'),
    simulate_order_report(103, 'AAPL', 'REJECTED', '2024-07-18T12:02:00Z', 'Stock 20'),
    simulate_order_report(104, 'AAPL', 'CANCELLED', '2024-07-18T12:03:00Z', 'Stock 30'),
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

def manejar_cancelado(order_data, symbol, status):
    actualizar_diccionario_enviadas(order_data, symbol, status)

def manejar_error(order_data, symbol, status):
    actualizar_diccionario_enviadas(order_data, symbol, status)

def manejar_rechazado(order_data, symbol, status):
    actualizar_diccionario_enviadas(order_data, symbol, status)
    procesar_estado_final(symbol, clOrdId)

def manejar_expirado(order_data, symbol, status):
    actualizar_diccionario_enviadas(order_data, symbol, status)

def manejar_lleno(order_data, symbol, clOrdId):
    procesar_estado_final(symbol, clOrdId)
# Función principal para manejar el reporte de orden
def order_report_handler(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']        
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']  
    print('____ORH___STATUS_ENTREGADO: ', status, 'symbol: ',symbol)
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
    global endingGlobal, endingEnviadas

    endingGlobal = True
    endingEnviadas = True
    print(f'Processing order {clOrdId} for {symbol} with status {status}')


    casos_estado = {
            'CANCELLED': manejar_cancelado,
            'ERROR': manejar_error,
            'REJECTED': manejar_rechazado,
            'EXPIRED': manejar_expirado,
            'FILLED': manejar_lleno
    }
    # Obtén la función correspondiente para el estado
    funcion_estado = casos_estado.get(status)


    # Si existe una función para el estado, llámala
    if funcion_estado:
        if status == 'FILLED':
            funcion_estado(order_data, symbol, clOrdId)
        if status == 'CANCELLED':
            funcion_estado(order_data, symbol, clOrdId)
        if status == 'ERROR':
            funcion_estado(order_data, symbol, clOrdId)
        if status == 'REJECTED':
            funcion_estado(order_data, symbol, clOrdId)
        if status == 'EXPIRED':
            funcion_estado(order_data, symbol, clOrdId)
    
    if process_operations():
        endingOperacionBot(endingGlobal, endingEnviadas, symbol)
        


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



def procesar_estado_final(symbol, clOrdId,endingGlobal,endingEnviadas):
   

    # Actualiza el estado de las operaciones enviadas
    for operacion_enviada in diccionario_operaciones_enviadas.values():
        if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId) and operacion_enviada['status'] != 'TERMINADA':
            operacion_enviada['status'] = 'TERMINADA'

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
                    endingGlobal = 'SI'
                else:
                    endingGlobal = 'NO'
            else:
                endingGlobal = 'NO'

    # Asegura que endingEnviadas siga siendo 'SI' si corresponde
     
        
        
              
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
                        ut_a_devolver = operacion['ut']
                    # Marca la operación como 'TERMINADA'
                    operacion['status'] = 'TERMINADA'
                    
                    # Llamar a la función para actualizar el diccionario global
                    actualizar_diccionario_global(symbol, ut_a_devolver)
                elif operacion['status'] == 'ANTERIOR' and status == 'REJECTED':
                    operacion['status'] = 'TERMINADA'
                elif operacion['status'] == 'CANCELLED':
                    operacion['status'] = 'TERMINADA'
                    
def actualizar_diccionario_global(symbol, ut_a_devolver):
    """Actualiza el diccionario global de operaciones."""
    operacionGlobal = diccionario_global_operaciones.get(symbol)
    if operacionGlobal:
        operacionGlobal['ut'] += int(ut_a_devolver)
        if operacionGlobal['status'] != '0':
            operacionGlobal['status'] = '0'
            
            
# Llamada a la función order_report_handler con cada caso de prueba
@test_order_report_handler.route('/test_order_report_handler')
def entradaTest():
    print('****************')
    for i, report in enumerate(test_cases):
        print(f'\n--- Test Case {i+1} ---')
        order_report_handler(report)