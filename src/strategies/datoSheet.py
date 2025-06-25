from flask import Blueprint, render_template, request,current_app, redirect, url_for, flash,jsonify
import routes.api_externa_conexion.get_login as get
from datetime import datetime
from models.sheetModels.GoogleSheetManager import GoogleSheetManager
from models.sheetModels.sheet_handler import SheetHandler
import json
from models.instrumentosSuscriptos import InstrumentoSuscriptos
from utils.db import db
from dotenv import load_dotenv
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#import routes.api_externa_conexion.cuenta as cuenta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os #obtener el directorio de trabajo actual
import json
import numpy as np
import tokens.token as Token
import jwt
from models.usuario import Usuario
from models.operacion import Operacion


load_dotenv()
#import drive
#drive.mount('/content/gdrive')



datoSheet = Blueprint('datoSheet',__name__)

newPath = os.path.join(os.getcwd(), 'strategies/credentials_module.json') 
directorio_credenciales = newPath 

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]


precios_data = {}

    
    
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
     
        if not get.autenticado_sheet:        
            # recibo la tupla pero como este es para el bot leo el primer elemento 
            credentials_path = os.path.join(os.getcwd(), 'strategies/pruebasheetpython.json')
            # Crear instancia del gestor de hojas
            get.sheet_manager = GoogleSheetManager(credentials_path)

            if get.sheet_manager.autenticar():
                get.autenticado_sheet = True
                handler = SheetHandler(get.sheet_manager, sheetId, sheet_name)
        else:
            # Autenticar
            if  get.autenticado_sheet:
                # Crear instancia del manejador de hoja con el gestor y los datos de la hoja
                handler = SheetHandler(get.sheet_manager, sheetId, sheet_name)
            else:
                    print("Error al autenticar. Revisa los detalles del error.")
                    get.autenticado_sheet = False
                    return render_template('notificaciones/noPoseeDatos.html',layout = 'layout_fichas')    
                
                # Ejemplo de uso de leerSheet
        return handler.leerSheet()
                
            

def leerDb(app):
     with app.app_context():   
        all_ins = db.session.query(InstrumentoSuscriptos).all()
        db.session.close()
        print("FUN_ cargaSymbolParaValidarDb en estrategiaSheetWS")
        return all_ins


def promedio_no_vacio(valores):
        valores_no_vacios = [v for v in valores if not np.isnan(v)]
        if len(valores_no_vacios) == 0:
            return np.nan
        return np.sum(valores_no_vacios) / len(valores_no_vacios)
    
def calculo_dolar_mep(message):
    # Definición de variables iniciales
    symbol = message["instrumentId"]["symbol"]
    
    # Inicializar valores_mep si no existe
    if not hasattr(get, 'valores_mep'):
        get.valores_mep = {
            'AL30': {'compra': [], 'venta': []},
            'GD30': {'compra': [], 'venta': []}
        }
    
    # Definir valores de compra y venta para los símbolos AL30 y GD30
    if 'AL30' in symbol:
        compra_al30 = float(message["marketData"]["HI"])
        venta_al30 = float(message["marketData"]["LO"])
        get.valores_mep['AL30']['compra'].append(compra_al30)
        get.valores_mep['AL30']['venta'].append(venta_al30)
      
    elif 'GD30' in symbol:
        compra_gd30 = float(message["marketData"]["HI"])
        venta_gd30 = float(message["marketData"]["LO"])
        get.valores_mep['GD30']['compra'].append(compra_gd30)
        get.valores_mep['GD30']['venta'].append(venta_gd30)
        
    # Función para calcular el promedio ignorando valores vacíos
   # promedio_no_vacio(get.valores_mep)
    # Calcular el promedio del dólar MEP para AL30
    dolar_mep_al30 = None
    if len(get.valores_mep['AL30']['compra']) >= 1 and len(get.valores_mep['AL30']['venta']) >= 1:
        promedio_compra_al30 = promedio_no_vacio(get.valores_mep['AL30']['compra'])
        promedio_venta_al30 = promedio_no_vacio(get.valores_mep['AL30']['venta'])
        if promedio_venta_al30 != 0:
            dolar_mep_al30 = promedio_compra_al30 / promedio_venta_al30
            print(f'Dólar MEP AL30: {dolar_mep_al30}')
    
    # Calcular el promedio del dólar MEP para GD30
    dolar_mep_gd30 = None
    if len(get.valores_mep['GD30']['compra']) >= 1 and len(get.valores_mep['GD30']['venta']) >= 1:
        promedio_compra_gd30 = promedio_no_vacio(get.valores_mep['GD30']['compra'])
        promedio_venta_gd30 = promedio_no_vacio(get.valores_mep['GD30']['venta'])
        if promedio_venta_gd30 != 0:
            dolar_mep_gd30 = promedio_compra_gd30 / promedio_venta_gd30
            print(f'Dólar MEP GD30: {dolar_mep_gd30}')
    
    return dolar_mep_al30, dolar_mep_gd30





def update_precios(message):
     # Definición de variables iniciales
    p_value = None
    suffix = None
    # Comprobación del sufijo del símbolo y asignación de valores
    symbol = message["instrumentId"]["symbol"]
    
     # Verificar si el símbolo termina con los sufijos deseados
   
    ###################### para buscar un patron visit en este caso #############
    #patron = r'\bHAVA\b'
    #resultado = re.search(patron, symbol)
  
    # Verificar si se encontró y extraer el valor
    #if resultado:
     #   visit = resultado.group()
      #  print(f'Encontrado: {visit}')
    ##############################################################################  
    if symbol.endswith("24hs"):
        p_value = float(message["marketData"]["LA"]["price"])  # Precio "last" para 24hs
       
        if symbol not in get.precios_data:
            get.precios_data[symbol] = {
                'p24hs': None, 'max24hs': None, 'min24hs': None, 'last24hs': None
            }
        get.precios_data[symbol]['max24hs'] = float(message["marketData"]["HI"])
        get.precios_data[symbol]['p24hs'] = float(message["marketData"]["LA"]["price"])
        get.precios_data[symbol]['last24hs'] = float(message["marketData"]["CL"]["price"])
        get.precios_data[symbol]['min24hs'] = float(message["marketData"]["LO"])
    

def actualizar_precios(sheetId, sheet_name, pais):
    try:
        if get.precios_data:
            batch_updates = []
            
            if len(get.symbols_sheet_valores) <= 0:
                if get.sheet_manager.autenticar():
                    get.sheet = get.sheet_manager.abrir_sheet(sheetId, sheet_name)
                    if get.sheet:
                        ranges = ['C:C']  # Rango de símbolos/tickers en la hoja de cálculo
                        try:
                            data = get.sheet.batch_get(ranges)
                            for index, row in enumerate(data[0]):
                                if isinstance(row, list) and row:
                                    symbol = str(row[0]).strip("['").strip("']")
                                    get.symbols_sheet_valores.append(symbol)                                    
                                    if symbol in get.precios_data:
                                        precios_data = get.precios_data[symbol]
                                        try:
                                            if 'max24hs' in precios_data:
                                                batch_updates.append({
                                                    'range': f"E{index + 1}", 
                                                    'values': [[str(precios_data['max24hs']).replace('.', ',')]]
                                                })
                                            if 'min24hs' in precios_data:
                                                batch_updates.append({
                                                    'range': f"F{index + 1}", 
                                                    'values': [[str(precios_data['min24hs']).replace('.', ',')]]
                                                })
                                            if 'p24hs' in precios_data:
                                                batch_updates.append({
                                                    'range': f"G{index + 1}", 
                                                    'values': [[str(precios_data['p24hs']).replace('.', ',')]]
                                                })
                                        except ValueError:
                                            print(f"El símbolo {symbol} no se encontró en la hoja de cálculo.")
                        except Exception as e:
                            print(f"Error en el proceso de actualización: {e}")
            else:
                for index, symbol in enumerate(get.symbols_sheet_valores):
                    if symbol in get.precios_data:
                        precios_data = get.precios_data[symbol]
                        try:
                            if 'max24hs' in precios_data:
                                batch_updates.append({
                                    'range': f"E{index + 1}", 
                                    'values': [[str(precios_data['max24hs']).replace('.', ',')]]
                                })
                            if 'min24hs' in precios_data:
                                batch_updates.append({
                                    'range': f"F{index + 1}", 
                                    'values': [[str(precios_data['min24hs']).replace('.', ',')]]
                                })
                            if 'p24hs' in precios_data:
                                batch_updates.append({
                                    'range': f"G{index + 1}", 
                                    'values': [[str(precios_data['p24hs']).replace('.', ',')]]
                                })
                        except ValueError:
                            print(f"El símbolo {symbol} no se encontró en la hoja de cálculo.")
            
            if batch_updates:
                try:
                    get.sheet.batch_update(batch_updates)
                    #print("Actualización en lotes exitosa.")
                except Exception as e:
                    print(f"Error en la actualización en lotes: {e}")
            else:
                print("No hay datos para actualizar.")
    except Exception as e:
        print(f"Error en el proceso de actualización: {e}")
        return False
    return True

# Función de codificación personalizada para datetime
def datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()




    # Defines the handlers that will process the Order Reports.

########################AQUI SE REALIZA EL JSON PARA LOS DATOS DEL SHEET#############
def construir_lista_de_datos(symbol, tipo_de_activo, trade_en_curso, ut, senial, gan_tot, dias_operado):
    datos = []
    for i in range(1, len(symbol)):
        datos.append({
            'symbol': symbol[i],
            'tipo_de_activo': tipo_de_activo[i],
            'trade_en_curso': trade_en_curso[i],
            'ut': ut[i],
            'senial': senial[i],
            'gan_tot': gan_tot[i],
            'dias_operado': dias_operado[i]
        })
    return datos
     
def guardar_datos_json(datos):
    path_app_modelo = os.path.join(os.getcwd(), 'strategies', 'listadoInstrumentos')
    file_path = os.path.join(path_app_modelo, 'datosSheetEstatico.json')

    with open(file_path, 'w') as json_file:
        json.dump(datos, json_file)
        
def leer_datos_json():
    path_app_modelo = os.path.join(os.getcwd(), 'strategies', 'listadoInstrumentos')
    file_path = os.path.join(path_app_modelo, 'datosSheetEstatico.json')
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print(f"No se pudo encontrar el archivo JSON en la ruta: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"El archivo JSON en la ruta {file_path} no tiene un formato válido.")
        return []

    # Verificar si los campos necesarios están presentes en el diccionario
    required_fields = ['symbol', 'tipo_de_activo', 'trade_en_curso', 'ut', 'senial', 'gan_tot', 'dias_operado']
    for field in required_fields:
        if field not in data:
            print(f"El campo '{field}' no está presente en el archivo JSON.")
            return []

    # Construir la lista de datos en el formato necesario para el bloque HTML
    datos = []
    for i in range(len(data['symbol'])):
        dato = {
            'symbol': data['symbol'][i],
            'tipo_de_activo': data['tipo_de_activo'][i],
            'trade_en_curso': data['trade_en_curso'][i],
            'ut': data['ut'][i],
            'senial': data['senial'][i],
            'gan_tot': data['gan_tot'][i],
            'dias_operado': data['dias_operado'][i]
        }
        datos.append(dato)

    return datos



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
            repuesta_instrumento = get.pyConectionWebSocketInicializada.get_market_data(ticker=symbol, entries=entries, depth=2)
           
            
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
   

@datoSheet.route('/datoSheet_enviar_senial', methods=['POST'])
def datoSheet_enviar_senial():
    try:
        if request.method == 'POST':
            data = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
            access_token = data.get('access_token')
            symbol = data.get('symbol')
            signal = data.get('signal')
            trade_en_curso = data.get('trade_en_curso')
            pais = data.get('pais')
            ut = data.get('ut')

            # Verificar token de acceso y su expiración
            if access_token and Token.validar_expiracion_token(access_token=access_token):
                app = current_app._get_current_object()
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                usuario = db.session.query(Usuario).filter_by(id=user_id).first()
               

                # Llamar a la función para actualizar la señal
                modifico = actualizar_senial(symbol, trade_en_curso, signal, ut, pais, get.SPREADSHEET_ID_PRUEBA, 'bot')
                
                if modifico:
                    # Si la señal fue 'closed.', actualiza la operación, si no, agrega una nueva operación
                    if signal == 'closed.':
                        actualiza_operacion(symbol, signal, user_id, trade_en_curso)
                    else:
                        agrega_operacion(symbol, signal, user_id, trade_en_curso)
                    db.session.close()
                    # Retornar un mensaje exitoso
                    return jsonify({'message': 'Señal agregada con éxito'}), 200
                else:
                    return jsonify({'error': 'Error al actualizar señal, no se encontró el símbolo'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


        
def actualizar_senial(symbol, trade_en_curso, signal,ut,pais,sheetId, sheet_name):
    try:
        batch_updates = []

        if get.sheet_manager.autenticar():
            get.sheet = get.sheet_manager.abrir_sheet(sheetId, sheet_name)
            if get.sheet:
                ranges = ['E:E']  # Rango de símbolos/tickers en la hoja de cálculo
                try:
                    data = get.sheet.batch_get(ranges)
                    symbol_found = False  # Variable para verificar si se encontró el símbolo
                   
                    # Recorrer los datos para encontrar el símbolo y hacer las actualizaciones necesarias
                    for index, row in enumerate(data[0]):
                        if isinstance(row, list) and row:
                            sheet_symbol = str(row[0]).strip("['").strip("']")  # Cambié 'symbol' por 'sheet_symbol' para no sobrescribir
                           
                            if sheet_symbol == symbol:  # Asegurarse de que coincide con el símbolo recibido
                                symbol_found = True  # Marcamos que el símbolo fue encontrado
                               
                                try:                                   
                                    
                                    # Actualizar la columna 'S' con 'min24hs' de precios_data si hay trade en curso
                                    variable = 'LONG_' if trade_en_curso else 'SHORT'
                                    batch_updates.append({
                                        'range': f"S{index + 1}",  # Columna 'S' para el estado de la operación
                                        'values': [[str(variable).replace('.', ',')]]
                                    })
                                        
                                    if ut:
                                        valor_ut = ut
                                        batch_updates.append({
                                            'range': f"T{index + 1}", 
                                            'values':  [[str(valor_ut).replace('.', ',')]]
                                        })
                                    # Actualizar la columna 'U' con la señal
                                    if signal:
                                        batch_updates.append({
                                            'range': f"U{index + 1}", 
                                            'values':  [[str(signal).replace('.', '.')]]
                                        })
                                    
                                except ValueError:
                                    print(f"Error al procesar el símbolo {symbol} en la hoja.")
                            
                    if not symbol_found:
                        new_row_index = len(data[0]) + 1  # Nueva fila al final de la hoja
                        batch_updates.append({
                            'range': f"E{new_row_index}",  # Columna 'E' para el símbolo
                            'values': [[symbol]]  # Agregar el símbolo
                        })
                        variable = 'LONG_' if trade_en_curso else 'SHORT'
                        batch_updates.append({
                            'range': f"S{new_row_index}",  # Columna 'S' para el estado de la operación
                            'values': [[str(variable).replace('.', ',')]]
                        })
                        if ut:
                            batch_updates.append({
                                'range': f"T{new_row_index}",  # Columna 'T' para 'ut'
                                'values': [[str(ut).replace('.', ',')]]
                            })
                        if signal:
                            batch_updates.append({
                                'range': f"U{new_row_index}",  # Columna 'U' para la señal
                                'values': [[signal]]
                            })
                        if pais:
                            nacion = 'ARG' if pais else 'USA'
                            batch_updates.append({
                                'range': f"V{new_row_index}", 
                                'values':  [[nacion]]
                            })    
                        
                        print(f"Símbolo {symbol} agregado al final de la lista en la fila {new_row_index}")
                        
                except Exception as e:
                    print(f"Error obteniendo datos de la hoja de cálculo: {e}")
                    return False  # Si ocurre un error, devuelve False
            else:
                print("No se pudo abrir la hoja.")
                return False

        # Si hay actualizaciones en batch, ejecutarlas
        if batch_updates:
            try:
                get.sheet.batch_update(batch_updates)
            except Exception as e:
                print(f"Error al hacer la actualización en lotes: {e}")
                return False
        else:
            print("No se encontraron actualizaciones para hacer.")
            return False

    except Exception as e:
        print(f"Error en el proceso de actualización: {e}")
        return False

    return True



def actualiza_operacion(symbol,signal,user_id,trade_en_curso):
    return True
    
def agrega_operacion(symbol,signal,user_id,trade_en_curso):
    
    
    return True



