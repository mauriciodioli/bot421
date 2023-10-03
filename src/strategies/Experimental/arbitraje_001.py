from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g
import routes.instrumentosGet as instrumentosGet
from utils.db import db
from models.orden import Orden
from models.usuario import Usuario
import jwt
import json
import random
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
import strategies.estrategiaSheetWS as shWS 
import strategies.datoSheet as datoSheet 
import requests
import routes.api_externa_conexion.cuenta as cuenta

from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import pprint
import websockets
import sys

arbitraje_001 = Blueprint('arbitraje_001',__name__)

# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
# ARBITRADOR 001
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
def decime_si_es_bono(symbol_str):
    if 'AL30' in symbol_str.upper()  or 'GD30' in symbol_str.upper():
        return 1
    else:
        return 0


def calcular_costo_operacion(symbol_str, pCI, p48hs, dz, tarifa=1):
  
    # comision y derechos de mercado de acuerdo a si es bono o si es otra cosa
    # comi: 0,5% para vol operado < 5millones
    # comi: 0,25% para vol operado > 5millones < 25 millones
    # comi: 0,1% para vol operado > 25millones 
    
    
        # Calcular la comisión
    if 'AL30' in symbol_str.upper()  or 'GD30' in symbol_str.upper():
        bruto_pCI = (pCI / 100) * dz
    else:
        bruto_pCI = pCI * dz
    comisionCI = tarifa * bruto_pCI + 0.000873 * bruto_pCI
    ivaCI = 0.21 * (tarifa * bruto_pCI + 0.000873 * bruto_pCI)
    # formula del guille cutella
    # Cantidad*precio*(1+(comi + d.de mdo)*1,21)
    sub_totalCI = comisionCI + ivaCI
    
    if 'AL30' in symbol_str.upper()  or 'GD30' in symbol_str.upper():
        bruto_p48hs = (p48hs / 100) * dz
    else:
        bruto_p48hs = p48hs * dz
    
    comision48hs = tarifa * bruto_p48hs + 0.000873 * bruto_p48hs
    iva48hs = 0.21 * (tarifa * bruto_p48hs + 0.000873 * bruto_p48hs)
    sub_total48hs = comision48hs + iva48hs
    comision = sub_totalCI + sub_total48hs

    return 1.234232



    

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
    
    return p48hs, z48hs, pCI, zCI

def buscar_valores_completos_i(symbol):
    # Extraer la parte base del símbolo
    symbol_base = symbol.rsplit(' - ', 1)[0]
    
    symbol_48hs = f"{symbol_base} - 48hs"
    symbol_CI = f"{symbol_base} - CI"
    
    p48hs = symbol_data_i.get(symbol_48hs, {}).get('p48hs', 0)
    z48hs = symbol_data_i.get(symbol_48hs, {}).get('z48hs', 0)
    pCI = symbol_data_i.get(symbol_CI, {}).get('pCI', 0)
    zCI = symbol_data_i.get(symbol_CI, {}).get('zCI', 0)
    
    return p48hs, z48hs, pCI, zCI


# Esta estrategia opera desde la apertura hasta las 16.25 hs porque 16.30 cierra el contado.
def Arbitrador001(message):#**66
    # esta linea tuve que modificar en datoSheet.py
    # sheet2 = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)
    
    
    
    

    # arbitraje directo o tipico : comprar el corto vender el largo
    Symbol = message["instrumentId"]["symbol"]
    p_value = 0
    z_value = 0
    suffix = ""
    if Symbol.endswith("48hs"):
        p_value = float(message["marketData"]["BI"][0]["price"])# precio para venderlo
        z_value = message["marketData"]["BI"][0]["size"]
        suffix = "48hs"
    elif Symbol.endswith("CI"):
        p_value = float(message["marketData"]["OF"][0]["price"])# precio para comprarlo
        z_value = message["marketData"]["OF"][0]["size"]
        suffix = "CI"
    if suffix:
        update_symbol_data(Symbol, p_value, z_value, suffix)        
    
    # arbitraje inverso :  comprar el largo, vender el corto, este es mas conveniente, da plata para caucho
    p_value = 0
    z_value = 0
    suffix = ""
    if Symbol.endswith("48hs"):
        p_value = float(message["marketData"]["OF"][0]["price"])# precio para comprarlo
        z_value = message["marketData"]["OF"][0]["size"]
        suffix = "48hs"
    elif Symbol.endswith("CI"):
        p_value = float(message["marketData"]["BI"][0]["price"])# precio para venderlo
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
    DIFP = -1
    DIFPi = -1
    dz = -1
    
    # se supone que tengo que tener p48 y pCI de lo mismo, y z48,zCI de lo mismo. VERIFICAR
    p48hs, z48hs, pCI, zCI = buscar_valores_completos(Symbol)
    # se supone que tengo que tener p48 y pCI de lo mismo, y z48,zCI de lo mismo. VERIFICAR
    p48hsi, z48hsi, pCIi, zCIi = buscar_valores_completos_i(Symbol)
    
    # Verificar que ninguno de los valores sea None, cero o negativo
    if all(val is not None and val > 0 for val in [p48hs, z48hs, pCI, zCI, p48hsi, z48hsi, pCIi, zCIi]):
    # tengo que ver para que lado me conviene el arbitraje: 
    #                       C_corto -> V_largo     o    C_largo -> V_corto   ???
    #*************************************************************************************
        DIF = p48hs - pCI   # C_corto -> V_largo   si y solo si   p48hs > pCI
        if (DIF>0):         
            if (pCI != 0):
                DIFP= (DIF / pCI)*100
            dz = min(zCI, z48hs)


        DIFi = pCIi - p48hsi # C_largo -> V_corto  si y solo si   pCIi > p48hsi  
        if (DIFi>0):         
            if (p48hsi != 0):
                DIFPi= (DIFi / p48hsi)*100
            dzi = min(zCIi, z48hsi)

    #else:# Al menos uno de los valores es None, cero o negativo
    #    print("Arbitrador001: Al menos uno de los datos de entrada es invalido.")
    umbrald=0.45
    if DIFP > 0.2 and dz > 0:
        current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
        bruto_pCI=0
        bruto_p48hs=0
        comision=0
        print(current_time,"D:",Symbol[13:19]," cpraCI=", pCI, " vta48=", p48hs,DIF, "d%= {:.2f}%".format(DIFP)," dz=",dz)#, "bruto_pCI=", int(bruto_pCI), "bruto_p48hs=", int(bruto_p48hs), "bruto_gan=", int(bruto_p48hs-bruto_pCI), "comi=", int(comision))

    #if DIFPi > 1 and dzi > 0:
        #current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
        #print(current_time,"I:",Symbol[13:19]," cpra48=", p48hsi, " vtaCI=",pCIi,  DIFi,"d%= {:.2f}%".format(DIFPi)," dz=",dzi )
        
        
    original_stdout = sys.stdout     
    # Ruta completa al archivo
    file_path = 'Z:\\python\\Arb01log0928.csv'
    # Redirigir la salida estándar al archivo
    with open(file_path, 'a') as f:
        sys.stdout = f
        #"timestamp","Direccion","Ticker"," cpra", " vta", "Gan bruta %"," liquidez delta"
        if (DIFP>1.5):
            print(current_time,",D:",",",Symbol[13:19],",", pCI,",", p48hs,",",DIF,",", "{:.2f}%".format(DIFP),",",dz)
        #if (DIFPi>0.9):
            #print(current_time,",I:",",",Symbol[13:19],",", p48hsi,",", pCIi,",",DIFi,",", "{:.2f}%".format(DIFPi),",",dzi)

    # Restaurar la salida estándar original

    sys.stdout = original_stdout
        
        
        
        
        
        
    mep = 380
    #print(" FUN Arbitrador001() .")
    return mep
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
#   FIN                 ARBITRADOR 001
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************


    
@arbitraje_001.route('/arbitrador-002/', methods=['POST'])
def arbitrador_002():
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            get.accountLocalStorage = data['cuenta']
            
            get.VariableParaBotonPanico = 0
            #ContenidoSheet_list = shWS.SuscripcionDeSheet()  # <<-- aca se suscribe al mkt data
            get.pyRofexInicializada.remove_websocket_market_data_handler(get.market_data_handler_0)
            get.pyRofexInicializada.remove_websocket_order_report_handler(get.order_report_handler_0)
            get.pyRofexInicializada.add_websocket_market_data_handler(market_data_handler_arbitraje_001)
            get.pyRofexInicializada.add_websocket_order_report_handler(order_report_handler_arbitraje_001)
            
           # get.pyRofexInicializada.order_report_subscription(
           #     account=get.accountLocalStorage, 
           #     snapshot=True, 
           #     handler=order_report_handler_arbitraje_001)
            
          #  pyRofexWebSocket = get.pyRofexInicializada.init_websocket_connection(
          #      market_data_handler=market_data_handler_arbitraje_001,
          #      order_report_handler=order_report_handler_arbitraje_001,
          #      error_handler=error_handler,
          #      exception_handler=exception_handler
          #  )

            ## esta no va, trabaja con los diccionarios del bot
            ##shWS.carga_operaciones(
              ##  ContenidoSheet_list[0], 
              ##  get.accountLocalStorage, 
              ##  usuario, 
                ##correo_electronico, 
                ##ContenidoSheet_list[1])
    
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
            return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except:
            print("no pudo leer la base de datos")
    return render_template('/estrategiaOperando.html')
     








def market_data_handler_arbitraje_001(message):
   
    if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
        print("FUN market_data_handler_estrategia: message[marketData][BI] es None o está vacío")
    elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
        print("FUN market_data_handler_estrategia: message[marketData][OF] es None o está vacío")
    elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:
        print("FUN market_data_handler_estrategia: message[marketData][LA] es None o está vacío")
    else:
        #print("FUN market_data_handler_estrategia: SI HAY DATOS. ")
        Arbitrador001(message)




def order_report_handler_arbitraje_001( order_report):
        # para este arbitrador el manejo de ordenes es 
        
        
        # Obtener el diccionario de datos del reporte de orden
        order_data = order_report['orderReport']
        # Leer un valor específico del diccionario
        clOrdId = order_data['clOrdId']
        symbol = order_data['instrumentId']['symbol']
        status = order_data['status']  
        timestamp_order_report = order_data['transactTime']  
        
        print("FUN order_report_handler_test: web soket mando un reporte. ")
     
            



def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))



