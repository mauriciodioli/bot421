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
import tokens.token as Token
import jwt
from models.usuario import Usuario
from models.brokers import Broker

suscripciones_producto_usuario = Blueprint('suscripciones_producto_usuario',__name__)

YOUR_ACCESS_TOKEN = 'TEST-7897622499833241-051414-fa868bef7e053a323b97ebbd953bf95b-630055'
preapproval_plan_id = 'YOUR_PREAPPROVAL_PLAN_ID'

@suscripciones_producto_usuario.route('/crearSuscricpionesMP/', methods=['GET'])
def crearSuscricpionesMP():
    # Obtiene el parámetro 'productoId' de la cadena de consulta
    OrigenLayout = request.args.get('layout')
   
    return render_template('sistemaDePagos/crearSuscripciones.html',layout = OrigenLayout)

@suscripciones_producto_usuario.route('/create_subscription', methods=['POST'])
def create_subscription():
    data = request.json
    frequency = data.get('frequency')
    amount = data.get('amount')
    reason = data.get('reason')

 # Aquí debes incluir tu lógica para autenticarte con la API de Mercado Libre
    # y obtener un token de acceso válido

    # URL de la API de suscripciones de Mercado Libre
    subscription_api_url = 'https://api.mercadolibre.com/subscriptions'

    # Datos de la suscripción a enviar
    subscription_data = {
        'frequency': frequency,
        'amount': amount,
        'reason': reason
    }

    headers = {
        'Authorization':YOUR_ACCESS_TOKEN,  # Reemplaza 'tu_token_de_acceso' con tu token real
        'Content-Type': 'application/json'
    }

    try:
        # Envía la solicitud para crear la suscripción
        response = requests.post(subscription_api_url, json=subscription_data, headers=headers)
        
        # Verifica si la solicitud fue exitosa
        if response.status_code == 201:  # Código 201 significa creado
            return jsonify({'message': 'Suscripción creada exitosamente'}), 201
        else:
            return jsonify({'error': 'Error al crear la suscripción'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500