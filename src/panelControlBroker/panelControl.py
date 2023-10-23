# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.orden import Orden
import threading
import strategies.datoSheet as datoSheet
import time
from flask import abort

panelControl = Blueprint('panelControl',__name__)

def obtener_pais():
    ip = request.remote_addr
    response = requests.get(f'http://ipinfo.io/{ip}')
    data = response.json()
    pais = data.get('country')
    return f'El país de la conexión es: {pais}'


@panelControl.route('/panel_control_sin_cuenta')
def panel_control_sin_cuenta():
   
    pais = request.args.get('country')
    layout = request.args.get('layoutOrigen')
    usuario_id = request.args.get('usuario_id')
      
    respuesta =  llenar_diccionario_cada_15_segundos_sheet(pais)
    if len(get.diccionario_global_sheet) != 0:
     
     datos_desempaquetados = forma_datos_para_envio_paneles(get.diccionario_global_sheet[pais],usuario_id)
     if len(datos_desempaquetados) != 0:
       get.diccionario_global_sheet_intercambio = datos_desempaquetados
     else:
       datos_desempaquetados = forma_datos_para_envio_paneles(get.diccionario_global_sheet[pais],usuario_id)
    else:
      enviar_leer_sheet(pais)
      datos_desempaquetados = forma_datos_para_envio_paneles(get.diccionario_global_sheet[pais],usuario_id)
  
    
    if layout == 'layout_signal':
        return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
    if layout == 'layout': 
        return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
    
@panelControl.route("/panel_control")
def panel_control():
     pais = request.args.get('country')
     layout = request.args.get('layoutOrigen')
     usuario_id = request.args.get('usuario_id')
     
     llenar_diccionario_cada_15_segundos_sheet(pais)     
     
     datos_desempaquetados = forma_datos_para_envio_paneles(get.diccionario_global_sheet[pais],usuario_id)
    
     if layout == 'layout_signal':
        return render_template("/paneles/panelSignalSinCuentas.html", datos = datos_desempaquetados)
     if layout == 'layout':         
        return render_template("/paneles/panelDeControlBroker.html", datos = datos_desempaquetados)


@panelControl.route("/panel_control_atomatico/<pais>/<usuario_id>")
def panel_control_atomatico(pais,usuario_id):
     
     llenar_diccionario_cada_15_segundos_sheet(pais)
     datos_desempaquetados = forma_datos_para_envio_paneles(get.diccionario_global_sheet[pais],usuario_id)
    
    
     return jsonify(datos=datos_desempaquetados)


def forma_datos_para_envio_paneles(ContenidoSheet,usuario_id):
    ContenidoSheet = zip(ContenidoSheet)
    ContenidoSheet = list(ContenidoSheet)
    
    datos_desempaquetados = list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
    for i, tupla_exterior in enumerate(datos_desempaquetados):
        tupla_interior = tupla_exterior[0]  # Extrae la tupla interior de la tupla exterior
        dato = list(tupla_interior)  # Convierte la tupla interior a una lista
        dato[0] = dato[0].replace("MERV - XMEV -", "")
        orden_existente = Orden.query.filter_by(symbol=dato[0], user_id=usuario_id).first()

        if orden_existente:
            dato_extra = (orden_existente.clOrdId_alta_timestamp, orden_existente.senial)
            dato += dato_extra
        else:
            dato += (None, None)

        dato.append(i+1)  
        datos_desempaquetados[i] = tuple(dato)
    return datos_desempaquetados



def llenar_diccionario_cada_15_segundos_sheet(pais):
    get.hilo_iniciado_panel_control

    # Verifica si ya hay un hilo iniciado para este país
    if pais in get.hilo_iniciado_panel_control and get.hilo_iniciado_panel_control[pais].is_alive():
        return f"Hilo para {pais} ya está en funcionamiento"

    # Si no hay un hilo iniciado para este país, lo inicia
    hilo = threading.Thread(target=ejecutar_en_hilo, args=(pais,))
    get.hilo_iniciado_panel_control[pais] = hilo
    hilo.start()

    return f"Hilo iniciado para {pais}"

def ejecutar_en_hilo(pais):
    while True:
        enviar_leer_sheet(pais)
        time.sleep(15)

def enviar_leer_sheet(pais):
      
     if pais not in ["argentina", "usa"]:
        # Si el país no es válido, retorna un código de estado HTTP 404 y un mensaje de error
        abort(404, description="País no válido")
        
     if pais == "argentina":
         ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
     elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_USA,'drpibotUSA')
     else:
         return "País no válido"
     
     get.diccionario_global_sheet[pais] = ContenidoSheet
     