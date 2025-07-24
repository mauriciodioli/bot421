
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
from utils.db_session import get_db_session 

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test


#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

updatePlanes = Blueprint('updatePlanes',__name__)


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


@updatePlanes.route('/updatePlanes_preapproval_plan/', methods=['PUT'])
def update_planes_preapproval_plan():
    try:
        data = request.json
        plan_id = data.get('id')
        frequency = data.get('frequency')
        amount = data.get('amount')
        reason = data.get('reason')
        frequency_type = data.get('frequency_type')
        currency_id = data.get('currency_id')
        repetitions = data.get('repetitions')
        billing_day = data.get('billing_day')
        access_token = data.get('access_token')

        if access_token and Token.validar_expiracion_token(access_token=access_token):
            app = current_app._get_current_object()

            try:
                user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                with get_db_session() as session:
                    plan = session.query(Plan).filter_by(idPlan=plan_id).first()

                    if plan is None:
                        return jsonify({"error": "Plan no encontrado o no autorizado"}), 404

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
                        "back_url": SUCCESS_URL
                    }

                    update_url = f"{PREAPPROVAL_PLAN_URL}/{plan_id}"
                    response = requests.put(update_url, json=payload, headers=headers)
                    response.raise_for_status()

                    plan.frequency = frequency
                    plan.amount = amount
                    plan.reason = reason
                    plan.frequency_type = frequency_type
                    plan.currency_id = currency_id
                    plan.repetitions = repetitions
                    plan.billing_day = billing_day

                    session.commit()
                    

                    return jsonify({"success": True, "message": "Plan updated successfully"})
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": str(err)}), err.response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
