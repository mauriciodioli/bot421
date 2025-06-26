<<<<<<< HEAD

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
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/suscripciones.html', layout = layout)
    
@suscripcionPlanUsuario.route('/productosComerciales_suscripciones_muestra_suscripciones/', methods=['GET'])
def productosComerciales_suscripciones_muestra_suscripciones():
    try:
        layout = request.args.get('layout', 'layout')
        access_token = request.args.get('access_token')

        # Validación del token
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 401
        
        # Validación de expiración del token
        if Token.validar_expiracion_token(access_token=access_token):
            app = current_app._get_current_object()
            user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            usuario = db.session.query(Usuario).filter_by(id=user_id).first()

            # Recuperar las suscripciones
            if usuario.roll == 'ADMINISTRADOR':
                suscripciones = db.session.query(SuscripcionPlanUsuario).all()
            else:
                suscripciones = db.session.query(SuscripcionPlanUsuario).filter_by(user_id=user_id).all()

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
                    'billing_day': suscripcion.billing_day,
                    'preapproval_plan_id': suscripcion.preapproval_plan_id
                }
                for suscripcion in suscripciones
            ]

            return jsonify({'suscripciones': suscripciones_serializados, 'layout': layout})

        # Token inválido o expirado
        return jsonify({'error': 'Invalid or expired access token'}), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
=======

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
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/suscripciones.html', layout = layout)
    
@suscripcionPlanUsuario.route('/productosComerciales_suscripciones_muestra_suscripciones/', methods=['GET'])
def productosComerciales_suscripciones_muestra_suscripciones():
    try:
        layout = request.args.get('layout', 'layout')
        access_token = request.args.get('access_token')

        # Validación del token
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 401
        
        # Validación de expiración del token
        if Token.validar_expiracion_token(access_token=access_token):
            app = current_app._get_current_object()
            user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            usuario = db.session.query(Usuario).filter_by(id=user_id).first()

            # Recuperar las suscripciones
            if usuario.roll == 'ADMINISTRADOR':
                suscripciones = db.session.query(SuscripcionPlanUsuario).all()
            else:
                suscripciones = db.session.query(SuscripcionPlanUsuario).filter_by(user_id=user_id).all()

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
                    'billing_day': suscripcion.billing_day,
                    'preapproval_plan_id': suscripcion.preapproval_plan_id
                }
                for suscripcion in suscripciones
            ]

            return jsonify({'suscripciones': suscripciones_serializados, 'layout': layout})

        # Token inválido o expirado
        return jsonify({'error': 'Invalid or expired access token'}), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
