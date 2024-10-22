from flask import Blueprint, render_template,current_app ,session,request, make_response,redirect, url_for, flash,jsonify
from utils.common import Marshmallow, db, get
import routes.instrumentosGet as instrumentosGet
import routes.api_externa_conexion.validaInstrumentos as val

import strategies.datoSheet as datoSheet
import routes.instrumentos as inst
from panelControlBroker.panelControl import enviar_leer_sheet
from panelControlBroker.panelControl import terminaConexionParaActualizarSheet
from strategies.datoSheet import update_precios
from werkzeug.exceptions import BadRequest
import pyRofex #lo utilizo para test
import time    #lo utilizo para test
import asyncio
from datetime import datetime, timedelta

from flask_paginate import Pagination, get_page_parameter

import json
import os
import copy

accionesTriggers = Blueprint('accionesTriggers',__name__)


@accionesTriggers.route("/herramAdmin_accionesTrigger_actualizaHorario/")
def herramAdmin_accionesTrigger_actualizaHorario(): 
    return render_template('automatizacion/actualizaHorarioShedule.html', layout='layout')

@accionesTriggers.route('/actualizaHorario', methods=['GET', 'POST'])
def actualiza_horario():
    mensaje_confirmacion = None
    if request.method == 'POST':
        hora_seleccionada = request.form.get('hora')
        response = make_response(render_template('automatizacion/actualizaHorarioShedule.html', hora=hora_seleccionada, layout='layout', mensaje='Hora almacenada correctamente'))
        
        # Almacenar la cookie
        response.set_cookie('horaGuardada', 'true', max_age=5*24*60*60)  # 5 días
        response.set_cookie('diferenciaHoraria', hora_seleccionada, max_age=7*24*60*60)  # 7 días
        
        return response
    
    return render_template('automatizacion/actualizaHorarioShedule.html', layout='layout')


@accionesTriggers.route('/get_server_time')
def get_server_time():
    from datetime import datetime
    # Obtener la hora actual del servidor
    hora_actual = datetime.now().strftime('%H:%M')
    return {'hora': hora_actual}





@accionesTriggers.route("/terminoEjecutarEstrategia")
def terminoEjecutarEstrategia(): 
    return render_template('notificaciones/terminoEjecutarEstrategia.html')
@accionesTriggers.route('/herramientasAdmin_accionesTriggers_actualizaLuzTrigger')
def herramientasAdmin_accionesTriggers_actualizaLuzTrigger():
    luz = get.luzShedule_funcionando
    get.luzShedule_funcionando = False
    return jsonify({'luzTrigger_control':luz})
def control_tiempo_lectura_verifiar_estado(tiempo_espera_ms, tiempo_inicial_ms):
    # Obtener el tiempo actual en milisegundos
    tiempo_actual_ms = int(datetime.now().timestamp()) * 1000
    
    # Calcular la diferencia de tiempo desde la última vez que fue llamada la función
    diferencia_tiempo_ms = tiempo_actual_ms - tiempo_inicial_ms
    
    # Lógica para determinar si se puede realizar la lectura del sheet
    if diferencia_tiempo_ms < tiempo_espera_ms:
        # Aún no ha pasado suficiente tiempo, no se realiza la lectura del sheet
        #print(f"No se realiza la lectura del sheet. Tiempo transcurrido: {diferencia_tiempo_ms} ms.")
        # Retornar False u otra indicación según sea necesario
        return False
    else:
        # Ha pasado suficiente tiempo, se realiza la lectura del sheet
        minutos = diferencia_tiempo_ms // 60000
        segundos = (diferencia_tiempo_ms % 60000) // 1000
        #print(f"Se realiza la lectura del sheet. Tiempo transcurrido: {minutos}m {segundos}s.")
       
        
        # Reiniciar el tiempo inicial para la próxima llamada
        get.marca_de_tiempo_para_verificar_estado = tiempo_actual_ms
        
        # Retornar True u otra indicación según sea necesario
        return True