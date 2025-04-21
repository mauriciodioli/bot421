from flask import Blueprint, render_template, request,current_app, redirect, url_for, flash,jsonify
import routes.api_externa_conexion.get_login as get
from datetime import datetime
from models.sheetModels.GoogleSheetManager import GoogleSheetManager
from models.sheetModels.sheet_handler import SheetHandler
from strategies.datoSheet import leerSheet
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
from datetime import datetime
import re
import numpy as np
import tokens.token as Token
import jwt
from models.usuario import Usuario
from models.operacion import Operacion


load_dotenv()
#import drive
#drive.mount('/content/gdrive')



conectionSheet = Blueprint('conectionSheet',__name__)

def actualizar_productosSheet_precios(sheetId, sheet_name, pais):
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
        




def conectionSheet_enviar_productos(respuesta):
    try:
        # Llamar a la función para actualizar la señal
        modifico = actualizar_senial(respuesta, get.SHEET_PRODUCTOS_GPT, 'productos_gpt_sheet')
        
        if modifico:                   
            # Retornar un mensaje exitoso
            return jsonify({'message': 'respuesta agregada con éxito'}), 200
        else:
            return jsonify({'error': 'Error al actualizar respuesta, no se encontró el sheet'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


        



def actualizar_senial(respuesta, sheetId, sheet_name): 
    try:
        if not get.sheet_manager.autenticar():
            print("Autenticación fallida")
            return

        hoja = get.sheet_manager.abrir_sheet(sheetId, sheet_name)

        if not respuesta:
            print("No se recibió respuesta válida")
            return

        # Obtener todos los datos (encabezado y contenido)
        datos = hoja.get_all_values()
        encabezado = datos[0]
        contenido = datos[1:]

        # Crear índices actuales por (pais, fecha)
        pais_fecha_indices = {}
        pais_ultimas_filas = {}
        for i, fila in enumerate(contenido, start=2):  # desde fila 2 real
            if len(fila) >= 7 and fila[1].strip():
                pais = fila[1]
                fecha = fila[6]
                pais_fecha_indices[(pais, fecha)] = i
                pais_ultimas_filas[pais] = i

        # Procesar nuevas filas
        lines = respuesta.split("\n")[1:]  # saltar encabezado
        filas_por_pais_fecha = {}
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        for line in lines:
            columnas = [item.strip() for item in line.split("|")]
            if len(columnas) != 6:
                continue
            columnas = [extraer_link(col) for col in columnas]
            columnas.append(fecha_actual)
            pais = columnas[1]
            clave = (pais, fecha_actual)
            filas_por_pais_fecha.setdefault(clave, []).append(columnas)

        for (pais, fecha), nuevas_filas in filas_por_pais_fecha.items():
            clave = (pais, fecha)
            if clave in pais_fecha_indices:
                ########################################################### se quita para no agregar en la misma fecha
                #hoja.append_rows(nuevas_filas)  # misma fecha → agregar al final 
                #####################################################################################################
                print(f"Ya existe entrada para {pais} con fecha {fecha}, no se agrega.")
                continue  # ❌ No agregar si ya existe esa fecha para ese país
            elif pais in pais_ultimas_filas:
                fila_inicio = pais_ultimas_filas[pais]
                hoja.update(f"A{fila_inicio}:G{fila_inicio + len(nuevas_filas) - 1}", nuevas_filas)
            else:
                hoja.append_rows([[""] * 7] + nuevas_filas)  # país nuevo → fila vacía + datos


        # Reordenar hoja completa (excepto encabezado)
        datos_actualizados = hoja.get_all_values()[1:]  # sin encabezado
        datos_limpios = [fila for fila in datos_actualizados if any(c.strip() for c in fila)]
        
        # Ordenar por país (col 1) y fecha (col 6) — índice base 0
        datos_ordenados = sorted(datos_limpios, key=lambda x: (x[1], x[6]))

        # Insertar filas vacías entre países
        datos_finales = []
        ultimo_pais = None
        for fila in datos_ordenados:
            pais = fila[1]
            if pais != ultimo_pais and ultimo_pais is not None:
                datos_finales.append([""] * 7)  # fila vacía
            datos_finales.append(fila)
            ultimo_pais = pais

        # Sobrescribir hoja
        hoja.update('A2:G', datos_finales)
        print("Datos actualizados y hoja ordenada correctamente.")

    except Exception as e:
        print(f"Error en el proceso de actualización: {e}")


def extraer_link(texto):
    # Extrae solo el link de un string tipo [Texto](URL)
    match = re.search(r"\((https?://[^\)]+)\)", texto)
    return match.group(1) if match else texto.strip()


