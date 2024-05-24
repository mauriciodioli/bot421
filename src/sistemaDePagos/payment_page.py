
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

payment_page = Blueprint('payment_page',__name__)

@payment_page.route('/pago', methods=['GET'])
def pago():
    # Obtener los valores de los inputs ocultos
    costo_base = request.args.get('costo_base')
    porcentaje_retorno = request.args.get('porcentaje_retorno')
    
    # Convertir los valores a números flotantes
    try:
        costo_base = float(costo_base)
        porcentaje_retorno = float(porcentaje_retorno)
    except (ValueError, TypeError):
        # Manejar el caso en que los valores no puedan ser convertidos a flotantes
        costo_base = 0
        porcentaje_retorno = 0
    
    # Calcular el total
   # total = costo_base * (1 + porcentaje_retorno / 100)
    total = costo_base
    # Renderizar la plantilla y pasar los valores como argumentos
    return render_template('sistemaDePagos/payment_page.html', costo_base=costo_base, porcentaje_retorno=porcentaje_retorno, total=total)


@payment_page.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        # Aquí se manejaría la lógica de procesamiento de pagos
        # Por ejemplo, integrar con una API de pasarela de pagos
        data = request.json
        card_number = data.get('card_number')
        amount = data.get('amount')
        
        # Respuesta simulada para el ejemplo
        response = {
            'status': 'success',
            'message': f'Payment of {amount} ARS with card ending {card_number[-4:]} processed successfully.'
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
payment_page.route('/producto/<int:producto_id>')
def producto(producto_id):
    return render_template(f'producto{producto_id}.html')

@payment_page.route('/payment_page_process_payment/', methods=['POST'])
def payment_page_process_payment():
    try:
        data = request.json
        card_number = data.get('card_number')
        amount = data.get('amount')
        response = {
            'status': 'success',
            'message': f'Payment of {amount} ARS with card ending {card_number[-4:]} processed successfully.'
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})