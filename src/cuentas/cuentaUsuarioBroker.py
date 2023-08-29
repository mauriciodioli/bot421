
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
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta

cuentas = Blueprint('cuentas',__name__)

@cuentas.route("/cuentas-Usuario-Broker/",  methods=["GET"])
def cuentas_Usuario_Broker():
   try:
      if request.method == 'GET': 
           cuentasBroker = db.session.query(Cuenta).all()
           db.session.close()
           return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentasBroker)
   except:
       print('no hay usuarios') 
   return 'problemas con la base de datos'

@cuentas.route("/eliminar-Cuenta-broker-administracion/",  methods=["POST"])
def eliminar_cuenta_broker_administracion():

    cuenta_id = request.form['eliminarCuentaId']
    cuenta = Cuenta.query.get(cuenta_id)
    db.session.delete(cuenta)
    db.session.commit()
    flash('Cuenta eliminada correctamente.')
    cuentas = db.session.query(Cuenta).all()
    db.session.close()
    return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentas)

