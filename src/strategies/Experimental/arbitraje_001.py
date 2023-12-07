from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,g
import routes.instrumentosGet as instrumentosGet
from utils.common import Marshmallow, db, get
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import time
from models.orden import Orden
from models.operacionHF import OperacionHF 
from models.usuario import Usuario
import jwt
import json
import random
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

flag_compra = False
flag_venta = False
flag_arbitraje_en_ejecucion = False
IDdelacompra = 0
IDdelaventa = 0
IDdelacompra_ = 0
IDdelaventa_ = 0
symbol_48hs =""
symbol_CI =""

ticker_en_curso_cpra=""
ticker_en_curso_vta=""
ticker_en_curso=""
price_en_curso=0
order_counter = 0
mapeo = {}
ordenes_activas = {}
caucion7d = {}
caucion1d = {}

# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
# ARBITRADOR 001
# ****************************************************************************************
# ****************************************************************************************
# ****************************************************************************************
# es el arbitrador001 pasa que quedaron asi las etiquetas
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



def Ganancia_neta_arb(Symbol,pCI,p48hs,dz): # **33
    # comision y derechos de mercado de acuerdo a si es bono o si es otra cosa
    # comi: 0,5% para vol operado < 5millones
    # comi: 0,25% para vol operado > 5millones < 25 millones
    # comi: 0,1% para vol operado > 25millones 
    
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
        arancel = importe_bruto_cpra * 0.005
        derecho_mercado = importe_bruto_cpra * 0.000015
        iva = 0 #(arancel + derecho_mercado) * 0.21
        # la plata que voy a usar mas los costos. Me cuesta mas la compra
        importe_neto_cpra = importe_bruto_cpra + (arancel + derecho_mercado + iva)

        importe_bruto_vta = dz * p48hs * 0.01
        arancel = importe_bruto_vta * 0.005
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
        arancel = importe_bruto_cpra * 0.005
        derecho_mercado = importe_bruto_cpra * 0.000803
        iva = (arancel + derecho_mercado) * 0.21
        # la plata que voy a usar mas los costos. Me cuesta mas la compra
        importe_neto_cpra = importe_bruto_cpra + (arancel + derecho_mercado + iva)

        importe_bruto_vta = dz * p48hs
        arancel = importe_bruto_vta * 0.005
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

    
    caucion = caucion7d["caucion7d"]
    perdida_tasa = (((caucion/365)*2)/100)*importe_neto_cpra
    #print("Perdida por 48hs de tasa", perdida_tasa)
    
    # esta es la verdadera ganancia del trade
    Ganancia_Trade = Ganancia_neta - perdida_tasa 
    

    return Ganancia_Trade, perdida_tasa, importe_neto_cpra, importe_neto_vta, pFac
    



    

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
    
    symbol_48hs = f"{symbol_base} - 48hs"# **22
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


# Esta estrategia opera desde la apertura hasta las 16.25 hs porque 16.30 cierra el contado.


def Arbitrador001(message):#
    print(message)
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



    
    
    # aca el codigo tiene que fijarse si existe PESOS - 1D, si no existe, usar PESOS - 7D, si no existe PESOS - 30D
    if "PESOS - 7D" in Symbol:
        caucion7d["caucion7d"] = float(message["marketData"]["OF"][0]["price"])# precio para venderlo

    #if "PESOS - 1D" in Symbol:
    #    caucion1d["caucion1d"] = float(message["marketData"]["OF"][0]["price"])# precio para venderlo
    

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
    # pero hay que ser tenendor 
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
    DIFi = -1
    DIFP = -1
    DIFPi = -1
    dz = -1
    

    # se supone que tengo que tener p48 y pCI de lo mismo, y z48,zCI de lo mismo. VERIFICAR
    p48hs, z48hs, symbol_48hs, pCI, zCI, symbol_CI = buscar_valores_completos(Symbol)
    # se supone que tengo que tener p48 y pCI de lo mismo, y z48,zCI de lo mismo. VERIFICAR
    p48hsi, z48hsi,symbol_48hsi, pCIi, zCIi,symbol_CIi = buscar_valores_completos_i(Symbol)
    
    # Verificar que ninguno de los valores sea None, cero o negativo
    if all(val is not None and val > 0 for val in [p48hs, z48hs, pCI, zCI]):
        DIF = p48hs - pCI   # C_corto -> V_largo   si y solo si   p48hs > pCI
        if (DIF>0):         
            if (pCI != 0):
                DIFP= (DIF / pCI)*100
            dz = min(zCI, z48hs)

    
    if all(val is not None and val > 0 for val in [p48hsi, z48hsi, pCIi, zCIi]):
        DIFi = pCIi - p48hsi # C_largo -> V_corto  si y solo si   pCIi > p48hsi  
        if (DIFi>0):         
            if (p48hsi != 0):
                DIFPi= (DIFi / p48hsi)*100
            dzi = min(zCIi, z48hsi)

    
    #*********************************************************
    # tengo que ver para que lado me conviene el arbitraje: 
    # C_corto -> V_largo     o    C_largo -> V_corto   ???
    #*********************************************************
    
    
    # C_corto -> V_largo    ?
    if DIFP > 1 and dz > 0:                 # aca se filtra mucho pero igual no se sabe si conviene
        
        [Ganancia_n_arb,per_tasa, imp_neto_cpra, imp_neto_vta, price_factor] = Ganancia_neta_arb(Symbol,pCI,p48hs,dz)
        print("Gn->", Ganancia_n_arb)

        #if Ganancia_n_arb>-300 and not flag_arbitraje_en_ejecucion and price_factor==1:
        #if Ganancia_n_arb>-300 and not flag_arbitraje_en_ejecucion:
        if True:
            
            ticker_en_curso_cpra = symbol_CI
            ticker_en_curso_vta = symbol_48hs

            flag_arbitraje_en_ejecucion=True
            current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
            #print(current_time,"D:",Symbol[13:19],"pF",price_factor," cpraCI=", pCI, " vta48=", p48hs,DIF, "d%= {:.2f}%".format(DIFP)," dz=",dz, "cau7d",caucion7d["caucion7d"],"pt",per_tasa,"inc", imp_neto_cpra,"inv",imp_neto_vta, "Gn", Ganancia_n_arb)
            print(current_time,"D:",Symbol,"pF",price_factor," cpraCI=", pCI, " vta48=", p48hs,DIF, "d%= {:.2f}%".format(DIFP)," dz=",dz, "cau7d",caucion7d["caucion7d"],"pt",per_tasa,"inc", imp_neto_cpra,"inv",imp_neto_vta, "Gn", Ganancia_n_arb)

            # Crear y enviar la compra. Con esto comienza a trabajar el order report
            miid = generate_ws_cli_ord_id(Symbol)
            tipo = get.pyRofexInicializada.OrderType.MARKET
            orden_ = OperacionHF(ticker=ticker_en_curso_cpra, accion='comprar',size=1,  price=pCI , order_type=tipo, _ws_client_order_id=miid)
            orden_.enviar_orden()
            #ordenes_activas[orden_.ws_Cliordid] = orden_  # Almacenar la orden en el diccionario
            #IDdelacompra  = orden_.ws_Cliordid
            #ticker_en_curso_cpra = Symbol
            price_en_curso = p48hs


            

    #if DIFPi > 1 and dzi > 0
        #current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
        #print(current_time,"I:",Symbol[13:19]," cpra48=", p48hsi, " vtaCI=",pCIi,  DIFi,"d%= {:.2f}%".format(DIFPi)," dz=",dzi )
    """    
    # bloque de escribir el log
    original_stdout = sys.stdout     
    # Ruta completa al archivo
    file_path = 'Z:\\python\\Arb01log1026.csv'
    # Redirigir la salida estándar al archivo
    with open(file_path, 'a') as f:
        sys.stdout = f
        #"timestamp","Direccion","Ticker"," cpra", " vta", "Gan bruta %"," liquidez delta"
        if (DIFP>0.5):
            print(current_time,";",Symbol[13:19],";",price_factor,";", pCI, ";", p48hs,";",DIF,";", "{:.2f}%".format(DIFP),";",dz,";",caucion7d["caucion7d"],";",per_tasa,";",imp_neto_cpra,";",imp_neto_vta,";",Ganancia_n_arb)
            
            # imprime los numeros con coma y con dos decimales, y separados por ;
            print(
                current_time, ";", 
                Symbol[13:19], ";", 
                "{:.2f}".format(price_factor).replace('.', ','), ";", 
                "{:.2f}".format(pCI).replace('.', ','), ";", 
                "{:.2f}".format(p48hs).replace('.', ','), ";", 
                "{:.2f}".format(DIF).replace('.', ','), ";", 
                "{:.2f}%".format(DIFP).replace('.', ','), ";", 
                "{:.2f}".format(dz).replace('.', ','), ";", 
                "{:.2f}".format(caucion7d["caucion7d"]).replace('.', ','), ";", 
                "{:.2f}".format(per_tasa).replace('.', ','), ";", 
                "{:.2f}".format(imp_neto_cpra).replace('.', ','), ";", 
                "{:.2f}".format(imp_neto_vta).replace('.', ','), ";", 
                "{:.2f}".format(Ganancia_n_arb).replace('.', ',')
            )

        #if (DIFPi>0.5):
            # atencion, separador debe ser ;
            #print(current_time,",I:",",",Symbol[13:19],",", p48hsi,",", pCIi,",",DIFi,",", "{:.2f}%".format(DIFPi),",",dzi)

    # Restaurar la salida estándar original

    sys.stdout = original_stdout
    """
            
            
            
            
            
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
    
    precio = float(message["marketData"]["BI"][0]["price"])
    current_time = datetime.now().strftime("%H:%M:%S,%f")[:-3]  # Formato hh:mm:ss,xxxx
    symbol = message["instrumentId"]["symbol"]
    tamaños = [1, 2, 3, 4, 5]  # Lista de tamaños para las órdenes

    for i in range(5):  # Itera 5 veces
        tamaño = tamaños[i]  # Obtiene el tamaño correspondiente de la lista
        orden_ = OperacionHF(ticker=symbol, accion='comprar', size=1, price=precio, order_type=get.pyRofexInicializada.OrderType.LIMIT)
                
      #  orden_.enviar_orden()
    time.sleep(2)  # Pausa de 2 segundos antes de continuar
    for i in range(5):  # Itera 5 veces
        tamaño = tamaños[i]  # Obtiene el tamaño correspondiente de la lista
        orden_ = OperacionHF(ticker=symbol, accion='vender', size=1, price=precio, order_type=get.pyRofexInicializada.OrderType.LIMIT)
                
       # orden_.enviar_orden()
    if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
        print(current_time, "FUN market_data_handler_arbitraje_001: [BI] vacio. Simbolo",symbol)
    elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
        print(current_time, "FUN market_data_handler_arbitraje_001: [OF] vacio.",symbol)
    #elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:
     #   print("FUN market_data_handler_arbitraje_001: message[marketData][LA] es None o está vacío")
    #else:
        #print("FUN market_data_handler_estrategia: SI HAY DATOS. ")
        #Arbitrador001(message)



def order_report_handler_arbitraje_001( order_report):
   
    print(order_report)

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
    
    
    
    # hay cosas repetidas que se anularan pronto
    order_data = order_report['orderReport']
    #clOrdID = order_data['clOrdId']        
    clOrdID = order_report.get('clOrdId', None)
    ws_Cliordid = order_report.get('ws_Cliordid', None) # es otro metodo de hacer lo mismo pero  no larga exeption sino none
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']  
    status = order_report.get('status', None) # es otro metodo de hacer lo mismo pero  no larga exeption sino none
    timestamp_order_report = order_data['transactTime']  


    
    if clOrdID is not None:
        if symbol == ticker_en_curso_cpra:
            IDdelacompra_ = order_data['clOrdId']        
            ordenes_activas[orden_.IDdelacompra_] = orden_
        elif symbol == ticker_en_curso_vta:
            IDdelaventa_ = order_data['clOrdId']        
            ordenes_activas[orden_.IDdelaventa_] = orden_
    
    
    
    
    # Encuentra la orden correspondiente usando clOrdID
    # ordenes_activas es un diccionario que mapea clOrdID a objetos OperacionHF
    orden = ordenes_activas.get(clOrdID, None)
    # Estados de una orden "NEW", "REJECTED","PARTIALLY_FILLED", "FILLED", "CANCELLED", y "PENDING_NEW".

    if orden:
        if  status == "PENDING_NEW":# Se está procesando pero aún no ha sido aceptada en el mercado.
            print(f"La orden {clOrdID} está en proceso de ser ingresada.")
        elif status == "NEW":# Esto significa que la orden está en el libro de órdenes pero aún no se ha ejecutado.
            print(f"La orden {clOrdID} ha ingresado correctamente.")
        elif status == "REJECTED":
            print(f"La orden {clOrdID} ha sido rechazada.")
            del ordenes_activas[clOrdID]# Eliminar del dicc
        elif status == "PARTIALLY_FILLED":
            print(f"La orden {clOrdID} ha sido parcialmente completada.")
        elif status == "FILLED":
            print(f"La orden {clOrdID} ha sido completada.")
            if clOrdID == IDdelacompra_:
                # Crear y enviar la venta
                del ordenes_activas[clOrdID]
                miid = generate_ws_cli_ord_id(ticker_en_curso_vta)
                tipo = get.pyRofexInicializada.OrderType.MARKET
                orden_ = OperacionHF(ticker=ticker_en_curso_vta, accion='venta',size=1,  price=price_en_curso , order_type=tipo, _ws_client_order_id=miid)
                #orden_ = OperacionHF(ticker=ticker_en_curso_vta, size=1, side='venta', type=tipo, ws_cli_ord_id=miid ,price=price_en_curso )
                orden_.enviar_orden()
                #ordenes_activas[orden_.ws_Cliordid] = orden_  # Almacenar la orden en el diccionario
                #ticker_en_curso_cpra = Symbol
                #IDdelaventa  = orden_.ws_Cliordid
            elif clOrdID == IDdelaventa_:
                print("FUN order_report_handler_arbitraje_001: Arbitraje terminado . ")
                del ordenes_activas[clOrdID]
                flag_arbitraje_en_ejecucion = False
                IDdelacompra=0
                IDdelaventa=0
                IDdelacompra_=0
                IDdelaventa_=0
        elif status == "CANCELLED":
            print(f"La orden {clOrdID} ha sido cancelada.")
            del ordenes_activas[clOrdID]# Eliminar del dicc
        else:
            print(f"Estado desconocido {status} para la orden {clOrdID}.")
    else:
        print(f"No se encontró la orden con clOrdID {clOrdID}.")
    

    
     
            



def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))



