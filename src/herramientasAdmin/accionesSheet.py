from flask import Blueprint, render_template,current_app ,session,request, redirect, url_for, flash,jsonify
from utils.common import Marshmallow, db, get
import routes.instrumentosGet as instrumentosGet
import routes.api_externa_conexion.validaInstrumentos as val

import strategies.datoSheet as datoSheet
import routes.instrumentos as inst
from panelControlBroker.panelControl import enviar_leer_sheet
from panelControlBroker.panelControl import terminaConexionParaActualizarSheet
from strategies.datoSheet import update_precios
from datetime import datetime


import pyRofex #lo utilizo para test
import time    #lo utilizo para test
import asyncio

from flask_paginate import Pagination, get_page_parameter

import json
import os
import copy

accionesSheet = Blueprint('accionesSheet',__name__)

@accionesSheet.route('/herramientasSheet_accionesSheet_detener')
def herramientasSheet_accionesSheet_detener():
    try:
        terminaConexionParaActualizarSheet(get.CUENTA_ACTUALIZAR_SHEET)
    except KeyError:
        print(f"No se pudo terminar la conexión para la cuenta {get.CUENTA_ACTUALIZAR_SHEET}.")
    
    # Si los diccionarios existen, .clear() no generará una excepción
    get.symbols_sheet_valores.clear()
    get.ContenidoSheet_list = None
    get.sheet_manager = None
    get.precios_data.clear()
    
    get.autenticado_sheet = False
    return render_template('notificaciones/stopProceso.html', layout='layout')

@accionesSheet.route('/herramientasSheet_accionesSheet_iniciar')
def herramientasSheet_accionesSheet_iniciar():
    try:
     app = current_app._get_current_object()
     if not get.conexion_existente(app,get.CUENTA_ACTUALIZAR_SHEET,
                                          get.CORREO_E_ACTUALIZAR_SHEET,
                                          get.VARIABLE_ACTUALIZAR_SHEET,
                                          get.ID_USER_ACTUALIZAR_SHEET):
          modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores','argentina')
          #modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores','argentina')
    except KeyError:
        print(f"No se pudo terminar la conexión para la cuenta {get.CUENTA_ACTUALIZAR_SHEET}.")
        return render_template('notificaciones/noPoseeDatos.html',layout = 'layout')
    return render_template('notificaciones/procesoIniciado.html', layout = 'layout')

@accionesSheet.route('/herramientasSheet_accionesSheet_controlMDH')
def herramientasSheet_accionesSheet_controlMDH():
    return render_template('notificaciones/controlMdh.html', layout = 'layout')

@accionesSheet.route('/herramientasSheet_accionesSheet_actualizaLuz')
def herramientasSheet_accionesSheet_actualizaLuz():
    luz = get.luzMDH_funcionando
    get.luzMDH_funcionando = False
    return jsonify({'luzMDH_control':luz})

@accionesSheet.route('/herramientasSheet_accionesSheet_actualizaLuz_thread')
def herramientasSheet_accionesSheet_actualizaLuz_thread():
    luz = get.luzThred_funcionando['luz']
    get.luzThred_funcionando['luz'] = False
    luzMDH = get.luzMDH_funcionando
    get.luzMDH_funcionando = False
    # Obtener los valores de hora, minuto y segundo del diccionario
    hora = get.luzThred_funcionando['hora']
    minuto = get.luzThred_funcionando['minuto']
    segundo = get.luzThred_funcionando['segundo']
   
   
    # Imprimir para verificar en la consola
    print(hora, minuto, segundo)
    
    # Devolver como respuesta un JSON que incluye el estado de 'luz' y la hora actual
    return jsonify({
        'luzMDH_control': luzMDH,
        'luzThread_control': luz,
        'hora': hora,
        'minuto': minuto,
        'segundo': segundo
    })
    
