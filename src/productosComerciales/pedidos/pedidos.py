
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

pedidos = Blueprint('pedidos',__name__)


@pedidos.route('/productosComerciales_pedidos_muestra/', methods=['POST'])
def productosComerciales_pedidos_muestra():    
    if not request.json or not request.json.get('accessToken'):
        return jsonify({'error': 'Access token no proporcionado.'}), 400
    
    access_token = request.json.get('accessToken')

    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
        
        try:
            user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                          
            user = db.session.query(Usuario).filter(Usuario.id == user_id).first()
            
            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404

            if user.activo:
                ambito = request.json.get('dominio')
                
                # Filtro de pedidos
                pedidos = db.session.query(Pedido).filter(
                    and_(Pedido.user_id == user_id, Pedido.ambito == ambito)
                ).all()
                
                # Procesar los datos
                data = []  # Lista para almacenar los datos de los pedidos
                for pedido in pedidos:
                    data.append({
                        'id': pedido.id,
                        'user_id': pedido.user_id,
                        'nombre_producto': pedido.nombre_producto,
                        'fecha_pedido': pedido.fecha_pedido,
                        'precio_venta': pedido.precio_venta,
                        'estado': pedido.estado
                    })
                
                return render_template(
                    'productosComerciales/pedidos/pedidos.html',
                    data=data,
                    layout='layout'
                )
            
            else:
                return jsonify({'message': 'El usuario no está activo.'}), 403
              
        except Exception as e:
            print("Error:", str(e))
            db.session.rollback()  # Hacer rollback de la sesión
            db.session.close()  # Cerrar la sesión
            return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    return jsonify({'error': 'Token inválido o expirado.'}), 401

@pedidos.route('/productosComerciales_pedidos_mostrar_carrito/', methods=['POST'])
def productosComerciales_pedidos_mostrar_carrito():
   try:
        # Obtener datos del request
        data = request.form or request.json
        
        
        access_token = data.get('access_token_btn_carrito_bajo') or data.get('access_token_btn_carrito')
        ambito = data.get('ambito_btn_carrito_bajo') or data.get('ambito_btn_carrito')

        
        
      
        if not access_token:
            return jsonify({'error': 'Token no proporcionado.'}), 401

        # Validar el token
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token inválido o expirado.'}), 401

        # Decodificar el token
        decoded_token = jwt.decode(
            access_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token inválido: falta el user_id.'}), 401
       
        # Buscar usuario
        user = db.session.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        if not user.activo:
            return jsonify({'error': 'El usuario no está activo.'}), 403

       
        pedidos = db.session.query(Pedido).filter_by(user_id=user_id, ambito=ambito, estado='pendiente').all()
        
        # Consultar publicaciones y pedidos
        publicaciones = db.session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito).all()
        if publicaciones:
            # Verificar asociaciones
            ids_publicaciones = {publicacion.id for publicacion in publicaciones}
            pedidos_con_publicaciones = [pedido for pedido in pedidos if pedido.publicacion_id in ids_publicaciones]

            if not pedidos_con_publicaciones:
                return render_template(
                    'productosComerciales/pedidos/carritoCompras.html',
                    data='',
                    layout='layout'
                )
         # Procesar datos de los pedidos
        pedidos_data = [
            {
                'id': pedido.id,
                'user_id': pedido.user_id,
                'nombre_producto': pedido.nombre_producto,
                'fecha_pedido': pedido.fecha_pedido,
                'precio_venta': pedido.precio_venta,
                'estado': pedido.estado,
                'cantidad': pedido.cantidad,
                'imagen_url': pedido.imagen,  # Incluir la URL de la imagen   
                'pagoOnline': pedido.pagoOnline       
            }
            for pedido in pedidos
        ]
        db.session.close()
        # Renderizar la plantilla
        return render_template(
            'productosComerciales/pedidos/carritoCompras.html',
            data=pedidos_data,
            layout='layout'
        )

   except Exception as e:
        print("Error:", str(e))
        db.session.rollback()  # Rollback de la sesión en caso de error
        return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

   finally:
        db.session.close()  # Cerrar la sesión siempre


@pedidos.route('/productosComerciales_pedidos_compras/', methods=['POST'])
def productosComerciales_pedidos_compras():
   try:
        # Obtener datos del request
        data = request.form or request.json
        access_token = data.get('access_token_btn_compras')
        if not access_token:
            return jsonify({'error': 'Token no proporcionado.'}), 401

        # Validar el token
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token inválido o expirado.'}), 401

        # Decodificar el token
        decoded_token = jwt.decode(
            access_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token inválido: falta el user_id.'}), 401
       
        # Buscar usuario
        user = db.session.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        if not user.activo:
            return jsonify({'error': 'El usuario no está activo.'}), 403

        # Obtener pedidos
        ambito = data.get('ambito_btn_compras')
         
        # Consultar publicaciones y pedidos
        publicaciones = db.session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito).all()
        pedidos = db.session.query(Pedido).filter_by(user_id=user_id, ambito=ambito).filter(
                                Pedido.estado.in_(["entregado", "terminado"])
                            ).all()

        # Verificar asociaciones
        ids_publicaciones = {publicacion.id for publicacion in publicaciones}
        pedidos_con_publicaciones = [pedido for pedido in pedidos if pedido.publicacion_id in ids_publicaciones]

        if pedidos_con_publicaciones:
            return render_template(
                'productosComerciales/pedidos/compras.html',
                data='',
                layout='layout'
            )

      
       
       # Procesar datos de los pedidos
        pedidos_data = [
            {
                'id': pedido.id,
                'user_id': pedido.user_id,
                'nombre_producto': pedido.nombre_producto,
                'fecha_pedido': pedido.fecha_pedido,
                'precio_venta': pedido.precio_venta,
                'respuesta': pedido.respuesta,
                'estado': pedido.estado,
                'imagen_url': pedido.imagen  # Incluir la URL de la imagen                
            }
            for pedido in pedidos
        ]
        db.session.close()
        # Renderizar la plantilla
        return render_template(
            'productosComerciales/pedidos/compras.html',
            data=pedidos_data,
            layout='layout'
        )

   except Exception as e:
        print("Error:", str(e))
        db.session.rollback()  # Rollback de la sesión en caso de error
        return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

   finally:
        db.session.close()  # Cerrar la sesión siempre

################################################################################################
#########################RETORNA DATOS PEDIDOS DESDE LAYOUT CARRITO SOLAMENTE##################
###############################################################################################

@pedidos.route('/productosComerciales_pedidos_mostrar_layout_carrito/', methods=['POST'])
def productosComerciales_pedidos_mostrar_layout_carrito():
    try:
        data = request.form or request.json
        access_token = data.get('access_token')
        if not access_token:
            return jsonify({'error': 'Token no proporcionado.'}), 401

        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token inválido o expirado.'}), 401

        decoded_token = jwt.decode(
            access_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token inválido: falta el user_id.'}), 401
        
        user = db.session.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        if not user.activo:
            return jsonify({'error': 'El usuario no está activo.'}), 403

        ambito = data.get('ambito_carrito')
        pedidos = db.session.query(Pedido).filter(Pedido.user_id == user_id, Pedido.ambito == ambito).all()

        pedidos_data = [
            {
                'id': pedido.id,
                'user_id': pedido.user_id,
                'nombre_producto': pedido.nombre_producto,
                'fecha_pedido': pedido.fecha_pedido,
                'precio_venta': pedido.precio_venta,
                'estado': pedido.estado,
                'ambito': pedido.ambito,
                'imagen_url': pedido.imagen
            }
            for pedido in pedidos
        ]
        db.session.close()

        # Enviar solo los datos del carrito como JSON
        return jsonify({'pedidos_data': pedidos_data})

    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    finally:
        db.session.close()











@pedidos.route('/productosComerciales_pedidos_eliminar_carrito/', methods=['POST'])
def productosComerciales_pedidos_eliminar_carrito():
    try:
        # Obtener datos del request
        data = request.json
        pedido_id = data.get('pedido_id')
        
        if not pedido_id:
            return jsonify({'error': 'ID de pedido no proporcionado.'}), 400
        
        # Buscar y eliminar el pedido
        pedido = db.session.query(Pedido).filter_by(id=pedido_id).first()
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado.'}), 404
        
        db.session.delete(pedido)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pedido eliminado correctamente.'})
    
    except Exception as e:
        print("Error al eliminar pedido:", str(e))
        db.session.rollback()
        return jsonify({'error': 'Hubo un error al eliminar el pedido.'}), 500
    
    finally:
        db.session.close()

@pedidos.route('/productosComerciales_pedidos_alta_carrito/', methods=['POST'])
def productosComerciales_pedidos_alta_carrito():
    try:
        # Obtener datos del request
        #print(request.form)
        data = request.form or request.json
        access_token = data.get('access_token_btn_carrito1')
        botonPagoOnline = data.get('precio_btn_PagoOnline')
        if not access_token:
            return jsonify({'error': 'Token no proporcionado.'}), 401

        # Validar el token
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token inválido o expirado.'}), 401

        # Decodificar el token
        decoded_token = jwt.decode(
            access_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token inválido: falta el user_id.'}), 401
       
        # Buscar usuario
        user = db.session.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado.'}), 404

        if not user.activo:
            return jsonify({'error': 'El usuario no está activo.'}), 403

        ####### guardar pedido en db ###########
       # Guardar pedido en la base de datos
         # Validar y procesar el precio
        texto = data.get('texto_btn_carrito', '')  # Clave corregida
        precio, resto = obtenerPrecio(texto) if texto else (None, None)
        if not precio:
            precio = 0

        if not guardarPedido(data,user_id,precio):
            return render_template('notificaciones/logeePrimero.html')

       


        # Obtener pedidos
        ambito = data.get('ambito_btn_carrito')
        pedidos = db.session.query(Pedido).filter( Pedido.user_id == user_id, Pedido.ambito == ambito, Pedido.estado == 'pendiente').all()
        
    
       # Procesar datos de los pedidos
        pedidos_data = [
            {
                'id': pedido.id,
                'user_id': pedido.user_id,
                'nombre_producto': pedido.nombre_producto,
                'fecha_pedido': pedido.fecha_pedido,
                'precio_venta': pedido.precio_venta,
                'estado': pedido.estado,
                'imagen_url': pedido.imagen,  # Incluir la URL de la imagen  
                'pagoOnline': botonPagoOnline            
            }
            for pedido in pedidos
        ]
        db.session.close()
        # Renderizar la plantilla
        return render_template(
            'productosComerciales/pedidos/carritoCompras.html',
            data=pedidos_data,
            layout='layout'
        )

    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()  # Rollback de la sesión en caso de error
        return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    finally:
        db.session.close()  # Cerrar la sesión siempre






#############################################################################
#############################################################################
#######################esto es para el chekbox de consultas##################
#############################################################################
#############################################################################

@pedidos.route('/productosComerciales_pedidos_alta_carrito_checkBox/<int:pedido_id>', methods=['POST'])
def productosComerciales_pedidos_alta_carrito_checkBox(pedido_id):
    try:
        data = request.get_json()  # Asegúrate de recibir datos en formato JSON
        nuevo_estado = data.get('estado')

        # Validar token
        access_token = data.get('access_token_btn_carrito1')
        if not access_token or not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'success': False, 'error': 'Token inválido o expirado.'}), 401

        # Decodificar token para obtener el user_id
        decoded_token = jwt.decode(
            access_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'success': False, 'error': 'Token inválido: falta el user_id.'}), 401
        publicacion_id = int(data.get('publicacion_id')) if data.get('publicacion_id') else data.get('publicacion_id')
        # Buscar el pedido
        publicacion = db.session.get(Publicacion, publicacion_id)

        if not publicacion:
            return jsonify({'success': False, 'error': 'publicacion no encontrada.'}), 404

         ####### guardar pedido en db ###########
       # Guardar pedido en la base de datos
         # Validar y procesar el precio
        texto = publicacion.texto  # Clave corregida
        precio, resto = obtenerPrecio(texto) if texto else (None, None)
        cantidad = data.get('cantidadCompra', 1)
        emailCliente = data.get('correo_electronico_cbox', '')        
        if not guardarPedidoDesdeConsultasChecbox(publicacion, user_id, precio,cantidad,emailCliente):
            return jsonify({'success': False, 'message': 'No se pudo guardar el pedido. Inicia sesión e inténtalo de nuevo.'}), 403

        return jsonify({'success': True, 'message': 'Pedido agregado correctamente.'})
    except Exception as e:
        current_app.logger.error(f"Error al actualizar pedido: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud.'}), 500






@pedidos.route('/productosComerciales_pedidos_process_order/', methods=['POST'])
def productosComerciales_pedidos_process_order():
    try:
        # Obtener los datos del cuerpo de la solicitud (JSON)
        data = request.get_json()

        # Obtener el token desde los encabezados
        access_token = request.headers.get('Authorization')
        
        # Verificar si el token está presente
        if not access_token or not access_token.startswith('Bearer '):
            return jsonify({'error': 'Token de acceso no proporcionado o inválido.'}), 401
        
        token = access_token.split(' ')[1]

        # Validar el token
        try:
            decoded_token = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token ha expirado.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido.'}), 401

        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token inválido: falta el user_id.'}), 401
        
        # Extraer y procesar datos del pedido
        imagen_url = data.get('imagen_btn_carrito', '')
        texto = data.get('texto_btn_carrito', '')
        precio_str = data.get('precio_btn_carrito', '')

        # Procesar el precio (si es válido)
        try:
            precio_venta = float(precio_str.strip('$').replace(',', '').replace('.', '')) if precio_str else None
        except ValueError:
            return jsonify({'error': 'El precio proporcionado no es válido.'}), 400
        
        # Obtener datos iniciales
        pedidos_str = data.get('pedido_data_json')
        pedidos = json.loads(pedidos_str)

        # Valores comunes a todos los pedidos (no se alteran)
        tiempo = datetime.utcnow()  # Fecha y hora actual
        cantidad = 0

        # Iterar sobre cada pedido y actualizarlo usando la nueva función
        for pedido_data in pedidos:
            print("Procesando pedido:", pedido_data)
            cantidad_pedido = actualizar_pedido(pedido_data, data, tiempo)
            if isinstance(cantidad_pedido, dict):  # Si hubo un error
                return jsonify(cantidad_pedido), 404
            cantidad += cantidad_pedido

        cargar_entrega_pedido(data, user_id, tiempo, cantidad)

        # Devolver una respuesta exitosa sin detalles del pedido
        return jsonify({
            'message': 'Pedido cargado correctamente',
            'success': True
        }), 200  # 200 es el código de éxito

    except Exception as e:
        # Rollback en caso de error
        db.session.rollback()
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500
    finally:
        db.session.close()  # Asegúrate de cerrar la sesión de la base de datos


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
   
def guardarPedidoDesdeConsultasChecbox(data, userId, precio,cantidad,emailCliente):
    try:
        """
        Guarda un nuevo pedido en la base de datos si no existe uno similar para el mismo usuario.

        :param data: Diccionario con los datos del pedido.
        :param userId: ID del usuario que realiza el pedido.
        :param precio: Precio del producto como cadena (e.g., '$ 100.00').
        :return: Objeto `Pedido` creado o None si ya existe un pedido duplicado.
        """
      
        # Validar y procesar el precio
        texto = data.texto
        precio_venta = float(precio.replace('$', '').replace(',', '').strip())
        tiempo = datetime.now()
        
        # Verificar si ya existe un pedido para este usuario con el mismo producto
      #  producto_existente = Pedido.query.filter_by(user_id=userId, nombre_producto=data.get('titulo_btn_carrrito') ).first()
        
       # if producto_existente:
        #    print(f"Pedido duplicado detectado para user_id={userId} y nombre_producto={data.get('titulo_btn_carrrito')}.")
         #   return None  # No guardar duplicados

        # Crear el nuevo pedido
        nuevo_pedido = Pedido(
            user_id=userId,
            publicacion_id=int(data.id),
            ambito=data.ambito,
            estado='pendiente',
            fecha_pedido=tiempo,
            fecha_entrega=tiempo,
            fecha_consulta=tiempo,
            fecha_baja=tiempo,
            lugar_entrega='',
            nombreCliente ='',
            apellidoCliente = '',
            telefonoCliente = '',
            comentarioCliente = '',
            emailCliente = emailCliente,
            cantidad=int(cantidad),
            precio_costo=precio_venta,
            precio_venta=precio_venta,
            ganancia=precio_venta,
            diferencia=precio_venta,
            nombre_producto=data.titulo,
            descripcion=texto,
            consulta='',
            respuesta='',
            asignado_a='gerente',
            tamaño='',
            provincia='',
            region='',
            sexo='',
            imagen=data.imagen,
            pagoOnline=data.pagoOnline 
        )

        # Guardar en la base de datos
        db.session.add(nuevo_pedido)
        db.session.commit()
        return nuevo_pedido
    
    except Exception as e:
        print(f"Error al guardar pedido: {e}")
        db.session.rollback()  # Revertir cambios en caso de error
        return None  # Indica fallo
def guardarPedido(data, userId, precio):
    try:
        """
        Guarda un nuevo pedido en la base de datos si no existe uno similar para el mismo usuario.

        :param data: Diccionario con los datos del pedido.
        :param userId: ID del usuario que realiza el pedido.
        :param precio: Precio del producto como cadena (e.g., '$ 100.00').
        :return: Objeto `Pedido` creado o None si ya existe un pedido duplicado.
        """
        imagen_url = data.get('imagen_btn_carrito')  # URL de la imagen enviada
        # Validar y procesar el precio
        texto = data.get('texto_btn_carrito', '')  # Clave corregida
        precio_venta = float(precio.strip('$').replace(',', '').replace('.', '')) if precio else None
        tiempo = datetime.now()
        
        # Verificar si ya existe un pedido para este usuario con el mismo producto
      #  producto_existente = Pedido.query.filter_by(user_id=userId, nombre_producto=data.get('titulo_btn_carrrito') ).first()
        
       # if producto_existente:
        #    print(f"Pedido duplicado detectado para user_id={userId} y nombre_producto={data.get('titulo_btn_carrrito')}.")
         #   return None  # No guardar duplicados
        botonPagoOnline = data.get('precio_btn_PagoOnline')
        pagoOnline = botonPagoOnline.lower() == "true" if botonPagoOnline else False
        # Crear el nuevo pedido
        nuevo_pedido = Pedido(
            user_id=userId,
            publicacion_id=int(data.get('publicacion_id_btn_carrito')),
            ambito=data.get('ambito_btn_carrito'),
            estado='pendiente',
            fecha_pedido=tiempo,
            fecha_entrega=tiempo,
            fecha_consulta=tiempo,
            fecha_baja=tiempo,
            lugar_entrega='',
            nombreCliente ='',
            apellidoCliente = '',
            telefonoCliente = '',
            comentarioCliente = '',
            emailCliente = '',
            cantidad=data.get('cantidadCompra', 1),
            precio_costo=precio_venta,
            precio_venta=precio_venta,
            ganancia=precio_venta,
            diferencia=precio_venta,
            nombre_producto=data.get('titulo_btn_carrito'),
            descripcion=texto,
            consulta='',
            respuesta='',
            asignado_a='gerente',
            tamaño='',
            provincia='',
            region='',
            sexo='',
            imagen=imagen_url,
            pagoOnline=pagoOnline
        )

        # Guardar en la base de datos
        db.session.add(nuevo_pedido)
        db.session.commit()
        return nuevo_pedido
    
    except Exception as e:
        print(f"Error al guardar pedido: {e}")
        db.session.rollback()  # Revertir cambios en caso de error
        return None  # Indica fallo

        
    


def obtenerPrecio(data):
    # Expresión regular para extraer el precio
    patron_precio = r'\$\s?\d+(?:\.\d{3})*(?:,\d+)?'

    # Buscar el precio
    coincidencia = re.search(patron_precio, data)

    if coincidencia:
        precio = coincidencia.group()  # El precio completo
        print("Precio separado:", precio)
        
        # El resto del texto sin el precio
        resto = data.replace(precio, '').strip()
        
        # Dividir el resto en palabras
        palabras = resto.split()
        
        # Obtener las primeras 7 palabras y agregar "..."
        resto_corto = ' '.join(palabras[:7]) + " ..."
        
        print("Resto del string (acortado):", resto_corto)
        return precio, resto_corto
    else:
        print("No se encontró un precio en el texto.")
        
        # Si no se encuentra el precio, retornar 0 y el resto del texto (acortado)
        resto_corto = ' '.join(data.split()[:7]) + " ..."
        return 0, resto_corto
