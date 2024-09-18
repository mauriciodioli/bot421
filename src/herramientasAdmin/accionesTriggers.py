from flask import Blueprint, render_template,current_app ,session,request, redirect, url_for, flash,jsonify
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


@accionesTriggers.route('/verificar_estado', methods=['POST'])
def verificar_estado():
    try:
        # Obtén los datos JSON del cuerpo de la solicitud
        data = request.get_json()
        
        # Verifica si los datos se obtuvieron correctamente
        if not data:
            raise BadRequest('No se recibió ningún dato JSON.')

        # Obtén los valores del JSON
        idTrigger = data.get('idTrigger')
        userId = data.get('userId')
        cuenta = data.get('cuenta')
        
        # Verifica si idTrigger y cuenta están presentes
        if idTrigger is None or cuenta is None:
            raise BadRequest('Faltan parámetros requeridos: idTrigger o cuenta.')

        # Verifica si la cuenta existe en el diccionario
        parametros = get.estrategias_usuario__endingOperacionBot.get(idTrigger)
        
        # Verifica si se encontraron parámetros
        if parametros:
            # Desglosar las variables
            account = parametros.get('account')
            user_id = parametros.get('user_id')
            symbol = parametros.get('symbol')
            status = parametros.get('status')
            mensaje = parametros.get('mensaje')
            # Compara el tiempo actual con el tiempo de inicio
            tiempo_actual = datetime.now()
            if tiempo_inicio:
                tiempo_inicio = datetime.strptime(tiempo_inicio, '%Y-%m-%d %H:%M:%S')
                if tiempo_actual - tiempo_inicio > timedelta(minutes=5):
                    return jsonify({'estado': 'terminado', 'account': account, 'mensaje': 'Operación superó los 5 minutos.'}), 200

            # Verifica el estado y responde apropiadamente
            if status == 'termino':
                return jsonify({'estado': 'listo', 'account': account, 'mensaje': mensaje}), 200
        
        return jsonify({'estado': 'en_proceso'}), 200

    except BadRequest as e:
        # Maneja los errores de solicitud incorrecta
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Maneja cualquier otro error
        return jsonify({'error': 'Ocurrió un error inesperado.', 'detalle': str(e)}), 500

@accionesTriggers.route('/herramientasAdmin_accionesTriggers_actualizaLuzTrigger')
def herramientasAdmin_accionesTriggers_actualizaLuzTrigger():
    luz = get.luzShedule_funcionando
    get.luzShedule_funcionando = False
    return jsonify({'luzTrigger_control':luz})