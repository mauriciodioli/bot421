
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
from sistemaDePagos.crearPlanes import cargarDatosPlan
import requests
from datetime import datetime, timedelta
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
import re

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test

#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

createSuscripcion = Blueprint('createSuscripcion',__name__)


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

@createSuscripcion.route('/create_order_suscripcion', methods=['POST'])
def create_order_suscripcion():    
    try:
       # Datos de la solicitud
        data = request.get_json()
        cardNumber = data.get("cardNumber")
        cardName = data.get("cardName")
        expiryDate =data.get("expiryDate")
        security_code = data.get("cvv")
        payer_email =data.get("email")
        transaction_amount = data.get("transaction_amount")
        reason = data.get("reason")
        access_token = data.get("access_token")
       # Limpiar espacios en blanco del número de tarjeta si los hay
        if cardNumber:
            cardNumber = re.sub(r"\s+", "", cardNumber)

        # Extraer el mes y el año de la fecha de vencimiento si está presente
        expiration_month = None
        expiration_year = None
        if expiryDate:
            expiration_month, expiration_year = expiryDate.split('/')

        # Obtener el año actual en formato de dos dígitos
        current_year = datetime.now().strftime("%y")

        # Si el año proporcionado es solo de dos dígitos, agregar el siglo
        if expiration_year and len(expiration_year) == 2:
            expiration_year = f"20{expiration_year}" if int(expiration_year) > int(current_year) else f"19{expiration_year}"

        # Construir el diccionario card_data
        card_data = {
            'card_number': cardNumber,
            'expiration_month': int(expiration_month) if expiration_month else None,
            'expiration_year': int(expiration_year) if expiration_year else None,
            'security_code': security_code,
            'cardholder': {
                'name': cardName
            }
        }
     
        
        #obtengo el token
        card_token_id = generate_card_token(card_data)
        
        #obtengo el payload de la suscripcion
       # payload = cargarDatosPlan(reason, payer_email, card_token_id)
          # Consultar el plan existente en la base de datos
        plan_existente = db.session.query(Plan).filter_by(reason=reason).first()

        if plan_existente is None:
            # Lanzar una excepción si el plan no existe
            raise Exception("Plan no encontrado en la base de datos")

        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Calcular la fecha un mes después
        fecha_un_mes_despues = fecha_actual + timedelta(days=30)

        # Formatear las fechas en el formato deseado
        start_date = fecha_actual.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = fecha_un_mes_despues.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Convertir los datos que deben ser enteros a enteros
        frequency = int(plan_existente.frequency)
        amount = int(plan_existente.amount)

        # Crear el payload con los datos del plan y otras informaciones
        payload = {
            "preapproval_plan_id": plan_existente.idPlan,
            "reason": plan_existente.reason,
            "external_reference": "YG-1234",
            "payer_email": payer_email,
            "card_token_id": card_token_id,
            "auto_recurring": {
                "frequency": frequency,
                "frequency_type": plan_existente.frequency_type,
                "start_date": start_date,
                "end_date": end_date,
                "transaction_amount": amount,
                "currency_id": plan_existente.currency_id
            },
            "back_url": "https://www.mercadopago.com.ar",
            "status": "authorized"
        }

        # Datos para crear la preaprobación
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+sdk_produccion
        }
       
        
     

        response = requests.post(PREAPPROVAL_URL, json=payload, headers=headers)
        response.raise_for_status()
        
       
        try:
            json_content = response.json()
            print("Contenido JSON:")
            print(json.dumps(json_content, indent=4))
            init_point = response.json()['init_point']
            print(init_point)
            return redirect(init_point)
        except json.JSONDecodeError:
            print("El contenido no es JSON válido.")
           
        
       
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


