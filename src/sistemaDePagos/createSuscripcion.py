
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
        pagoTarjetaPrevia = data.get('pagoTarjetaPrevia')
        access_token = data.get("access_token")
        isChecked = data.get('isChecked')
       
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            correo_electronico = decoded_token.get("correo_electronico")
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")
            if pagoTarjetaPrevia == False:
                cardName = data.get("cardName")
                expiryDate =data.get("expiryDate")
                security_code = data.get("cvv")
                payer_email =data.get("email")
            else:
                tarjeta_existente = db.session.query(TarjetaUsuario).filter_by(user_id=user_id).first()
                db.session.close()
                cardName = tarjeta_existente.nombreApellidoTarjeta
                expiryDate =tarjeta_existente.fecha_vencimiento
                security_code = tarjeta_existente.cvv
                payer_email = tarjeta_existente.correo_electronico
                    
            
            cardNumber = data.get("cardNumber")           
            transaction_amount = data.get("transaction_amount")        
            reason = data.get("reason")
        
            if cardNumber:
                cardNumber = re.sub(r"\s+", "", cardNumber)
            
            required_fields = ["cardNumber", "cardName", "expiryDate", "security_code", "payer_email", "transaction_amount", "reason", "access_token"]
            
            for field in required_fields:
                 if not locals()[field]: 
                    return jsonify({"message": f"El campo {field} es obligatorio."}), 400
        # Crear un diccionario con los datos recogidos
            datos = {
                "cardNumber": cardNumber,
                "cardName": cardName,
                "expiryDate": expiryDate,
                "cvv": security_code,
                "email": payer_email,
                "transaction_amount": transaction_amount,
                "reason": reason
            }
            
            if isChecked == True:
                cargarTarjeta(user_id,numero_de_cuenta,datos)

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
            
    
            # Consultar el plan existente en la base de datos
            plan_existente = db.session.query(Plan).filter_by(reason=reason).first()
            db.session.close()
            if plan_existente is None:
                # Lanzar una excepción si el plan no existe
                raise Exception("Plan no encontrado en la base de datos")


            # Cargar el payload para la suscripción
            payload = cargarDatosPlan(reason, payer_email, card_token_id)
        
            # Datos para crear la preaprobación
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+sdk_produccion
            }
        
            try:
        

                response = requests.post(PREAPPROVAL_URL, json=payload, headers=headers)                
                json_content = response.json()
                # Imprimir el JSON ordenado
                print(json.dumps(json_content, indent=4))
                #carga suscripcion en tabla suscripcion plan usuario
                cargarSuscripcion(user_id,numero_de_cuenta,json_content)
                init_point = json_content['init_point']
                return jsonify({
                    'success': True,
                    'init_point': init_point
                })
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                return jsonify({
                    'success': False,
                    'message': 'Error processing the payment.'
                })
            except json.JSONDecodeError:
                print("Invalid JSON response")
                return jsonify({
                    'success': False,
                    'message': 'Invalid JSON response from MercadoPago.'
                })
            
            
            
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


def cargarSuscripcion(user_id, numero_de_cuenta, json_content):
    try:
        # Extraer los datos necesarios de json_content
        payer_id = int(json_content.get("payer_id"))
        preapproval_plan_id = json_content.get("preapproval_plan_id")
        status = json_content.get("status")
        reason = json_content.get("reason")
        date_created = json_content.get("date_created")
        frequency = int(json_content.get("auto_recurring", {}).get("frequency"))
        frequency_type = json_content.get("auto_recurring", {}).get("frequency_type")
        currency_id = json_content.get("auto_recurring", {}).get("currency_id")
        start_date = json_content.get("auto_recurring", {}).get("start_date")
        end_date = json_content.get("auto_recurring", {}).get("end_date")
        billing_day = int(json_content.get("auto_recurring", {}).get("billing_day"))
        quotas = int(json_content.get("auto_recurring", {}).get("transaction_amount"))
        pending_charge_amount = float(json_content.get("summarized",{}).get("pending_charge_amount"))
        next_payment_date = json_content.get("next_payment_date")
        payment_method_id = json_content.get("payment_method_id")
        card_id = json_content.get("card_id")

        # Verificar si ya existe una suscripción para este usuario y este id de plan
        suscripcion_existente = db.session.query(SuscripcionPlanUsuario).filter_by(
            user_id=user_id,
            preapproval_plan_id=preapproval_plan_id
        ).first()

        if suscripcion_existente:
            return jsonify({"message": "Ya existe una suscripción para este usuario y este id de plan"}), 400

        # Crear la nueva suscripción
        nueva_suscripcion = SuscripcionPlanUsuario(
            payer_id=payer_id,
            user_id=user_id,
            accountCuenta=numero_de_cuenta,
            status=status,
            reason=reason,
            date_created=date_created,
            preapproval_plan_id=preapproval_plan_id,
            frequency=frequency,
            frequency_type=frequency_type,
            currency_id=currency_id,
            start_date=start_date,
            end_date=end_date,
            billing_day=billing_day,
            quotas=quotas,
            pending_charge_amount=pending_charge_amount,
            next_payment_date=next_payment_date,
            payment_method_id=payment_method_id,
            card_id=card_id
        )

        # Agregar y confirmar la nueva suscripción en la base de datos
        db.session.add(nueva_suscripcion)
        db.session.commit()
        db.session.close()

        return jsonify({"message": "Suscripción creada con éxito", "suscripcion": nueva_suscripcion.id}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500



def cargarTarjeta(user_id,numero_de_cuenta,data):
    # Convertir los datos a la estructura esperada por altaTarjeta
    # Obtener el objeto Usuario correspondiente al user_id
    if data["cardNumber"]:
       cardNumber = re.sub(r"\s+", "", data["cardNumber"])  # Aquí se corrige el uso de data["cardNumber"]

    datos_tarjeta = {
        "user_id": int(user_id),  # Asegúrate de obtener esto correctamente según tu lógica
        "numeroTarjeta":cardNumber,
        "fecha_vencimiento": data["expiryDate"],
        "cvv": data["cvv"],
        "nombreApellidoTarjeta": data["cardName"],
        "correo_electronico": data["email"],
        "accountCuenta":numero_de_cuenta  # Asegúrate de que este campo esté presente si es necesario
    }

    # Llamar a la función altaTarjeta con los datos JSON
    response = altaTarjeta(datos_tarjeta)
    return response

