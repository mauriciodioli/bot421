
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
from dotenv import load_dotenv
import os

# Inicializar la instancia de MercadoPago con tus credenciales
#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

success_failure = Blueprint('success_failure',__name__)

@success_failure.route('/success/', methods=['GET'])
async def success():
    try:
        payment_id = request.args.get('collection_id')
        status = request.args.get('collection_status')
        external_reference = request.args.get('external_reference')
        payment_type = request.args.get('payment_type')
        
        response = {
            'status': 'success',
            'payment_id': payment_id,
            'status': status,
            'external_reference': external_reference,
            'payment_type': payment_type
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@success_failure.route('/webhook/', methods=['POST'])
async def webhook():
    try:
        data = await request.get_json()
        # Procesa los datos del webhook según tus necesidades
        print("Webhook received:", data)
        # Aquí puedes manejar la lógica de procesamiento de los datos recibidos
        
        return jsonify({'status': 'received'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
@success_failure.route('/failure/', methods=['GET'])
def failure():
    try:
        card_number = request.args.get('card_number')
        amount = request.args.get('amount')
        response = {'status': 'failure', 'message': 'Payment failed', 'card_number': card_number, 'amount': amount}
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
@success_failure.route('/pending/', methods=['GET'])
def pending():    
    try:
        card_number = request.args.get('card_number')
        amount = request.args.get('amount')
        response = {'status': 'pending', 'message': 'Payment pending', 'card_number': card_number, 'amount': amount}
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})