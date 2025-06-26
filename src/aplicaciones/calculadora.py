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
import jwt
from models.usuario import Usuario
from models.brokers import Broker
from models.cuentas import Cuenta


calculadora = Blueprint('calculadora',__name__)

@calculadora.route("/calculadora_standar_cuentas_endPointBrokers/")
def calculadora_standar_cuentas_endPointBrokers():
    
    return render_template('aplicaciones/calculadora.html', layout='layout')
@calculadora.route('/calculadora_standar_calcular', methods=['POST'])
def calculadora_standar_calcular():
    data = request.json
    operacion = data.get('operacion')
    numeros = data.get('numeros', [])

    if not numeros:
        return jsonify({'error': 'No se proporcionaron números'})

    try:
        numeros = list(map(float, numeros))
        resultado = None

        if operacion == '+':
            resultado = sum(numeros)
        elif operacion == 'resta':
            resultado = numeros[0] - sum(numeros[1:])
        elif operacion == '*':
            resultado = np.prod(numeros)
        elif operacion == '/':
            resultado = numeros[0]
            for num in numeros[1:]:
                resultado /= num
        else:
            return jsonify({'error': 'Operación no válida'})

        return jsonify({'resultado': resultado})
    except ValueError:
        return jsonify({'error': 'Entrada inválida'})


@calculadora.route('/calculadora_standar_normalizar', methods=['POST'])
def calculadora_standar_normalizar():
    data = request.json.get('datos', [])
    if not data:
        return jsonify({'error': 'Datos vacíos'})
    try:
        scaler = MinMaxScaler()
        data_np = np.array(data).reshape(-1, 1)
        normalizados = scaler.fit_transform(data_np).flatten().tolist()
        return jsonify({'normalizados': normalizados})
    except Exception as e:
        return jsonify({'error': str(e)})

@calculadora.route('/calculadora_standar_onehot', methods=['POST'])
def calculadora_standar_onehot():
    categorias = request.json.get('categorias', [])
    if not categorias:
        return jsonify({'error': 'Categorías vacías'})
    try:
        encoder = OneHotEncoder(sparse_output=False)
        encoded = encoder.fit_transform(np.array(categorias).reshape(-1, 1)).tolist()
        return jsonify({'onehot': encoded})
    except Exception as e:
        return jsonify({'error': str(e)})
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
import jwt
from models.usuario import Usuario
from models.brokers import Broker
from models.cuentas import Cuenta


calculadora = Blueprint('calculadora',__name__)

@calculadora.route("/calculadora_standar_cuentas_endPointBrokers/")
def calculadora_standar_cuentas_endPointBrokers():
    
    return render_template('aplicaciones/calculadora.html', layout='layout')
@calculadora.route('/calculadora_standar_calcular', methods=['POST'])
def calculadora_standar_calcular():
    data = request.json
    operacion = data.get('operacion')
    numeros = data.get('numeros', [])

    if not numeros:
        return jsonify({'error': 'No se proporcionaron números'})

    try:
        numeros = list(map(float, numeros))
        resultado = None

        if operacion == '+':
            resultado = sum(numeros)
        elif operacion == 'resta':
            resultado = numeros[0] - sum(numeros[1:])
        elif operacion == '*':
            resultado = np.prod(numeros)
        elif operacion == '/':
            resultado = numeros[0]
            for num in numeros[1:]:
                resultado /= num
        else:
            return jsonify({'error': 'Operación no válida'})

        return jsonify({'resultado': resultado})
    except ValueError:
        return jsonify({'error': 'Entrada inválida'})


@calculadora.route('/calculadora_standar_normalizar', methods=['POST'])
def calculadora_standar_normalizar():
    data = request.json.get('datos', [])
    if not data:
        return jsonify({'error': 'Datos vacíos'})
    try:
        scaler = MinMaxScaler()
        data_np = np.array(data).reshape(-1, 1)
        normalizados = scaler.fit_transform(data_np).flatten().tolist()
        return jsonify({'normalizados': normalizados})
    except Exception as e:
        return jsonify({'error': str(e)})

@calculadora.route('/calculadora_standar_onehot', methods=['POST'])
def calculadora_standar_onehot():
    categorias = request.json.get('categorias', [])
    if not categorias:
        return jsonify({'error': 'Categorías vacías'})
    try:
        encoder = OneHotEncoder(sparse_output=False)
        encoded = encoder.fit_transform(np.array(categorias).reshape(-1, 1)).tolist()
        return jsonify({'onehot': encoded})
    except Exception as e:
        return jsonify({'error': str(e)})
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
