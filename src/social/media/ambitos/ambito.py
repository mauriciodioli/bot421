# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort    
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambito_usuario import Ambito_usuario


ambito = Blueprint('ambito', __name__)

@ambito.route('/social-media-ambitos-ambitos')
def social_media_ambitos_ambitos():
    try:      
        datos = db.session.query(Ambitos).all()
        accion = 'crear'
        
        return render_template('media/publicaciones/ambitos.html', 
                               datos=datos, 
                               layout='layout_administracion', 
                               accion=accion)
    except Exception as e:
        print(f'Error al obtener los ámbitos: {e}')
        return 'Problemas con la base de datos', 500
    finally:
        db.session.close()




# Crear un nuevo Ambito
@ambito.route('/social-media-publicaciones-ambitos', methods=['POST'])
def crear_ambito():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Extraer datos necesarios para crear un nuevo ámbito
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        idioma = data.get('idioma', None)
        valor = data.get('valor', None)
        estado = data.get('estado', None)
        user_id = data.get('user_id')        
        user_id = int(user_id)
        # Validar campos obligatorios
        if not nombre or not descripcion or not user_id:
            return jsonify({"error": "Los campos 'nombre', 'descripcion' y 'user_id' son obligatorios"}), 400

        # Validar que el user_id exista
        user = db.session.query(Usuario).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "El user_id proporcionado no existe"}), 400

        # Crear el nuevo ámbito
        nuevo_ambito = Ambitos(
            nombre=nombre,
            descripcion=descripcion,
            idioma=idioma,
            valor=valor,
            estado=estado
        )
        db.session.add(nuevo_ambito)
        db.session.commit()  # Se requiere para obtener el ID asignado automáticamente

        # Crear la relación en Ambito_usuario
        ambito_usuario = Ambito_usuario(
            ambito_id=int(nuevo_ambito.id),  # Usamos el ID generado
            publicacion_id=None,
            user_id=user_id,  # Usamos el ID proporcionado en la solicitud user_id,
            estado=1
        )
        db.session.add(ambito_usuario)
        db.session.commit()
        db.session.close()
        # Serializar y devolver el nuevo ámbito
        return jsonify(ambito_schema.dump(nuevo_ambito)), 201

    except Exception as e:
        db.session.rollback()  # Deshacer cualquier cambio en caso de error
        return jsonify({"error": str(e)}), 500


# Obtener todos los ambitos
@ambito.route('/social-media-publicaciones-obtener-ambitos', methods=['GET'])
def obtener_ambitos():
    try:
        ambitos = db.session.query(Ambitos).all()
        # Convertir los objetos a dicts serializables
        resultado = [
            {
                "id": ambito.id,
                "user_id": 'none',
                "nombre": ambito.nombre,
                "descripcion": ambito.descripcion,
                "idioma": ambito.idioma,
                "valor": ambito.valor,
                "estado": ambito.estado,
            }
            for ambito in ambitos
        ]
        db.session.close()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Obtener un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['GET'])
def obtener_ambito(id):
    try:
        # Buscar el ambito por su ID
        ambito = Ambitos.query.get(id)

        # Verificar si el ambito existe
        if ambito:
            return jsonify(ambitos_schema.dump(ambito)), 200
        else:
            return jsonify({"error": "Ambito no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['PUT'])
def actualizar_ambito(id):
    try:
        # Obtener el ambito existente
        ambito = Ambitos.query.get(id)

        # Verificar si el ambito existe
        if not ambito:
            return jsonify({"error": "Ambito no encontrado"}), 404

        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Actualizar los campos del ambito
        ambito.nombre = data.get('nombre', ambito.nombre)
        ambito.descripcion = data.get('descripcion', ambito.descripcion)
        ambito.idioma = data.get('idioma', ambito.idioma)
        ambito.valor = data.get('valor', ambito.valor)
        ambito.estado = data.get('estado', ambito.estado)
        ambito.user_id = data.get('user_id', ambito.user_id)

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Serializar y devolver el ambito actualizado
        return jsonify(ambitos_schema.dump(ambito)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Eliminar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['DELETE'])
def eliminar_ambito(id):
    try:
        # Buscar el ambito por su ID
        ambito = Ambitos.query.get(id)

        # Verificar si el ambito existe
        if not ambito:
            return jsonify({"error": "Ambito no encontrado"}), 404

        # Eliminar el ambito de la base de datos
        db.session.delete(ambito)
        db.session.commit()
        db.session.close()

        return jsonify({"message": "Ambito eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
