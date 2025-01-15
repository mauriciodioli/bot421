
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
        # Validar datos del JSON
        if not request.json or not request.json.get('accessToken_pagoPedido'):
            return jsonify({'error': 'Access token no proporcionado.'}), 400
        
        # Obtener el access token
        access_token = request.json.get('accessToken_pagoPedido')

        # Validar el token
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token no válido o expirado.'}), 401

        # Decodificar el token
        app = current_app._get_current_object()
        try:
            user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'El token ha expirado.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'El token es inválido.'}), 401
        
        # Buscar el usuario en la base de datos
        user = Usuario.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404
        
        if not user.activo:
            return jsonify({'error': 'El usuario no está activo.'}), 403

        # Obtener datos de la solicitud
        data = request.json
        required_fields = ['title', 'quantity', 'currency_id', 'unit_price', 'final_price', 'porcentaje_retorno']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'El campo {field} es obligatorio.'}), 400

        # Procesar campos
        try:
            costo_base = float(data.get('unit_price'))
            final_price = float(data.get('final_price'))
            porcentaje_retorno = float(data.get('porcentaje_retorno'))
        except ValueError:
            return jsonify({'error': 'Los valores de precio deben ser numéricos.'}), 400

        # Actualizar el pedido
        cargaDatosDePedidoParaEnvio(data, user_id)

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



def cargaDatosDePedidoParaEnvio(data, userId):
    try:
        # Validar datos obligatorios
        if not userId:
            raise ValueError("El userId es obligatorio.")
        
        publicacion_id = data.get('publicacion_id_btn_carrito')
        if not publicacion_id:
            raise ValueError("La publicación ID es obligatoria.")

        # Buscar el pedido existente
        pedido = Pedido.query.filter_by(
            user_id=userId,
            nombre_producto=data.get('titulo_btn_carrito'),
            publicacion_id=int(publicacion_id),
            ambito=data.get('ambito_pagoPedido')
        ).first()

        if not pedido:
            # Si el pedido no existe, devolver un mensaje
            print(f"No se encontró un pedido para user_id={userId} y publicacion_id={publicacion_id}.")
            return None

        # Extraer y procesar datos del pedido
        imagen_url = data.get('imagen_btn_carrito', '')
        texto = data.get('texto_btn_carrito', '')
        precio_str = data.get('precio_btn_carrito', '')

        # Procesar el precio (si es válido)
        precio_venta = float(precio_str.strip('$').replace(',', '').replace('.', '')) if precio_str else None
        tiempo = datetime.now()

        # Actualizar los campos del pedido existente
        pedido.estado = 'terminado'
        pedido.fecha_pedido = tiempo
        pedido.fecha_entrega = tiempo
        pedido.nombreCliente = data.get('nombreCliente', pedido.nombreCliente)
        pedido.apellidoCliente = data.get('apellidoCliente', pedido.apellidoCliente)
        pedido.telefonoCliente = data.get('telefonoCliente', pedido.telefonoCliente)
        pedido.emailCliente = data.get('emailCliente', pedido.emailCliente)
        pedido.comentarioCliente = data.get('comentarioCliente', pedido.comentarioCliente)
        pedido.cantidad = data.get('cantidadCompra', pedido.cantidad)
        pedido.precio_costo = precio_venta
        pedido.precio_venta = precio_venta
        pedido.descripcion = texto
        pedido.imagen = imagen_url

        # Guardar los cambios
        db.session.commit()
        db.session.close()
        return pedido

    except Exception as e:
        print(f"Error al actualizar el pedido: {e}")
        db.session.rollback()
        return None
