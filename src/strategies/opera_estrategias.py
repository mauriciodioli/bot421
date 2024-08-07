from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
import routes.instrumentos as instrumentos
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst

from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import requests
import time
import json
from models.orden import Orden
from models.instrumentosSuscriptos import InstrumentoSuscriptos
from utils.db import db
import pyRofex

import random
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#import routes.api_externa_conexion.cuenta as cuenta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint


#import drive
#drive.mount('/content/gdrive')



opera_estrategias = Blueprint('opera_estrategias',__name__)


################ AQUI DEFINO LA COMPRA POR WS ################
def OperacionWs(pyRofexInicializada, diccionario_global_operaciones,diccionario_operaciones_enviadas,Symbol, tipo_de_activo, Liquidez_ahora_cedear,senial, message):
    try:
        print("FUN: OperacionWs__  FIN diccionario_operaciones_enviadas ")
        trade_en_curso = diccionario_global_operaciones[Symbol]['tradeEnCurso']
        ut = diccionario_global_operaciones[Symbol]['ut']
        #saldocta = 1000000  
        ut = abs(int(ut))
        
        
        
        saldoExiste = False
    
   
    
        # La clave "price" existe en message["marketData"]["OF"][0]  ???
        if "OF" in message["marketData"]:
            if isinstance(message["marketData"]["OF"], list) and len(message["marketData"]["OF"]) > 0:
                if "price" in message["marketData"]["OF"][0]:
                    plataoperacion1=ut*message["marketData"]["OF"][0]["price"]
                else:
                    plataoperacion1=0
            else:
                plataoperacion1=0
        else:
            plataoperacion1=0
                
                
        # La clave "price" existe en message["marketData"]["BI"][0] ???
        if "BI" in message["marketData"]:
            if isinstance(message["marketData"]["BI"], list) and len(message["marketData"]["BI"]) > 0:
                if "price" in message["marketData"]["BI"][0]:
                    plataoperacion2=ut*message["marketData"]["OF"][0]["price"]
                else:
                    plataoperacion2=0
            else:
                plataoperacion2=0
        else:
            plataoperacion2=0

        # La clave "price" existe en message["marketData"]["LA"]
        if "LA" in message["marketData"]:
            if "price" in message["marketData"]["LA"]:
                    plataoperacion3=ut*message["marketData"]["LA"]["price"]
            else:
                plataoperacion3=0
        else:
            plataoperacion3=0


        
        #if saldocta > ut * message["marketData"]["OF"][0]["price"] or saldocta > ut * message["marketData"]["BI"][0]["price"] or saldocta > ut * message["marketData"]["LA"]["price"]:
        #if saldocta > plataoperacion1 or saldocta > plataoperacion2 or saldocta > plataoperacion3:
        # aca comprobamos que existan el bid, el offer y el last. si alguno no existe, no tiene 
        # liquidez el instrumento. Si los tres valores existen, comprobamos
        # que el spread sea coherente (no difieran mas del 1%), si el spread es muy amplio, 
        # no hay liquidez y podemos llegar a pagar cualquier cosa.
        saldocta = diccionario_global_operaciones[Symbol]['saldo']        
        if (saldocta > plataoperacion1 and  
            saldocta > plataoperacion2 and 
            saldocta > plataoperacion3):
                saldoExiste = True
            #abs(plataoperacion1 - plataoperacion2) <= 0.01 * max(plataoperacion1, plataoperacion2) and
            #abs(plataoperacion1 - plataoperacion3) <= 0.01 * max(plataoperacion1, plataoperacion3) and
            #abs(plataoperacion2 - plataoperacion3) <= 0.01 * max(plataoperacion2, plataoperacion3)            
            #):
                
        else:
            print("FUN: OperacionWs__ No se puede operar Saldo Insuficiente, o no hay liquidez. El Saldo es: ",saldocta)
            
        if saldoExiste == True: 
           
                 
            if diccionario_global_operaciones[Symbol]['ut'] > 0 :
                _ws_client_order_id =  1001+random.randint(1, 100000)
            
                if senial == 'OPEN.':#    **55                    
                    precio = message["marketData"]["OF"][0]["price"]   
                    if precio:
                        pass
                    else:
                        precio = message["marketData"]["LA"]["price"]    
                        precio = float(message["marketData"]["LA"]["price"])
                        #precio = float(message["marketData"]["BI"][0]["price"])
                        #precio1 = float(message["marketData"]["BI"][1]["price"])
                        #precio2 = float(message["marketData"]["BI"][2]["price"])
                        #precio = float(message["marketData"]["OF"][0]["price"])#
                   
                    print('operaciones Symbol ',Symbol, 'OPEN.')
                    user_id = diccionario_global_operaciones[Symbol]['user_id']
                    userCuenta = diccionario_global_operaciones[Symbol]['userCuenta']
                    accountCuenta = diccionario_global_operaciones[Symbol]['accountCuenta']
                    #pyRofexInicializada.send_order_via_websocket(ticker=Symbol,size=ut,side=pyRofexInicializada.Side.BUY,order_type=pyRofexInicializada.OrderType.LIMIT,ws_client_order_id=_ws_client_order_id,price=precio,environment=accountCuenta)

                    ws_client_order_id = _ws_client_order_id
                        
                 

                    diccionario = {
                            "Symbol": Symbol,
                            "_t_": tipo_de_activo,
                            "_tr_": trade_en_curso,
                            "_s_": senial,
                            "_ut_": ut,
                            "precio Offer": precio,
                            "_ws_client_order_id": ws_client_order_id,
                            "_cliOrderId": 0,
                            "timestamp": datetime.now(),
                            "status": "1",
                            "statusActualBotonPanico": "",
                            "user_id": user_id,
                            "userCuenta": userCuenta,
                            "accountCuenta": accountCuenta
                        }
                    diccionario_operaciones_enviadas[len(diccionario_operaciones_enviadas) + 1] = diccionario
                    #restar del diccionario global                    
                    
                   
                    #pprint.pprint(g et.diccionario_operaciones_enviadas)
                    #print("get.diccionario_global_operaciones[Symbol]['ut'] ",get.diccionario_global_operaciones[Symbol]['ut'])
                    diccionario_global_operaciones[Symbol]['ut'] = diccionario_global_operaciones[Symbol]['ut'] - ut
                    #print("get.diccionario_global_operaciones[Symbol]['ut'] ",get.diccionario_global_operaciones[Symbol]['ut'])
                
                   
                
                elif senial == 'closed.':# **66
                 
                    precio = message["marketData"]["BI"][0]["price"]   
                    if precio:
                       pass
                    else:
                        precio = message["marketData"]["LA"]["price"]  
                        precio = float(message["marketData"]["LA"]["price"])# agresivo
                    #precio = float(message["marketData"]["OF"][0]["price"])
                    #precio = float(message["marketData"]["OF"][0]["price"])
                 
                    user_id = diccionario_global_operaciones[Symbol]['user_id']
                    userCuenta = diccionario_global_operaciones[Symbol]['userCuenta']
                    accountCuenta = diccionario_global_operaciones[Symbol]['accountCuenta']
                    print('operaciones Symbol ',Symbol, 'closed.')
                    #pyRofexInicializada.send_order_via_websocket(ticker=Symbol,size=ut,side=pyRofexInicializada.Side.SELL,order_type=pyRofexInicializada.OrderType.LIMIT,ws_client_order_id=_ws_client_order_id,price=precio,environment=accountCuenta)
                    ws_client_order_id = _ws_client_order_id
                    
                    

                    diccionario = {
                        "Symbol": Symbol,
                        "_t_": tipo_de_activo,
                        "_tr_": trade_en_curso,
                        "_s_": senial,
                        "_ut_": ut,
                        "precio Offer": precio,
                        "_ws_client_order_id": ws_client_order_id,
                        "_cliOrderId": 0,
                        "timestamp": datetime.now(),
                        "status": "1",
                        "statusActualBotonPanico": "",
                        "user_id": user_id,
                        "userCuenta": userCuenta,
                        "accountCuenta": accountCuenta
                    }
                    diccionario_operaciones_enviadas[len(diccionario_operaciones_enviadas) + 1] = diccionario
                    #pprint.pprint(g et.diccionario_operaciones_enviadas)                            
                    print("FUN: OperacionWs__  FIN diccionario_operaciones_enviadas ")
                    #print("get.diccionario_global_operaciones[Symbol]['ut'] ",get.diccionario_global_operaciones[Symbol]['ut'])
                    diccionario_global_operaciones[Symbol]['ut'] = diccionario_global_operaciones[Symbol]['ut'] - ut
                    #print("get.diccionario_global_operaciones[Symbol]['ut'] ",get.diccionario_global_operaciones[Symbol]['ut'])
          
    except Exception as e:
           
            print("Error en estrategies/opera_estrategi.py OperacionWs:", e)

      
def OperacionWs1(pyRofexInicializada, diccionario_global_operaciones, diccionario_operaciones_enviadas, Symbol, tipo_de_activo, Liquidez_ahora_cedear, senial, message):
    try:
        print("FUN: OperacionWs__  FIN diccionario_operaciones_enviadas ")
        trade_en_curso = diccionario_global_operaciones[Symbol]['tradeEnCurso']
        ut = abs(int(diccionario_global_operaciones[Symbol]['ut']))
        saldocta = diccionario_global_operaciones[Symbol]['saldo']

        # Obtener precios
        precio_of = message["marketData"].get("OF", [{}])[0].get("price", 0)
        precio_bi = message["marketData"].get("BI", [{}])[0].get("price", 0)
        precio_la = message["marketData"].get("LA", {}).get("price", 0)

        plataoperacion1 = ut * precio_of
        plataoperacion2 = ut * precio_bi
        plataoperacion3 = ut * precio_la

        if saldocta > plataoperacion1 and saldocta > plataoperacion2 and saldocta > plataoperacion3:
            if diccionario_global_operaciones[Symbol]['ut'] > 0:
                _ws_client_order_id = 1001 + random.randint(1, 100000)
                
                # Definir precios y sides según el tipo de señal
                if senial == 'OPEN.':
                    precio = precio_of if precio_of else precio_la
                    side = pyRofexInicializada.Side.BUY
                elif senial == 'closed.':
                    precio = precio_bi if precio_bi else precio_la
                    side = pyRofexInicializada.Side.SELL
                else:
                    print(f"Señal desconocida: {senial}")
                    return
                
                # Enviar orden
                pyRofexInicializada.send_order_via_websocket(ticker=Symbol,size=ut,side=side,order_type=pyRofexInicializada.OrderType.LIMIT,ws_client_order_id=_ws_client_order_id,price=precio,environment=diccionario_global_operaciones[Symbol]['accountCuenta'])
                
                ws_client_order_id = _ws_client_order_id

                diccionario = {
                    "Symbol": Symbol,
                    "_t_": tipo_de_activo,
                    "_tr_": trade_en_curso,
                    "_s_": senial,
                    "_ut_": ut,
                    "precio Offer": precio,
                    "_ws_client_order_id": ws_client_order_id,
                    "_cliOrderId": 0,
                    "timestamp": datetime.now(),
                    "status": "1",
                    "statusActualBotonPanico": "",
                    "user_id": diccionario_global_operaciones[Symbol]['user_id'],
                    "userCuenta": diccionario_global_operaciones[Symbol]['userCuenta'],
                    "accountCuenta": diccionario_global_operaciones[Symbol]['accountCuenta']
                }
                diccionario_operaciones_enviadas[len(diccionario_operaciones_enviadas) + 1] = diccionario

                diccionario_global_operaciones[Symbol]['ut'] -= ut

        else:
            print(f"FUN: OperacionWs__ No se puede operar Saldo Insuficiente, o no hay liquidez. El Saldo es: {saldocta}")

    except Exception as e:
        print(f"Error en estrategies/opera_estrategi.py OperacionWs: {e}")

        
        
 
   









