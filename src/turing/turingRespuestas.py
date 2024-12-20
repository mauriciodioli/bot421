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
from models.turing.respuesta import Respuesta, RespuestaSchema
from models.turing.preguntas import Pregunta, PreguntaSchema
from turing.turingUser import turingUser_crear_user
from models.turing.respuestaUsuario import RespuestaUsuario, RespuestaUsuarioSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema


turingRespuestas = Blueprint('turingRespuestas', __name__)
@turingRespuestas.route('/turing-turingRespuestas-crear', methods=['GET', 'POST'])
def social_media_turing_turingRespuestas_crear():
    try:
        data = request.get_json()
        
        # Obtener datos del cliente
        ip_cliente = data.get('ip_cliente', 'default_value')  # Proporciona un valor por defecto
        
        # Verificar si el usuario ya existe
        usuario = turingUser_crear_user(ip_cliente)
        
        # Crear la nueva respuesta
        nueva_respuesta = Respuesta(
            pregunta_id=int(data['pregunta_id']),
            usuario_id=usuario.id,
            idioma=data.get('idioma'),
            valor=data['valor'],
            estado=data.get('estado'),
            dificultad=data.get('dificultad'),
            categoria=data.get('categoria'),
            respuesta=data.get('respuesta_humano')
        )
        
        # Agregar la nueva respuesta a la sesión
        db.session.add(nueva_respuesta)
        db.session.commit()  # Guarda la respuesta en la base de datos
        
        # Acceder al id de la respuesta después de hacer commit
        respuesta_id = nueva_respuesta.id
        tiempo = datetime.now()  # Guardar el tiempo actual
        
        nueva_respuesta_usuario = RespuestaUsuario(
            usuario_id=usuario.id,
            pregunta_id=int(data['pregunta_id']),
            respuesta_id=respuesta_id,
            valor_respuesta_usuario=data.get('valor_respuesta_usuario'),
            valor_respuesta_turing=data.get('valor_respuesta_turing'),
        )
        
        # Agregar la nueva relación de usuario-respuesta
        db.session.add(nueva_respuesta_usuario)
        db.session.commit()
        
        # Serializar la nueva respuesta para enviarla como respuesta
        nueva_respuesta = serialize(nueva_respuesta, usuario)
        return jsonify(nueva_respuesta), 201

    except Exception as e:
        db.session.rollback()  # Revertir cualquier cambio en la base de datos en caso de error
        return jsonify({'error': str(e)}), 400

    finally:
        # Asegurar que la sesión de la base de datos se cierre
        db.session.close()

      


@turingRespuestas.route('/turing-testTuring-obtener-respuestas-id', methods=['POST'])
def turing_testTuring_obtener_respuestas_id():
    try:
        # Obtener los datos enviados en el cuerpo de la solicitud
        data = request.get_json()
        if not data:
            return {'error': 'No se proporcionaron datos.'}, 400
        
        # Obtener parámetros del cliente
        pregunta_id = int(data.get('pregunta_id'))  # Elimina 'default_value'; pregunta_id puede ser None si no existe
        if not pregunta_id:
            return {'error': 'El parámetro "pregunta_id" es obligatorio.'}, 400
        
        # Buscar la pregunta en la base de datos por el ID proporcionado
        pregunta = db.session.query(Pregunta).filter_by(id=pregunta_id).first()

        if not pregunta:
            return {'error': f'No se encontró una pregunta con id {pregunta_id}.'}, 404
          # Obtener datos del cliente
        ip_cliente = data.get('ip_cliente', 'default_value')  # Proporciona un valor por defecto
        
        # Verificar si el usuario ya existe
        usuario = turingUser_crear_user(ip_cliente)
        # Serializar y devolver la pregunta encontrada
        return jsonify(serialize_pregunta(pregunta, usuario))
    
    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al obtener la pregunta: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500
    
    finally:
        # Cerrar la sesión de la base de datos para liberar recursos
        db.session.close()



  
def serialize(respuesta, usuario): 
    if respuesta is None:
        return {'error': 'respuesta no encontrada'}, 404

    # Si usuario es None, omitir el campo de 'nombre'
    result = {
        'id': respuesta.id,  
        'pregunta_id': respuesta.pregunta_id,
        'usuario_id': respuesta.usuario_id,
        'idioma': respuesta.idioma,
        'valor': respuesta.valor,
        'estado': respuesta.estado,
        'dificultad': respuesta.dificultad,
        'categoria': respuesta.categoria,
        'respuesta':respuesta.respuesta
    }

    # Si el usuario está presente, incluir el nombre del usuario
    if respuesta:
        result['nombre'] = usuario.nombre
    
    return result


def serialize_pregunta(pregunta, usuario): 
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
        'usuario_id': usuario.id
    }

    # Si el usuario está presente, incluir el nombre del usuario
    if usuario:
        result['nombre'] = usuario.nombre
    
    return result
