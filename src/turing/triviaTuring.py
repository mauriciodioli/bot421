<<<<<<< HEAD
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import math
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
from models.turing.trivia import Trivia
from turing.turingUser import turingUser_crear_user
from models.turing.respuestaUsuario import RespuestaUsuario, RespuestaUsuarioSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema


triviaTuring = Blueprint('triviaTuring', __name__)


@triviaTuring.route('/turing-triviaTuring-crear', methods=['POST'])
def turing_triviaTuring_crear():
    try:
        # Obtener los datos enviados en formato JSON
        datos = request.get_json()

        # Extraer los valores específicos del JSON
        pregunta_respuesta_id = datos.get('pregunta_respuesta_id')
        usuario_id = datos.get('usuario_id')
        fecha_creacion = datos.get('fecha_creacion')
        respuesta_trivia = datos.get('respuesta')
        quienResponde = datos.get('quienResponde')

        # Validar que se hayan recibido los datos necesarios
        if not (pregunta_respuesta_id and usuario_id and fecha_creacion and respuesta_trivia):
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        acierto = 0
        if respuesta_trivia == 'Maquina':
            if quienResponde == 'respondidoPorIA':
                acierto = 1
            if quienResponde == 'respondidoPorUsuario':
                acierto = 0    
                
                

        elif respuesta_trivia == 'Humano':
            if quienResponde == 'respondidoPorIA':
                acierto = 0
            if quienResponde == 'respondidoPorUsuario':
                acierto = 1    

        # Buscar o crear una nueva trivia para el usuario
        trivia = db.session.query(Trivia).filter_by(user_id=usuario_id, fecha=datetime.now().date()).first()
        if not trivia:
            trivia = Trivia(
                user_id=usuario_id,
                estado=respuesta_trivia,
                total_respuestas=0,
                total_respuestas_correctas=0,
                total_respuestas_incorrectas=0,
                fecha=datetime.now().date()
            )
            db.session.add(trivia)

        # Actualizar la trivia con los resultados
        resutaldo_devolver = calcula_respuesta(trivia, acierto)

        db.session.commit()

        # Responder al cliente con éxito
        return jsonify({
            'resutaldo_devolver': resutaldo_devolver,
            'acierto': acierto
            }), 200

    except Exception as e:
        # Manejo de errores
        print(f"Error al procesar los datos: {str(e)}")
        return jsonify({'error': 'Ocurrió un error al procesar los datos'}), 500

    finally:
        # Cerrar la sesión para liberar los recursos
        db.session.close()


def calcula_respuesta(trivia, acierto):
    trivia.total_respuestas += 1
    if acierto == 1:
        trivia.total_respuestas_correctas += 1
    else:
        trivia.total_respuestas_incorrectas += 1

    # Calcular el porcentaje de respuestas correctas
    if trivia.total_respuestas > 0:
        trivia.porcentaje = (trivia.total_respuestas_correctas / trivia.total_respuestas) * 100
    else:
        trivia.porcentaje = 0

    return math.ceil(trivia.porcentaje)
     
=======
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import math
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
from models.turing.trivia import Trivia
from turing.turingUser import turingUser_crear_user
from models.turing.respuestaUsuario import RespuestaUsuario, RespuestaUsuarioSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema


triviaTuring = Blueprint('triviaTuring', __name__)


@triviaTuring.route('/turing-triviaTuring-crear', methods=['POST'])
def turing_triviaTuring_crear():
    try:
        # Obtener los datos enviados en formato JSON
        datos = request.get_json()

        # Extraer los valores específicos del JSON
        pregunta_respuesta_id = datos.get('pregunta_respuesta_id')
        usuario_id = datos.get('usuario_id')
        fecha_creacion = datos.get('fecha_creacion')
        respuesta_trivia = datos.get('respuesta')
        quienResponde = datos.get('quienResponde')

        # Validar que se hayan recibido los datos necesarios
        if not (pregunta_respuesta_id and usuario_id and fecha_creacion and respuesta_trivia):
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        acierto = 0
        if respuesta_trivia == 'Maquina':
            if quienResponde == 'respondidoPorIA':
                acierto = 1
            if quienResponde == 'respondidoPorUsuario':
                acierto = 0    
                
                

        elif respuesta_trivia == 'Humano':
            if quienResponde == 'respondidoPorIA':
                acierto = 0
            if quienResponde == 'respondidoPorUsuario':
                acierto = 1    

        # Buscar o crear una nueva trivia para el usuario
        trivia = db.session.query(Trivia).filter_by(user_id=usuario_id, fecha=datetime.now().date()).first()
        if not trivia:
            trivia = Trivia(
                user_id=usuario_id,
                estado=respuesta_trivia,
                total_respuestas=0,
                total_respuestas_correctas=0,
                total_respuestas_incorrectas=0,
                fecha=datetime.now().date()
            )
            db.session.add(trivia)

        # Actualizar la trivia con los resultados
        resutaldo_devolver = calcula_respuesta(trivia, acierto)

        db.session.commit()

        # Responder al cliente con éxito
        return jsonify({
            'resutaldo_devolver': resutaldo_devolver,
            'acierto': acierto
            }), 200

    except Exception as e:
        # Manejo de errores
        print(f"Error al procesar los datos: {str(e)}")
        return jsonify({'error': 'Ocurrió un error al procesar los datos'}), 500

    finally:
        # Cerrar la sesión para liberar los recursos
        db.session.close()


def calcula_respuesta(trivia, acierto):
    trivia.total_respuestas += 1
    if acierto == 1:
        trivia.total_respuestas_correctas += 1
    else:
        trivia.total_respuestas_incorrectas += 1

    # Calcular el porcentaje de respuestas correctas
    if trivia.total_respuestas > 0:
        trivia.porcentaje = (trivia.total_respuestas_correctas / trivia.total_respuestas) * 100
    else:
        trivia.porcentaje = 0

    return math.ceil(trivia.porcentaje)
     
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
