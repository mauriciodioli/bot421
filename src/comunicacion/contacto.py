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

contacto = Blueprint('contacto',__name__)




@contacto.route('/llamada/<variable>')
def llamada(variable):
    if variable == 'index-contacto':    
        return render_template('comunicacion/contacto.html')
    # Añadir más productos según sea necesario
    else:
        return "No puede llamar a contacto.html", 404
    
@contacto.route('/comunicacion_contacto_consultas/<layout>/<user_id>', methods=['GET'])
def comunicacion_contacto_consultas(layout, user_id):
    return render_template('comunicacion/consultas.html', layout=layout, user_id=user_id)

    