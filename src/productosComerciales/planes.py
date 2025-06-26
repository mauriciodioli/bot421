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
from models.payment_page.plan import Plan



#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

planes = Blueprint('planes',__name__)

@planes.route('/productosComerciales_planes_muestra/', methods=['GET'])
def productosComerciales_planes_muestra():
    return render_template('productosComerciales/planes.html', layout = 'layout_administracion')
    
@planes.route('/productosComerciales_planes_muestra_planes/', methods=['GET'])
def productosComerciales_planes_muestra_planes():
    try:
        planes = db.session.query(Plan).all()
        db.session.close()

        # Serializar los planes
        planes_serializados = [
            {
                'id': plan.idPlan,
                'frequency': plan.frequency,
                'amount': plan.amount,
                'reason': plan.reason,
                'frequency_type': plan.frequency_type,
                'currency_id': plan.currency_id,
                'repetitions': plan.repetitions,
                'billing_day': plan.billing_day
            } for plan in planes
        ]

        return jsonify({'planes': planes_serializados})
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
from models.payment_page.plan import Plan



#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

planes = Blueprint('planes',__name__)

@planes.route('/productosComerciales_planes_muestra/', methods=['GET'])
def productosComerciales_planes_muestra():
    return render_template('productosComerciales/planes.html', layout = 'layout_administracion')
    
@planes.route('/productosComerciales_planes_muestra_planes/', methods=['GET'])
def productosComerciales_planes_muestra_planes():
    try:
        planes = db.session.query(Plan).all()
        db.session.close()

        # Serializar los planes
        planes_serializados = [
            {
                'id': plan.idPlan,
                'frequency': plan.frequency,
                'amount': plan.amount,
                'reason': plan.reason,
                'frequency_type': plan.frequency_type,
                'currency_id': plan.currency_id,
                'repetitions': plan.repetitions,
                'billing_day': plan.billing_day
            } for plan in planes
        ]

        return jsonify({'planes': planes_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
