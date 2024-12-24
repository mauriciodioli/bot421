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
import os

ACCESS_TOKEN_IA = os.getenv("HUGGINGFACE_API_TOKEN")
API_URLS = {
    "gpt2Model": os.getenv("API_URL_GPT2"),
    "bertModel": os.getenv("API_URL_BERT"),
    "distilbertModel": os.getenv("API_URL_DISTILBERT"),
}
# Verificar que las URLs estén configuradas correctamente
for model, url in API_URLS.items():
    if not url:
        raise ValueError(f"La URL para el modelo {model} no está configurada en el archivo .env.")


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
        nueva_respuesta = serialize(nueva_respuesta, usuario,'respondidoPorUsuario')
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
        # Obtener los datos enviados en la solicitud
        data = request.get_json()
        if not data:
            return {'error': 'No se proporcionaron datos.'}, 400

        # Validar y obtener parámetros necesarios
        pregunta_id = data.get('pregunta_id')
        if not pregunta_id or not str(pregunta_id).isdigit():
            return {'error': 'El parámetro "pregunta_id" es obligatorio y debe ser un número válido.'}, 400

        pregunta_id = int(pregunta_id)
        model_activado = data.get('boton_modelo_activado', 'false')
        selected_model = data.get('selectedModel')
        ip_cliente = data.get('ip_cliente', 'default_value')

        # Buscar la pregunta en la base de datos
        pregunta = db.session.query(Pregunta).filter_by(id=pregunta_id).first()
        if not pregunta:
            return {'error': f'No se encontró una pregunta con id {pregunta_id}.'}, 404

        # Verificar o crear usuario asociado a la IP del cliente
        usuario = turingUser_crear_user(ip_cliente)

        # Selección aleatoria entre IA y usuario
        valores = ['respuesta_ia', 'respuesta_usuario']
        valor_aleatorio = random.choice(valores)
      

        # Lógica de respuesta
        if model_activado == 'true':
            if valor_aleatorio == 'respuesta_ia':
                # Respuesta generada por IA
                if not selected_model:
                    return {'error': 'El modelo seleccionado es obligatorio cuando el modelo está activado.'}, 400

                respuesta_ia = respuestaIa(pregunta, selected_model)
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_ia, 'respondidoPorIA'))

            elif valor_aleatorio == 'respuesta_usuario':
                # Respuesta proporcionada por el usuario
                respuesta_usuario = obtener_respuesta_usuario(pregunta,pregunta_id)
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_usuario, 'respondidoPorUsuario'))
        else:
            # Respuesta proporcionada por el usuario si el modelo no está activado
            respuesta_usuario = obtener_respuesta_usuario(pregunta,pregunta_id)
            return jsonify(serialize_pregunta(pregunta, usuario, respuesta_usuario, 'respondidoPorUsuario'))

    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al procesar la solicitud: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500

    finally:
        # Cerrar la sesión de la base de datos para liberar recursos
        db.session.close()


def respuestaIa(pregunta, selectedModel):
    try:
        # Verificar que el modelo seleccionado es válido
        if selectedModel not in API_URLS:
            return {"error": f"Modelo '{selectedModel}' no soportado."}, 400

        # Definir los headers y payload para la generación de respuesta
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN_IA}"}

        # Configurar los parámetros dependiendo del modelo
        if selectedModel == 'distilbertModel':
            payload_respuesta = {
                "inputs": pregunta.descripcion,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "repetition_penalty": 1.2
                }
            }
            # Elimina num_return_sequences si existe
            payload_respuesta["parameters"].pop("num_return_sequences", None)

        elif selectedModel == 'bertModel':  # BERT no usa 'temperature'
            # Asegurar que el texto contiene [MASK]
            pregunta.descripcion = agregar_mask(pregunta.descripcion)
            payload_respuesta = {"inputs": pregunta.descripcion}

        else:  # Para GPT-2 y otros modelos que soporten temperature
            payload_respuesta = {
                "inputs": pregunta.descripcion,
                "parameters": {
                    "max_length": 150,
                    "num_return_sequences": 1,
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "repetition_penalty": 1.2
                }
            }

        # Realizar la solicitud al modelo seleccionado para generar la respuesta
        response = requests.post(API_URLS[selectedModel], headers=headers, json=payload_respuesta)
        print(response.status_code, response.text)  # Depuración

        if response.status_code == 200:
            response_json = response.json()
            resumen = response_json[0].get('generated_text', None)

            # Limitar al primer punto o 20 palabras
            if resumen:
                if '.' in resumen:
                    respuesta_corta = resumen.split('.')[0] + '.'  # Tomar hasta el primer punto
                else:
                    respuesta_corta = ' '.join(resumen.split()[:20])  # Tomar las primeras 20 palabras
                print("Resumen:", respuesta_corta)
                return respuesta_corta
            else:
                return "Resumen no disponible"

       
        else:
            return {"error": f"Error al llamar a la API: {response.text}"}, response.status_code

    except requests.exceptions.RequestException as e:
        return {"error": f"Error en la solicitud HTTP: {str(e)}"}, 500




      
  
def serialize(respuesta, usuario,quienResponde): 
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
        'respuesta':respuesta.respuesta,
        'quienResponde':quienResponde
    }

    # Si el usuario está presente, incluir el nombre del usuario
    if respuesta:
        result['nombre'] = usuario.nombre
    
    return result


def serialize_pregunta(pregunta, usuario, respuesta_ia=None, quienResponde=None):
    # Validar si la pregunta no existe
    if pregunta is None:
        return {'error': 'Pregunta no encontrada'}, 404

    # Crear el diccionario base
    result = {
        'id': pregunta.id,
        'descripcion': pregunta.descripcion,
        'idioma': pregunta.idioma,
        'valor': pregunta.valor,
        'estado': pregunta.estado,
        'dificultad': pregunta.dificultad,
        'categoria': pregunta.categoria,
        'respuesta_ia': pregunta.respuesta_ia if respuesta_ia is None else respuesta_ia,  # Prioriza respuesta_ia
        'usuario_id': usuario.id if usuario else None,  # Maneja usuario opcional
        'quienResponde': quienResponde
    }

    # Incluir el nombre del usuario si está presente
    if usuario:
        result['nombre'] = usuario.nombre

    return result


def agregar_mask(pregunta, placeholder="__"):
    """
    Reemplaza un marcador de posición con [MASK] en una pregunta.
    Si no encuentra el marcador, agrega [MASK] al final.
    """
    if placeholder in pregunta:
        return pregunta.replace(placeholder, "[MASK]")
    else:
        return pregunta.strip() + " [MASK]"
    
  # Función auxiliar para obtener respuesta de usuario
def obtener_respuesta_usuario(pregunta,pregunta_id_):
    pregunta_usuario = db.session.query(PreguntaUsuario).filter_by(pregunta_id=pregunta_id_).first()
    if pregunta_usuario and pregunta.id == pregunta_usuario.pregunta_id:
        return pregunta.respuesta_ia
    return None