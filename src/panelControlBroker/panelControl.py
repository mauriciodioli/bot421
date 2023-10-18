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
    if pais == "argentina":
         ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
    elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_USA,'bot')
    else:
         return "País no válido"
     
   
    datos_desempaquetados = list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
     
    for i, dato in enumerate(datos_desempaquetados):
        dato = list(dato)
        dato.append(i+1)  # El +1 es porque los índices empiezan en 0, pero parece que tus números de orden empiezan en 1.
        dato[0] = dato[0].replace("MERV - XMEV -", "")
        datos_desempaquetados[i] = tuple(dato)
        
    return render_template("/paneles/panelSheetCompleto.html", datos = datos_desempaquetados)

@panelControl.route("/panel_control/<pais>")
def panel_control(pais):
     if pais == "argentina":
         ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
     elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_USA,'bot')
     else:
         return "País no válido"
     
     print(ContenidoSheet)
     datos_desempaquetados = list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
     
     for i, dato in enumerate(datos_desempaquetados):
        dato = list(dato)
        dato.append(i+1)  # El +1 es porque los índices empiezan en 0, pero parece que tus números de orden empiezan en 1.
        datos_desempaquetados[i] = tuple(dato)
         
     return render_template("/paneles/panelDeControlBroker.html", datos = datos_desempaquetados)


@panelControl.route("/panel_control_atomatico/<pais>")
def panel_control_atomatico(pais):
     if pais == "argentina":
         ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
     elif pais == "usa":
          ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_USA,'bot')
     else:
         return "País no válido"
     
     datos_desempaquetados =  list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
   
     return jsonify(datos=datos_desempaquetados)


