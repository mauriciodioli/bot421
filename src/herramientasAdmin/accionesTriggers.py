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
import threading

import pandas as pd
import pyRofex #lo utilizo para test
import time    #lo utilizo para test
import asyncio

from flask_paginate import Pagination, get_page_parameter

import json
import os
import copy

accionesTriggers = Blueprint('accionesTriggers',__name__)


@accionesTriggers.route('/verificar_estado', methods=['POST'])
def verificar_estado():
    data = request.get_json()  # Obtén los datos JSON del cuerpo de la solicitud
    idTrigger = data.get('idTrigger')
    userId = data.get('userId')  # Obtener userId
    cuenta = data.get('cuenta')  # Obtener userCuenta
    
    # Verifica si la cuenta existe en el diccionario
    parametros = get.estrategias_usuario__endingOperacionBot.get(idTrigger)
    
    if  parametros:
        # Desglosar las variables
        account = parametros.get('account')
        user_id = parametros.get('user_id')
        symbol = parametros.get('symbol')
        status = parametros.get('status')
        mensaje = parametros.get('mensaje')
    
    if parametros and parametros.get('status') == 'termino':
        return jsonify({'estado': 'listo', 'account': parametros['account'],'mensaje':parametros['mensaje']}), 200
    return jsonify({'estado': 'en_proceso'}), 200

@accionesTriggers.route('/herramientasAdmin_accionesTriggers_actualizaLuzTrigger')
def herramientasAdmin_accionesTriggers_actualizaLuzTrigger():
    luz = get.luzShedule_funcionando
    get.luzShedule_funcionando = False
    return jsonify({'luzTrigger_control':luz})