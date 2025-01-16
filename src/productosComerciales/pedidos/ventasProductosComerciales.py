
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
    # Obtener datos del formulario
    access_token = request.form.get('access_token_form_Ventas')
    ambito = request.form.get('ambito_form_Ventas')

    if not access_token:
        return jsonify({'error': 'Access token no proporcionado.'}), 400

    if Token.validar_expiracion_token(access_token=access_token):
        app = current_app._get_current_object()

        try:
            # Decodificar el token para obtener el user_id
            user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            user = db.session.query(Usuario).filter(Usuario.id == user_id).first()

            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404

            if not user.activo:
                return jsonify({'message': 'El usuario no está activo.'}), 403

            # Consultar publicaciones y pedidos
            publicaciones = db.session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito).all()
            pedidos = db.session.query(Pedido).filter_by(user_id=user_id, ambito=ambito).all()

            # Verificar asociaciones
            ids_publicaciones = {publicacion.id for publicacion in publicaciones}
            pedidos_con_publicaciones = [pedido for pedido in pedidos if pedido.publicacion_id in ids_publicaciones]

            if not pedidos_con_publicaciones:
                return render_template(
                    'productosComerciales/pedidos/ventas.html',
                    data='',
                    layout='layout'
                )

            # Consultar entregas
            entregas = db.session.query(PedidoEntregaPago).filter_by( ambito=ambito, estado="pendiente").all()
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

        except Exception as e:
            current_app.logger.error(f"Error en la solicitud: {e}")
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
        pedido_entrega = db.session.query(PedidoEntregaPago).filter_by(id=pedido_id).first()
        
        if not pedido_entrega:
            return jsonify({"error": "Pedido no encontrado."}), 404

       
        data = json.loads(pedido_entrega.pedido_data_json)
       
        
        # Lista para almacenar los detalles de los pedidos encontrados
        detalles = []
       
       # Guardamos consulta y total desde el pedido
        consulta = pedido_entrega.comentarioCliente  # O el campo correcto para la consulta
        total = pedido_entrega.precio_venta          # O el campo correcto para el total

        for item in data:
            id_pedido = item['id']

            # Realizamos la consulta para obtener el pedido correspondiente por id
            pedido = db.session.query(Pedido).filter(Pedido.id == int(id_pedido)).first()

            if pedido:
               
                # Agregamos los detalles del pedido a la lista
                detalles.append({
                    'id': pedido.id,
                    'descripcion': pedido.descripcion,
                    'nombre_producto': pedido.nombre_producto,
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio'],
                    'subtotal': int(item['cantidad']) * float(item['precio'])
                })

        # Cerramos la sesión de la base de datos
        db.session.close()

        # Devolvemos los detalles, consulta y total como respuesta JSON
        return jsonify({
            "detalles": detalles,
            "consulta": consulta,
            "total": total
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Error al obtener los detalles del pedido."}), 500
    
    
@ventasProductosComerciales.route('/productosComerciales_pedidos_ventasProductosComerciales_actualizarEstado_pedido/<int:pedido_id>', methods=['POST'])  # Cambiar a POST
def productosComerciales_pedidos_ventasProductosComerciales_actualizarEstado_pedido(pedido_id):
    try:
        data = request.json
        nuevo_estado = data.get('estado')  # Obtener el nuevo estado del cuerpo de la solicitud


        # Buscar el pedido y actualizar su estado
        pedido_entrega = db.session.query(PedidoEntregaPago).filter_by(id=pedido_id).first()
        
        if pedido_entrega:
            pedido_entrega.estado = nuevo_estado
        
        
            data = json.loads(pedido_entrega.pedido_data_json)
        
        
            for item in data:
                id_pedido = item['id']

                # Realizamos la consulta para obtener el pedido correspondiente por id
                pedido = db.session.query(Pedido).filter(Pedido.id == int(id_pedido)).first()

                if pedido:               
                    # Agregamos los detalles del pedido a la lista
                    pedido.estado = nuevo_estado
                    db.session.commit()
                
            
            
            
            db.session.commit()
            db.session.close()
            return jsonify({"success": True, "message": "Estado actualizado correctamente"})
        else:
            return jsonify({"success": False, "message": "Pedido no encontrado"}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": "Error al actualizar el estado"}), 500
    


@ventasProductosComerciales.route('/productosComerciales_pedidos_ventasProductosComerciales_DatosDelCliente_pedido/<int:pedido_id>', methods=['GET'])  # Cambié a GET
def productosComerciales_pedidos_ventasProductosComerciales_DatosDelCliente_pedido(pedido_id):
    try:
        # Buscar el pedido por ID
        pedido_entrega = db.session.query(PedidoEntregaPago).filter_by(id=pedido_id).first()
        
        if pedido_entrega:
            # Agregar los detalles del cliente a la respuesta
            detalles = [{
                'id': pedido_entrega.id,
                'nombreCliente': pedido_entrega.nombreCliente,
                'apellidoCliente': pedido_entrega.apellidoCliente,
                'emailCliente': pedido_entrega.emailCliente,
                'telefonoCliente': pedido_entrega.telefonoCliente
            }]
            db.session.close()
            return jsonify({
                "detalles": detalles            
            }), 200
        else:
            return jsonify({"success": False, "message": "Pedido no encontrado"}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": "Error al cargar datos del cliente"}), 500



@ventasProductosComerciales.route('/productosComerciales_pedidos_ventasProductosComerciales_cancela_pedido/<int:pedido_id>', methods=['POST'])
def productosComerciales_pedidos_ventasProductosComerciales_cancela_pedido(pedido_id):
    try:
        # Lógica para cancelar el pedido
        pedido = db.session.query(PedidoEntregaPago).filter(PedidoEntregaPago.id == pedido_id).first()
        
        if pedido:
            # Verifica si el pedido ya está cancelado
            if pedido.estado == 'cancelado':
                return jsonify({"success": False, "message": "El pedido ya está cancelado"}), 400

            # Cambiar el estado del pedido a 'cancelado'
            pedido.estado = 'cancelado'
            db.session.commit()
            db.session.close()
            return jsonify({"success": True, "message": "Pedido cancelado exitosamente"}), 200
        else:
            return jsonify({"success": False, "message": "Pedido no encontrado"}), 404

    except Exception as e:
        print("Error:", e)
        db.session.rollback()
        return jsonify({"success": False, "message": "Hubo un error al cancelar el pedido"}), 500








@ventasProductosComerciales.route('/productosComerciales_pedidos_recargaAutomatica_muestra/', methods=['POST'])
def productosComerciales_pedidos_recargaAutomatica_muestra():
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
                entregas = db.session.query(PedidoEntregaPago).filter_by(user_id=user_id, ambito=ambito, estado="pendiente").all()

                data = [
                    {
                        "id": entrega.id,
                        "fecha_entrega": entrega.fecha_entrega.strftime('%d/%m/%Y') if entrega.fecha_entrega else '',
                        "nombreCliente": entrega.nombreCliente,
                        "lugar_entrega": entrega.lugar_entrega,
                        "estado": entrega.estado,
                        "precio_venta": entrega.precio_venta
                    }
                    for entrega in entregas
                ]
                db.session.close()
                return jsonify(data)  # Devuelve los datos como JSON, no como una plantilla HTML

            else:
                return jsonify({'message': 'El usuario no está activo.'}), 403

        except Exception as e:
            print("Error:", str(e))
            db.session.rollback()
            db.session.close()
            return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    return jsonify({'error': 'Token inválido o expirado.'}), 401
