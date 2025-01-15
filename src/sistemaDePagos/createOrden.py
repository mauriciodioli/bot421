
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
from models.pedidos.pedido import Pedido
from models.pedidos.pedidoEntregaPago import PedidoEntregaPago
from datetime import datetime, timedelta
import mercadopago

from config import DOMAIN # mercado pago
from config import MERCADOPAGO_URL
from config import MERCADOPAGO_KEY_API #para produccion
from config import sdk_produccion # test
from config import sdk_prueba # test

#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

createOrden = Blueprint('createOrden',__name__)


# Definir URLs utilizando el dominio
SUCCESS_URL = f"{DOMAIN}/success"
FAILURE_URL = f"{DOMAIN}/failure"
PENDING_URL = f"{DOMAIN}/pending"
NOTIFICATION_URL = f"{DOMAIN}/webhook"

# Definir URLs de la API de MercadoPago
CARD_TOKEN_URL = f"{MERCADOPAGO_URL}/v1/card_tokens"
PREFERENCE_URL = f"{MERCADOPAGO_URL}/checkout/preferences"
PREAPPROVAL_PLAN_URL = f"{MERCADOPAGO_URL}/preapproval_plan"
PREAPPROVAL_URL = f"{MERCADOPAGO_URL}/preapproval"


mp = mercadopago.SDK(sdk_produccion)
@createOrden.route('/sistemaDePagos_create_order/', methods=['POST'])
def sistemaDePagos_create_order():
    try:
        # Obtener el token desde el header "Authorization"
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token no proporcionado'}), 400
        
        access_token = auth_header.split(" ")[1]  # El token está después de "Bearer "

        # Validar si el token está expirado o no es válido
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token no válido o expirado.'}), 401

        # Decodificar el token
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get("sub")
        numero_de_cuenta = decoded_token.get("numero_de_cuenta")

        # Buscar el usuario en la base de datos
        user = Usuario.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404
        
        if not user.activo:
            return jsonify({'error': 'El usuario no está activo.'}), 403

        # Obtener los datos del JSON
        data = request.json
        
        # Validar los campos obligatorios
        required_fields = ['title', 'quantity', 'currency_id', 'unit_price', 'final_price', 'porcentaje_retorno']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'El campo {field} es obligatorio.'}), 400

        # Procesar campos numéricos
        try:
            costo_base = float(data.get('unit_price'))
            final_price = float(data.get('final_price'))
            porcentaje_retorno = float(data.get('porcentaje_retorno'))
        except ValueError:
            return jsonify({'error': 'Los valores de precio deben ser numéricos.'}), 400


        # Obtener datos iniciales
        pedidos_str = data.get('pedido_data_json')
        pedidos = json.loads(pedidos_str)

        # Valores comunes a todos los pedidos (no se alteran)
        tiempo = datetime.utcnow()  # Fecha y hora actual
        cantidad = 0
        # Actualizar el pedido
        for pedido_data in pedidos:
            cantidad_pedido = actualizar_pedido(pedido_data, data, tiempo)
            if isinstance(cantidad_pedido, dict):  # Si hubo un error
                return jsonify(cantidad_pedido), 404
            cantidad += cantidad_pedido
        cargar_entrega_pedido(data, user_id, tiempo, cantidad)

        # Preparar datos para la preferencia
        preference_data = {
            "items": [
                {
                    "title": data['title'],
                    "quantity": data['quantity'],
                    "unit_price": final_price,
                    "currency_id": data['currency_id']
                }
            ],
            "back_urls": {
                "success": SUCCESS_URL,
                "failure": FAILURE_URL,
                "pending": PENDING_URL
            },
            "notification_url": NOTIFICATION_URL,
            "auto_return": "approved"
        }

        # Encabezados de la solicitud
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {sdk_produccion}',  # Token de acceso
            'X-Idempotency-Key': '123546'
        }

        # Crear preferencia
        url = f"{MERCADOPAGO_URL}/checkout/preferences"
        preference_response = create_preference(preference_data, headers, url)
        init_point = preference_response.get("init_point")

        # Devolver la URL de inicialización
        return jsonify({"init_point": init_point})

    except requests.HTTPError as e:
        return jsonify({"error": str(e)}), e.response.status_code
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@createOrden.route('/create_order/', methods=['POST'])
def create_order():
    try:
        # Obtén los datos de la solicitud
        data = request.get_json()
 # Accede a los datos JSON enviados
        data = request.json

        # Extrae los campos del JSON
        title = data.get('title')  # Ejemplo: "Donation"
        quantity = data.get('quantity')  # Ejemplo: 1
        currency_id = data.get('currency_id')  # Ejemplo: "USD"
        costo_base = data.get('unit_price')  # Ejemplo: 100.0
        final_price = data.get('final_price')  # Ejemplo: 90.0 (con descuento)
        porcentaje_retorno = data.get("porcentaje_retorno")
        
        costo_base = float(costo_base)
        porcentaje_retorno = float(porcentaje_retorno)
       

        # Crea los datos de la preferencia
        preference_data = {
            "items": [
                {
                    "title": title,  # Título del artículo
                    "quantity": 1,
                    "unit_price": final_price,  # Precio unitario
                    "currency_id": currency_id
                }
            ],
            "back_urls": {
                "success": SUCCESS_URL,
                "failure": FAILURE_URL,
                "pending": PENDING_URL
            },
            "notification_url": NOTIFICATION_URL,
            "auto_return": "approved"
        }

        # Encabezados para la solicitud
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + sdk_produccion,  # Token de acceso
            'X-Idempotency-Key': '123546'
        }

        # Llama a la función create_preference
        url = f"{MERCADOPAGO_URL}/checkout/preferences"
        preference_response = create_preference(preference_data, headers, url)
        init_point = preference_response.get("init_point")

        # Devuelve la URL de inicialización de la preferencia
        return jsonify({"init_point": init_point})

    except requests.HTTPError as e:
        return jsonify({"error": str(e)}), e.response.status_code

def create_preference(preference_data, headers, url):    
    response = requests.post(
        url,
        json=preference_data,
        headers=headers
    )
    response.raise_for_status()
    return response.json()

































def actualizar_pedido(pedido_data, data, tiempo):
    # Consultar el pedido en la base de datos
    pedido_existente = db.session.query(Pedido).filter_by(id=int(pedido_data.get("id"))).first()

    if not pedido_existente:
        return {'error': f'Pedido {pedido_data.get("id")} no encontrado'}, 404

    # Actualizar solo los campos necesarios
    pedido_existente.estado = 'terminado'
    pedido_existente.fecha_pedido = tiempo
    pedido_existente.fecha_entrega = tiempo
    pedido_existente.nombreCliente = data.get('nombreCliente', pedido_existente.nombreCliente)
    pedido_existente.apellidoCliente = data.get('apellidoCliente', pedido_existente.apellidoCliente)
    pedido_existente.telefonoCliente = data.get('telefonoCliente', pedido_existente.telefonoCliente)
    pedido_existente.emailCliente = data.get('emailCliente', pedido_existente.emailCliente)
    pedido_existente.comentarioCliente = data.get('comentariosCliente', pedido_existente.comentarioCliente)
    pedido_existente.cantidad = data.get('cantidadCompra', pedido_existente.cantidad)
    pedido_existente.cluster_id = int(data.get('cluster_pedido', pedido_existente.cluster_id))
    pedido_existente.lugar_entrega = data.get('direccionCliente', pedido_existente.lugar_entrega)
    
    # Guardar los cambios
    db.session.commit()
    return pedido_existente.cantidad

    
def cargar_entrega_pedido(data, user_id, tiempo,cantidad):
    try:
        
        nuevo_pedido_entrega_pago = PedidoEntregaPago(
            user_id=user_id,
            publicacion_id=1,
            cliente_id=1,
            ambito=data.get('ambito_pagoPedido'),
            estado='pendiente',
            fecha_pedido=tiempo,
            fecha_entrega=tiempo,
            lugar_entrega=data.get('direccionCliente', ''),
            cantidad=cantidad,
            precio_venta=float(data.get('final_price', '')),
            consulta=tiempo,
            asignado_a='',
            talla='',
            pais='arg',
            provincia='',
            region='',
            sexo='',
            nombreCliente=data.get('nombreCliente', ''),
            apellidoCliente=data.get('apellidoCliente', ''),
            emailCliente=data.get('emailCliente', ''),
            telefonoCliente=data.get('telefonoCliente', ''),
            comentarioCliente=data.get('comentariosCliente', ''),
            cluster_id=int(data.get('cluster_pedido', '')),
            pedido_data_json=data.get('pedido_data_json', '')
        )
        db.session.add(nuevo_pedido_entrega_pago)
        # Antes de hacer commit, puedes imprimir la consulta SQL
       # print(str(nuevo_pedido_entrega_pago.__table__.insert().compile(dialect=db.engine.dialect)))
        db.session.commit()
        return nuevo_pedido_entrega_pago
    except Exception as e:
        # Rollback en caso de error
        db.session.rollback()
        return jsonify({'error': f'Ocurú un error: {str(e)}'}), 500