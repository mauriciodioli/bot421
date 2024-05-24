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

descrpcionProductos = Blueprint('descrpcionProductos',__name__)



@descrpcionProductos.route('/descripcionProductos', methods = ['GET'])
def descripcionProductos():
   
    return render_template('productosComerciales/descripcionProductos.html')

@descrpcionProductos.route('/detalle/<producto>')
def detalle_producto(producto):
    if producto == "motor-de-operaciones":
        return render_template('productosComerciales/detalle_motor_operaciones.html')
    elif producto == "bot-automatico":
        return render_template('productosComerciales/detalle_bot_automatico.html')
    elif producto == "sistema-operaciones":
        return render_template('productosComerciales/detalle_sistema_operaciones.html')
    elif producto == "copy-trader":
        return render_template('productosComerciales/detalle_copy_trader.html')
    elif producto == "panel-manual":
        return render_template('productosComerciales/detalle_panel_manual.html')
    elif producto == "fichas-tokens":
        return render_template('productosComerciales/detalle_tokens.html')
    elif producto == "index-cursos":
        return render_template('productosComerciales/detalle_cursos.html')
    elif producto == "index-fintech":
        return render_template('productosComerciales/detalle_fintech.html')
    elif producto == "index-monedas-virtuales":
        return render_template('productosComerciales/detalle_monedas_virtuales.html')
    # Añadir más productos según sea necesario
    else:
        return "Producto no encontrado", 404