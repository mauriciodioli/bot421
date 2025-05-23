# Creating  Routes
from unittest import result
from flask import current_app,session
import os
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.payment_page.tarjetaUsuario import TarjetaUsuario
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest




payPal = Blueprint('payPal',__name__)

USE_SANDBOX = True  # Cambialo a False para producción
if USE_SANDBOX:
    environment = SandboxEnvironment(
        client_id=os.environ["PAYPAL_CLIENT_ID"],
        client_secret=os.environ["PAYPAL_CLIENT_SECRET"]
    )
else:
    environment = LiveEnvironment(
        client_id=os.environ["PAYPAL_CLIENT_ID"],
        client_secret=os.environ["PAYPAL_CLIENT_SECRET"]
    )

client = PayPalHttpClient(environment)

@payPal.route("/create_orders_paypal/", methods=["POST"])
def create_orders_paypal():
    data = request.get_json()

    currency = data.get("currency_id", "USD").upper()
    amount = data.get("costo_base", "10.00")
    reason = data.get("reason", "Sin descripción")

    supported_currencies = ["USD", "EUR", "GBP", "MXN", "BRL"]

    # Convertir de ARS a USD si es necesario
    if currency == "ARS":
        try:
            amount = str(round(float(amount) / 1400, 2))  # ← tu tasa de conversión actual
        except (ValueError, TypeError):
            return jsonify({"error": "Monto inválido para conversión ARS → USD"}), 400
        currency = "USD"

    # Verificación final de moneda
    if currency not in supported_currencies:
        return jsonify({
            "error": f"Moneda '{currency}' no soportada por PayPal.",
            "soportadas": supported_currencies
        }), 400

    # Crear la orden
    request_order = OrdersCreateRequest()
    request_order.prefer("return=representation")
    request_order.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": amount
            },
            "description": reason
        }]
    })

    response = client.execute(request_order)
    return jsonify(orderID=response.result.id)



@payPal.route("/capture_order_paypal/<order_id>", methods=["POST"])
def capture_order_paypal(order_id):
    request_capture = OrdersCaptureRequest(order_id)
    request_capture.request_body({})
    response = client.execute(request_capture)
    return jsonify(response.result.__dict__['_dict'])

