
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
import mercadopago
import asyncio
import httpx

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test

#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

createOrden = Blueprint('createOrden',__name__)


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

@createOrden.route('/create_order/', methods=['POST'])
async def create_order():
    try:
        # Obtén los datos de la solicitud
        data = request.get_json()

        # Extrae los valores necesarios
        costo_base = data.get("items")[0].get("unit_price")
        porcentaje_retorno = request.form.get("porcentaje_retorno", 0)
        costo_base = float(costo_base)
        # Crea los datos de la preferencia
        preference_data = {
            "items": [
                {
                    "title": "Donacion de prueba",  # Título del artículo
                    "quantity": 1,
                    "unit_price": costo_base,  # Precio unitario
                    "currency_id": "ARS"
                }
            ],
            "back_urls": {
                "success": SUCCESS_URL,
                "failure": FAILURE_URL,
                "pending": PENDING_URL
            },
            "notification_url": NOTIFICATION_URL,
             "auto_return": "approved"
        }

       # Encabezados para la solicitud
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + sdk_produccion,  # Token de acceso
            'X-Idempotency-Key':'123546'
        }

        # Llama a la función create_preference
        url = f"{MERCADOPAGO_URL}/checkout/preferences"
       
        preference_response = await create_preference(sdk_produccion, preference_data, headers,url)
        init_point = preference_response.get("init_point")
       
        # Devuelve la URL de inicialización de la preferencia
        return jsonify({"init_point": init_point})

    except httpx.HTTPStatusError as e:
        return jsonify({"error": str(e)}), e.response.status_code
    
async def create_preference(sdk, preference_data, headers,url):
    async with httpx.AsyncClient() as client:
       
        response = await client.post(
            url,
            json=preference_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    