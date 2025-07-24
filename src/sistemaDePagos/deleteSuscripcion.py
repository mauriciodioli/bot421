
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
from models.cuentas import Cuenta
from sistemaDePagos.tarjetaUsuario import altaTarjeta
from models.payment_page.plan import Plan
from models.payment_page.tarjetaUsuario import TarjetaUsuario
from models.payment_page.suscripcionPlanUsuario import SuscripcionPlanUsuario
import mercadopago
import asyncio
import re

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test
from utils.db_session import get_db_session 


#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

deleteSuscripcion = Blueprint('deleteSuscripcion',__name__)


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
# URL para cancelar la suscripción preaprobada



mp = mercadopago.SDK(sdk_produccion)

@deleteSuscripcion.route('/deleteSuscripcion_order_suscripcion/<preapproval_id>', methods=['DELETE'])
def deleteSuscripcion_order_suscripcion(preapproval_id):
    # Datos de la solicitud
    data = request.get_json()  
    access_token = data.get("access_token")   
    layout =  data.get('layout')
   
    
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        correo_electronico = decoded_token.get("correo_electronico")
        numero_de_cuenta = decoded_token.get("numero_de_cuenta")
        user_id = decoded_token.get("sub")
         # Verificar si ya existe una suscripción para este usuario y este id de plan
        url = f"{PREAPPROVAL_URL}/{preapproval_id}"
        
        # Configurar los headers de la solicitud
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+sdk_produccion
        }
        # El payload con el nuevo estado de la suscripción
        payload = {
            "status": "cancelled"
        }
    
        try:
            response = requests.put(url, json=payload, headers=headers)
            json_content = response.json()
            with get_db_session() as session:
                #carga suscripcion en tabla suscripcion plan usuario
                suscripciones = session.query(SuscripcionPlanUsuario).filter_by(user_id=user_id).all()
                
         
                # Serializar los planes
                suscripciones_serializados = [
                    {
                        'payer_id': suscripcion.payer_id,
                        'accountCuenta': suscripcion.accountCuenta,
                        'status': suscripcion.status,
                        'reason': suscripcion.reason,
                        'date_created': suscripcion.date_created,
                        'frequency': suscripcion.frequency,
                        'quotas': suscripcion.quotas,
                        'pending_charge_amount': suscripcion.pending_charge_amount,
                        'payment_method_id': suscripcion.payment_method_id,
                        'billing_day': suscripcion.billing_day
                    } for suscripcion in suscripciones
                ]

                return jsonify({'suscripciones': suscripciones_serializados, 'layout': layout})
            
        except Exception as e:
            print("Excepción al cancelar la suscripción: ", str(e))
