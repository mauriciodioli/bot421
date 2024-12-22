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
        # Obtener los datos enviados en el cuerpo de la solicitud
        data = request.get_json()
        model_activado = data.get('boton_modelo_activado', 'false')
        if not data:
            return {'error': 'No se proporcionaron datos.'}, 400
        
        # Obtener parámetros del cliente
        pregunta_id = int(data.get('pregunta_id'))  # Elimina 'default_value'; pregunta_id puede ser None si no existe
        if not pregunta_id:
            return {'error': 'El parámetro "pregunta_id" es obligatorio.'}, 400
        
        # Buscar la pregunta en la base de datos por el ID proporcionado
        pregunta = db.session.query(Pregunta).filter_by(id=pregunta_id).first()
        if model_activado == 'true':
          selectedModel = data.get('seselectedModel')         
          respuesta_ia =respuestaIa(pregunta,selectedModel)

            
        if not pregunta:
            return {'error': f'No se encontró una pregunta con id {pregunta_id}.'}, 404
          # Obtener datos del cliente
        ip_cliente = data.get('ip_cliente', 'default_value')  # Proporciona un valor por defecto
        
        # Verificar si el usuario ya existe
        usuario = turingUser_crear_user(ip_cliente)
        # Serializar y devolver la pregunta encontrada
       # Verifica si la bandera 'boton_modelo_activado' está presente y es True
       
         # Obtener la respuesta del usuario
        respuesta_usuario = None  # Inicializar la variable
        pregunta_usuario = db.session.query(PreguntaUsuario).filter_by(id=pregunta_id).first()
        if pregunta_usuario and pregunta.id == pregunta_usuario.pregunta_id:
            respuesta_usuario = pregunta.respuesta_ia  # Ajuste para obtener la respuesta del usuario

        # Seleccionar aleatoriamente entre 'respuesta_ia' y 'respuesta_usuario'
        valores = ['respuesta_ia', 'respuesta_usuario']
        valor_aleatorio = random.choice(valores)

        # Verificar si es respuesta_ia o respuesta_usuario
        if valor_aleatorio == 'respuesta_ia':
            if model_activado == 'true':
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_ia, 'respondidoPorIA'))
            else:
                return jsonify(serialize_pregunta(pregunta, usuario, None, 'respondidoPorIA'))

        elif valor_aleatorio == 'respuesta_usuario':
            return jsonify(serialize_pregunta(pregunta, usuario, respuesta_usuario, 'respondidoPorUsuario'))

    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al obtener la pregunta: {str(e)}")
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
                            "max_length": 150,  # Mantén los otros parámetros si son necesarios
                            "temperature": 0.7, 
                            "top_p": 0.8,
                            "top_k": 40,
                            "repetition_penalty": 1.2
                        }
                    }
             # Elimina num_return_sequences
            payload_respuesta["parameters"].pop("num_return_sequences", None)
        
        if selectedModel == 'bertModel':  # BERT no usa 'temperature'
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
            try:
                response_json = response.json()
                generated_text = response_json[0].get('generated_text', None)

                if generated_text:
                    # Preparar el payload para el resumen usando el mismo modelo seleccionado
                    payload_resumen = {
                        "inputs": generated_text,
                        "parameters": {
                            "max_length": 10,  # Resumen limitado a 10 palabras
                            "num_return_sequences": 1,
                            "temperature": 0.7,
                            "top_p": 0.8,
                            "top_k": 40,
                            "repetition_penalty": 1.2
                        }
                    }

                    # Realizar la solicitud para el resumen usando el modelo seleccionado
                    response_resumen = requests.post(API_URLS[selectedModel], headers=headers, json=payload_resumen)
                    print(response_resumen.status_code, response_resumen.text)  # Depuración

                    if response_resumen.status_code == 200:
                        response_json_resumen = response_resumen.json()
                        resumen = response_json_resumen[0].get('generated_text', None)
                        return resumen if resumen else "Resumen no disponible"
                    else:
                        return {
                            "error": f"Error al llamar a la API para el resumen: {response_resumen.text}"
                        }, response_resumen.status_code

                else:
                    return "Texto generado no disponible"
            except Exception as e:
                return {"error": f"Error al procesar la respuesta JSON: {str(e)}"}, 500

        elif response.status_code == 503:
            return {"error": "El servidor no está disponible en este momento."}, 503
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