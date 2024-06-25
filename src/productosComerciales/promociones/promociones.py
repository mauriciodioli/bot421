
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
from models.payment_page.Promotion import Promotion



#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

promociones = Blueprint('promociones',__name__)

@promociones.route('/sistemaDePagos_get_planes_promociones', methods=['GET'])
def sistemaDePagos_get_planes_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/promociones.html', layout = layout)
    
@promociones.route('/productosComerciales_promociones_muestra_promociones', methods=['GET'])
def productosComerciales_promociones_muestra_promociones():  
    try:
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.idPlan,
                'frequency': promocione.frequency,
                'amount': promocione.amount,
                'reason': promocione.reason,
                'frequency_type': promocione.frequency_type,
                'currency_id': promocione.currency_id,
                'repetitions': promocione.repetitions,
                'billing_day': promocione.billing_day
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




@promociones.route('/sistemaDePagos_get_promociones', methods=['POST'])
def sistemaDePagos_carrucelPromocionOfertas_get_promociones():
    data = request.json
    access_token = data.get('access_token')
    correo_electronico = data.get('correo_electronico')
    reason = data.get('reason')
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        numero_de_cuenta = decoded_token.get("numero_de_cuenta")
        user_id = decoded_token.get("sub")        

        # Consultar el plan existente en la base de datos
        plan_existente = db.session.query(Plan).filter_by(reason=reason).first()

        if plan_existente is None:
            # Lanzar una excepción si el plan no existe
                raise Exception("Plan no encontrado en la base de datos")

    print('llegamos')
    
    response_data = {
        'message': 'sistemaDePagos',
        'html': render_template('carrucelPromocionOfertas.html')  # Ensure you have the correct HTML template
    }
    return jsonify(response_data)