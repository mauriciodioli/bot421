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
import jwt
from models.usuario import Usuario
from models.brokers import Broker

suscripciones_producto_usuario = Blueprint('suscripciones_producto_usuario',__name__)



@suscripciones_producto_usuario.route('/crearSuscricpionesMP/', methods=['GET'])
def crearSuscricpionesMP():
    # Obtiene el parámetro 'productoId' de la cadena de consulta
    OrigenLayout = request.args.get('layout')
   
    return render_template('sistemaDePagos/crearSuscripciones.html',layout = OrigenLayout)
