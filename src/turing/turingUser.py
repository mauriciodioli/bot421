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

from models.turing.preguntas import Pregunta, PreguntaSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema
from models.turing.testTuringUser import TestTuringUser


turingUser = Blueprint('turingUser', __name__)


def turingUser_crear_user(ip_cliente):
    
    usuario = db.session.query(TestTuringUser).filter_by(ip_cliente=ip_cliente).first()
    if usuario:
        return usuario
    else:
        # Genera un número entre 1 y 100 como nombre (puedes cambiar esto)
        nombre = random.randint(1, 100)
        nombre = str(nombre) + "_" + ip_cliente
        # Si el usuario no existe, crearlo
        nuevo_usuario = TestTuringUser(nombre=nombre, 
                                ip_cliente=ip_cliente,
                                fecha_registro=datetime.now(),
                                estado="activo",
                                )
        db.session.add(nuevo_usuario)
        db.session.commit()
       
        return nuevo_usuario
    
def turingUser_eliminar_user(id):
    user = db.session.query(TestTuringUser).filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        db.session.close()
        return True
    else:
        return False





@turingUser.route('/turing-turingUser-obtener-id/<int:id>', methods=['GET'])
def obtener_pregunta_usuario(id):
    try:
        # Obtener el ID máximo de la tabla Pregunta
        max_id = db.session.query(db.func.max(TestTuringUser.id)).scalar()
        
        # Determinar el siguiente ID, bucle para encontrar el próximo válido
        siguiente_id = id + 1 if id + 1 <= max_id else 1
        usuario = None

        while siguiente_id <= max_id:  # Buscar pregunta existente
            usuario = db.session.query(TestTuringUser).get(siguiente_id)
            if usuario:  # Si existe, salir del bucle
                break
            siguiente_id += 1  # Incrementar para buscar el siguiente ID válido
        
        if not usuario:  # Si no se encontró ninguna pregunta válida
            return {'error': 'Pregunta no encontrada'}, 404
      # Obtén el primer registro filtrado de PreguntaUsuario
        pregunta_usuario_filtrado = db.session.query(PreguntaUsuario).filter_by(user_id=usuario.id).first()

        # Asegúrate de que el resultado no sea None antes de acceder a sus atributos
        if pregunta_usuario_filtrado:
            pregunta_a_enviar = db.session.query(Pregunta).filter_by(id=pregunta_usuario_filtrado.pregunta_id).first()
            return jsonify(serialize(pregunta_a_enviar, usuario))  # Enviar los datos serializados
        else:
            return jsonify({'not_found': True})  # Indicar que no se encontraron datos
       
    except Exception as e:
        # Loguear el error para depuración (puedes usar una herramienta de logging aquí)
        print(f"Error al obtener la pregunta: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500
    
    finally:
        # Cerrar la sesión para liberar los recursos
        db.session.close()  # O también puedes usar db.session.close() dependiendo de tu configuración.



def serialize(pregunta, usuario): 
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
        'respuesta_ia': pregunta.respuesta_ia
    }

    # Si el usuario está presente, incluir el nombre del usuario
    if usuario:
        result['nombre'] = usuario.nombre
    
    return result
