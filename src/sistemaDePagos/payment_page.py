
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


# Inicializar la instancia de MercadoPago con tus credenciales
#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

payment_page = Blueprint('payment_page',__name__)
sdk_prueba = "APP_USR-5717567227383881-060409-1e8fafe5e95b1bc7f5b5c9a86dc40999-1835443126" #de prueba en el usuario vendedor
sdk = "APP_USR-5717567227383881-060409-1e8fafe5e95b1bc7f5b5c9a86dc40999-1835443126" #de produccion en el usuario vendedor de prueba
YOUR_ACCESS_TOKEN = 'TEST-7897622499833241-051414-fa868bef7e053a323b97ebbd953bf95b-630055' #de produccion
preapproval_plan_id = 'YOUR_PREAPPROVAL_PLAN_ID'


mp = mercadopago.SDK(YOUR_ACCESS_TOKEN)

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

@payment_page.route('/crear_preferencia', methods=['POST'])
def crear_preferencia():
    
    preference_id = obtener_preference_id()
    return jsonify({'preference_id': preference_id})

@payment_page.route('/pagoMercadoPago/', methods=['POST'])
def pagoMercadoPago():
    try:
        # Obtén los datos del formulario HTML
        costo_base = float(request.form.get("costo_base", 0))
        porcentaje_retorno = float(request.form.get("porcentaje_retorno", 0))
        
        # Calcula el total
        total = costo_base * (1 + porcentaje_retorno / 100)
        
        # Renderiza la plantilla "mercadoPago.html" y pasa los datos como argumentos
        return render_template('sistemaDePagos/mercadoPago.html', costo_base=costo_base, porcentaje_retorno=porcentaje_retorno, total=total)
    
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input data"}), 400

@payment_page.route('/pago/', methods=['POST'])
def pago():
     # Convertir los valores a números flotantes
    try:
        data = request.form
        costo_base = int(data['costo_base'])
        porcentaje_retorno = float(data['porcentaje_retorno'])
    
   
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
  
    return jsonify({"init_point": 'sistemaDePagos/mercadoPago.html'})

@payment_page.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        data = request.json
        payment_data = {
            "transaction_amount": data['transaction_amount'],
            "token": data['token'],
            "description": data['description'],
            "payment_method_id": data['payment_method_id'],
            "installments": data['installments'],
            "payer": {
                "email": data['payer']['email']
            }
        }
        result = mp.payment().create(payment_data)
        payment = result["response"]
        return jsonify(payment)
    except Exception as e:
        return jsonify({'error': str(e)})

payment_page.route('/producto/<int:producto_id>')
def producto(producto_id):
    return render_template(f'producto{producto_id}.html')


async def create_preference(sdk, preference_data, headers,url):
    async with httpx.AsyncClient() as client:
       
        response = await client.post(
            url,
            json=preference_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

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
                "success": "https://89ae-190-225-182-66.ngrok-free.app/success",
                "failure": "https://89ae-190-225-182-66.ngrok-free.app/failure",
                "pending": "https://89ae-190-225-182-66.ngrok-free.app/pending"
            },
             "notification_url": "https://89ae-190-225-182-66.ngrok-free.app/webhook",
             "auto_return": "approved"
        }

       # Encabezados para la solicitud
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + sdk,  # Token de acceso
            'X-Idempotency-Key':'123546'
        }

        # Llama a la función create_preference
        url = "https://api.mercadopago.com/checkout/preferences"
        preference_response = await create_preference(sdk, preference_data, headers,url)
        init_point = preference_response.get("init_point")
       
        # Devuelve la URL de inicialización de la preferencia
        return jsonify({"init_point": init_point})

    except httpx.HTTPStatusError as e:
        return jsonify({"error": str(e)}), e.response.status_code


    
@payment_page.route('/success/', methods=['GET'])
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

@payment_page.route('/webhook/', methods=['POST'])
async def webhook():
    try:
        data = await request.get_json()
        # Procesa los datos del webhook según tus necesidades
        print("Webhook received:", data)
        # Aquí puedes manejar la lógica de procesamiento de los datos recibidos
        
        return jsonify({'status': 'received'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
@payment_page.route('/failure/', methods=['GET'])
def failure():
    try:
        card_number = request.args.get('card_number')
        amount = request.args.get('amount')
        response = {'status': 'failure', 'message': 'Payment failed', 'card_number': card_number, 'amount': amount}
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
@payment_page.route('/pending/', methods=['GET'])
def pending():    
    try:
        card_number = request.args.get('card_number')
        amount = request.args.get('amount')
        response = {'status': 'pending', 'message': 'Payment pending', 'card_number': card_number, 'amount': amount}
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


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
        url = 'https://api.mercadopago.com/preapproval_plan'
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
            "back_url": "https://89ae-190-225-182-66.ngrok-free.app/success",
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

        response = requests.post(url, json=payload, headers=headers)
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

        # Datos para crear la preaprobación
        url = 'https://api.mercadopago.com/preapproval'
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

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.HTTPError as e:
        error_response = e.response.json()
        return jsonify({"error": error_response}), e.response.status_code