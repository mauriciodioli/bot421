
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
import re

from models.usuario import Usuario
from models.brokers import Broker
from models.payment_page.plan import Plan
from models.pedidos.pedido import Pedido


from models.pedidos.pedidoEntregaPago import PedidoEntregaPago
from models.publicaciones.publicaciones import Publicacion



#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

ventasProductosComerciales = Blueprint('ventasProductosComerciales',__name__)


@ventasProductosComerciales.route('/productosComerciales_pedidos_ventasProductosComerciales_muestra/', methods=['POST'])
def productosComerciales_pedidos_ventasProductosComerciales_muestra():
    # Usar request.form para obtener datos del formulario
    access_token = request.form.get('access_token_form_Ventas')
    ambito = request.form.get('ambito_form_Ventas')

    if not access_token:
        return jsonify({'error': 'Access token no proporcionado.'}), 400

    if Token.validar_expiracion_token(access_token=access_token):
        app = current_app._get_current_object()

        try:
            user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            user = db.session.query(Usuario).filter(Usuario.id == user_id).first()

            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404

            if user.activo:
                # Procesar el ámbito y otras lógicas según sea necesario
                entregas = db.session.query(PedidoEntregaPago).filter_by(user_id=user_id, ambito=ambito).all()

                data = [
                    {
                        "id": entrega.id,
                        "user_id": entrega.user_id,
                        "fecha_entrega": entrega.fecha_entrega,
                        "nombreCliente": entrega.nombreCliente,
                        "apellidoCliente": entrega.apellidoCliente,
                        "emailCliente": entrega.emailCliente,
                        "telefonoCliente": entrega.telefonoCliente,
                        "lugar_entrega": entrega.lugar_entrega,
                        "ambito": entrega.ambito,
                        "estado": entrega.estado,
                        "precio_venta": entrega.precio_venta,
                        "pedido_data_json": entrega.pedido_data_json,
                    }
                    for entrega in entregas
                ]
                db.session.close()
                return render_template(
                    'productosComerciales/pedidos/ventas.html',
                    data=data,
                    layout='layout'
                )

            else:
                return jsonify({'message': 'El usuario no está activo.'}), 403

        except Exception as e:
            print("Error:", str(e))
            db.session.rollback()
            db.session.close()
            return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    return jsonify({'error': 'Token inválido o expirado.'}), 401


@ventasProductosComerciales.route('/productosComerciales_pedidos_ventasProductosComerciales_detalle_pedido/<int:pedido_id>', methods=['GET'])
def productosComerciales_pedidos_ventasProductosComerciales_detalle_pedido(pedido_id):
    """
    Obtiene el detalle del campo pedido_data_json para un PedidoEntregaPago específico.
    """
    try:
        pedido = db.session.query(PedidoEntregaPago).filter_by(id=pedido_id).first()
        
        if not pedido:
            return jsonify({"error": "Pedido no encontrado."}), 404

       
        data = json.loads(pedido.pedido_data_json)
       
        
        # Lista para almacenar los detalles de los pedidos encontrados
        detalles = []

        # Iteramos sobre cada item en 'data'
        for item in data:
            id_pedido = item['id']
            
            # Realizamos la consulta para obtener el pedido correspondiente por id
            pedido = db.session.query(Pedido).filter(Pedido.id == int(id_pedido)).first()  # Usamos .first() para obtener solo un pedido

            if pedido:
                # Si el pedido se encuentra, lo agregamos a la lista de detalles
                detalles.append({
                    'id': pedido.id,
                    'descripcion': pedido.descripcion,  # O cualquier otro campo que necesites
                    'nombre_producto': pedido.nombre_producto
                })

        # Cerramos la sesión de la base de datos
        db.session.close()

        # Devolvemos los detalles como respuesta JSON
        return jsonify({"detalles": detalles}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Error al obtener los detalles del pedido."}), 500