
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

@payment_page.route('/pago')
def pago():
    return render_template('pago.html')


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