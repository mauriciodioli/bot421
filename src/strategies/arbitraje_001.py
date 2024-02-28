# este viene con la cuenta madioli26@hotmail.com pass 12345678
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g
import routes.instrumentosGet as instrumentosGet
import numpy as np
from utils.common import Marshmallow, db, get
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import time
from models.orden import Orden
from models.operacionHF import OperacionHF 
from models.usuario import Usuario
import jwt
import csv
import json
import math
from math import floor
import random
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
import strategies.estrategiaSheetWS as shWS 
import strategies.datoSheet as datoSheet 
import requests
import routes.api_externa_conexion.cuenta as cuenta

from datetime import datetime, timedelta
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import pprint
import websockets
import sys
from collections import deque

arbitraje_001 = Blueprint('arbitraje_001',__name__)


# Cola para almacenar los últimos 10,000 valores
#window_size = 180 # seria media hora, porque muestrea cada 10 seg
window_size = 180 # seria media hora, porque muestrea cada 10 seg
moving_average_window = deque(maxlen=window_size)
# Inicializar el historial de spreads
# historial_spreads = {'AL': deque(maxlen=window_size), 'GD': deque(maxlen=window_size)}



arbitrador_activo = 3       # 1: Cci V48, 2: V48 Cci, 3:Ratio
miid_vg_a = 0
miid_g_ca = 0
miid_g_va = 0
miid_cg_a = 0
miid_vg_a_flag = 1
miid_g_ca_flag = 1
miid_g_va_flag = 1
miid_cg_a_flag = 1
flag_compra = False
flag_venta = False
flag_arbitraje_en_ejecucion = False
IDdelacompra = 0
IDdelaventa = 0
IDdelacompra_ = 0
IDdelaventa_ = 0
symbol_48hs =""
symbol_CI =""
symbol_48hsi =""
symbol_CIi =""

recibido_pesos_1d = False
recibido_pesos_3d = False
recibido_pesos_4d = False
recibido_pesos_5d = False
recibido_pesos_6d = False
caucion1 =0
caucion3 =0
caucion4 =0
caucion5 =0
caucion6 =0

# del arb de ratio. arb003  # **77
al30OF = 0  
al30OFz = 0
al30BID = 0
al30BIDz = 0
gd30OF = 0
gd30OFz = 0
gd30BID = 0
gd30BIDz = 0
al30_last = 0
gd30_last = 0
nALop= 0
nALop_rt = 0         # real trading # **66
ALacum= 10000
nGDop= 1000
nGDop_rt = 100       # real trading
nALop_temporal= 0
nGDop_temporal= 0
GDacum= 10000
limite_inferior = 1
limite_superior = 2000
diviciones = 0
contador1 = 0 


ticker_en_curso_cpra=""
ticker_en_curso_vta=""
ticker_en_curso=""
price_en_curso=0
price_en_curso_cpra=0
order_counter = 0
mapeo = {}
ordenes_activas = {}
inhibidos = {}
time_after_5_minutes = None
time_after_10_seconds = datetime.now() + timedelta(seconds=10)
caucion7d = 0
caucion1d = 0
order_counter2 = 0
price_factor = 0

# arbitrador ratio
AL30 = 0 
GD30 = 0






# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
# ARBITRADOR 001
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
# es el arbitrador 001 pasa que quedaron asi las etiquetas
@arbitraje_001.route('/arbitrador-002/', methods=['POST'])
def arbitrador_002():
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            get.accountLocalStorage = data['cuenta']
            get.VariableParaBotonPanico = 0
            
            # ejecuciones de setup para este arbitrador
            Cargar_Factores()# Carga diccionario de factores
            get.pyRofexInicializada.order_report_subscription(account= get.accountLocalStorage , snapshot=True,handler = order_report_handler_arbitraje_001)
  
            get.pyRofexInicializada.add_websocket_market_data_handler(market_data_handler_arbitraje_001)
            get.pyRofexInicializada.add_websocket_order_report_handler(order_report_handler_arbitraje_001)
            #get.pyRofexInicializada.remove_websocket_market_data_handler(shWS.market_data_handler_estrategia)
            

    
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
            return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except:
            print("no pudo leer la base de datos")
    
    return ''




def Acumular_volumen_Operado(symbol_str, pCI, p48hs, dz, tarifa=1):
    # acumulamos volumen operado
    return 0



def Ganancia_neta_arb(Symbol,pCI,p48hs,dz,comi,dias_tasa):
    # comision y derechos de mercado de acuerdo a si es bono o si es otra cosa
    # comi: 0,5% para vol operado < 5millones
    # comi: 0,25% para vol operado > 5millones < 25 millones
    # comi: 0,1% para vol operado > 25millones 
    #comi = 0.005
    ARANCEL = 0.5       # en %
    D_de_Mercado = 0.0803 # en %
    D_de_Mercado_bono = 0.0015 # en %
    IVA = 21  # en %
    Ganancia_neta=0
    importe_neto_cpra=0
    importe_neto_vta=0
    
    pFac = pFactor(Symbol)  # Llamar a la función y almacenar el resultado
    if pFac == 0.01:

        importe_bruto_cpra = dz * pCI * 0.01
        arancel = importe_bruto_cpra * comi
        derecho_mercado = importe_bruto_cpra * 0.000015
        iva = 0 #(arancel + derecho_mercado) * 0.21
        # la plata que voy a usar mas los costos. Me cuesta mas la compra
        importe_neto_cpra = importe_bruto_cpra + (arancel + derecho_mercado + iva)

        importe_bruto_vta = dz * p48hs * 0.01
        arancel = importe_bruto_vta * comi
        derecho_mercado = importe_bruto_vta * 0.000015
        iva = 0 #(arancel + derecho_mercado) * 0.21
        # la plata que voy a cobrar menos los costos. Recibo menos plata que el bruto
        importe_neto_vta = importe_bruto_vta - (arancel + derecho_mercado + iva)

        Ganancia_neta = importe_neto_vta - importe_neto_cpra
        # Imprimir el importe neto
        #print("Ganancia Neta", Ganancia_neta)

    elif pFac == 1:

        # Recordando que datos tengo :  pCI,p48hs,dz

        
        importe_bruto_cpra = dz * pCI
        arancel = importe_bruto_cpra * comi
        derecho_mercado = importe_bruto_cpra * 0.000803
        iva = (arancel + derecho_mercado) * 0.21
        # la plata que voy a usar mas los costos. Me cuesta mas la compra
        importe_neto_cpra = importe_bruto_cpra + (arancel + derecho_mercado + iva)

        importe_bruto_vta = dz * p48hs
        arancel = importe_bruto_vta * comi
        derecho_mercado = importe_bruto_vta * 0.000803
        iva = (arancel + derecho_mercado) * 0.21
        # la plata que voy a cobrar menos los costos. Recibo menos plata que el bruto
        importe_neto_vta = importe_bruto_vta - (arancel + derecho_mercado + iva)

        Ganancia_neta = importe_neto_vta - importe_neto_cpra
        # Imprimir el importe neto
        #print("Ganancia Neta", Ganancia_neta)


    elif pFac < 0:
        print("Error del diccionario de factores, el symbolo no figura.")
    else:
        print("Eerror del diccionario de factores")  # Esta línea maneja cualquier otro caso no especificado

    # verificae existencia de cau1d, si existe, calcular la perdida para 2d.
    #  si cau1d no existe y cau3d existe: perdida para 3d
    #  si cau3d no existe y cau4d existe: perdida para 4d
    #  si cau4d no existe y cau5d existe: perdida para 5d
    # y asi hasta 6 o 7d. No creo exista una situacion de inactividad bursatil de mas de 5 o 6 d.
    caucion = caucion7d
    perdida_tasa = (((caucion/365)*dias_tasa)/100)*importe_neto_cpra
    #print("Perdida por 48hs de tasa", perdida_tasa)
    
    # esta es la verdadera ganancia del trade
    Ganancia_Trade = Ganancia_neta - perdida_tasa 
    

    return Ganancia_Trade, perdida_tasa, importe_neto_cpra, importe_neto_vta, pFac


def Ganancia_neta_arbi(Symbol,pCI,p48hs,dz,comi,dias_tasa):
    # comision y derechos de mercado de acuerdo a si es bono o si es otra cosa
    # comi: 0,5% para vol operado < 5millones
    # comi: 0,25% para vol operado > 5millones < 25 millones
    # comi: 0,1% para vol operado > 25millones 
    #comi = 0.005
    ARANCEL = 0.5       # en %
    D_de_Mercado = 0.0803 # en %
    D_de_Mercado_bono = 0.0015 # en %
    IVA = 21  # en %
    Ganancia_neta=0
    importe_neto_cpra=0
    importe_neto_vta=0
    
    pFac = pFactor(Symbol)  # Llamar a la función y almacenar el resultado
    if pFac == 0.01:
                        # aca va el p48hs
        importe_bruto_cpra = dz * p48hs * 0.01
        arancel = importe_bruto_cpra * comi
        derecho_mercado = importe_bruto_cpra * 0.000015
        iva = 0 #(arancel + derecho_mercado) * 0.21
        # la plata que voy a usar mas los costos. Me cuesta mas la compra
        importe_neto_cpra = importe_bruto_cpra + (arancel + derecho_mercado + iva)
                        # aca va el pCI
        importe_bruto_vta = dz * pCI * 0.01
        arancel = importe_bruto_vta * comi
        derecho_mercado = importe_bruto_vta * 0.000015
        iva = 0 #(arancel + derecho_mercado) * 0.21
        # la plata que voy a cobrar menos los costos. Recibo menos plata que el bruto
        importe_neto_vta = importe_bruto_vta - (arancel + derecho_mercado + iva)

        Ganancia_neta = importe_neto_vta - importe_neto_cpra
        # Imprimir el importe neto
        #print("Ganancia Neta", Ganancia_neta)

    elif pFac == 1:

        # Recordando que datos tengo :  pCI,p48hs,dz

                        # aca va el p48hs        
        importe_bruto_cpra = dz * p48hs
        arancel = importe_bruto_cpra * comi
        derecho_mercado = importe_bruto_cpra * 0.000803
        iva = (arancel + derecho_mercado) * 0.21
        # la plata que voy a usar mas los costos. Me cuesta mas la compra
        importe_neto_cpra = importe_bruto_cpra + (arancel + derecho_mercado + iva)

        importe_bruto_vta = dz * pCI
        arancel = importe_bruto_vta * comi
        derecho_mercado = importe_bruto_vta * 0.000803
        iva = (arancel + derecho_mercado) * 0.21
        # la plata que voy a cobrar menos los costos. Recibo menos plata que el bruto
        importe_neto_vta = importe_bruto_vta - (arancel + derecho_mercado + iva)

        Ganancia_neta = importe_neto_vta - importe_neto_cpra
        # Imprimir el importe neto
        #print("Ganancia Neta", Ganancia_neta)


    elif pFac < 0:
        print("Error del diccionario de factores, el symbolo no figura.")
    else:
        print("Eerror del diccionario de factores")  # Esta línea maneja cualquier otro caso no especificado

    # verificar existencia de cau1d, si existe, calcular la GANANCIA para 2d.
    #  si cau1d no existe y cau3d existe: GANANCIA para 3d
    #  si cau3d no existe y cau4d existe: GANANCIA para 4d
    #  si cau4d no existe y cau5d existe: GANANCIA para 5d
    # y asi hasta 6 o 7d. No creo exista una situacion de inactividad bursatil de mas de 5 o 6 d.
    caucion = caucion7d
    Ganancia_tasa = (((caucion/365)*dias_tasa)/100)*importe_neto_cpra
    #perdida_tasa = 0        # en el inverso no hay perdida de tasa
    
    # esta es la verdadera ganancia del trade. La ganancia por trading mas la gan por tasa
    Ganancia_Trade = Ganancia_neta + Ganancia_tasa
    

    return Ganancia_Trade, Ganancia_tasa, importe_neto_cpra, importe_neto_vta, pFac
    



    

# Diccionario para almacenar los valores
symbol_data = {}
symbol_data_i = {}
# Función para actualizar el diccionario con nuevos datos
def update_symbol_data(symbol, p_value, z_value, suffix):
    if suffix == "48hs":
        symbol_data[symbol] = {'p48hs': p_value, 'z48hs': z_value}
    elif suffix == "CI":
        symbol_data[symbol] = {'pCI': p_value, 'zCI': z_value}

# Función para actualizar el diccionario con nuevos datos
def update_symbol_data_i(symbol, p_value, z_value, suffix):
    if suffix == "48hs":
        symbol_data_i[symbol] = {'p48hs': p_value, 'z48hs': z_value}
    elif suffix == "CI":
        symbol_data_i[symbol] = {'pCI': p_value, 'zCI': z_value}


def buscar_valores_completos(symbol):
    # Extraer la parte base del símbolo
    symbol_base = symbol.rsplit(' - ', 1)[0]
    
    symbol_48hs = f"{symbol_base} - 48hs"
    symbol_CI = f"{symbol_base} - CI"
    
    p48hs = symbol_data.get(symbol_48hs, {}).get('p48hs', 0)
    z48hs = symbol_data.get(symbol_48hs, {}).get('z48hs', 0)
    pCI = symbol_data.get(symbol_CI, {}).get('pCI', 0)
    zCI = symbol_data.get(symbol_CI, {}).get('zCI', 0)
    
    return p48hs, z48hs, symbol_48hs,pCI, zCI,symbol_CI

def buscar_valores_completos_i(symbol):
    # Extraer la parte base del símbolo
    symbol_base = symbol.rsplit(' - ', 1)[0]
    
    symbol_48hs = f"{symbol_base} - 48hs"
    symbol_CI = f"{symbol_base} - CI"
    
    p48hs = symbol_data_i.get(symbol_48hs, {}).get('p48hs', 0)
    z48hs = symbol_data_i.get(symbol_48hs, {}).get('z48hs', 0)
    pCI = symbol_data_i.get(symbol_CI, {}).get('pCI', 0)
    zCI = symbol_data_i.get(symbol_CI, {}).get('zCI', 0)
    
    return p48hs, z48hs,symbol_48hs, pCI, zCI,symbol_CI




def generate_ws_cli_ord_id(ticker):
    global order_counter
    order_counter += 1001+random.randint(1, 100000)
    #timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return order_counter





def update_moving_average_and_bollinger_bands_c(new_value):
    # Añadir el nuevo valor a la cola
    moving_average_window.append(new_value)
    
    # Inicializar el diccionario de bandas de Bollinger
    bollinger_bands = {'ready': False}

    # Comprobar si hay suficientes datos
    if len(moving_average_window) < window_size:
        bollinger_bands.update({
            'MA': 0,
            'Upper_1SD': 0,
            'Lower_1SD': 0,
            'Upper_1.5SD': 0,
            'Lower_1.5SD': 0,
            'Upper_2SD': 0,
            'Lower_2SD': 0,
            'ready': False
        })

        return bollinger_bands

    # Si hay suficientes datos, se procede a calcular
    moving_average = np.mean(moving_average_window)
    std_dev = np.std(moving_average_window)

    # Completar las bandas de Bollinger y actualizar 'ready' a True
    bollinger_bands.update({
        'MA': moving_average,
        'Upper_1SD': moving_average + std_dev,
        'Lower_1SD': moving_average - std_dev,
        'Upper_1.5SD': moving_average + 1.5 * std_dev,
        'Lower_1.5SD': moving_average - 1.5 * std_dev,
        'Upper_2SD': moving_average + 2 * std_dev,
        'Lower_2SD': moving_average - 2 * std_dev,
        'ready': True
    })

    return bollinger_bands




def evaluar_ratio_con_bandas(ratio, bandas):
    # Evaluar para valores positivos
    if bandas['Upper_1SD'] <= ratio < bandas['Upper_1.5SD']:
        return 1
    elif bandas['Upper_1.5SD'] <= ratio < bandas['Upper_2SD']:
        return 2
    elif bandas['Upper_2SD'] <= ratio :
        return 3
    elif bandas['Lower_1.5SD'] < ratio <= bandas['Lower_1SD']:
        return -1
    elif bandas['Lower_2SD'] < ratio <= bandas['Lower_1.5SD']:
        return -2
    elif ratio <= bandas['Lower_2SD']:
        return -3

    # Si no se cumple ninguna de las condiciones anteriores, devuelve 0
    return 0

#"""

"""
#def update_estadistica_spread(al30BID, al30OF, gd30BID, gd30OF, historial_spreads):
def update_estadistica_spread(al30BID, al30OF, gd30BID, gd30OF):
    # Calcular spreads actuales
    spreadAL = al30OF - al30BID
    spreadGD = gd30OF - gd30BID

    # Añadir los nuevos spreads al historial (deque)
    historial_spreads['AL'].append(spreadAL)
    historial_spreads['GD'].append(spreadGD)

    # Verificar si se han acumulado suficientes valores para calcular estadísticas
    if len(historial_spreads['AL']) < 9999 or len(historial_spreads['GD']) < 9999:
        return False

    # Calcular la media y la desviación estándar de los spreads usando NumPy
    media_spreadAL = np.mean(historial_spreads['AL'])
    media_spreadGD = np.mean(historial_spreads['GD'])
    desv_std_spreadAL = np.std(historial_spreads['AL'])
    desv_std_spreadGD = np.std(historial_spreads['GD'])

    # Establecer límites basados en la desviación estándar
    limite_superior_AL = media_spreadAL + 3 * desv_std_spreadAL
    limite_inferior_AL = media_spreadAL - 3 * desv_std_spreadAL
    limite_superior_GD = media_spreadGD + 3 * desv_std_spreadGD
    limite_inferior_GD = media_spreadGD - 3 * desv_std_spreadGD

    # Verificar si el último spread está dentro de los límites
    return (limite_inferior_AL <= spreadAL <= limite_superior_AL) and \
           (limite_inferior_GD <= spreadGD <= limite_superior_GD)
"""


def Options_scanner_01(p48hs, z48hs, symbol_48hs, p48hsi, z48hsi,symbol_48hsi,current_time):

    if(al30_last>0):
        ratio = 100*((gd30_last-al30_last)/al30_last)
    else:
        ratio = 0   # para que sea mas facil el filtrado

def sindecimalesA_a_G(limite_inferior, limite_superior ):
    # cuantos AL vendo tal que pueda comprar una cantidad lo mas cercana 
    # posible a un entero de GDs, dentro de los limites estipulados
    global nALop_rt
    global nGDop_rt 
    global gd30OF
    global al30BID
    
    decimal = 2 # un valor para que se reemplaze siempre
    for nALop_iter in range(limite_inferior, limite_superior + 1):
        
        nGDop_temporal2 = nALop_iter* (al30BID/gd30OF)
        #nALop_temporal2 = nGDop_iter * (gd30BID / al30OF)
        decimal2 = nGDop_temporal2 - int(nGDop_temporal2 )
        if decimal2 < decimal : 
            decimal = decimal2
            nALop_rt = nALop_iter
            nGDop_rt = nGDop_temporal2 
    
    return nALop_rt,nGDop_rt 

def sindecimalesG_a_A(limite_inferior, limite_superior ):
    # cuantos GD vendo tal que pueda comprar una cantidad lo mas cercana 
    # posible a un entero de ALs, dentro de los limites estipulados
    global nALop_rt
    global nGDop_rt 
    global gd30BID
    global al30OF
    decimal = 2 # un valor para que se reemplaze siempre
    for nGDop_iter in range(limite_inferior, limite_superior + 1):

        nALop_temporal2 = nGDop_iter * (gd30BID / al30OF)
        decimal2 = nALop_temporal2 - int(nALop_temporal2)
        if decimal2 < decimal : 
            decimal = decimal2
            nALop_rt = nALop_temporal2
            nGDop_rt = nGDop_iter
            indice = nGDop_iter 
    
    return nALop_rt,nGDop_rt


def particionarAG(diviciones=4, parteini=0.8, partefin=1):
            # aca tengo que convertir ALs a GDs

    
    if (diviciones==0):
        return 0    

    
    parte = nALop // diviciones
    resto = nALop - parte * diviciones
    parcialgd = 0
    parcialal = 0
    #print(f"{contador1} g<a_ parte:{parte} resto:{resto}")
    # vender nALop comprar nGDop
    for i in range(diviciones):
        [nALa,nGDa] = sindecimalesA_a_G(int(0.8*parte),int(parte) )  # me va dar un nGDop-->nALop 
        parcialgd = parcialgd + nGDa # suma parcial de cuantos voy haciendo
        parcialal = parcialal + nALa # suma parcial de cuantos voy haciendo
        restogd = nGDop - parcialgd # cuantos me faltan
        restoal = nALop - parcialal # cuantos me faltan
        print(f"{contador1} g<a_{i} nALa:{nALa} nGDa:{nGDa:.3f}")
        #print(f"{contador1} g>a_{i} nGDa:{nGDa} parcialgd :{parcialgd } nALa:{nALa} parcialal :{parcialal } ")
    
    [nALa,nGDa] = sindecimalesA_a_G(restoal,restoal)
    print(f"{contador1} g<a_{diviciones} nALa:{nALa} nGDa:{nGDa:.3f} ")
    resto2al = nALa
    resto2gd = nGDa
    
    controlgd = int(parcialgd) + int(resto2gd)
    controlal = int(parcialal) + int(resto2al)
    if (controlgd >=nGDop):
        print (f"Conversion Correcta: control de GDs:{controlgd:.3f}  nGDop:{nGDop}" )
    else:
        print (f"*****    Conversion INCorrecta: control de GDs:{controlgd :.3f}  nGDop:{nGDop}")
        completar = 1- (nGDa- int(nGDa))
        agregar = gd30OF*0.01*completar 
        nGDa_final = math.ceil(nGDa)
        print (f"*****    completar con {completar :.3f} GDs, o sea {agregar:.3f} $ para comprar {nGDa_final} GDs")

    
    
    
    return 0
    


def particionarGA(diviciones=4, parteini=0.8, partefin=1):
    
    global al30OF

    if (diviciones==0):
        return 0    

    #print(f"particionarGA parteini{parteini} diviciones:{diviciones}")
    
    parte = nGDop // diviciones 
    #resto = nGDop - parte * diviciones 
    parcialgd = 0
    parcialal = 0
    #print(f"{contador1} g>a_ parte:{parte} resto:{resto}")
    # vender nGDop  comprar nALop
    for i in range(diviciones):
        [nALa,nGDa] = sindecimalesG_a_A(int(parteini*parte),int(partefin*parte) )  # me va dar un nGDop-->nALop 
        parcialgd = parcialgd + nGDa # suma parcial de cuantos voy haciendo
        parcialal = parcialal + nALa # suma parcial de cuantos voy haciendo
        restogd = nGDop - parcialgd # cuantos me faltan
        #restoal = nALop - parcialal # cuantos me faltan
        print(f"{contador1} g>a_{i} nGDa:{nGDa} nALa:{nALa:.3f}")

    
    [nALa,nGDa] = sindecimalesG_a_A(restogd,restogd)
    print(f"{contador1} g>a_{diviciones} nGDa:{nGDa} nALa:{nALa:.3f} ")
    #resto2al = nALa
    #controlgd = int(parcialgd) + int(restogd)
    controlal = int(parcialal) + int(nALa)
    #if(contador1==257):
    #    print(f"contador257: controlal{controlal} = parcialal{parcialal} + nALa{nALa}")
    
    if (controlal >=nALop):
        print (f"Conversion Correcta: control de ALs:{controlal:.3f}  nALop:{nALop}" )
        return 1
    else:
        print (f"*****    Conversion INCorrecta: control de ALs:{controlal:.3f}  nALop:{nALop}")
        completar = 1- (nALa - int(nALa))
        agregar = al30OF*0.01*completar 
        nALa_final = math.ceil(nALa)
        print (f"*****    completar con {completar :.3f} ALs, o sea {agregar:.3f} $ para comprar {nALa_final} ALs")
        return -1
        

    return 0

import csv

def leer_y_asignar_variables(ruta_archivo):
    # Crear un diccionario para almacenar los valores leídos
    variables = {}

    # Intentar abrir el archivo y leer los datos
    try:
        with open(ruta_archivo, mode='r') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                for clave, valor in fila.items():
                    # Convertir a tipo adecuado si es necesario
                    if valor.replace('.', '', 1).isdigit():
                        valor = float(valor)
                    variables[clave] = valor
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_archivo}")

    # Imprimir y devolver las variables
    #for clave, valor in variables.items():
    #    print(f"{clave}: {valor}")

    return variables


def escribir_variables(ruta_archivo, diccionario):
    try:
        with open(ruta_archivo, mode='w', newline='') as archivo:
            if diccionario:
                campos = diccionario.keys()
                escritor = csv.DictWriter(archivo, fieldnames=campos)

                escritor.writeheader()
                escritor.writerow(diccionario)
            else:
                print("El diccionario está vacío.")
    except IOError:
        print(f"No se pudo escribir en el archivo: {ruta_archivo}")


def Ratio_de_bonos_scanner_02(symbol_AL48h_para_op,symbol_GD48h_para_op):
    global AL30
    global GD30
    global al30OF
    global al30OFz 
    global al30BID 
    global al30BIDz 
    global gd30OF 
    global gd30OFz
    global gd30BID
    global gd30BIDz
    global al30_last
    global gd30_last
    global time_after_10_seconds
    global miid_vg_a
    global miid_g_ca
    global miid_g_va
    global miid_cg_a
    global miid_vg_a_flag
    global miid_g_ca_flag
    global miid_g_va_flag
    global miid_cg_a_flag
    
    global nALop
    global nALop_rt         # real trading  
    global nALop_temporal
    global ALacum

    global nGDop
    global nGDop_rt                # real trading
    global nGDop_temporal
    global GDacum
    global limite_inferior
    global limite_superior
    global contador1
    global diviciones

    #print(" ",end='\r')
    #print("r","al30BID",al30BID,"al30BIDz",al30BIDz,"al30OF",al30OF,"al30OFz",al30OFz, end='')  # chequeado
    #print(" gd30BID", gd30BID, "gd30BIDz", gd30BIDz, "gd30OF", gd30OF, "gd30OFz", gd30OFz)      # chequeado
    #print(" ",end='\r')

    #;{al30OF};{al30OFz};{al30BID};{al30BIDz};{gd30OF};{gd30OFz};{gd30BID};{gd30BIDz}

    # el OFFER esta arriba y el BID esta abajo
    #   al30OF      al30OFz     al30_last           gd30OF      gd30OFz     
    #   al30BID     al30BIDz    gd30_last           gd30BID     gd30BIDz
    

    ruta_archivo = 'Z:\\python\\comunicacion.csv'
    
    
    output_string = ""  # Inicializar la cadena de salida
    output_string2 = ""  # Inicializar la cadena de salida
    output_string3 = ""  # Inicializar la cadena de salida
    comip = 0.0025    # 0.25% porque intrad esta bonif una de las op
    comip = comip *2  # es el doble por ser gd->$->al
    # **88
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Señal GD ----> AL
    # Conversión de GD a AL de test: del bid al offer
    plata =(gd30BID/100)*nGDop
    comi = plata*comip
    nALop_temporal = int(plata / (al30OF/100) if (al30OF>0) else 0)
    #print("\b\b\b\b....", end='')
    if nALop_temporal > nALop:  # Señal GD ----> AL

        #leemos archivo de comunicacion
        #nALop,ALacum,nGDop,GDacum,Flag_Operar
        variables = leer_y_asignar_variables(ruta_archivo)
        # Imprimir las variables de comunicacion
        if "nALop" in variables:
            #print(f"nALop: {variables['nALop']}")
            nALop=variables['nALop']
        if "ALacum" in variables:
            #print(f"ALacum: {variables['ALacum']}")
            ALacum = variables['ALacum']
        if "nGDop" in variables:
            #print(f"nGDop: {variables['nGDop']}")
            nGDop=variables['nGDop']
        if "GDacum" in variables:
            #print(f"GDacum: {variables['GDacum']}")
            GDacum = variables['GDacum']
        if "Flag_Operar" in variables:
            #print(f"Flag_Operar: {variables['Flag_Operar']}")
            Flag_Operar = variables['Flag_Operar']

        #print("\b\b\b\b****")#, end='')
        nALop = nALop_temporal # Actualizar 
        contador1+= 1
        contador = 0
        parteini = 0.8
        partefin = 1
        #particionarGA(diviciones, parteini,partefin)


        # verifico que tengo almacenados bonos para vender
        # alerta: aca tambien verificar si los sizes de bid y offer coinciden con la op que quiero hacer
        # si entra, vende GDs y compra ALs, sino no opera.
        
        #   al30OF      al30OFz     al30_last           gd30OF      gd30OFz     
        #   al30BID     al30BIDz    gd30_last           gd30BID     gd30BIDz
        # aca tengo que convertir GDs a ALs. gd30BIDz a al30OFz
        #nALop_previo = nALop        # por si tengo que suspender la operacion
        #nGDop_previo = nGDop
       
        if  GDacum >= nGDop and nGDop<gd30BIDz and nALop<al30OFz and miid_g_ca_flag==1 and miid_vg_a_flag==1 and int(variables['Flag_Operar'])>0: #66
            miid_vg_a_flag=1    # cerado de los flag de opercion exitosa
            miid_g_ca_flag=1    # cerar si se opera, si no se opera dejar en 1
            # aca operar 
            # vender gd 
            ticker_en_curso_vta_ga = symbol_GD48h_para_op
            cantidad_arb01_ga = nGDop
            precio_vta_ga = gd30BID
            miid_vg_a = generate_ws_cli_ord_id(ticker_en_curso_vta_ga)
            tipo_ga = get.pyRofexInicializada.OrderType.LIMIT
            #orden_ga = OperacionHF(ticker=ticker_en_curso_vta_ga,accion='venta',size=cantidad_arb01_ga,price=precio_vta_ga,ws_client_order_id=miid_vg_a, order_type=tipo_ga )
            #orden_ga.enviar_orden()
            # comprar al
            ticker_en_curso_cpra_ga = symbol_AL48h_para_op
            cantidad_arb01_ga = nALop
            precio_cpra_ga = al30OF
            miid_g_ca = generate_ws_cli_ord_id(ticker_en_curso_cpra_ga)
            tipo_ga = get.pyRofexInicializada.OrderType.LIMIT
            #orden_ga = OperacionHF(ticker=ticker_en_curso_cpra_ga, accion='comprar',size=cantidad_arb01_ga,  price=precio_cpra_ga , ws_client_order_id=miid_g_ca, order_type=tipo_ga )
            #orden_ga.enviar_orden()
            # despues imprimo y aviso lo que hice
            print(f"\n\n{contador1} +++++++++++++++++++++  Señal GD ----> AL !!! +++++++++++++++++++++ ")
            print(f"nALop: {variables['nALop']}")
            print(f"ALacum: {variables['ALacum']}")
            print(f"nGDop: {variables['nGDop']}")
            print(f"GDacum: {variables['GDacum']}")
            print(f" vg==>ca:... nALop:{nALop} nGDop:{nGDop} ")
            current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
            print(f"{current_time} Si se puede operar GD->AL: ")
            print(f"GDacum {GDacum} >= nGDop {nGDop }")
            print(f"nGDop {nGDop} < gd30BIDz {gd30BIDz }")
            print(f"nALop {nALop} < al30OFz {al30OFz}")
            ALacum = int(ALacum + nALop)     
            GDacum = int(GDacum - nGDop)
            variables['ALacum'] = ALacum
            variables['GDacum'] = GDacum
            variables['nALop'] = nALop
            variables['nGDop'] = nGDop
            #variables['Flag_Operar'] = 0    # no opero mas hasta que me autoricen
            escribir_variables(ruta_archivo, variables)

            #ENCABEZADO n; time;Flag;signal;nAL;precioAL;zALs;nGD;precioGD;zGDs;ALacum;GDacum;al30BIDz;al30BID;al30OF;al30OFz;gd30BIDz;gd30BID;gd30OF;gd30OFz
            flag_operacion = 1
            print(f"{contador1} vg==>ca__c{nALop} ALs a {al30OF:.2f}__v{nGDop} GDs a {gd30BID:.2f} ALacum:{ALacum} GDacum:{GDacum}")
            mensaje2 = f"{contador1}; {current_time};{flag_operacion}; vg==>ca;{nALop};{al30OF:.2f}; {al30OFz:.0f};{nGDop};{gd30BID:.2f};{gd30BIDz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
        else:
            print("\n\n ----------------- Señal que no se pudo operar GD->AL: -----------------")
            print(f"{contador1} vg==>ca:... nALop:{nALop} nGDop:{nGDop} ")
            if (GDacum < nGDop ): 
                print(f"No tengo suficientes GDs {GDacum} para operar nGDop {nGDop }")
            if (nGDop > gd30BIDz ): 
                print(f"nGDop {nGDop} No es < gd30BIDz {gd30BIDz }")
            if (nALop > al30OFz): 
                print(f"nALop {nALop} No es < al30OFz {al30OFz}")
            if(int(variables['Flag_Operar'])==0):
                print(f" variables['Flag_Operar'] es {variables['Flag_Operar']}")

            flag_operacion = 0
            current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
            print(f"{contador1} vg==>ca No se pudo operar.")
            mensaje2 = f"{contador1}; {current_time};{flag_operacion}; vg==>ca;{nALop};{al30OF:.2f}; {al30OFz:.0f};{nGDop};{gd30BID:.2f};{gd30BIDz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida

            
            #nALop = nALop_previo        # se suspende la operacion
            #nGDop = nGDop_previo
        
        """    
        if (flag_operacion==1):
            #if  GDacum >= nGDop and nGDop<gd30BIDz and nALop<al30OFz and int(variables['Flag_Operar'])>0: #66
            #   al30OF      al30OFz     al30_last           gd30OF      gd30OFz     
            #   al30BID     al30BIDz    gd30_last           gd30BID     gd30BIDz

            #ENCABEZADO n; time;Flag;signal;nAL;precioAL;zALs;nGD;precioGD;zGDs;ALacum;GDacum;al30BIDz;al30BID;al30OF;al30OFz;gd30BIDz;gd30BID;gd30OF;gd30OFz
            print(f"{contador1} vg==>ca__c{nALop} ALs a {al30OF:.2f}__v{nGDop} GDs a {gd30BID:.2f} ALacum:{ALacum} GDacum:{GDacum}")
            mensaje2 = f"{contador1}; {current_time};{flag_operacion}; vg==>ca;{nALop};{al30OF:.2f}; {al30OFz:.0f};{nGDop};{gd30BID:.2f};{gd30BIDz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
        else:
            print(f"{contador1} vg==>ca No se pudo operar.")
            mensaje2 = f"{contador1}; {current_time};{flag_operacion}; vg==>ca;{nALop};{al30OF:.2f}; {al30OFz:.0f};{nGDop};{gd30BID:.2f};{gd30BIDz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
        """
        
    else:    
        pass
        #mensaje2 = f"{current_time}; _-_ ;{nALop_temporal} ;{nALop};{nGDop_temporal} ;{ nGDop};{al30OF};{al30OFz};{al30BID};{al30BIDz};{gd30OF};{gd30OFz};{gd30BID};{gd30BIDz} \n "
        #output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
        #print("n", end='')
        #print("g>a...nop", end='')
        #output_string += ";g>a:...;"
                
    
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Señal AL ----> GD
    # Conversión de AL a GD de test: del bid al offer
    plata =(al30BID/100)*nALop
    comi = plata*comip
    nGDop_temporal = int(plata / (gd30OF/100) if (gd30OF>0) else 0)
    #print("\b\b\b\b----", end='')
    if nGDop_temporal > nGDop:  # Señal AL ----> GD
        #leemos archivo de comunicacion
        variables = leer_y_asignar_variables(ruta_archivo)
        # Imprimir las variables de comunicacion
        if "nALop" in variables:
            #print(f"nALop: {variables['nALop']}")
            nALop=variables['nALop']
        if "ALacum" in variables:
            #print(f"ALacum: {variables['ALacum']}")
            ALacum = variables['ALacum']
        if "nGDop" in variables:
            #print(f"nGDop: {variables['nGDop']}")
            nGDop=variables['nGDop']
        if "GDacum" in variables:
            #print(f"GDacum: {variables['GDacum']}")
            GDacum = variables['GDacum']
        if "Flag_Operar" in variables:#print(f"Flag_Operar: {variables['Flag_Operar']}")
            Flag_Operar = variables['Flag_Operar']

        #print("\b\b\b\b****")#, end='')
        contador1+= 1
        nGDop = nGDop_temporal  # Actualizar
        #print("a", end='')
        contador = 0
        parteini = 0.8
        partefin = 1
        #particionarAG(diviciones, parteini,partefin)

        # verifico que tengo almacenados bonos para vender
        # alerta: aca tambien verificar si los sizes de bid y offer coinciden con la op que quiero hacer
        # si entra, vende ALs y compra GDs, sino no opera.
        

        #   al30OF      al30OFz     gd30OF      gd30OFz     
        #   al30BID     al30BIDz    gd30BID     gd30BIDz
        # aca tengo que convertir ALs a GDs. gd30BIDz a al30OFz
        #nALop_previo = nALop        # por si tengo que suspender la operacion
        #nGDop_previo = nGDop
        #if GDacum >= nGDop and nGDop<gd30BIDz and nALop<al30OFz:
        #Señal AL ----> GD
        if ALacum >= nALop and nGDop<gd30OFz and nALop<al30BIDz and miid_g_va_flag==1 and miid_cg_a_flag ==1 and int(variables['Flag_Operar'])>0:
            miid_g_va_flag = 1 # si activo las op aca cerar
            miid_cg_a_flag = 1
            # aca operar 
            # vender AL
            ticker_en_curso_vta_ga = symbol_AL48h_para_op
            cantidad_arb01_ga = nALop
            precio_vta_ga = al30BID
            miid_g_va = generate_ws_cli_ord_id(ticker_en_curso_vta_ga)
            tipo_ga = get.pyRofexInicializada.OrderType.LIMIT
            #orden_ga = OperacionHF(ticker=ticker_en_curso_vta_ga,accion='venta',size=cantidad_arb01_ga,price=precio_vta_ga,ws_client_order_id=miid_g_va, order_type=tipo_ga )
            #orden_ga.enviar_orden()
            # comprar GD
            ticker_en_curso_cpra_ga = symbol_GD48h_para_op
            cantidad_arb01_ga = nGDop
            precio_cpra_ga = gd30OF
            miid_cg_a = generate_ws_cli_ord_id(ticker_en_curso_cpra_ga)
            tipo_ga = get.pyRofexInicializada.OrderType.LIMIT
            #orden_ga = OperacionHF(ticker=ticker_en_curso_cpra_ga, accion='comprar',size=cantidad_arb01_ga,  price=precio_cpra_ga , ws_client_order_id=miid_cg_a, order_type=tipo_ga )
            #orden_ga.enviar_orden()
            # despues imprimo y aviso lo que hice
            print(f"\n\n{contador1} +++++++++++++++++++++  Señal AL ----> GD !!! +++++++++++++++++++++ ")
            print(f"nALop: {variables['nALop']}")
            print(f"ALacum: {variables['ALacum']}")
            print(f"nGDop: {variables['nGDop']}")
            print(f"GDacum: {variables['GDacum']}")
            print(f"va==>cg:... nALop:{nALop} nGDop:{nGDop} ")#{time}
            current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
            print(f"{current_time} Si se puede operar AL->GD: ")
            print(f"ALacum {ALacum} >= nALop{nALop}")
            print(f"nGDop {nGDop} < gd30OFz {nGDop}")
            print(f"nALop {nALop} < al30BIDz {al30BIDz}")
            ALacum = int(ALacum - nALop)
            GDacum = int(GDacum + nGDop)
            variables['ALacum'] = ALacum
            variables['GDacum'] = GDacum
            variables['nALop'] = nALop
            variables['nGDop'] = nGDop
            #variables['Flag_Operar'] = 0    # no opero mas hasta que me autoricen
            
            escribir_variables(ruta_archivo, variables)
            flag_operacion = 1
            print(f"{contador1} va==>cg __c{nGDop} GDs a {gd30OF:.2f} __v{nALop} ALs a {al30BID:.2f} ALacum:{ALacum} GDacum:{GDacum}")# total:{totalB}")
            #ENCABEZADO n; time;Flag;signal;nAL;precioAL;zALs;nGD;precioGD;zGDs;ALacum;GDacum;al30BIDz;al30BID;al30OF;al30OFz;gd30BIDz;gd30BID;gd30OF;gd30OFz
            mensaje2 = f"{contador1}; {current_time};{flag_operacion};va==>cg;{nALop};{al30BID:.2f}; {al30BIDz:.0f};{nGDop};{gd30OF:.2f};{gd30OFz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string3 += mensaje2  # Agregar el mensaje a la cadena de salida

            
        else:
            print("\n\n ----------------- Señal que no se pudo operar AL->GD: -----------------")
            print(f"{contador1} va==>cg:... nALop:{nALop} nGDop:{nGDop} ")#{time}
            if (ALacum < nALop): 
                print(f"No tengo suficientes ALs {ALacum} para operar nALop {nALop}")
            if (nGDop > gd30OFz): 
                print(f"nGDop {nGDop} NO es < gd30OFz {gd30OFz}")
            if (nALop > al30BIDz): 
                print(f"nALop {nALop} NO es < al30BIDz {al30BIDz}")
            if(int(variables['Flag_Operar'])==0):
                print(f" variables['Flag_Operar'] es {variables['Flag_Operar']}")

            flag_operacion = 0
            current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
            mensaje2 = f"{contador1}; {current_time};{flag_operacion};va==>cg;{nALop};{al30BID:.2f}; {al30BIDz:.0f};{nGDop};{gd30OF:.2f};{gd30OFz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string3 += mensaje2  # Agregar el mensaje a la cadena de salida
            print(f"{contador1} va==>cg No se pudo operar.")
            
            
            
            #nALop = nALop_previo        # se suspende la operacion
            #nGDop = nGDop_previo


        """
        if (flag_operacion==1):
            print(f"{contador1} va==>cg __c{nGDop} GDs a {gd30OF:.2f} __v{nALop} ALs a {al30BID:.2f} ALacum:{ALacum} GDacum:{GDacum}")# total:{totalB}")
            #ENCABEZADO n; time;Flag;signal;nAL;precioAL;zALs;nGD;precioGD;zGDs;ALacum;GDacum;al30BIDz;al30BID;al30OF;al30OFz;gd30BIDz;gd30BID;gd30OF;gd30OFz
            mensaje2 = f"{contador1}; {current_time};{flag_operacion};va==>cg;{nALop};{al30BID:.2f}; {al30BIDz:.0f};{nGDop};{gd30OF:.2f};{gd30OFz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
        else:
            mensaje2 = f"{contador1}; {current_time};{flag_operacion};va==>cg;{nALop};{al30BID:.2f}; {al30BIDz:.0f};{nGDop};{gd30OF:.2f};{gd30OFz:.0f};{ALacum};{GDacum};{al30BIDz};{al30BID};{al30OF};{al30OFz};{gd30BIDz};{gd30BID};{gd30OF};{gd30OFz} "
            output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
            print(f"{contador1} va==>cg No se pudo operar.")
        """ 

    else:
        pass
        #mensaje2 = f"{current_time}; _-_ ;{nALop_temporal} ;{nALop};{nGDop_temporal} ;{ nGDop};{al30OF};{al30OFz};{al30BID};{al30BIDz};{gd30OF};{gd30OFz};{gd30BID};{gd30BIDz} "
        #output_string2 += mensaje2  # Agregar el mensaje a la cadena de salida
        #print("n", end='')
        #print("a>g:...nop", end='')
        #output_string += ";a>g:...;"

    #return nGDop
    

    
    print("*", end='')                  # aviso que esta vivo despues de toda la logica


    #ENCABEZADO n; time;Flag;signal;nAL;precioAL;zALs;nGD;precioGD;zGDs;ALacum;GDacum;al30BIDz;al30BID;al30OF;al30OFz;gd30BIDz;gd30BID;gd30OF;gd30OFz
    # setup
    #   LogOperaciones_6feb.csv y la del 7feb
    #   nALop,ALacum,nGDop,GDacum,_1,_2,Flag_Operar,str_1,str_2
    #   1080,5000,1000,5000,0.0,0.0,1.0,,
    # setup
    #   LogOperaciones_8feb.csv
    #   nALop,ALacum,nGDop,GDacum,_1,_2,Flag_Operar,str_1,str_2
    #   1080,0,1000,2000,0.0,0.0,1.0,,

    if output_string2 != "":
        original_stdout = sys.stdout     
        file_ = 'Z:\\python\\LogOperaciones_15feb.csv'
        with open(file_, 'a') as f:# Redirigir la salida estándar al archivo
            sys.stdout = f
            print(            output_string2            )
            sys.stdout = original_stdout

    if output_string3 != "":
        original_stdout = sys.stdout     
        file_ = 'Z:\\python\\LogOperaciones_15feb.csv'
        with open(file_, 'a') as f:# Redirigir la salida estándar al archivo
            sys.stdout = f
            print(            output_string3            )
            sys.stdout = original_stdout
            
    return nGDop
"""        
    if output_string != "":
        original_stdout = sys.stdout     
        file_ = 'Z:\\python\\ratio_20240117.csv'
        with open(file_, 'a') as f:# Redirigir la salida estándar al archivo
            sys.stdout = f
            print(
            output_string
            )
            sys.stdout = original_stdout

"""    
    
    
#return nGDop







def ArbitradorRatio(message):#
    #print(message)
    #mensaje = message
    # esta linea tuve que modificar en datoSheet.py
    # sheet2 = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)
    global flag_compra
    global flag_venta
    global flag_arbitraje_en_ejecucion
    global IDdelacompra 
    global IDdelaventa 
    global IDdelacompra_ 
    global IDdelaventa_ 
    global symbol_48hs
    global symbol_CI
    global symbol_48hsi
    global symbol_CIi
    global ticker_en_curso_cpra
    global ticker_en_curso_vta
    global price_en_curso
    global price_en_curso_cpra
    global recibido_pesos_1d
    global recibido_pesos_3d 
    global recibido_pesos_4d 
    global recibido_pesos_5d 
    global recibido_pesos_6d 
    global caucion7d
    global order_counter2
    global price_factor
    global caucion1 
    global caucion3 
    global caucion4 
    global caucion5 
    global caucion6 
    global time_after_5_minutes
    global time_after_10_seconds

    global al30OF 
    global al30OFz 
    global al30BID 
    global al30BIDz 
    global gd30OF 
    global gd30OFz
    global gd30BID
    global gd30BIDz
    global al30_last
    global gd30_last
    

    
    file_path = 'Z:\\python\\Arb_log_240103.csv'
    
    # variables basicas
    Symbol = message["instrumentId"]["symbol"]
    p_value = 0
    z_value = 0
    suffix = ""
    
    #Definir los límites de tiempo
    #start_time_1105 = datetime.now().replace(hour=11, minute=5, second=0, microsecond=0)
    #end_timeCI_1630 = datetime.now().replace(hour=16, minute=30, second=0, microsecond=0)

    #end_time_17 = datetime.now().replace(hour=16, minute=59, second=0, microsecond=0)
    
    # Extraer la parte base del símbolo
    #symbol_base = Symbol.rsplit(' - ', 1)[0]
    #symbol_48hs = f"{symbol_base} - 48hs"
    #symbol_CI = f"{symbol_base} - CI"
    
    #if "MERV - XMEV - AL30 - 48hs" in symbol_48hs:
    symbol_AL48h_para_op = "MERV - XMEV - AL30 - 48hs"
    if "MERV - XMEV - AL30 - 48hs" in Symbol:
        #al30_last = p_last48hs
        al30OF = float(message["marketData"]["OF"][0]["price"])#p48hsi        # precio para comprarlo
        al30OFz = float(message["marketData"]["OF"][0]["size"])#z48hsi
        al30BID = float(message["marketData"]["BI"][0]["price"])#p48hs # precio para venderlo
        al30BIDz = float(message["marketData"]["BI"][0]["size"])#z48hs
        #symbol_base = Symbol.rsplit(' - ', 1)[0]
        #symbol_AL48h_para_op = symbol_base
        
    
    symbol_GD48h_para_op="MERV - XMEV - GD30 - 48hs"
    if "MERV - XMEV - GD30 - 48hs" in Symbol:
        #gd30_last = p_last48hs
        gd30OF = float(message["marketData"]["OF"][0]["price"])#p48hsi        # precio para venderlo
        gd30OFz = float(message["marketData"]["OF"][0]["size"])#z48hsi
        gd30BID = float(message["marketData"]["BI"][0]["price"])#p48hs          # precio para venderlo
        gd30BIDz = float(message["marketData"]["BI"][0]["size"])#z48hs
        #symbol_base = Symbol.rsplit(' - ', 1)[0]
        #symbol_GD48h_para_op = symbol_base

    # **77  Ratios 
    #current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
    ratio = Ratio_de_bonos_scanner_02(symbol_AL48h_para_op,symbol_GD48h_para_op)  # H_FREQ SCANNER


            
    mep = 380
        
    return mep







# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
#   FIN                 ARBITRADOR RATIO
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
    
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
#                    ARBITRADOR 001
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
# Esta estrategia opera desde la apertura hasta las 16.25 hs porque 16.30 cierra el contado.
def Arbitrador001(message):#
    #print(message)
    #mensaje = message
    # esta linea tuve que modificar en datoSheet.py
    # sheet2 = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)
    global flag_compra
    global flag_venta
    global flag_arbitraje_en_ejecucion
    global IDdelacompra 
    global IDdelaventa 
    global IDdelacompra_ 
    global IDdelaventa_ 
    global symbol_48hs
    global symbol_CI
    global symbol_48hsi
    global symbol_CIi
    global ticker_en_curso_cpra
    global ticker_en_curso_vta
    global price_en_curso
    global price_en_curso_cpra
    global recibido_pesos_1d
    global recibido_pesos_3d 
    global recibido_pesos_4d 
    global recibido_pesos_5d 
    global recibido_pesos_6d 
    global caucion7d
    global order_counter2
    global price_factor
    global caucion1 
    global caucion3 
    global caucion4 
    global caucion5 
    global caucion6 
    global time_after_5_minutes
    global time_after_10_seconds

    global al30OF 
    global al30OFz 
    global al30BID 
    global al30BIDz 
    global gd30OF 
    global gd30OFz
    global gd30BID
    global gd30BIDz
    global al30_last
    global gd30_last
    

    
    file_path = 'Z:\\python\\Arb_log_240103.csv'
    
    # variables basicas
    Symbol = message["instrumentId"]["symbol"]
    p_value = 0
    z_value = 0
    suffix = ""
    
    # Definir los límites de tiempo
    start_time_1105 = datetime.now().replace(hour=11, minute=5, second=0, microsecond=0)
    end_timeCI_1630 = datetime.now().replace(hour=16, minute=30, second=0, microsecond=0)
    end_time_17 = datetime.now().replace(hour=16, minute=59, second=0, microsecond=0)

    
    
    
    #if "PESOS - 1D" in Symbol:
    #    caucion7d = float(message["marketData"]["OF"][0]["price"])# precio para venderlo
    # marcamos una variable de estado
    if "PESOS - 1D" in Symbol:
        recibido_pesos_1d = True
        caucion1 = float(message["marketData"]["OF"][0]["price"])# precio para venderlo
    elif "PESOS - 3D" in Symbol:
        recibido_pesos_3d = True
        caucion3 = float(message["marketData"]["OF"][0]["price"])# precio para venderlo
    elif "PESOS - 4D" in Symbol:
        recibido_pesos_4d = True
        caucion4 = float(message["marketData"]["OF"][0]["price"])# precio para venderlo
    elif "PESOS - 5D" in Symbol:
        recibido_pesos_5d = True
        caucion5 = float(message["marketData"]["OF"][0]["price"])# precio para venderlo
    elif "PESOS - 6D" in Symbol:
        recibido_pesos_6d = True
        caucion6 = float(message["marketData"]["OF"][0]["price"])# precio para venderlo

    # Lógica para determinar dias_tasa
    if recibido_pesos_1d:
        dias_tasa = 2# si existe este, mañana dia habil, pero liquidacion 48hs, asi que son dos dias
        caucion7d = caucion1
    elif recibido_pesos_3d:
        dias_tasa = 3# si existe este y los anteriores no: mañana sab=1d, dom=2d, lun=3d.  
        caucion7d = caucion3
    elif recibido_pesos_4d:
        dias_tasa = 4# si existe este y los anteriores no: mañana sab=1d, dom=2d, lun=3d, mar=4d  
        caucion7d = caucion4
    elif recibido_pesos_5d:
        dias_tasa = 5# ...
        caucion7d = caucion5
    elif recibido_pesos_6d:
        dias_tasa = 6# ...
        caucion7d = caucion6
    else:
        dias_tasa = 2



    if Symbol.endswith("48hs"):
        p_last48hs = float(message["marketData"]["LA"]["price"])# precio last no es lista es dicc
        p_value = float(message["marketData"]["BI"][0]["price"])# precio para venderlo
        Precio_BI_48 = p_value
        z_value = message["marketData"]["BI"][0]["size"]
        suffix = "48hs"
    elif Symbol.endswith("CI"):
        p_lastCI = float(message["marketData"]["LA"]["price"])# precio last no es lista es dicc
        p_value = float(message["marketData"]["OF"][0]["price"])# precio para comprarlo
        Precio_OF_CI = p_value
        z_value = message["marketData"]["OF"][0]["size"]
        suffix = "CI"
    if suffix:
        update_symbol_data(Symbol, p_value, z_value, suffix)        
    
    

    # arbitraje inverso :  comprar el largo, vender el corto, este es mas conveniente, da plata para caucho
    # pero hay que ser tenendor 
    p_value = 0
    z_value = 0
    suffix = ""
    if Symbol.endswith("48hs"):
        p_value = float(message["marketData"]["OF"][0]["price"])# precio para comprarlo
        Precio_OF_48 = p_value
        z_value = message["marketData"]["OF"][0]["size"]
        suffix = "48hs"
    elif Symbol.endswith("CI"):
        p_value = float(message["marketData"]["BI"][0]["price"])# precio para venderlo
        Precio_BI_CI = p_value
        z_value = message["marketData"]["BI"][0]["size"]
        suffix = "CI"
    if suffix:
        update_symbol_data_i(Symbol, p_value, z_value, suffix)        



    pCI=0       # precio del CI
    zCI=0       # zise del CI 
    p48hs=0     # ...
    z48hs=0      
    pCIi=0      # precio del CI arbitraje inverso
    zCIi=0      # ...
    p48hsi=0
    z48hsi=0      
    DIF = -1    # Inicializar DIF para evitar errores si no se actualiza
    DIFi = -1
    DIFP = -1
    DIFPi = -1
    dz = -1
    

    # se supone que tengo que tener p48 y pCI de lo mismo, y z48,zCI de lo mismo. VERIFICAR
    p48hs, z48hs, symbol_48hs, pCI, zCI, symbol_CI = buscar_valores_completos(Symbol)
    # se supone que tengo que tener p48 y pCI de lo mismo, y z48,zCI de lo mismo. VERIFICAR
    p48hsi, z48hsi,symbol_48hsi, pCIi, zCIi,symbol_CIi = buscar_valores_completos_i(Symbol)
    
    
    current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
    
    if "MERV - XMEV - AL30 - 48hs" in symbol_48hs:
        al30_last = p_last48hs
        al30OF = float(message["marketData"]["OF"][0]["price"])#p48hsi        # precio para comprarlo
        al30OFz = float(message["marketData"]["OF"][0]["size"])#z48hsi
        al30BID = float(message["marketData"]["BI"][0]["price"])#p48hs # precio para venderlo
        al30BIDz = float(message["marketData"]["BI"][0]["size"])#z48hs
        
    
    if "MERV - XMEV - GD30 - 48hs" in symbol_48hs:
        gd30_last = p_last48hs
        gd30OF = float(message["marketData"]["OF"][0]["price"])#p48hsi        # precio para venderlo
        gd30OFz = float(message["marketData"]["OF"][0]["size"])#z48hsi
        gd30BID = float(message["marketData"]["BI"][0]["price"])#p48hs          # precio para venderlo
        gd30BIDz = float(message["marketData"]["BI"][0]["size"])#z48hs

    # H_FREQ BONOS SCANER Y OPTIONS SCANNER 
    # estan en desarrollo por ahora comentados Mauricio, no les des bola
    # **77  Ratios 
    # ratio = Ratio_de_bonos_scanner_02(current_time)  # H_FREQ SCANNER
    current_time_check = datetime.now()
    if time_after_10_seconds is not None and current_time_check >= time_after_10_seconds:
        #ratio = Ratio_de_bonos_scanner_01(current_time)
        #Options_scanner_01(p48hs, z48hs, symbol_48hs, p48hsi, z48hsi,symbol_48hsi,current_time)
        time_after_10_seconds = datetime.now() + timedelta(seconds=10)  # inicializo contador de 10 seg
    
    
    # Verificar que ninguno de los valores sea None, cero o negativo
    if all(val is not None and val > 0 for val in [p48hs, z48hs, pCI, zCI, caucion7d]):
        DIF = p48hs - pCI   # C_corto -> V_largo   si y solo si   p48hs > pCI
        if (DIF>0):         
            if (pCI != 0):
                DIFP= (DIF / pCI)*100
            dz = min(zCI, z48hs)
    
    
    if all(val is not None and val > 0 for val in [p48hsi, z48hsi, pCIi, zCIi, caucion7d]):
        DIFi = pCIi - p48hsi # C_largo -> V_corto  si y solo si   pCIi > p48hsi  
        if (DIFi>0):         
            if (p48hsi != 0):
                DIFPi= (DIFi / p48hsi)*100
            dzi = min(zCIi, z48hsi)

    precios_coherentes_flag01 = 0
    if Symbol.endswith("48hs"):
        if (Precio_OF_48>Precio_BI_48) :
            precios_coherentes_flag01 = 1
    elif Symbol.endswith("CI"):
        if (Precio_OF_CI>Precio_BI_CI) :
            precios_coherentes_flag01 = 1
    
    #*********************************************************
    # tengo que ver para que lado me conviene el arbitraje: 
    # C_corto -> V_largo     o    C_largo -> V_corto   ???
    #*********************************************************
    # C_corto -> V_largo    ?
    
    # 11:35 empieza el trading, colocar un control
    # 16:30 se termina el trading, colocar un control
    if DIFP > 1 and dz > 0 and precios_coherentes_flag01>0 :                 # aca se filtra mucho pero igual no se sabe si conviene
        print(".", end='') # punto para saber que esta vivo
        
        #print("Dir: vol acum:",order_counter2, end='')
        #"""    
            

        current_time_check = datetime.now()
        if time_after_5_minutes is not None and current_time_check >= time_after_5_minutes:
            inhibidos.clear()    # Limpiar el diccionario de inhibidos
            time_after_5_minutes = None


        cantidad_arb01 = math.ceil(0.1 * dz)  # el 10% pero paso a valor entero
        if cantidad_arb01 < 1:
            cantidad_arb01 = 1

        total = cantidad_arb01*pCI            # el volumen en $ no supera un umbral
        #print("cantidad_arb01 10%",cantidad_arb01,"total",total)
        # Ajusta cantidad_arb01 si total es mayor a 10000
        if total > 50000:
            cantidad_arb01 = math.ceil(10000 / pCI)   # entero
            if cantidad_arb01 < 1:
                cantidad_arb01 = 1


        
        #[Ganancia_n_arb,per_tasa, imp_neto_cpra, imp_neto_vta, price_factor] = Ganancia_neta_arb(Symbol,pCI,p48hs,dz,0.005)
        # 0.5% es 0.005                0.25% es 0.0025          0.1% es 0.001
        [Ganancia_n_arb,per_tasa, imp_neto_cpra, imp_neto_vta, price_factor] = Ganancia_neta_arb(Symbol,pCI,p48hs,cantidad_arb01,0.001,dias_tasa)
        #print("Gn->", Ganancia_n_arb)


        
        cadena_op = "__D"
        if Ganancia_n_arb > 0 and symbol_CI not in inhibidos and symbol_48hs not in inhibidos and not flag_arbitraje_en_ejecucion:
            cadena_op = "opD"
        
        original_stdout = sys.stdout     
        #ile_path = 'Z:\\python\\Arb01log231122.csv'
        with open(file_path, 'a') as f:# Redirigir la salida estándar al archivo
            sys.stdout = f
            print(
            current_time, ";", 
            Symbol[13:19], ";", 
            cadena_op, ";", 
            "{:.2f}".format(price_factor).replace('.', ','), ";", 
            "{:.2f}".format(pCI).replace('.', ','), ";", 
            "{:.2f}".format(p48hs).replace('.', ','), ";", 
            "{:.2f}".format(DIF).replace('.', ','), ";", 
            "{:.2f}%".format(DIFP).replace('.', ','), ";", 
            "{:.2f}".format(dz).replace('.', ','), ";", 
            "{:.2f}".format(cantidad_arb01).replace('.', ','), ";", 
            "{:.2f}".format(caucion7d).replace('.', ','), ";",
            "{:.2f}".format(dias_tasa).replace('.', ','), ";",
            "{:.2f}".format(per_tasa).replace('.', ','), ";", 
            "{:.2f}".format(imp_neto_cpra).replace('.', ','), ";", 
            "{:.2f}".format(imp_neto_vta).replace('.', ','), ";", 
            "{:.2f}".format(Ganancia_n_arb).replace('.', ','), ";",
            "{:.2f}".format(order_counter2).replace('.', ',')
            )
            sys.stdout = original_stdout
        

        if Ganancia_n_arb > 0 and order_counter2 < 300000 and symbol_CI not in inhibidos and symbol_48hs not in inhibidos and not flag_arbitraje_en_ejecucion:
        #if True:  
            #66
            ticker_en_curso_cpra = symbol_CI
            ticker_en_curso_vta = symbol_48hs
            
            #print(current_time,"D",Symbol,"F",price_factor,"pCI", pCI, "p48", p48hs,DIF, "d%= {:.2f}%".format(DIFP),"z",dz, "c7d",caucion7d,"pt",per_tasa,"inc", imp_neto_cpra,"inv",imp_neto_vta, "Gn", Ganancia_n_arb)

            # Crear y enviar la compra. Con esto comienza a trabajar el order report
            miid = generate_ws_cli_ord_id(Symbol)
            tipo = get.pyRofexInicializada.OrderType.MARKET
                    
            #print(current_time,"D",Symbol[13:19],"Pci",pCI, "P48", p48hs,DIF, "d%= {:.2f}%".format(DIFP),"z",dz,"cantidad_arb01",cantidad,"Gn", Ganancia_n_arb)
            print(current_time,"D",Symbol[13:19],"d%= {:.2f}%".format(DIFP),"Dias tasa",dias_tasa, "Tasa",caucion7d,"Perd. Tasa:",per_tasa,"Gan neta:", Ganancia_n_arb)
            
            # Condición para comprobar si la hora actual está en el rango permitido
            current_time_check = datetime.now()
            if (start_time_1105 <= current_time_check <= end_timeCI_1630):
                # **44  # rango 11:35 a 16:30
                pass
                """
                flag_arbitraje_en_ejecucion=True
                orden_ = OperacionHF(ticker=ticker_en_curso_cpra, accion='comprar',size=cantidad_arb01,  price=pCI , ws_client_order_id=miid, order_type=tipo )
                orden_.enviar_orden()
                """
            else:
                pass
                #print("Arbitrador01 Fuera de Horario.")
            
            #ordenes_activas[miid] = orden_  # Almacenar la orden en el diccionario
            IDdelacompra = miid
            ticker_en_curso_cpra = Symbol
            price_en_curso_cpra = pCI
            price_en_curso = p48hs


            

    #
    #           ARBITRAJE INVERSO       *****************************************************************
    #
    elif DIFPi > 1 and dzi > 0 and precios_coherentes_flag01>0 :                 # aca se filtra mucho pero igual no se sabe si conviene            
        print("i", end='')
        #print("Inv: vol acum:",order_counter2)
        current_time_check = datetime.now()
        if time_after_5_minutes is not None and current_time_check >= time_after_5_minutes:
            inhibidos.clear()    # Limpiar el diccionario de inhibidos
            time_after_5_minutes = None

        current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
        #[Ganancia_n_arb,per_tasa, imp_neto_cpra, imp_neto_vta, price_factor] = Ganancia_neta_arb(Symbol,pCI,p48hs,dz,0.005)
        [Ganancia_n_arb,per_tasa, imp_neto_cpra, imp_neto_vta, price_factor] = Ganancia_neta_arbi(Symbol,pCIi,p48hsi,1,0.00025,dias_tasa)
        #print("Gn->", Ganancia_n_arb)


        #"""
        cadena_op = "__I"
        if Ganancia_n_arb > 0 and symbol_CIi not in inhibidos and symbol_48hsi not in inhibidos and not flag_arbitraje_en_ejecucion:
            cadena_op = "opI"
        
        original_stdout = sys.stdout     
        #ile_path = 'Z:\\python\\Arb01log231122.csv'
        with open(file_path, 'a') as f:# Redirigir la salida estándar al archivo
            sys.stdout = f
            print(
            current_time, ";", 
            Symbol[13:19], ";", 
            cadena_op, ";", 
            "{:.2f}".format(price_factor).replace('.', ','), ";", 
            "{:.2f}".format(pCIi).replace('.', ','), ";", 
            "{:.2f}".format(p48hsi).replace('.', ','), ";", 
            "{:.2f}".format(DIFi).replace('.', ','), ";", 
            "{:.2f}%".format(DIFPi).replace('.', ','), ";", 
            "{:.2f}".format(dzi).replace('.', ','), ";", 
            "{:.2f}".format(caucion7d).replace('.', ','), ";",
            "{:.2f}".format(dias_tasa).replace('.', ','), ";",
            "{:.2f}".format(per_tasa).replace('.', ','), ";", 
            "{:.2f}".format(imp_neto_cpra).replace('.', ','), ";", 
            "{:.2f}".format(imp_neto_vta).replace('.', ','), ";", 
            "{:.2f}".format(Ganancia_n_arb).replace('.', ','), ";",
            "{:.2f}".format(order_counter2).replace('.', ',')
            )
            sys.stdout = original_stdout
        #"""
        
        if Ganancia_n_arb > 0 and symbol_CIi not in inhibidos and symbol_48hsi not in inhibidos and not flag_arbitraje_en_ejecucion:
        #if True:  
        # aca hay que consultar una lista de los activos en cartera y cuanta cantidad de cada uno, 
        
            
            
            ticker_en_curso_cpra = symbol_48hsi
            ticker_en_curso_vta = symbol_CIi

            
            current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
        
            #print(current_time,"I",Symbol[13:19],"pCI", pCIi, "p48", p48hsi,DIFi, "d%= {:.2f}%".format(DIFPi),"z",dzi, "c7d",caucion7d,"pt",per_tasa,"inc", imp_neto_cpra,"inv",imp_neto_vta, "Gn", Ganancia_n_arb)
            #print(current_time,"I",Symbol[13:19],"d%= {:.2f}%".format(DIFPi), "c7d",caucion7d,"Gan Taza:",per_tasa,"Gan neta:", Ganancia_n_arb)
            #print(current_time,"I",Symbol[13:19],"d%= {:.2f}%".format(DIFP),"Dias tasa",dias_tasa, "Tasa",caucion7d,"Gan Tasa:",per_tasa,"Gan neta:", Ganancia_n_arb)

            # Crear y enviar la compra. Con esto comienza a trabajar el order report
            miid = generate_ws_cli_ord_id(Symbol)
            tipo = get.pyRofexInicializada.OrderType.MARKET
            
            # **44
            """
            #flag_arbitraje_en_ejecucion=True
            #orden_ = OperacionHF(ticker=ticker_en_curso_cpra, accion='comprar',size=1,  price=pCI , ws_client_order_id=miid, order_type=tipo )
            #orden_.enviar_orden()
            """
            
            #ordenes_activas[miid] = orden_  # Almacenar la orden en el diccionario
            IDdelacompra = miid
            ticker_en_curso_cpra = Symbol
            price_en_curso_cpra = p48hsi 
            price_en_curso = pCIi


            



        #"""
        
        
        
        #"""
            
            
            
    mep = 380
        
    return mep







# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
#   FIN                 ARBITRADOR 001
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
def Cargar_Factores():
        repuesta_listado_instrumento = get.pyRofexInicializada.get_detailed_instruments()
        listado_instrumentos = repuesta_listado_instrumento['instruments']

        
        for instrumento in listado_instrumentos:
            sec_desc = instrumento['securityDescription']
            price_factor = instrumento['priceConvertionFactor']
            mapeo[sec_desc] = price_factor


def pFactor(Simbolo):
    return mapeo.get(Simbolo, -1)#  si no llega a estar el simbolo adentro del diccionario, devuelve -1


    





def market_data_handler_arbitraje_001(message):
    #print(message)
    
    #precio = float(message["marketData"]["OF"][0]["price"])
    #current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
    #symbol = message["instrumentId"]["symbol"]
    #orden_ = OperacionHF(ticker=symbol, accion='comprar', size=1, price=precio, order_type=get.pyRofexInicializada.OrderType.MARKET)
    #orden_.enviar_orden()
    #print(current_time, "FUN market data handler_arbitraje_001: Simbolo",symbol, "precio",precio)
    
    if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
        #print(current_time, "[BI] vacio. Simbolo",symbol)
        pass
    elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
        #print(current_time, "[OF] vacio.",symbol)
        pass
    #elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:
     #   print("FUN market data handler_arbitraje_001: message[marketData][LA] es None o está vacío")
    else:
        print("FUN market_data_handler_estrategia: SI HAY DATOS. ")
        #Arbitrador001(message)
        #ArbitradorRatio(message)




def append_order_report_to_csv(report, rutaORH):
    with open(rutaORH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Comprobar si el archivo está vacío para escribir las cabeceras
        file.seek(0)
        if file.tell() == 0:
            headers = []
            for key, value in report.items():
                if isinstance(value, dict):
                    for sub_key in value.keys():
                        headers.append(f"{key}_{sub_key}")
                else:
                    headers.append(key)
            writer.writerow(headers)
        
        # Escribir los valores
        values = []
        for key, value in report.items():
            if isinstance(value, dict):
                for sub_value in value.values():
                    values.append(sub_value)
            else:
                values.append(value)
        writer.writerow(values)

def print_order_report(report):
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
            
# ****************************************************************************************
#   ORDER REPORT HANDLER
# ****************************************************************************************
def order_report_handler_arbitraje_001( order_report): 
#"""
    global arbitrador_activo
    global flag_compra
    global flag_venta
    global flag_arbitraje_en_ejecucion
    global IDdelacompra
    global IDdelaventa 

    global miid_vg_a
    global miid_g_ca
    global miid_g_va
    global miid_cg_a
    global miid_vg_a_flag
    global miid_g_ca_flag
    global miid_g_va_flag
    global miid_cg_a_flag



    global IDdelacompra_
    global IDdelaventa_
    global symbol_48hs
    global symbol_CI
    global symbol_48hsi
    global symbol_CIi
    global ticker_en_curso_cpra
    global ticker_en_curso_vta
    global price_en_curso
    global price_en_curso_cpra
    global caucion7d
    global time_after_5_minutes
    global order_counter2
    global price_factor


    current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
    print(current_time, "Order_report_handler_arbitraje_001")
    #print(order_report)
    #print_order_report(order_report)  # para chequer
    
    order_data = order_report['orderReport']

    # Ruta del archivo CSV
    rutaORH = 'Z:\\python\\operacionesORH_01.csv'
    append_order_report_to_csv(order_report, rutaORH)
    # Verifica si 'clOrdId' está en order_data
    if 'clOrdId' in order_data:
        clOrdID = order_data['clOrdId']
    else:
        clOrdID = -1    # Manejo del caso en que no existe

    
    if 'wsClOrdId' in order_data:
        ws_Cliordid = order_data['wsClOrdId']        
    else:
        ws_Cliordid = -1    # Manejo del caso en que no existe
    
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']
    precio = order_data['price']
    cantidad = order_data['orderQty']
    #status = order_report.get('status', None) # es otro metodo de hacer lo mismo pero  no larga exeption sino none
    timestamp_order_report = order_data['transactTime']

    
    if int(ws_Cliordid)>-1:
        if int(ws_Cliordid) == IDdelacompra:
            clOrdID_num = int(clOrdID) if isinstance(clOrdID, str) else clOrdID # si es cadena
            if clOrdID_num>-1:
                IDdelacompra_ = order_data['clOrdId']
        elif int(ws_Cliordid) == IDdelaventa:
            clOrdID_num = int(clOrdID) if isinstance(clOrdID, str) else clOrdID # si es cadena
            if clOrdID_num>-1:
                IDdelaventa_ = order_data['clOrdId']
        elif int(ws_Cliordid) == miid_vg_a:
            clOrdID_num = int(clOrdID) if isinstance(clOrdID, str) else clOrdID # si es cadena
            if clOrdID_num>-1:
                miid_vg_a_id = order_data['clOrdId']
        elif int(ws_Cliordid) == miid_g_ca:
            clOrdID_num = int(clOrdID) if isinstance(clOrdID, str) else clOrdID # si es cadena
            if clOrdID_num>-1:
                miid_g_ca_id = order_data['clOrdId']
        elif int(ws_Cliordid) == miid_g_va:
            clOrdID_num = int(clOrdID) if isinstance(clOrdID, str) else clOrdID # si es cadena
            if clOrdID_num>-1:
                miid_g_va_id = order_data['clOrdId']
        elif int(ws_Cliordid) == miid_cg_a:
            clOrdID_num = int(clOrdID) if isinstance(clOrdID, str) else clOrdID # si es cadena
            if clOrdID_num>-1:
                miid_cg_a_id = order_data['clOrdId']
    

    # **88
    # Estados de una orden: "NEW", "REJECTED","EXPIRED","PARTIALLY_FILLED", "FILLED", "CANCELLED", y "PENDING_NEW".
    if status: # si no está vacía o nula 
        if  status == "PENDING_NEW":# Se está procesando pero aún no ha sido aceptada en el mercado.
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado PENDING_NEW.")
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado PENDING_NEW.")
            else:
                print(f"Orden desconocida {clOrdID} estado PENDING_NEW.")
        elif status == "NEW":# Esto significa que la orden está en el libro de órdenes pero aún no se ha ejecutado.
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado NEW.")
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado NEW.")
            else:
                print(f"Orden desconocida {clOrdID} estado NEW.")
        elif status == "REJECTED":
            inhibidos[symbol] = True                    # <<< a la lista de inhibidos
            time_after_5_minutes = datetime.now() + timedelta(minutes=5)    # inicializo contador de 5 min
            flag_arbitraje_en_ejecucion = False         # puedo rehabilitar el arb ya que este papel sera evitado.
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado REJECTED.")
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado REJECTED.")
            else:
                print(f"Orden desconocida {clOrdID} estado REJECTED.")
        elif status == "EXPIRED":
            # **55
            inhibidos[symbol] = True                    # <<< a la lista de inhibidos
            time_after_5_minutes = datetime.now() + timedelta(minutes=5)    # inicializo contador de 5 min
            flag_arbitraje_en_ejecucion = False         # puedo rehabilitar el arb ya que este papel sera evitado.
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado REJECTED.")
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado REJECTED.")
            else:
                print(f"Orden desconocida {clOrdID} estado REJECTED.")
        elif status == "PARTIALLY_FILLED":
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado PARTIALLY_FILLED.")
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado PARTIALLY_FILLED.")
            else:
                print(f"Orden desconocida {clOrdID} estado PARTIALLY_FILLED.")
        elif status == "FILLED":
            if (arbitrador_activo==3): # **99
                print(f"Orden de compra {clOrdID} estado FILLED.")
                if int(clOrdID) == int(miid_vg_a_id):
                    print(f"Orden de venta de GDs estado FILLED.")
                    miid_vg_a_flag = 1
                elif int(clOrdID) == int(miid_g_ca_id):
                    print(f"Orden de compra de ALs estado FILLED.")
                    miid_g_ca_flag = 1
                elif int(clOrdID) == int(miid_g_va_id):
                    print(f"Orden de venta de ALs estado FILLED.")
                    miid_g_va_flag = 1
                elif int(clOrdID) == int(miid_cg_a_id):
                    print(f"Orden de compra de GDs estado FILLED.")
                    miid_cg_a_flag = 1
                
                
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado FILLED.")
                if (arbitrador_activo==1):
                    # Crear y enviar la venta
                    miid = generate_ws_cli_ord_id(ticker_en_curso_vta)#66
                    tipo = get.pyRofexInicializada.OrderType.MARKET # **22
                    orden_ = OperacionHF(ticker=ticker_en_curso_vta, accion='venta',size=cantidad,  price=price_en_curso , ws_client_order_id=miid, order_type=tipo )
                    orden_.enviar_orden()
                    IDdelaventa = miid
                    order_counter2 = order_counter2 + price_factor*precio*cantidad # cuanto volumen voy operando?
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado FILLED.")
                if (arbitrador_activo==1):
                    order_counter2 = order_counter2 + price_factor*precio*cantidad # cuanto volumen voy operando?
                    flag_arbitraje_en_ejecucion = False
                    IDdelacompra=0
                    IDdelaventa=0
                    IDdelacompra_=0
                    IDdelaventa_=0
            else:
                print(f"Orden desconocida {clOrdID} estado FILLED.")
        elif status == "CANCELLED":
            inhibidos[symbol] = True                    # <<< a la lista de inhibidos
            time_after_5_minutes = datetime.now() + timedelta(minutes=5)    # inicializo contador de 5 min
            flag_arbitraje_en_ejecucion = False         # puedo rehabilitar el arb ya que este papel sera evitado.
            if int(clOrdID) == int(IDdelacompra_):
                print(f"Orden de compra {clOrdID} estado CANCELLED.")
            elif int(clOrdID) == int(IDdelaventa_):
                print(f"Orden de venta {clOrdID} estado CANCELLED.")
            else:
                print(f"Orden desconocida {clOrdID} estado CANCELLED.")
        else:
            print(f"Estado desconocido {status} para la orden {clOrdID}.")
            inhibidos[symbol] = True                    # <<< a la lista de inhibidos
            time_after_5_minutes = datetime.now() + timedelta(minutes=5)    # inicializo contador de 5 min
            flag_arbitraje_en_ejecucion = False         # puedo rehabilitar el arb ya que este papel sera evitado.

    else:
        print(f"Estado invalido contiene {status} . Arbitrador en Pausa.")
    
#"""
    
     
            



def error_handler(message):
    print("********************* error_handler: {0}".format(message))
  
def exception_error(message):
    print("********************* exception_error: {0}".format(message))  

def exception_handler(e):
    print("********************* exception_handler: {0}".format(e.msg))

# ****************************************************************************************
#   FIN                 ORDER REPORT HANDLER
# ****************************************************************************************



