
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
from models.payment_page.suscripcionPlanUsuario import SuscripcionPlanUsuario



#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

suscripcionPlanUsuario = Blueprint('suscripcionPlanUsuario',__name__)

@suscripcionPlanUsuario.route('/productosComerciales_suscripciones_muestra/', methods=['GET'])
def productosComerciales_suscripciones_muestra():
    return render_template('productosComerciales/suscripciones.html', layout = 'layout')
    
@suscripcionPlanUsuario.route('/productosComerciales_suscripciones_muestra_suscripciones/', methods=['GET'])
def productosComerciales_suscripciones_muestra_suscripciones():
    try:
        suscripciones = db.session.query(SuscripcionPlanUsuario).all()
        db.session.close()

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

        return jsonify({'suscripciones': suscripciones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
