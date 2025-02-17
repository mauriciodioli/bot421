import secrets
from functools import wraps
from flask import (
    Flask,
    Blueprint,
    request,
    redirect,
    jsonify,
    url_for,
    render_template,
    flash,
    make_response
)
from flask import request, make_response, jsonify

from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    set_access_cookies, 
    set_refresh_cookies,
    get_jwt_identity)


import bcrypt
from datetime import datetime, timedelta

from flask_login import LoginManager, login_required, login_user, UserMixin

import jwt
import os
import redis
from flask_dance.consumer import oauth_authorized

from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from requests.exceptions import HTTPError
from models.usuario import Usuario
from datetime import datetime, timedelta
from utils.db import db
import json
import uuid
from usuarios.autenticacion import autenticacion

# Configuración del Blueprint para el registro de usuarios
usuarioUbicacionC = Blueprint("usuarioUbicacionC", __name__)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))  # Convertir a entero
REDIS_DB = int(os.getenv("REDIS_DB"))  # Convertir a entero
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


@usuarioUbicacionC.route('/usuarios-usuarioUbicacion-update-location/', methods=['POST'])
def usuarios_update_location():
    data = request.get_json()
    
    # Obtener el user_id desde la cookie
    user_id = request.cookies.get("user_id")
    
      # Si no hay user_id en la cookie, generamos uno temporal
    new_user_id = False  # Para saber si la cookie debe guardarse
    is_temp_user = False  # Verificar si es usuario temporal
    if not user_id:
        user_id = f"temp_{os.urandom(6).hex()}"
        new_user_id = True  # Marcar que hay un nuevo user_id
        is_temp_user = True
    elif user_id.startswith("temp_"):
        is_temp_user = True

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Clave única en Redis
    redis_key = f"user_location:{user_id}"

    # Recuperar última ubicación
    last_location = redis_client.get(redis_key)
    now = datetime.utcnow()
    
    if last_location:
        last_location = json.loads(last_location)
        last_update = datetime.strptime(last_location.get("timestamp", now.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')

        # Si la ubicación cambió y han pasado más de 24 horas, actualizamos
        if (last_location["latitude"] != latitude or last_location["longitude"] != longitude) and (now - last_update > timedelta(hours=24)):
            redis_client.set(redis_key, json.dumps({"latitude": latitude, "longitude": longitude, "timestamp": now.strftime('%Y-%m-%d %H:%M:%S')}))
            
            # Solo actualizar la base de datos si no es un usuario temporal
            if not is_temp_user:
                response = update_user_location_db(user_id, latitude, longitude)
            else:
                response = jsonify({"status": "Ubicación actualizada en caché pero no en BD", "latitude": latitude, "longitude": longitude, "user_id": user_id})
        else:
            response = jsonify({"status": "Ubicación sin cambios", "latitude": latitude, "longitude": longitude, "user_id": user_id})
    else:
        # Primera vez guardando en Redis
        redis_client.set(redis_key, json.dumps({"latitude": latitude, "longitude": longitude, "timestamp": now.strftime('%Y-%m-%d %H:%M:%S')}))
        
        # Solo actualizar la base de datos si no es un usuario temporal
        if not is_temp_user:
            response = update_user_location_db(user_id, latitude, longitude)
        else:
            response = jsonify({"status": "Ubicación guardada en caché pero no en BD", "latitude": latitude, "longitude": longitude, "user_id": user_id})

    # Solo guardar la cookie si es un nuevo usuario
    if new_user_id:
        response.set_cookie("user_id", user_id, max_age=60*60*24*30)  # 30 días

    return response




def update_user_location_db(user_id, latitude, longitude):
    """ Guarda o actualiza la ubicación del usuario en la base de datos si han pasado 24 horas """
    try:
        # Buscar si el usuario ya tiene una ubicación guardada
        usuario = db.session.query(Usuario).filter_by(id=user_id).first()
        usuarioRegion = db.session.query(UsuarioRegion).filter_by(user_id=user_id).first()
        usuario_ubicacion = db.session.query(UsuarioUbicacion).filter_by(user_id=user_id).first() # Suponiendo que existe un modelo UsuarioUbicacion

        if usuario_ubicacion:
            # Si el registro existe, actualizamos la latitud y longitud
            usuario_ubicacion.latitud = latitude
            usuario_ubicacion.longitud = longitude
        else:
            # Si no existe, creamos un nuevo registro de ubicación
            codigo_postal = usuario.codigoPostal
            id_region = usuarioRegion.id
            nuevo_registro = UsuarioUbicacion(
                user_id=user_id, 
                id_region=id_region, 
                codigoPostal=codigo_postal, 
                latitud=latitude, 
                longitud=longitude
            )
            db.session.add(nuevo_registro)

        db.session.commit()
        return jsonify({
            "status": "Ubicación guardada o actualizada en la base de datos", 
            "latitude": latitude, 
            "longitude": longitude, 
            "user_id": user_id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "Error al guardar ubicación", "error": str(e)})

