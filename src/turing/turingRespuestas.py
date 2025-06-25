# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort    
from utils.db import db
import routes.api_externa_conexion.get_login as get
from turing.conectionSheet import conectionSheet_enviar_productos

import jwt
import random
from datetime import datetime
from models.turing.respuesta import Respuesta, RespuestaSchema
from models.turing.preguntas import Pregunta, PreguntaSchema
from turing.turingUser import turingUser_crear_user
from models.turing.respuestaUsuario import RespuestaUsuario, RespuestaUsuarioSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema
import os
import re
import openai


# Variables globales
total_tokens = 0
total_gastado = 0.0
saldo_disponible = 5.00  # configurá el saldo inicial real

# Costos actuales GPT-4 Turbo (pueden cambiar)
COSTO_INPUT = 0.01 / 1000
COSTO_OUTPUT = 0.03 / 1000  


PUBLIC_KEY_DS = os.getenv("PUBLIC_KEY_DS")
ACCESS_TOKEN_IA = os.getenv("HUGGINGFACE_API_TOKEN")
API_URLS = {
    "gpt4": os.getenv("API_URL_GPT4"),
    "gpt2Model": os.getenv("API_URL_GPT2"),
    "bertModel": os.getenv("API_URL_BERT"),
    "distilbertModel": os.getenv("API_URL_DISTILBERT"),
    "deepSeekModel": os.getenv("API_URL_DEEPSEEK"),
}

HEADER = {
    "Authorization": f"Bearer {PUBLIC_KEY_DS}",
    "Content-Type": "application/json"
}

credentials_path = os.getenv("SECRET_KEY_GPT4_PATH")
# Abre el archivo JSON de credenciales
with open(credentials_path, 'r') as f:
    credentials = json.load(f)

# Accede a las credenciales y úsalo
api_key = credentials['api_key']


# Instanciamos el cliente de OpenAI
client = openai.OpenAI(api_key=api_key)


# Verificar que las URLs estén configuradas correctamente
for model, url in API_URLS.items():
    if not url:
        raise ValueError(f"La URL para el modelo {model} no está configurada en el archivo .env.")


# Define el contexto de la conversación (puedes ir agregando mensajes aquí)
contador_preguntas = 0

context = []




turingRespuestas = Blueprint('turingRespuestas', __name__)
@turingRespuestas.route('/turing-turingRespuestas-crear/', methods=['GET', 'POST'])
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

      
@turingRespuestas.route('/turing-testTuring-obtener-respuestas-id/', methods=['POST'])
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
        model_activado = data.get('boton_modelo_activado')
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
            if valor_aleatorio == 'respuesta_ia'or'respuesta_usuario':
                # Respuesta generada por IA
                if not selected_model:
                    return {'error': 'El modelo seleccionado es obligatorio cuando el modelo está activado.'}, 400

                respuesta_ia = respuestaIa(pregunta, selected_model)
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_ia, 'respondidoPorIA'))

            elif valor_aleatorio == 'respuesta_usuario':
                # Respuesta proporcionada por el usuario
                respuesta_usuario, estado_respuesta= obtener_respuesta_usuario(pregunta,pregunta_id)
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_usuario, 'respondidoPorUsuario'))
        else:
           # Respuesta proporcionada por el usuario si el modelo no está activado
            respuesta_usuario, estado_respuesta = obtener_respuesta_usuario(pregunta, pregunta_id)

            # Verificar el estado de la respuesta
            if estado_respuesta == 'respondidoPorUsuario':
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_usuario, estado_respuesta))
            else:
                # Manejo de casos donde el usuario no respondió
                return jsonify(serialize_pregunta(pregunta, usuario, respuesta_usuario, 'respondidoPorIA'))

    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al procesar la solicitud: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500

    finally:
        # Cerrar la sesión de la base de datos para liberar recursos
        db.session.close()



def respuestaIa(pregunta, selectedModel, contexto=None):
    try:
        
        global contador_preguntas, context, total_tokens, total_gastado, saldo_disponible
        # Verificar que el modelo seleccionado es válido
        if selectedModel not in API_URLS:
            return {"error": f"Modelo '{selectedModel}' no soportado."}, 400

        headers = {"Authorization": f"Bearer {ACCESS_TOKEN_IA}"}
        
         # Incrementamos el contador de preguntas
        contador_preguntas += 1
        
        # Si ya hemos hecho 6 preguntas, iniciamos el contexto con un mensaje de "system"
        if contador_preguntas > 6:
            context = [
                {"role": "system", "content": "Ahora que tenemos algo de contexto, puedes responder a las preguntas de manera coherente con la conversación."},
                *context  # Aseguramos que el contexto previo también esté presente
            ]

        # Añadir la pregunta del usuario al contexto
        context.append({"role": "user", "content": pregunta.descripcion})  # Asegúrate de que 'pregunta.descripcion' sea lo correcto
        
        if selectedModel == 'gpt4':
            input_tokens = contar_tokens(pregunta.descripcion)

           # response = client.chat.completions.create(
           #     model="gpt-4-turbo",
           #     messages=[{"role": "user", "content": pregunta.descripcion}],
           # )
            respuesta = """
                | numero | pais     | producto               | categoria   | descripcion                          | precio_amazon | precio_ebay | precio_aliexpress | proveedor_mas_barato | link_proveedor                                | precio_reventa_sugerido | margen_estimado | imagen                                          |
                |--------|----------|-----------------------------|--------------|----------------------------------------------|----------------|-------------|--------------------|------------------------|--------------------------------------------------------------------------------------|--------------------------|------------------|-------------------------------------------------|
                | 1      | México   | Cepillo alisador iónico     | tecnología   | Alisa el cabello sin dañarlo                 | 26.90          | 24.50       | 17.99              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=cepillo+alisador+i%C3%B3nico        | 39.99                   | 122%             | https://ae01.alicdn.com/kf/H12345abc.jpg        |
                | 2      | España   | Camiseta térmica unisex     | moda         | Mantiene el calor y absorbe sudor            | 17.90          | 15.20       | 11.50              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=camiseta+t%C3%A9rmica+unisex        | 28.00                   | 135%             | https://ae01.alicdn.com/kf/Hshirt567.jpg        |
                | 3      | Argentina| Lámpara LED luna            | hogar        | Luz nocturna con diseño de luna              | 19.50          | 18.00       | 12.99              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=l%C3%A1mpara+LED+luna               | 29.90                   | 130%             | https://ae01.alicdn.com/kf/Hmoonlamp123.jpg     |
                | 4      | Chile    | Dispensador automático agua | hogar        | Ideal para mascotas y personas               | 22.00          | 20.99       | 16.50              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=dispensador+autom%C3%A1tico+agua    | 34.99                   | 112%             | https://ae01.alicdn.com/kf/Hwaterdispenser.jpg  |
                | 5      | Colombia | Cepillo de limpieza facial  | autocuidado | Exfolia suavemente y mejora la piel          | 14.80          | 13.90       | 9.90               | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=cepillo+limpieza+facial             | 22.99                   | 132%             | https://ae01.alicdn.com/kf/Hfacebrush111.jpg    |
                | 6      | Perú     | Mochila antirrobo USB            | tecnología   | Con puerto USB y bolsillos ocultos            | 28.90          | 26.40       | 21.99              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=mochila+antirrobo+usb               | 44.99                   | 105%             | https://ae01.alicdn.com/kf/HmochilaUSB.jpg      |
                | 7      | Portugal | Reloj inteligente deportivo      | tecnología   | Monitorea ritmo, sueño y pasos                | 32.50          | 29.00       | 24.99              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=reloj+inteligente+deportivo         | 49.90                   | 95%              | https://ae01.alicdn.com/kf/Hsmartwatch88.jpg    |
                | 8      | Uruguay  | Fuente de agua para gatos        | mascotas     | Flujo constante, reduce estrés del animal     | 25.90          | 23.40       | 18.75              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=fuente+de+agua+para+gatos           | 34.90                   | 86%              | https://ae01.alicdn.com/kf/Hpetwatercat.jpg     |
                | 9      | Italia   | Gorro térmico unisex            | moda         | Ideal para climas fríos y urbanos             | 12.99          | 11.80       | 8.70               | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=gorro+termico+unisex                | 19.99                   | 130%             | https://ae01.alicdn.com/kf/Hbeanie999.jpg       |
                | 10     | Alemania | Organizador de cables magnético | hogar        | Ordena cargadores y auriculares fácilmente    | 9.99           | 9.20        | 6.90               | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=organizador+cables+magnetico        | 14.99                   | 117%             | https://ae01.alicdn.com/kf/Hcablemag.jpg        |
                | 11     | Brasil   | Difusor de aromas USB           | hogar        | Aroma constante con luces LED decorativas     | 17.50          | 15.99       | 12.60              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=difusor+aromas+usb                  | 27.90                   | 121%             | https://ae01.alicdn.com/kf/Husbscents.jpg       |
                | 12     | Francia  | Soporte ergonómico para laptop  | tecnología   | Mejora postura y ventilación del equipo       | 21.99          | 20.00       | 16.80              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=soporte+ergonomico+laptop           | 34.00                   | 102%             | https://ae01.alicdn.com/kf/Hstandpc.jpg         |
                | 13     | Bolivia  | Lentes de bloqueo de luz azul   | autocuidado | Protege tus ojos frente a pantallas           | 14.00          | 13.50       | 10.20              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=lentes+bloqueo+luz+azul             | 22.99                   | 118%             | https://ae01.alicdn.com/kf/Hbluelight.jpg       |
                | 14     | Paraguay | Almohada cervical memory foam   | autocuidado | Brinda soporte ortopédico para el cuello      | 33.00          | 30.90       | 25.50              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=almohada+cervical+memory+foam       | 49.90                   | 85%              | https://ae01.alicdn.com/kf/Hneckpillow.jpg      |
                | 15     | Bélgica  | Portacepillos UV desinfectante  | hogar        | Esteriliza cepillos de dientes automáticamente| 27.90          | 25.70       | 19.99              | AliExpress             | https://www.aliexpress.com/wholesale?SearchText=portacepillos+uv+desinfectante      | 39.90                   | 100%             | https://ae01.alicdn.com/kf/Huvtoothbrush.jpg    |
                """

          #  if response.choices and len(response.choices) > 0:
           # respuesta = response.choices[0].message.content
            output_tokens = contar_tokens(respuesta)

            # Cálculo de costos
            tokens_usados = input_tokens + output_tokens
            costo = (input_tokens * COSTO_INPUT) + (output_tokens * COSTO_OUTPUT)
            total_tokens += tokens_usados
            total_gastado += costo
            saldo_disponible -= costo

            print(f"📌 Tokens usados: {tokens_usados} (input: {input_tokens}, output: {output_tokens})")
            print(f"💸 Costo consulta: ${costo:.4f}")
            print(f"📊 Total gastado: ${total_gastado:.4f}")
            print(f"💰 Saldo disponible: ${saldo_disponible:.4f}")

            if saldo_disponible <= 0:
                print("🚨 ¡Te quedaste sin saldo disponible para GPT!")

            # Guardar en Sheet si corresponde
            guardaEnSheet = re.match(r"^\s*sheet\b", pregunta.descripcion.strip(), re.IGNORECASE)
            if guardaEnSheet:
                conectionSheet_enviar_productos(respuesta)

            return respuesta
           # else:
            #    return "No se recibió una respuesta válida del modelo."

           
        elif selectedModel == 'deepSeekModel':
            # Configuración especial para DeepSeek
            headers = {
                "Authorization": f"Bearer {PUBLIC_KEY_DS}",
                "Content-Type": "application/json"
            }

            # Definir el payload con la pregunta
            payload = {
                "model": "deepseek-chat",  # Especificar el modelo
                "messages": [{"role": "user", "content": pregunta.descripcion}],
                "temperature": 0.7,
                "top_p": 0.8
            }

            # Realiza la solicitud POST
            response = requests.post(API_URLS[selectedModel], headers=headers, json=payload)
        
        else:
            # Configuración para otros modelos (DistilBERT, BERT, GPT-2, etc.)
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
                payload_respuesta["parameters"].pop("num_return_sequences", None)

            elif selectedModel == 'bertModel':
                pregunta.descripcion = agregar_mask(pregunta.descripcion)
                payload_respuesta = {"inputs": pregunta.descripcion}

            else:  # GPT-2 u otros modelos similares
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

            response = requests.post(API_URLS[selectedModel], headers=headers, json=payload_respuesta)

        print(response.status_code, response.text)  # Depuración

        if response.status_code == 200:
            response_json = response.json()
            resumen = response_json.get("choices", [{}])[0].get("message", {}).get("content", None)

            if resumen:
                return truncar_resumen(resumen, pregunta.descripcion)
            else:
                return "Resumen no disponible"

        return {"error": f"Error al llamar a la API: {response.text}"}, response.status_code

    except Exception as e:
        # Loguear el error para depuración
        print(f"Error al procesar la solicitud: {str(e)}")
        return {'error': 'Ocurrió un error al procesar la solicitud.'}, 500
    except requests.exceptions.RequestException as e:
        # Manejo de otros errores relacionados con la solicitud HTTP
        return {"error": f"Error en la solicitud HTTP: {str(e)}"}, 500



def contar_tokens(texto):
    """
    Estimación de tokens basada en caracteres y palabras.
    Aproximadamente: 1 token ≈ 4 caracteres o 0.75 palabras.
    """
    caracteres = len(texto)
    palabras = len(texto.split())
    
    # Estimación conservadora
    estimacion_por_caracteres = caracteres / 4
    estimacion_por_palabras = palabras / 0.75

    # Promedio de ambas estimaciones para mayor precisión
    return int((estimacion_por_caracteres + estimacion_por_palabras) / 2)

      
  
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
def obtener_respuesta_usuario(pregunta, pregunta_id_):
    # Buscar la pregunta del usuario en la base de datos
    pregunta_usuario = db.session.query(PreguntaUsuario).filter_by(pregunta_id=pregunta_id_).first()

    # Verificar si la pregunta existe y coincide con el ID
    if pregunta_usuario and pregunta.id == pregunta_usuario.pregunta_id:
        return pregunta.respuesta_ia, 'respondidoPorUsuario'
    else:
        return pregunta.respuesta_ia, 'no_respondeUsuario_responde_ia'



def truncar_resumen(resumen, pregunta):
    # Verificar si la pregunta está en el resumen
    if pregunta in resumen:
        resumen = resumen.replace(pregunta, '').strip()  # Eliminar la pregunta del resumen
    
    
    if '.' in resumen:  # Si hay un punto en el resumen
        # Tomar la primera proposición completa hasta el primer punto
        respuesta_corta = ' '.join(resumen.split()[:20])
    else:  # Si no hay un punto, tomar las primeras 20 palabras
        respuesta_corta = ' '.join(resumen.split()[:20])
    
    print("Resumen:", respuesta_corta)
    return respuesta_corta


