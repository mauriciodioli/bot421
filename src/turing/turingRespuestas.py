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
    "gpt2": os.getenv("API_URL_GPT2"),
    "bert": os.getenv("API_URL_BERT"),
    "distilbert": os.getenv("API_URL_DISTILBERT"),
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
          respuesta_ia =respuestaIa(pregunta)

            
        if not pregunta:
            return {'error': f'No se encontró una pregunta con id {pregunta_id}.'}, 404
          # Obtener datos del cliente
        ip_cliente = data.get('ip_cliente', 'default_value')  # Proporciona un valor por defecto
        
        # Verificar si el usuario ya existe
        usuario = turingUser_crear_user(ip_cliente)
        # Serializar y devolver la pregunta encontrada
       # Verifica si la bandera 'boton_modelo_activado' está presente y es True
       
        if model_activado == 'true':
            return jsonify(serialize_pregunta(pregunta, usuario, respuesta_ia))
        else:
            return jsonify(serialize_pregunta(pregunta, usuario, None))

    
    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al obtener la pregunta: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500
    
    finally:
        # Cerrar la sesión de la base de datos para liberar recursos
        db.session.close()





def respuestaIa(pregunta):
    try:
        # Define los headers y payload para la solicitud de respuesta completa
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN_IA}"}
        payload_respuesta = {
            "inputs": pregunta.descripcion,
            "parameters": {
                "max_length": 150,           # Limitar la longitud máxima a 50 palabras
                "num_return_sequences": 1,  # Solo una respuesta
                "temperature": 0.7,         # Reducir aleatoriedad
                "top_p": 0.8,               # Reducir la diversidad
                "top_k": 40,                # Limitar las opciones posibles
                "repetition_penalty": 1.2   # Evitar respuestas repetitivas
            }
        }

        # Realizar la solicitud para la respuesta completa
        response = requests.post(API_URLS["gpt2"], headers=headers, json=payload_respuesta)
        print(response.status_code, response.text)  # Depuración: muestra el código de estado

        if response.status_code == 200:
            try:
                response_json = response.json()
                generated_text = response_json[0].get('generated_text', None)
                if generated_text:
                    # Ahora que tenemos la respuesta completa, pedimos el resumen
                    payload_resumen = {
                        "inputs": generated_text,  # Usar la respuesta completa para resumir
                        "parameters": {
                            "max_length": 10,  # Limitar el resumen a 10 palabras
                            "num_return_sequences": 1,
                            "temperature": 0.7,
                            "top_p": 0.8,
                            "top_k": 40,
                            "repetition_penalty": 1.2  # Mantener la misma penalización de repetición
                        }
                    }

                    # Realizar la solicitud para el resumen
                    response_resumen = requests.post(API_URLS["gpt2"], headers=headers, json=payload_resumen)
                    print(response_resumen.status_code, response_resumen.text)  # Depuración

                    if response_resumen.status_code == 200:
                        try:
                            response_json_resumen = response_resumen.json()
                            resumen = response_json_resumen[0].get('generated_text', None)
                            if resumen:
                                return resumen  # Devuelve el resumen generado
                            else:
                                return "Resumen no disponible"
                        except Exception as e:
                            return {"error": f"Error al procesar el resumen: {str(e)}"}, 500
                    else:
                        return {"error": f"Error al llamar a la API para el resumen: {response_resumen.text}"}, response_resumen.status_code

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


def serialize_pregunta(pregunta, usuario, respuesta_ia):
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
        'respuesta_ia': pregunta.respuesta_ia,
        'usuario_id': usuario.id
    }

    # Incluir el nombre del usuario si el usuario está presente
    if usuario:
        result['nombre'] = usuario.nombre

    # Incluir la respuesta_ia si está presente
    if respuesta_ia:
        result['respuesta_ia'] = respuesta_ia  # Evitar la coma al final que convierte el valor en una tupla

    return result

