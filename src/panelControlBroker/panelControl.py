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
import strategies.datoSheet as datoSheet

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
    if pais == "argentina":
         ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
    elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'drpibotUSA')
    else:
         return "País no válido"
     
    datos_desempaquetados = forma_datos_para_envio_paneles(ContenidoSheet) 
       
    if layout == 'layout_signal':
        return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)
    if layout == 'layout': 
        return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)

@panelControl.route("/panel_control/<pais>/<layout>")
def panel_control(pais, layout):
     if pais == "argentina":
         ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
     elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'drpibotUSA')
     else:
         return "País no válido"
     
     
     datos_desempaquetados = forma_datos_para_envio_paneles(ContenidoSheet)
    
     if layout == 'layout_signal':
        return render_template("/paneles/panelSignalSinCuentas.html", datos = datos_desempaquetados)
     if layout == 'layout':         
        return render_template("/paneles/panelDeControlBroker.html", datos = datos_desempaquetados)


@panelControl.route("/panel_control_atomatico/<pais>")
def panel_control_atomatico(pais):
     if pais == "argentina":
         ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
     elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'drpibotUSA')
     else:
         return "País no válido"
     datos_desempaquetados = forma_datos_para_envio_paneles(ContenidoSheet)
    
    
     return jsonify(datos=datos_desempaquetados)


def forma_datos_para_envio_paneles(ContenidoSheet):
    datos_desempaquetados = list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
    for i, dato in enumerate(datos_desempaquetados):
        dato = list(dato)
        dato.append(i+1)  # El +1 es porque los índices empiezan en 0, pero parece que tus números de orden empiezan en 1.
        datos_desempaquetados[i] = tuple(dato)
        dato[0] = dato[0].replace("MERV - XMEV -", "")
        datos_desempaquetados[i] = tuple(dato)
        orden_existente = Orden.query.filter_by(symbol=dato[0]).first()
        if orden_existente:  # Asegúrate de que se encontró una orden
            dato_extra = (orden_existente.clOrdId_alta_timestamp, orden_existente.senial)
            datos_desempaquetados[i] += dato_extra
        else:
            # Si no se encontró una orden, puedes manejarlo de alguna manera o simplemente dejar los campos vacíos
            datos_desempaquetados[i] += (None, None)
    return datos_desempaquetados
