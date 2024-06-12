
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
from models.payment_page.tarjetaUsuario import TarjetaUsuario
import mercadopago

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test

#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

payment_page = Blueprint('payment_page',__name__)


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


@payment_page.route('/pyment_page_carga_numero_tarjeta/', methods=['POST'])
def pyment_page_carga_numero_tarjeta():    
      if request.method == 'POST':
         access_token = request.form['access_token']
         if access_token and Token.validar_expiracion_token(access_token=access_token): 
            # Decodificar el token una sola vez
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])

            # Obtener los valores del token decodificado
            correo_electronico = decoded_token.get("correo_electronico")
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")

            tarjeta_existente = db.session.query(TarjetaUsuario).filter_by(user_id=user_id).first()

         return jsonify({"message": "Tarjeta creada con éxito", "tarjeta": tarjeta_existente.numeroTarjeta}), 201

    
@payment_page.route('/pago/', methods=['POST'])
def pago():
    if request.method == 'POST':
        costo_base = float(request.form['costo_base'])
        reason = request.form['reason']
        porcentaje_retorno = float(request.form['porcentaje_retorno'])

        # Calcular el total
        total = costo_base * (1 + porcentaje_retorno / 100)

        # Aquí puedes realizar cualquier operación adicional necesaria

        # Renderizar el template con los datos necesarios
        return render_template('sistemaDePagos/payment_page.html', costo_base=costo_base, porcentaje_retorno=porcentaje_retorno, total=total, reason = reason)
    else:
        return "Método de solicitud no permitido"



@payment_page.route('/crear_preferencia', methods=['POST'])
def crear_preferencia():
    
    preference_id = obtener_preference_id()
    return jsonify({'preference_id': preference_id})



payment_page.route('/producto/<int:producto_id>')
def producto(producto_id):
    return render_template(f'producto{producto_id}.html')





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



