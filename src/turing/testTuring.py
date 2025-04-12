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
import random
from datetime import datetime
from turing.turingUser import turingUser_crear_user
from models.turing.preguntas import Pregunta, PreguntaSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema
import os



testTuring = Blueprint('testTuring', __name__)



@testTuring.route('/turing-testTuring', methods=['GET', 'POST'])
def social_media_turing_testTuring():
    try:
        return render_template('turing/testTuring.html')
    except Exception as e:
        return str(e)
    
   
    
    
    
# Crear pregunta
@testTuring.route('/turing-testTuring-crear', methods=['POST'])
def crear_pregunta():
    try:
        data = request.get_json()
        
        # Obtiene la IP del cliente, proporciona un valor por defecto si no se encuentra
        ip_cliente = data.get('ip_cliente', 'default_value')
      
        # Verifica si el usuario ya existe
        usuario = turingUser_crear_user(ip_cliente)
      
        # Crear nueva pregunta
        nueva_pregunta = Pregunta(
            descripcion=data.get('descripcion'),
            idioma=data.get('idioma'),
            valor=data['valor'],
            estado=data.get('estado'),
            dificultad=data.get('dificultad'),
            categoria=data.get('categoria'),
            respuesta_ia=data.get('respuesta_ia')
        )
        
        # Agrega la nueva pregunta a la sesión
        db.session.add(nueva_pregunta)
        db.session.commit()  # Guarda la pregunta en la base de datos
        
        # Accede al id de la pregunta después de hacer commit
        pregunta_id = nueva_pregunta.id
        
        # Crear nueva relación entre usuario y pregunta
        tiempo = datetime.now()
        nueva_pregunta_usuario = PreguntaUsuario(
            user_id=usuario.id,  # Asegúrate de que `usuario.id` esté definido
            pregunta_id=pregunta_id,
            dificultad=data.get('dificultad'),
            estado=data.get('estado'),
            tiempo=tiempo.strftime('%Y-%m-%d %H:%M:%S'),
            fecha=tiempo.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Agrega la nueva relación a la sesión
        db.session.add(nueva_pregunta_usuario)
        db.session.commit()
        
        # Serializa la nueva pregunta
        respuesta_serializada = serialize(nueva_pregunta,usuario,'respondidoPorUsuario')
        
        return jsonify(respuesta_serializada), 201

    except Exception as e:
        # Realiza rollback de la sesión en caso de error
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    finally:
        # Asegura el cierre de la sesión al final
        db.session.close()



# Leer todas las preguntas
@testTuring.route('/turing-testTuring-obtener', methods=['GET'])
def obtener_preguntas():
    preguntas = Pregunta.query.all()
    return preguntas_schema.jsonify(preguntas), 200


# Leer una pregunta por ID
@testTuring.route('/turing-testTuring-obtener-id/<int:id>/categoria/<string:categoria>', methods=['GET'])
def obtener_pregunta(id, categoria):
    try:
        # Realiza validaciones si es necesario
        if not isinstance(id, int):
            return jsonify({"error": "El campo 'id' debe ser un número entero"}), 400

        if not categoria or not isinstance(categoria, str):
            return jsonify({"error": "El campo 'categoria' es obligatorio y debe ser un string"}), 400

        # Obtener el ID máximo de la tabla Pregunta
        max_id = db.session.query(db.func.max(Pregunta.id)).scalar()
        
        # Determinar el siguiente ID, bucle para encontrar el próximo válido
        siguiente_id = id + 1 if id + 1 <= max_id else 1
        pregunta = None

        while siguiente_id <= max_id:  # Buscar pregunta existente
            pregunta = db.session.query(Pregunta).filter(Pregunta.id == siguiente_id).first()

            if pregunta:  # Si existe, salir del bucle
                if pregunta.categoria == categoria:
                    break
               
            siguiente_id += 1  # Incrementar para buscar el siguiente ID válido

        if not pregunta:  # Si no se encontró ninguna pregunta válida
            return {'error': 'Pregunta no encontrada'}, 404

        return jsonify(serialize(pregunta,None,'respondidoPorIA'))
    
    except Exception as e:
        # Loguear el error para depuración (puedes usar una herramienta de logging aquí)
        print(f"Error al obtener la pregunta: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500
    
    finally:
        # Cerrar la sesión para liberar los recursos
        db.session.close()  # O también puedes usar db.session.close() dependiendo de tu configuración.



    
# Actualizar pregunta
@testTuring.route('/turing-testTuring-actualizar/<int:id>', methods=['PUT'])
def actualizar_pregunta(id):
    try:
        data = request.get_json()
        pregunta = Pregunta.query.get_or_404(id)

        pregunta.nombre = data.get('nombre', pregunta.nombre)
        pregunta.descripcion = data.get('descripcion', pregunta.descripcion)
        pregunta.idioma = data.get('idioma', pregunta.idioma)
        pregunta.valor = data.get('valor', pregunta.valor)
        pregunta.estado = data.get('estado', pregunta.estado)
        pregunta.dificultad = data.get('dificultad', pregunta.dificultad)
        pregunta.categoria = data.get('categoria', pregunta.categoria)

        db.session.commit()
        return pregunta_schema.jsonify(pregunta), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Eliminar pregunta
@testTuring.route('/turing-testTuring-eliminar/<int:id>', methods=['DELETE'])
def eliminar_pregunta(id):
    pregunta = Pregunta.query.get_or_404(id)
    db.session.delete(pregunta)
    db.session.commit()
    return jsonify({'message': 'Pregunta eliminada exitosamente'}), 200

# --- testTuring PARA PREGUNTA_USUARIO ---

def crear_pregunta_usuario(user_id,pregunta_id,dificultad,estado,tiempo,fecha):
    try:
        data = request.get_json()
        nueva_pregunta_usuario = PreguntaUsuario(
            user_id=data['user_id'],
            pregunta_id=data['pregunta_id'],
            dificultad=data.get('dificultad'),
            estado=data.get('estado'),
            tiempo=data.get('tiempo'),
            fecha=data['fecha']
        )
        db.session.add(nueva_pregunta_usuario)
        db.session.commit()
        return pregunta_usuario_schema.jsonify(nueva_pregunta_usuario), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Leer todas las preguntas-usuario


# Leer una pregunta-usuario por ID
def obtener_pregunta_usuario(id):
    pregunta_usuario = PreguntaUsuario.query.get_or_404(id)
    return pregunta_usuario_schema.jsonify(pregunta_usuario), 200

def obtener_pregunta_usuario(pregunta_id):
    pregunta_usuario = PreguntaUsuario.query.get_or_404(pregunta_id)
    return pregunta_usuario_schema.jsonify(pregunta_usuario), 200

# Actualizar pregunta-usuario
def actualizar_pregunta_usuario(id):
    try:
        data = request.get_json()
        pregunta_usuario = PreguntaUsuario.query.get_or_404(id)

        pregunta_usuario.user_id = data.get('user_id', pregunta_usuario.user_id)
        pregunta_usuario.pregunta_id = data.get('pregunta_id', pregunta_usuario.pregunta_id)
        pregunta_usuario.dificultad = data.get('dificultad', pregunta_usuario.dificultad)
        pregunta_usuario.estado = data.get('estado', pregunta_usuario.estado)
        pregunta_usuario.tiempo = data.get('tiempo', pregunta_usuario.tiempo)
        pregunta_usuario.fecha = data.get('fecha', pregunta_usuario.fecha)

        db.session.commit()
        return pregunta_usuario_schema.jsonify(pregunta_usuario), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Eliminar pregunta-usuario
def eliminar_pregunta_usuario(id):
    pregunta_usuario = PreguntaUsuario.query.get_or_404(id)
    db.session.delete(pregunta_usuario)
    db.session.commit()
    return jsonify({'message': 'PreguntaUsuario eliminada exitosamente'}), 200


def serialize(pregunta, usuario,quienResponde): 
    if pregunta is None:
        return {'error': 'Pregunta no encontrada'}, 404

    # Si usuario es None, omitir el campo de 'nombre'
    result = {
        'id': pregunta.id,  
        'descripcion': pregunta.descripcion,
        'idioma': pregunta.idioma,
        'valor': pregunta.valor,
        'estado': pregunta.estado,
        'dificultad': pregunta.dificultad,
        'categoria': pregunta.categoria,
        'respuesta_ia': pregunta.respuesta_ia,
        'quienResponde':quienResponde
    }

    # Si el usuario está presente, incluir el nombre del usuario
    if usuario:
        result['nombre'] = usuario.nombre
    
    return result
