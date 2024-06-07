
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
from models.payment_page.plan import Plan
import mercadopago
import asyncio
import httpx

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test

#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

crearPlanes = Blueprint('crearPlanes',__name__)

preapproval_plan_id = 'YOUR_PREAPPROVAL_PLAN_ID'

# Definir URLs utilizando el dominio
SUCCESS_URL = f"{DOMAIN}/success"
FAILURE_URL = f"{DOMAIN}/failure"
PENDING_URL = f"{DOMAIN}/pending"
NOTIFICATION_URL = f"{DOMAIN}/webhook"

# Definir URLs de la API de MercadoPago
CARD_TOKEN_URL = f"{MERCADOPAGO_URL}/v1/card_tokens"
PREFERENCE_URL = f"{MERCADOPAGO_URL}/checkout/preferences"
PREAPPROVAL_PLAN_URL = f"{MERCADOPAGO_URL}/preapproval_plan"
PREAPPROVAL_URL = f"{MERCADOPAGO_URL}/preapproval"


mp = mercadopago.SDK(sdk_produccion)


@crearPlanes.route('/create_preapproval_html', methods=['GET'])
def create_preapproval_html():
    layout = request.args.get('layout', 'layout')  # Obtiene el valor de 'layout' de la URL, 'default' es un valor predeterminado
    return render_template('sistemaDePagos/crearPlanes.html', layout=layout)

@crearPlanes.route('/create_preapproval_plan/', methods=['POST'])
def create_preapproval_plan():
    try:
        data = request.json
        frequency = data.get('frequency')
        amount = data.get('amount')
        reason = data.get('reason')
        frequency_type = data.get('frequency_type')
        currency_id = data.get('currency_id')
        repetitions =  data.get('repetitions')
        billing_day =  data.get('billing_day')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + sdk_prueba
        }
        payload = {
            "reason": reason,
            "auto_recurring": {
                "frequency": frequency,
                "frequency_type": frequency_type,
                "repetitions": repetitions,
                "billing_day": billing_day,
                "billing_day_proportional": True,
                "free_trial": {
                    "frequency": frequency,
                    "frequency_type": frequency_type
                },
                "transaction_amount": amount,
                "currency_id": currency_id
            },
            "payment_methods_allowed": {
                "payment_types": [
                    {}
                ],
                "payment_methods": [
                    {}
                ]
            },
            "back_url": SUCCESS_URL
        }
      
        response = requests.post(PREAPPROVAL_PLAN_URL, json=payload, headers=headers)
        
        response.raise_for_status()
        
        
        # Convertir el contenido JSON en un diccionario de Python
    
        response_data = response.json()
       # Intentamos encontrar el registro con el symbol específico
        idPlan = response_data.get('id')
        plan_existente = db.session.query(Plan).filter_by(reason=reason).first()


        if not plan_existente:
            # Si no existe, creamos un nuevo registro
            nuevo_plan = Plan(
                idPlan=idPlan,
                frequency=frequency,
                amount=amount,
                reason=reason,
                frequency_type=frequency_type,
                repetitions=repetitions,
                billing_day=billing_day
            )
            db.session.add(nuevo_plan)
        
            db.session.commit() 
        
        db.session.close()
        return jsonify(response.json())
    except requests.HTTPError as e:
        error_response = e.response.json()
        return jsonify({"error": error_response}), e.response.status_code