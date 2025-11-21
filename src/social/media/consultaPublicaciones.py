
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
from utils.db_session import get_db_session 


from models.pedidos.pedidoEntregaPago import PedidoEntregaPago
from models.publicaciones.publicaciones import Publicacion



#mp = MercadoPago("CLIENT_ID", "CLIENT_SECRET")

consultaPublicaciones = Blueprint('consultaPublicaciones',__name__)

@consultaPublicaciones.route('/media_consultaPublicaciones_muestra/', methods=['POST'])
def media_consultaPublicaciones_muestra():
    try:
        # Obtener datos del request
        data = request.form or request.json
        access_token = data.get('access_token_btn_consultas')
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
        with get_db_session() as session:
            # Buscar usuario
            user = session.query(Usuario).filter(Usuario.id == user_id).first()
            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404

            if not user.activo:
                return jsonify({'error': 'El usuario no está activo.'}), 403

            # Obtener y validar el ámbito
            ambito = data.get('ambito_btn_consultas')
            if not ambito:
                return jsonify({'error': 'Ámbito no proporcionado.'}), 400

            # Filtro de publicaciones
            publicaciones = session.query(Publicacion).with_entities(
                                    Publicacion.id,
                                    Publicacion.user_id,
                                    Publicacion.titulo,
                                    Publicacion.correo_electronico,
                                    Publicacion.descripcion,
                                    Publicacion.fecha_creacion,                                
                                    Publicacion.texto,
                                    Publicacion.imagen
                                ).filter(
                                    Publicacion.user_id == user_id,
                                    Publicacion.ambito == ambito,
                                    Publicacion.estado == 'activo',
                                    Publicacion.botonCompra.is_(True)  # Ignora NULL automáticamente
                                ).all()



            # Procesar los datos
            data = []
            if not publicaciones:
                return render_template(
                                'media/publicaciones/consultasPublicaciones.html',
                                data='',
                                layout='layout'
                            )
            for publicacion in publicaciones:
                precio, resto = obtenerPrecio(publicacion.texto) if publicacion.texto else (None, None)
                data.append({
                    'id': publicacion.id,
                    'user_id': publicacion.user_id,
                    'nombre_producto': publicacion.titulo,
                    'texto': publicacion.texto,
                    'precio_venta': precio,  # Corregido
                    'correoElectronico': publicacion.correo_electronico,  # Corregido
                    'descripcion': publicacion.descripcion,
                    'fechaCreacion': publicacion.fecha_creacion,
                    'imagen_url':publicacion.imagen
                })
           
            return render_template(
                'media/publicaciones/consultasPublicaciones.html',
                data=data,
                layout='layout'
            )

    except Exception as e:
        print("Error:", str(e))
      
        return jsonify({'error': 'Hubo un error en la solicitud.'}), 500


@consultaPublicaciones.route('/obtener_detalle_publicacion/<int:id>', methods=['GET'])
def obtener_detalle_publicacion(id):
    try:
        with get_db_session() as session:
            # Obtener la publicación por ID
            publicacion = session.query(Publicacion).filter(Publicacion.id == id).first()
            
            if not publicacion:
                return jsonify({'error': 'Publicación no encontrada'}), 404
            
            detalle = {
                'user_id': publicacion.user_id,
                'nombre_producto': publicacion.titulo,
                'texto': publicacion.texto,
                'correoElectronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'fechaCreacion': publicacion.fecha_creacion
            }
          
            return jsonify(detalle)  # Devuelve JSON

    except Exception as e:
        return jsonify({'error': 'Error al obtener los datos de la publicación'}), 500

@consultaPublicaciones.route('/media_consultaPublicaciones_lupa_muestra/', methods=['POST'])
def media_consultaPublicaciones_lupa_muestra():
    try:
        # Obtener datos del request
        data = request.form or request.json
        access_token = data.get('accessToken')
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
        with get_db_session() as session:
            # Buscar usuario
            user = session.query(Usuario).filter(Usuario.id == user_id).first()
            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404

            if not user.activo:
                return jsonify({'error': 'El usuario no está activo.'}), 403

            # Obtener y validar el ámbito
            ambito = data.get('ambito')
            if not ambito:
                return jsonify({'error': 'Ámbito no proporcionado.'}), 400
            id_consulta = int(data.get('consulta'))
            # Filtro de publicaciones
            publicaciones = session.query(Publicacion).with_entities(
                Publicacion.id,
                Publicacion.user_id,
                Publicacion.titulo,
                Publicacion.correo_electronico,
                Publicacion.descripcion,
                Publicacion.fecha_creacion,                                
                Publicacion.texto,
                Publicacion.imagen
            ).filter(
                Publicacion.user_id == id_consulta,
                Publicacion.ambito == ambito,
                Publicacion.estado == 'activo',
                Publicacion.botonCompra.is_(True)  # Ignora NULL automáticamente
            ).all()

            # Procesar los datos
            data = []
            if not publicaciones:
                return jsonify({'data': []})  # Si no hay publicaciones, regresa un array vacío

            for publicacion in publicaciones:
                precio = publicacion.precio if publicacion.precio else 0
               
                data.append({
                    'id': publicacion.id,
                    'user_id': publicacion.user_id,
                    'nombre_producto': publicacion.titulo,
                    'texto': publicacion.texto,
                    'precio_venta': precio,
                    'correoElectronico': publicacion.correo_electronico,
                    'descripcion': publicacion.descripcion,
                    'fechaCreacion': publicacion.fecha_creacion,
                    'imagen_url': publicacion.imagen
                })
            

            # Regresa los datos en formato JSON
            return jsonify({'data': data, 'layout': 'layout'})

    except Exception as e:
        print("Error:", str(e))
       
        return jsonify({'error': 'Hubo un error en la solicitud.'}), 500




























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
