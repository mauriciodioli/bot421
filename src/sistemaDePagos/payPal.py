# Creating  Routes
from unittest import result
from flask import current_app,session
import os
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
  # ⏱ Tiempo actual
from datetime import datetime
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.pedidos.pedido import Pedido
from models.pedidos.pedidoEntregaPago import PedidoEntregaPago
from models.payment_page.tarjetaUsuario import TarjetaUsuario
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from dotenv import load_dotenv
from utils.db_session import get_db_session 
load_dotenv()



payPal = Blueprint('payPal',__name__)

USE_SANDBOX = True  # Cambialo a False para producción
if USE_SANDBOX:
    environment = SandboxEnvironment(
        client_id=os.environ["PAYPAL_CLIENT_ID"],
        client_secret=os.environ["PAYPAL_CLIENT_SECRET"]
    )
else:
    environment = LiveEnvironment(
        client_id=os.environ["PAYPAL_CLIENT_ID"],
        client_secret=os.environ["PAYPAL_CLIENT_SECRET"]
    )

client = PayPalHttpClient(environment)

@payPal.route("/create_orders_paypal/", methods=["POST"])
def create_orders_paypal():
    data = request.get_json()

    currency = data.get("currency_id", "USD").upper()
    amount = data.get("costo_base", "10.00")
    reason = data.get("reason", "Sin descripción")
    supported_currencies = ["USD", "EUR", "GBP", "MXN", "BRL"]

    # ✅ Validación de monto vacío o inválido
    if not amount or str(amount).strip() == "":
        return jsonify({"error": "Pedido no procesado: costo_base no proporcionado."}), 400

    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "Pedido no procesado: costo_base no es un número válido."}), 400

    # Conversión ARS → USD
    if currency == "ARS":
        amount_float = round(amount_float / 1400, 2)
        currency = "USD"
    
    if currency in ["€", "EUR"]:    
        amount_float = round(amount_float * 1.1, 2)  # ejemplo: 1 EUR = 1.10 USD (ajustá la tasa)   
        currency = "USD"
        
    # Conversión PLN → USD
    if currency == "ZŁ":
        amount_float = round(amount_float / 4.0, 2)
        currency = "USD"

    if currency not in supported_currencies:
        return jsonify({
            "error": f"Moneda '{currency}' no soportada por PayPal.",
            "soportadas": supported_currencies
        }), 400

    # Crear orden PayPal
    request_order = OrdersCreateRequest()
    request_order.prefer("return=representation")
    request_order.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": str(amount_float)
            },
            "description": reason
        }]
    })

    try:
        response = client.execute(request_order)
        order_id = response.result.id
    except Exception as e:
        return jsonify({"error": f"No se pudo crear la orden PayPal: {str(e)}"}), 500

  
    tiempo = datetime.utcnow()

    # 🛒 Procesar pedidos
    try:
     #   pedidos_str = data.get('pedido_data_json_pagoPedido')
      #  pedidos = json.loads(pedidos_str)
        cantidad_total = 0

      #  for pedido_data in pedidos:
      #      cantidad_pedido = actualizar_pedido(pedido_data, data, tiempo)
       #     if isinstance(cantidad_pedido, dict):  # error
       #         return jsonify(cantidad_pedido), 404
        #    cantidad_total += cantidad_pedido

       # user_id = data.get("user_id", 1)
        #entrega = cargar_entrega_pedido(data, user_id, tiempo, cantidad_total)
        entrega = '1'

    except Exception as e:
        return jsonify({"error": f"No se pudo registrar el pedido: {str(e)}"}), 500

    return jsonify({
        "orderID": order_id,
        "estado": "pendiente",
      #  "entrega_id": entrega.id if hasattr(entrega, "id") else None
        "entrega_id": entrega
    })



@payPal.route("/capture_order_paypal/<order_id>", methods=["POST"])
def capture_order_paypal(order_id):
    request_capture = OrdersCaptureRequest(order_id)
    request_capture.request_body({})
    response = client.execute(request_capture)
    return jsonify(response.result.__dict__['_dict'])




def actualizar_pedido(pedido_data, data, tiempo):
    with get_db_session() as session:
        # Consultar el pedido en la base de datos
        pedido_existente = session.query(Pedido).filter_by(id=int(pedido_data.get("id"))).first()

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
        session.commit()
        return pedido_existente.cantidad

    
def cargar_entrega_pedido(data, user_id, tiempo,cantidad):
    try:
        with get_db_session() as session:
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
            session.add(nuevo_pedido_entrega_pago)
            # Antes de hacer commit, puedes imprimir la consulta SQL
        # print(str(nuevo_pedido_entrega_pago.__table__.insert().compile(dialect=db.engine.dialect)))
            session.commit()
            return nuevo_pedido_entrega_pago
    except Exception as e:
        # Rollback en caso de error
  
        return jsonify({'error': f'Ocurú un error: {str(e)}'}), 500
  