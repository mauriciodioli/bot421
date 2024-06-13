
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
from datetime import datetime, timedelta
import jwt
from models.usuario import Usuario
from models.brokers import Broker
from models.payment_page.plan import Plan
import mercadopago


from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test


#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

crearPlanes = Blueprint('crearPlanes',__name__)


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
                currency_id=currency_id,
                billing_day=billing_day
            )
            db.session.add(nuevo_plan)
        
            db.session.commit() 
        planes = db.session.query(Plan).all()
        db.session.close()

        # Serializar los planes
        planes_serializados = [
            {
                'id': plan.idPlan,
                'frequency': plan.frequency,
                'amount': plan.amount,
                'reason': plan.reason,
                'frequency_type': plan.frequency_type,
                'currency_id': plan.currency_id,
                'repetitions': plan.repetitions,
                'billing_day': plan.billing_day
            } for plan in planes
        ]

        return jsonify({'planes': planes_serializados})
    except requests.HTTPError as e:
        error_response = e.response.json()
        return jsonify({"error": error_response}), e.response.status_code
    

def cargarDatosPlan(reason, payer_email, card_token_id):
    try:
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
            "back_url": SUCCESS_URL,
            "status": "authorized"
        }

       
        # Retorna el JSON como string
        return payload

    except Exception as e:
        # Manejar la excepción aquí
        return {"error": str(e)}
