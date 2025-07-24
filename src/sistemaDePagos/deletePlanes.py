
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
from utils.db_session import get_db_session 


#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

deletePlanes = Blueprint('deletePlanes',__name__)


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

@deletePlanes.route('/deletePlanes_preapproval_plan/<string:plan_id>', methods=['GET'])
def deletePlanes_preapproval_plan(plan_id): 
    try:
        access_token = request.args.get('access_token')
        if access_token and Token.validar_expiracion_token(access_token=access_token):
            app = current_app._get_current_object()

            try:
                user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                with get_db_session() as session:
                    plan = session.query(Plan).filter_by(idPlan=plan_id).first()

                    if plan is None:
                        return jsonify({"error": "Plan no encontrado o no autorizado"}), 404

                    session.delete(plan)
                    session.commit()
                 

                    return jsonify({"success": True, "message": "Plan eliminado correctamente"})
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token inválido"}), 401
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "No autorizado"}), 401
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": str(err)}), err.response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
