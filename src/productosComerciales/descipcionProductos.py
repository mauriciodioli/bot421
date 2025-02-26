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



@descrpcionProductos.route('/descripcionProductos', methods=['GET'])
def descripcionProductos():
    # Obtiene el parámetro 'productoId' de la cadena de consulta
    OrigenLayout = request.args.get('layout')
   
    return render_template('productosComerciales/descripcionProductos.html',layout = OrigenLayout)

@descrpcionProductos.route('/detalle/<producto>/<OrigenLayout>')
def detalle_producto(producto,OrigenLayout):
    if producto == "motor-de-operaciones":
        return render_template('productosComerciales/detalle_motor_operaciones.html',layout = OrigenLayout)
    elif producto == "bot-automatico":
        return render_template('productosComerciales/detalle_bot_automatico.html',layout = OrigenLayout)
    elif producto == "sistema-operaciones":
        return render_template('productosComerciales/detalle_sistema_operaciones.html',layout = OrigenLayout)
    elif producto == "copy-trader":
        return render_template('productosComerciales/detalle_copy_trader.html',layout = OrigenLayout)
    elif producto == "panel-manual":
        return render_template('productosComerciales/detalle_panel_manual.html',layout = OrigenLayout)
    elif producto == "fichas-tokens":
        return render_template('productosComerciales/detalle_tokens.html',layout = OrigenLayout)
    elif producto == "index-cursos":
        return render_template('productosComerciales/detalle_cursos.html',layout = OrigenLayout)
    elif producto == "index-fintech":
        return render_template('productosComerciales/detalle_fintech.html',layout = OrigenLayout)
    elif producto == "index-monedas-virtuales":
        return render_template('productosComerciales/detalle_monedas_virtuales.html',layout = OrigenLayout)
    elif producto == "index-dominios":
        return render_template('productosComerciales/detalle_dominios.html',layout = OrigenLayout)
    elif producto == "sobreNosotros":
        return render_template('estaticas/sobreNosotros.html',layout = OrigenLayout)
    elif producto == "cuenta-demo":
        return render_template('estaticas/cuentaDemo.html',layout = OrigenLayout)
    
   
    # Añadir más productos según sea necesario
    else:
        return "Producto no encontrado", 404