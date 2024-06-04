from flask import Blueprint, render_template, request, jsonify, current_app
import requests
import os
import json
import logging

# Crear el Blueprint
suscripciones_producto_usuario = Blueprint('suscripciones_producto_usuario', __name__)

# Variables globales (para propósitos de demostración, en producción utiliza un almacenamiento seguro)
YOUR_ACCESS_TOKEN = 'Bearer TEST-7897622499833241-051414-fa868bef7e053a323b97ebbd953bf95b-630055'
PREAPPROVAL_PLAN_ID = '2c938084726fca480172750000000000'  # Reemplaza con tu preapproval_plan_id

# Configuración de logging
src_directory1 = os.getcwd()  # Obtiene el directorio actual
logs_file_path = os.path.join(src_directory1, 'logs.log')

logging.basicConfig(level=logging.INFO, filename=logs_file_path,
                    format='%(asctime)s %(levelname)s %(message)s')

@suscripciones_producto_usuario.route('/crearSuscricpionesMP/', methods=['GET'])
def crearSuscricpionesMP():
    # Obtiene el parámetro 'layout' de la cadena de consulta
    OrigenLayout = request.args.get('layout')
    return render_template('sistemaDePagos/crearSuscripciones.html', layout=OrigenLayout)

@suscripciones_producto_usuario.route('/create_subscription', methods=['POST'])
def create_subscription():
    # Obtener los datos JSON de la solicitud
    data = request.json
    
    # Construir el cuerpo de la solicitud para Mercado Pago
    payload = {
        "auto_recurring": {
            "frequency": data.get('frequency'),
            "frequency_type": "months",
            "start_date": "2020-06-02T13:07:14.260Z",  # Estas fechas deberían ser dinámicas o configurables
            "end_date": "2022-07-20T15:59:52.581Z",
            "transaction_amount": data.get('amount'),
            "currency_id": "ARS"
        },
        "back_url": "https://www.mercadopago.com.ar",
        "card_token_id": data.get('card_token_id'),
        "external_reference": "YG-1234",
        "payer_email": data.get('payer_email'),
        "preapproval_plan_id": PREAPPROVAL_PLAN_ID,
        "reason": data.get('reason'),
        "status": "authorized"
    }

    # Realizar la solicitud POST a la API de Mercado Pago
    headers = {
        'Content-Type': 'application/json',
        'Authorization': YOUR_ACCESS_TOKEN
    }
    response = requests.post('https://api.mercadopago.com/preapproval', json=payload, headers=headers)

    # Registrar la respuesta en los logs
    if response.status_code == 200:
        current_app.logger.info(f"Subscription created successfully: {response.json()}")
        return jsonify({"message": "Subscription created successfully", "response": response.json()})
    else:
        current_app.logger.error(f"Failed to create subscription: {response.json()}")
        return jsonify({"error": "Failed to create subscription", "details": response.json()}), response.status_code
