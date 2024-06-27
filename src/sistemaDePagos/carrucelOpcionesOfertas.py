
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



from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test


carrucelOpcionesOfertas = Blueprint('carrucelOpcionesOfertas',__name__)

@carrucelOpcionesOfertas.route('sistemaDePagos_getOfertas/',methods=['POST'])
def sistemaDePagos_getOfertas():
    data = request.json
    # Process data if necessary (e.g., validation, authentication)
   # promotions = get_promotions()
    return render_template('notificaciones/noPoseeDatos.html',layou='layout.html')