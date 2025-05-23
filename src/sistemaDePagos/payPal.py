# Creating  Routes
from pipes import Template
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
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest




payPal = Blueprint('payPal',__name__)

client_id  = os.environ["PAYPAL_CLIENT_ID"]
client_secret  = os.environ["TU_CLIENT_SECRET"]

environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)

@payPal.route("/create_orders_pypal/", methods=["POST"])
def create_orders_pypal():
    request_order = OrdersCreateRequest()
    request_order.prefer("return=representation")
    request_order.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": "10.00"
            }
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

