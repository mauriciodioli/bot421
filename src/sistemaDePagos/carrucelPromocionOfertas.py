
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

carrucelPromocionOfertas = Blueprint('carrucelPromocionOfertas',__name__)



@carrucelPromocionOfertas.route('/sistemaDePagos_carrucelPromocionOfertas_get_promociones', methods=['POST'])
def sistemaDePagos_carrucelPromocionOfertas_get_promociones():
    try:
        data = request.json
        access_token = data.get('access_token')
        correo_electronico = data.get('correo_electronico')
        reason = data.get('reason')
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")        

            promociones = db.session.query(Promotion).all()
            db.session.close()

            # Serializar los planes
            promociones_serializados = [
                {
                    'id': promocione.idPlan,
                    'description': promocione.description,
                    'price': promocione.price,
                    'reason': promocione.reason,
                    'discount': promocione.discount,
                    'image_url': promocione.image_url,
                    'state': promocione.state,
                    'cluster': promocione.cluster,
                    'currency_id': promocione.currency_id 
                        
                } for promocione in promociones
            ]

            return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
