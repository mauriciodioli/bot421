<<<<<<< HEAD
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




user_id = 'apipuntillo22583398'
userCuenta = 'dpuntillo@gmail.com'
accountCuenta = '10861'
saldo = 1581539.79

diccionario_operaciones_enviadas = {
   
}

 #{'Symbol': 'MERV - XMEV - BBAR - 24hs', '_cliOrderId': 1, 'status': 'TERMINADA'},
# Simulación de diccionarios globales y operaciones enviadas
diccionario_global_operaciones = {
    'MERV - XMEV - AGRO - 24hs': {'symbol': 'MERV - XMEV - AGRO - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - ADBE - 24hs': {'symbol': 'MERV - XMEV - ADBE - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - AMD - 24hs': {'symbol': 'MERV - XMEV - AGRO - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - AVGO - 24hs': {'symbol': 'MERV - XMEV - AVGO - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - BABA - 24hs': {'symbol': 'MERV - XMEV - BABA - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - ALUA - 24hs': {'symbol': 'MERV - XMEV - ALUA - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - BBAR - 24hs': {'symbol': 'MERV - XMEV - BBAR - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - TRAN - 24hs': {'symbol': 'MERV - XMEV - TRAN - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - GILD - 24hs': {'symbol': 'MERV - XMEV - GILD - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - MELI - 24hs': {'symbol': 'MERV - XMEV - MELI - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - NVDA - 24hs': {'symbol': 'MERV - XMEV - NVDA - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - WMT - 24hs': {'symbol': 'MERV - XMEV - WMT - 24hs', 'ut': 0, 'status': '0'}
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


# Escenarios de prueba
test_cases = [
    simulate_order_report(1001, 'MERV - XMEV - AGRO - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1002, 'MERV - XMEV - ADBE - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1003, 'MERV - XMEV - AMD - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1004, 'MERV - XMEV - AVGO - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1005, 'MERV - XMEV - BABA - 24hs', 'FILLED', '2024-07-18T12:01:00Z', 'Stock 10'),
    simulate_order_report(1006, 'MERV - XMEV - ALUA - 24hs', 'FILLED', '2024-07-18T12:02:00Z', 'Stock 20'),
    simulate_order_report(1007, 'MERV - XMEV - BBAR - 24hs', 'FILLED', '2024-07-18T12:03:00Z', 'Stock 30'),
    simulate_order_report(1008, 'MERV - XMEV - TRAN - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1009, 'MERV - XMEV - GILD - 24hs', 'FILLED', '2024-07-18T12:04:00Z', 'Stock 40'),
    simulate_order_report(1010, 'MERV - XMEV - MELI - 24hs', 'FILLED', '2024-07-18T12:05:00Z', 'Stock 50'),
    simulate_order_report(1011, 'MERV - XMEV - NVDA - 24hs', 'FILLED', '2024-07-18T12:06:00Z', 'Stock 60'),
    simulate_order_report(1012, 'MERV - XMEV - WMT - 24hs', 'FILLED', '2024-07-18T12:07:00Z', 'Stock 70'),
    simulate_order_report(1013, 'MERV - XMEV - AGRO - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 5'),
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


operaciones_a_simular = [
    {'symbol': 'MERV - XMEV - AGRO - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'SHORT', 'ut': 10, 'senial': 'closed.', 'status': '0'},
    {'symbol': 'MERV - XMEV - ADBE - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - AMD - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - AVGO - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 5, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - BABA - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 2, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - ALUA - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'LONG_', 'ut': 32, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - BBAR - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'LONG_', 'ut': 6, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - TRAN - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'LONG_', 'ut': 16, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - GILD - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - MELI - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - NVDA - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 4, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - WMT - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 5, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - AGRO - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'SHORT', 'ut': 5, 'senial': 'closed.', 'status': '0'},
]

# Diccionario para registrar cuántas veces se actualiza cada operación
registro_actualizaciones = {}
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
        
    # Registra cuántas veces se ha actualizado esta operación
    if clOrdId not in registro_actualizaciones:
        registro_actualizaciones[clOrdId] = 0
    registro_actualizaciones[clOrdId] += 1    
        
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
 # Verifica si la operación ya está en el estado 'TERMINADA'
    if diccionario_operaciones_enviadas.get(clOrdId) == 'TERMINADA':
        print(f"[AVISO] La operación {clOrdId} ya estaba en estado TERMINADA, se intentó actualizar nuevamente.")
        # Puedes optar por no actualizarla de nuevo, según la lógica:
        return
    # Actualiza el estado de las operaciones enviadas
    endingEnviadas = actualizar_estado_operaciones( symbol, clOrdId)    
    # Revisa las operaciones globales
    for key, operacionGlobal in diccionario_global_operaciones.items():
        if operacionGlobal['symbol'] == symbol:
            if operacionGlobal['ut'] == 0:
                # Verifica si todas las operaciones relacionadas están terminadas
                all_enviadas_validas = all(
                    operacion['status'] == 'TERMINADA'
                    for operacion in diccionario_operaciones_enviadas.values()
                    if operacion["Symbol"] == symbol
                )
                any_enviada_anterior = any(
                    operacion['status'] == 'ANTERIOR'
                    for operacion in diccionario_operaciones_enviadas.values()
                     if operacion["Symbol"] == symbol
                )
                if all_enviadas_validas and not any_enviada_anterior:
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
        
#def actualizar_diccionario_global(symbol, ut_a_devolver, status_terminado=False):
 #   """Actualiza el diccionario global de operaciones."""
 #   operacionGlobal = diccionario_global_operaciones.get(symbol)
 #   if operacionGlobal:
 #       if status_terminado:
 #           operacionGlobal['ut'] = int(ut_a_devolver)
 #       else:
 #           operacionGlobal['ut'] += int(ut_a_devolver)
        
 #       if operacionGlobal['status'] != '0':
 #           operacionGlobal['status'] = '0'
            
def actualizar_diccionario_global(symbol, ut_a_devolver):
    """Actualiza el diccionario global de operaciones."""
    operacionGlobal = diccionario_global_operaciones.get(symbol)
    if operacionGlobal:
         if int(ut_a_devolver) > 0:  
            operacionGlobal['ut'] += int(ut_a_devolver)
         else:   
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
    for i, operacion in enumerate(operaciones_a_simular, start=1001):
        diccionario_operaciones_enviadas[i] = simulate_operacion_enviada(
        clOrdId=i,
        symbol=operacion['symbol'],
        status=operacion['status'],
        ut=operacion['ut'],
        user_id=user_id,
        userCuenta=userCuenta,
        accountCuenta=accountCuenta,
        saldo=saldo
        )
    for i, report in enumerate(test_cases):
        print(f'\n--- Test Case {i+1} ---')
        order_report_handler(report)
=======
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




user_id = 'apipuntillo22583398'
userCuenta = 'dpuntillo@gmail.com'
accountCuenta = '10861'
saldo = 1581539.79

diccionario_operaciones_enviadas = {
   
}

 #{'Symbol': 'MERV - XMEV - BBAR - 24hs', '_cliOrderId': 1, 'status': 'TERMINADA'},
# Simulación de diccionarios globales y operaciones enviadas
diccionario_global_operaciones = {
    'MERV - XMEV - AGRO - 24hs': {'symbol': 'MERV - XMEV - AGRO - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - ADBE - 24hs': {'symbol': 'MERV - XMEV - ADBE - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - AMD - 24hs': {'symbol': 'MERV - XMEV - AGRO - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - AVGO - 24hs': {'symbol': 'MERV - XMEV - AVGO - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - BABA - 24hs': {'symbol': 'MERV - XMEV - BABA - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - ALUA - 24hs': {'symbol': 'MERV - XMEV - ALUA - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - BBAR - 24hs': {'symbol': 'MERV - XMEV - BBAR - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - TRAN - 24hs': {'symbol': 'MERV - XMEV - TRAN - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - GILD - 24hs': {'symbol': 'MERV - XMEV - GILD - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - MELI - 24hs': {'symbol': 'MERV - XMEV - MELI - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - NVDA - 24hs': {'symbol': 'MERV - XMEV - NVDA - 24hs', 'ut': 0, 'status': '0'},
    'MERV - XMEV - WMT - 24hs': {'symbol': 'MERV - XMEV - WMT - 24hs', 'ut': 0, 'status': '0'}
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


# Escenarios de prueba
test_cases = [
    simulate_order_report(1001, 'MERV - XMEV - AGRO - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1002, 'MERV - XMEV - ADBE - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1003, 'MERV - XMEV - AMD - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1004, 'MERV - XMEV - AVGO - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1005, 'MERV - XMEV - BABA - 24hs', 'FILLED', '2024-07-18T12:01:00Z', 'Stock 10'),
    simulate_order_report(1006, 'MERV - XMEV - ALUA - 24hs', 'FILLED', '2024-07-18T12:02:00Z', 'Stock 20'),
    simulate_order_report(1007, 'MERV - XMEV - BBAR - 24hs', 'FILLED', '2024-07-18T12:03:00Z', 'Stock 30'),
    simulate_order_report(1008, 'MERV - XMEV - TRAN - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 10'),
    simulate_order_report(1009, 'MERV - XMEV - GILD - 24hs', 'FILLED', '2024-07-18T12:04:00Z', 'Stock 40'),
    simulate_order_report(1010, 'MERV - XMEV - MELI - 24hs', 'FILLED', '2024-07-18T12:05:00Z', 'Stock 50'),
    simulate_order_report(1011, 'MERV - XMEV - NVDA - 24hs', 'FILLED', '2024-07-18T12:06:00Z', 'Stock 60'),
    simulate_order_report(1012, 'MERV - XMEV - WMT - 24hs', 'FILLED', '2024-07-18T12:07:00Z', 'Stock 70'),
    simulate_order_report(1013, 'MERV - XMEV - AGRO - 24hs', 'FILLED', '2024-07-18T12:00:00Z', 'Stock 5'),
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


operaciones_a_simular = [
    {'symbol': 'MERV - XMEV - AGRO - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'SHORT', 'ut': 10, 'senial': 'closed.', 'status': '0'},
    {'symbol': 'MERV - XMEV - ADBE - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - AMD - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - AVGO - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 5, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - BABA - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 2, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - ALUA - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'LONG_', 'ut': 32, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - BBAR - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'LONG_', 'ut': 6, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - TRAN - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'LONG_', 'ut': 16, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - GILD - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - MELI - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 1, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - NVDA - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 4, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - WMT - 24hs', 'tipo_de_activo': 'CEDEAR', 'tradeEnCurso': 'LONG_', 'ut': 5, 'senial': 'OPEN.', 'status': '0'},
    {'symbol': 'MERV - XMEV - AGRO - 24hs', 'tipo_de_activo': 'ARG', 'tradeEnCurso': 'SHORT', 'ut': 5, 'senial': 'closed.', 'status': '0'},
]

# Diccionario para registrar cuántas veces se actualiza cada operación
registro_actualizaciones = {}
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
        
    # Registra cuántas veces se ha actualizado esta operación
    if clOrdId not in registro_actualizaciones:
        registro_actualizaciones[clOrdId] = 0
    registro_actualizaciones[clOrdId] += 1    
        
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
 # Verifica si la operación ya está en el estado 'TERMINADA'
    if diccionario_operaciones_enviadas.get(clOrdId) == 'TERMINADA':
        print(f"[AVISO] La operación {clOrdId} ya estaba en estado TERMINADA, se intentó actualizar nuevamente.")
        # Puedes optar por no actualizarla de nuevo, según la lógica:
        return
    # Actualiza el estado de las operaciones enviadas
    endingEnviadas = actualizar_estado_operaciones( symbol, clOrdId)    
    # Revisa las operaciones globales
    for key, operacionGlobal in diccionario_global_operaciones.items():
        if operacionGlobal['symbol'] == symbol:
            if operacionGlobal['ut'] == 0:
                # Verifica si todas las operaciones relacionadas están terminadas
                all_enviadas_validas = all(
                    operacion['status'] == 'TERMINADA'
                    for operacion in diccionario_operaciones_enviadas.values()
                    if operacion["Symbol"] == symbol
                )
                any_enviada_anterior = any(
                    operacion['status'] == 'ANTERIOR'
                    for operacion in diccionario_operaciones_enviadas.values()
                     if operacion["Symbol"] == symbol
                )
                if all_enviadas_validas and not any_enviada_anterior:
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
        
#def actualizar_diccionario_global(symbol, ut_a_devolver, status_terminado=False):
 #   """Actualiza el diccionario global de operaciones."""
 #   operacionGlobal = diccionario_global_operaciones.get(symbol)
 #   if operacionGlobal:
 #       if status_terminado:
 #           operacionGlobal['ut'] = int(ut_a_devolver)
 #       else:
 #           operacionGlobal['ut'] += int(ut_a_devolver)
        
 #       if operacionGlobal['status'] != '0':
 #           operacionGlobal['status'] = '0'
            
def actualizar_diccionario_global(symbol, ut_a_devolver):
    """Actualiza el diccionario global de operaciones."""
    operacionGlobal = diccionario_global_operaciones.get(symbol)
    if operacionGlobal:
         if int(ut_a_devolver) > 0:  
            operacionGlobal['ut'] += int(ut_a_devolver)
         else:   
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
    for i, operacion in enumerate(operaciones_a_simular, start=1001):
        diccionario_operaciones_enviadas[i] = simulate_operacion_enviada(
        clOrdId=i,
        symbol=operacion['symbol'],
        status=operacion['status'],
        ut=operacion['ut'],
        user_id=user_id,
        userCuenta=userCuenta,
        accountCuenta=accountCuenta,
        saldo=saldo
        )
    for i, report in enumerate(test_cases):
        print(f'\n--- Test Case {i+1} ---')
        order_report_handler(report)
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
