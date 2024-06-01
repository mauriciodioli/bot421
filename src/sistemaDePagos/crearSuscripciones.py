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
#from mercadopago import MercadoPago

# Inicializar la instancia de MercadoPago con tus credenciales
#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

payment_page = Blueprint('payment_page',__name__)


YOUR_ACCESS_TOKEN = 'TEST-7897622499833241-051414-fa868bef7e053a323b97ebbd953bf95b-630055'
preapproval_plan_id = 'YOUR_PREAPPROVAL_PLAN_ID'


@payment_page.route('/create_subscription', methods=['POST'])
def create_subscription(): # Obtener los datos enviados desde el cliente
    data = request.json
    frequency = data.get('frequency')
    amount = data.get('amount')
    reason = data.get('reason')

    # Realizar la solicitud de creación de suscripción a MercadoPago
    url = 'https://api.mercadopago.com/preapproval_plan'
    headers = {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
        'Content-Type': 'application/json'
    }
    body = {
        "auto_recurring": {
            "frequency": frequency,
            "frequency_type": "months",
            "repetitions": 12,
            "billing_day": 10,
            "billing_day_proportional": False,
            "transaction_amount": amount,
            "currency_id": "ARS"
        },
        "back_url": "https://www.yoursite.com",
        "payment_methods_allowed": {
            "payment_types": [
                {
                    "id": "credit_card"
                }
            ],
            "payment_methods": [
                {
                    "id": "bolbradesco"
                }
            ]
        },
        "reason": reason
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))

    # Manejar la respuesta de MercadoPago
    if response.status_code == 201:
        return jsonify({'message': 'Subscription Created'}), 201
    else:
        return jsonify({'error': response.json()}), 400

