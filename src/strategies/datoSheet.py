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

import random
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#import routes.api_externa_conexion.cuenta as cuenta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import os #obtener el directorio de trabajo actual
import sys
import csv

#import drive
#drive.mount('/content/gdrive')



datoSheet = Blueprint('datoSheet',__name__)

newPath = os.path.join(os.getcwd(), 'strategies/credentials_module.json') 
directorio_credenciales = newPath 

#SPREADSHEET_ID='1pyPq_2tZJncV3tqOWKaiR_3mt1hjchw12Bl_V8Leh74'#drpiBot2
#SPREADSHEET_ID='1yQeBg8AWinDLaErqjIy6OFn2lp2UM8SRFIcVYyLH4Tg'#drpiBot3 de pruba
SPREADSHEET_ID='1GMv6fwa1-4iwhPBZqY6ZNEVppPeyZY0R4JB39Xmkc5s'#drpiBot de produccion
#1GMv6fwa1-4iwhPBZqY6ZNEVppPeyZY0R4JB39Xmkc5s

class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2
    
class Ordenes(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2 
    #NEW  
    #PENDING_NEW
    #TIMESTAMP_ENVIO
    

    
    
def login():
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = directorio_credenciales
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credenciales)
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth(port_numbers=[8092])
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
        
    gauth.SaveCredentialsFile(directorio_credenciales)
    credenciales = GoogleDrive(gauth)
    return credenciales

def autenticar_y_abrir_sheet(sheetId, sheet_name):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 
                 'https://www.googleapis.com/auth/drive']
        newPath = os.path.join(os.getcwd(), 'strategies/pruebasheetpython.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(newPath, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheetId).worksheet(sheet_name)  # Abre el sheet especificado
        return sheet
    except Exception as e:
        print(f"Error al autenticar y abrir la hoja de cálculo: {e}")
        return None  # Puedes devolver None o manejar de otra manera el error en tu aplicación


#def leerSheet_arbitrador001(): 

def leerSheet(sheetId,sheet_name): 
     
     # recibo la tupla pero como este es para el bot leo el primer elemento 
     sheet= autenticar_y_abrir_sheet(sheetId,sheet_name) 
     if sheet: 
        symbol = sheet.col_values(5)       # ticker de mercado
        tipo_de_activo = sheet.col_values(22)  # cedear, arg o usa
        trade_en_curso = sheet.col_values(19)  # long, short o nada
        ut = sheet.col_values(20)              # cantidad a operar
        senial = sheet.col_values(21)          # Open o Close
        gan_tot = sheet.col_values(26)
        dias_operado = sheet.col_values(30)    # Dias habiles operado
        #FlagCCLCedear_col = sheet.col_values(12)          # flag del CCL correcto
        
        #union = zip(symbol,tipo_de_activo,trade_en_curso,ut,senial)
        union = zip(symbol, tipo_de_activo, trade_en_curso, ut, senial, gan_tot, dias_operado)

   
       # for dato in union:
       #  if ((dato[1] == 'USA' or dato[1] == 'ARG' or dato[1] == 'CEDEAR') and 
       #         dato[2] == 'LONG_' or (dato[2] == 'SHORT' and dato[1] != 'ARG' and dato[1] != 'CEDEAR')):
       #         if (dato[3] > '0'):
       #             if (dato[4] == 'OPEN.' or dato[4] == 'closed.'):
       #                 print(f"Datos {dato} - Pasa la condición")
       #             else:
       #                 print(f"Datos {dato} - No pasa la condición de la posición 4")
       #         else:
       #             print(f"Datos {dato} - No pasa la condición de la posición 3")
       #  else:
       #         print(f"Datos {dato} - No pasa la condición inicial")
        
        return union
     else:
       
        return render_template('notificaciones/noPoseeDatos.html')
def leerDb(app):
     with app.app_context():   
        all_ins = db.session.query(InstrumentoSuscriptos).all()
        db.session.close()
        print("FUN_ cargaSymbolParaValidarDb en estrategiaSheetWS 178")
        return all_ins

def modificar_columna_ut(Symbol,new_ut_values):
    # Obtener el objeto sheet una vez, en lugar de repetir la autenticación
    sheet = autenticar_y_abrir_sheet()
    cell =  sheet.find(Symbol) 
    row = cell.row
    valores_de_la_fila = sheet.row_values(row)
    current_ut_values = valores_de_la_fila[19]
   
        # Leer la columna "ut" actual
    if current_ut_values != new_ut_values:  
         sheet.update_cell(row,20,str(new_ut_values)) 
   
   

    # Opcionalmente, puedes retornar las listas leídas si necesitas usarlas en otra parte del código
    return "current_ut_values"
 

# Función de codificación personalizada para datetime
def datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()




    # Defines the handlers that will process the Order Reports.

     

def calcularMepAl30():
    print("____________calcularMepAl30_____________")
    #resultado = requests.post('http://127.0.0.1:5000/instrument_by_symbol_para_CalculoMep/', data ={'symbol':symbol})
    
    #traer los precios del al30
    #print("____traer los precios del al30")
    resultado = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs")    
    resultado2 = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs")    
   
   # al30_ci = resultado['OF'][0]['price'] #vendedora OF
   # al30D_ci =resultado2['BI'][0]['price'] #compradora BI
    #print("__________al30_ci____________",al30_ci)
    #print("__________al30D_ci____________",al30D_ci)
    
    # simulo compra de bono      
    #print("____simulo compra de bono ")  
   # al30ci_unitaria = al30_ci/100
    #cantidad_al30ci=int(10000/al30ci_unitaria)
    #print("__________cantidad_al30ci_________",cantidad_al30ci)
    
    # ahora simulo la venta de los bonos D
    #print("ahora simulo la venta de los bonos D")
    #al30D_ci_unitaria = al30D_ci/100
    #dolaresmep = al30D_ci_unitaria * cantidad_al30ci
    #mep = 10000 / dolaresmep
    mep = 380
    print("____________calcularMepAl30_____________")
    return mep

##########################AQUI SE REALIZA CALCULO DE MEP CEDEARS####################
def calcularMepCedears(Symbol):
     #traer los precios del cedear
     print("_calcularMepCedears_______ le da 380")
     resultado = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs") 
     #resultado2 = instrument_by_symbol_para_CalculoMep("MERV - XMEV - GGAL - 48hs") 
     
    # ko_ci = resultado['OF'][0]['price'] #vendedora OF ko_ci punta vendedora (porque es lo que yo deberia comprar si quiero dolar mep)
    # koD_ci =resultado2['BI'][0]['price'] #compradora BI koD_ci punta compradora (el que me compra lo bonos para tener mis dolares)
    # size = resultado2['BI'][0]['size']
   #  print("__________ko_ci____________",ko_ci)
   #  print("__________koD_ci____________",koD_ci)
   #  print("__________size____________",size)
     #mep= ko_ci / koD_ci
     if len(resultado['OF']) > 0:
        offer_price = resultado['OF'][0]['price'] #vendedora OF
     else:
        offer_price=0
        
     if len(resultado['BI']) > 0:
        bid_price =resultado['BI'][0]['price'] #compradora BI
     else:
        bid_price=0
     
     mep=380
     size=10
     dato = [mep,size,offer_price,bid_price]
     return dato

def compruebaLiquidez(ut,size):
    #print(ut,"_CompruebaLiquidez____________",size) 
    liquidez = int(ut) - int(size) # 100 - 3 = 97 /////// 4 - 10 = -6 
    #print("_____________liquidez____________",liquidez)
    if liquidez >= 0:    
       cantidadAComprar = size
       vecesAOperar =int(liquidez/size)
    if liquidez < 0:
        cantidadAComprar = ut
        vecesAOperar=0
    #dato = [vecesAOperar,cantidadAComprar]
    dato = 2
    #print("_____________vecesAOperar____________",vecesAOperar)
    return dato
       
    
##########################AQUI LLAMO A UN INSTRUMENTO####################

def instrument_by_symbol_para_CalculoMep(symbol):
      print("__________entra a instrument_by_symbol____________") 
      try:
        
            entries =  [ get.pyRofexInicializada.MarketDataEntry.OFFERS,get.pyRofexInicializada.MarketDataEntry.BIDS,get.pyRofexInicializada.MarketDataEntry.LAST ]
            
            #print("symbolllllllllllllllllllllll ",symbol)
           #https://api.remarkets.primary.com.ar/rest/instruments/detail?symbol=DLR/NOV23&marketId=ROFX
            repuesta_instrumento = pyConectionWebSocketInicializada.get_market_data(ticker=symbol, entries=entries, depth=2)
           
            
            #repuesta_instrumento = get.pyRofexInicializada.get_instrument_details(ticker=symbol)
            #for repuesta_instrumento in repuesta_instrumento:        
            objeto = repuesta_instrumento['marketData']   
           # for objeto in objeto:     
            
           # print("instrumentooooooooooooooooooooooooooooo LA ",objeto['LA'])
           # print("instrumentooooooooooooooooooooooooooooo BI ",objeto['BI'])            
           # print("instrumentooooooooooooooooooooooooooooo OF ",objeto['OF'])
            #jdato = str(objeto['LA'])
            #jdato1 = str(objeto['BI'])
            #jdato2 = str(objeto['OF'])
            #if jdato.find('price')==-1:
            #    print("no tiene nada LA ",jdato.find('price'))
                
            #elif jdato1.find('price')==-1:
            #    print("no tiene nada BI ",jdato1.find('price'))
                
            
            #elif jdato2.find('price')==-1:
            #    print("no tiene nada OF",jdato2.find('price'))
           
            return objeto
        
      except:       
        flash('instrument_by_symbol_para_CalculoMep__: Symbol Incorrect')   
        return render_template("instrumentos.html" )
   









