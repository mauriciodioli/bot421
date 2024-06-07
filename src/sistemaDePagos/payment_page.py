
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

payment_page = Blueprint('payment_page',__name__)

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


    

@payment_page.route('/crear_preferencia', methods=['POST'])
def crear_preferencia():
    
    preference_id = obtener_preference_id()
    return jsonify({'preference_id': preference_id})



payment_page.route('/producto/<int:producto_id>')
def producto(producto_id):
    return render_template(f'producto{producto_id}.html')


@payment_page.route('/create_order/', methods=['POST'])
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



@payment_page.route('/create_order_plan/', methods=['POST'])
def create_order_plan():
    try:
        # Obtén los datos de la solicitud
        data = request.get_json()

        # Extrae los valores necesarios
        costo_base = data.get("items")[0].get("unit_price")
        porcentaje_retorno = data.get("porcentaje_retorno", 0)
        costo_base = float(costo_base)

        # Asegúrate de que el costo base sea al menos 15 ARS
        if costo_base < 15.00:
            return jsonify({"error": "El monto mínimo permitido es de 15 ARS"}), 400

        # Crea los datos de la preferencia  
             
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + sdk_prueba
        }
        payload = {
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "repetitions": 12,
                "billing_day": 10,
                "billing_day_proportional": False,
                "free_trial": {
                    "frequency": 1,
                    "frequency_type": "months"
                },
                "transaction_amount": costo_base,  # Usa el costo_base obtenido
                "currency_id": "ARS"
            },
            "back_url": SUCCESS_URL,
            "payment_methods_allowed": {
                "payment_types": [
                    {"id": "credit_card"}
                ],
                "payment_methods": [
                    {"id": "bolbradesco"}
                ]
            },
            "reason": "Bot de estrategias"
        }

        response = requests.post(PREAPPROVAL_PLAN_URL, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.HTTPError as e:
        # Imprime el contenido de la respuesta de error
        error_response = e.response.json()
        print(f"Error: {error_response}")
        return jsonify({"error": error_response}), e.response.status_code


@payment_page.route('/create_order_suscripcion', methods=['POST'])
def create_order_suscripcion():    
    try:
        # Datos de la solicitud
        data = request.get_json()
        preapproval_plan_id = data.get("preapproval_plan_id")
        payer_email = data.get("payer_email")
        card_token_id = data.get("card_token_id")
        transaction_amount = data.get("transaction_amount")
        
        
        # Ejemplo de uso
        card_data = {
            'card_number': '5031755734530604',
            'expiration_month': 11,
            'expiration_year': 2025,
            'security_code': '123',
            'cardholder': {
                'name': 'APRO'
            }
        }
        
        card_token_id = generate_card_token(card_data)
        # Datos para crear la preaprobación
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+sdk_prueba
        }
        payload = {
            "preapproval_plan_id": preapproval_plan_id,
            "reason": "Yoga classes",
            "external_reference": "YG-1234",
            "payer_email": payer_email,
            "card_token_id": card_token_id,
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "start_date": "2020-06-02T13:07:14.260Z",
                "end_date": "2022-07-20T15:59:52.581Z",
                "transaction_amount": transaction_amount,
                "currency_id": "ARS"
            },
            "back_url": "https://www.mercadopago.com.ar",
            "status": "authorized"
        }

        response = requests.post(PREAPPROVAL_URL, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.HTTPError as e:
        error_response = e.response.json()
        return jsonify({"error": error_response}), e.response.status_code
    

    
    
def generate_card_token(card_data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+sdk_prueba  # Reemplaza con tu token de acceso real
    }

    response = requests.post(CARD_TOKEN_URL, json=card_data, headers=headers)
    response.raise_for_status()
    
    return response.json()['id']

async def create_preference(sdk, preference_data, headers,url):
    async with httpx.AsyncClient() as client:
       
        response = await client.post(
            url,
            json=preference_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
def obtener_preference_id():
    # Configurar el SDK de Mercado Pago con tu clave pública
    global mp
    # Crear un objeto de preferencia de pago
    preference = {
        "items": [
            {
                "title": "Producto de ejemplo",
                "quantity": 1,
                "currency_id": "ARS",  # Moneda (ARS para Argentina)
                "unit_price": 1000  # Precio en centavos
            }
        ]
    }
    
    # Crear la preferencia en Mercado Pago
    preference_response = mp.preference().create(preference)   
    preference_result = preference_response["response"]

    # Obtener el ID de preferencia de la respuesta
    preference_id = preference_result['id']

    return preference_id

#Llamar a create_preapproval_plan() para crear un plan de preaprobación.
#Llamar a create_preference() o create_order() para crear una preferencia de pago.
#Después de que el cliente complete el pago, redirigirlo a la página de éxito (/success) o manejar la lógica de redireccionamiento según tu flujo.
#Finalmente, llamar a create_order_suscripcion() para suscribir al cliente al plan de preaprobación creado previamente.



