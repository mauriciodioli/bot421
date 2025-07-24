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
from utils.db_session import get_db_session 

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

        # Fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        # Parsear respuesta en filas con estructura completa (13 col + fecha)
        nuevas_filas_original = parsear_respuesta_13_columnas_completa(respuesta)
        nuevas_filas = [fila + [fecha_actual] for fila in nuevas_filas_original]

        if not nuevas_filas:
            print("⚠️ No se encontraron filas válidas en la respuesta.")
            return

        # Obtener datos actuales
        datos = hoja.get_all_values()
        encabezado = datos[0]
        contenido = datos[1:]

        pais_fecha_indices = {}
        pais_ultimas_filas = {}
        for i, fila in enumerate(contenido, start=2):  # desde fila 2 real
            if len(fila) >= 14:
                pais = fila[1].strip()
                fecha = fila[13].strip()
                pais_fecha_indices[(pais, fecha)] = i
                pais_ultimas_filas[pais] = i

        # Agrupar nuevas filas por (pais, fecha)
        filas_por_pais_fecha = {}
        for fila in nuevas_filas:
            pais = fila[1]
            clave = (pais, fecha_actual)
            filas_por_pais_fecha.setdefault(clave, []).append(fila)

        # Insertar/actualizar según existencia de la clave (pais, fecha)
        for (pais, fecha), filas in filas_por_pais_fecha.items():
            if (pais, fecha) in pais_fecha_indices:
                print(f"⚠️ Ya existe entrada para {pais} con fecha {fecha}, no se agrega.")
                continue
            elif pais in pais_ultimas_filas:
                fila_inicio = pais_ultimas_filas[pais]
                hoja.update(f"A{fila_inicio}", filas)
            else:
                hoja.append_rows([[""] * 14] + filas)

        # Reordenar hoja
        datos_actualizados = hoja.get_all_values()[1:]
        datos_limpios = [fila for fila in datos_actualizados if any(c.strip() for c in fila)]

        # Ordenar por país (col 1) y fecha (col 14, índice 13)
        datos_ordenados = sorted(datos_limpios, key=lambda x: (x[1], x[13]))

        # Insertar filas vacías entre países
        datos_finales = []
        ultimo_pais = None
        for fila in datos_ordenados:
            pais = fila[1]
            if pais != ultimo_pais and ultimo_pais is not None:
                datos_finales.append([""] * 14)
            datos_finales.append(fila)
            ultimo_pais = pais

        # Escribir hoja
        hoja.update("A2:N", datos_finales)
        print("✅ Datos actualizados y hoja ordenada correctamente.")

    except Exception as e:
        print(f"❌ Error en el proceso de actualización: {e}")


def extraer_link(texto):
    # Extrae solo el link de un string tipo [Texto](URL)
    match = re.search(r"\((https?://[^\)]+)\)", texto)
    return match.group(1) if match else texto.strip()


def parsear_respuesta_13_columnas_completa(respuesta):
    lineas = [l for l in respuesta.strip().split("\n") if "|" in l]
    filas = []

    for linea in lineas:
        if "numero" in linea.lower() or "---" in linea:
            continue  # saltar encabezado o separador

        columnas = [extraer_link(c).strip() for c in linea.strip().split("|") if c.strip()]
        if len(columnas) == 13:
            link_corregido = corregir_link_aliexpress(columnas[9])  # ✅ esto sí se puede
            fila = [
                columnas[0],  # numero
                columnas[1],  # pais
                columnas[2],  # producto
                columnas[3],  # categoria
                columnas[4],  # descripcion
                columnas[5],  # precio_amazon
                columnas[6],  # precio_ebay
                columnas[7],  # precio_aliexpress
                columnas[8],  # proveedor_mas_barato
                link_corregido, # link_proveedor_mas_barato
                columnas[10], # precio_reventa_sugerido
                columnas[11], # margen_estimado
                columnas[12], # imagen
               
            ]
            filas.append(fila)
    return filas



def corregir_link_aliexpress(url):
    match = re.search(r"100\d{9,}", url)
    if match:
        product_id = match.group(0)
        return f"https://www.aliexpress.com/i/{product_id}.html"
    return url
