import jwt
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,current_app
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    set_access_cookies, 
    set_refresh_cookies,
    get_jwt_identity)
import random
import secrets
from utils.db import db
from models.usuario import Usuario
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError


token = Blueprint('token',__name__)

SECRET_KEY = 'supersecreto'
# Duración de los tokens
TOKEN_DURATION = 1440  # minutos
REFRESH_TOKEN_DURATION = 43200  # minutos

def generar_token(user_id, valor, cuenta):
    llave = secrets.token_hex(32)
    print(llave)
    # Generar un número aleatorio utilizando el ID de usuario y el valor proporcionado
   
    random_number = random.randint(1, 10000)

    # Obtener la fecha de generación actual
    fecha_generacion = datetime.now()

    # Agregar los datos al token como claims personalizados
    token_data = {
        'user_id': user_id,
        'random_number': random_number,
        'fecha_generacion': fecha_generacion.isoformat(),
        'valor': valor,
        'cuenta': cuenta
    }

  
    # Crear el token
    token_generado = jwt.encode(token_data, llave , algorithm='HS256')
    dato = token_generado + llave
    return dato

def permiso_para_procesar_logica(token_acceso, token_actualizacion, correo_electronico, numero_de_cuenta, tipo_de_acceso):
    if validar_token(token_acceso, "acceso", correo_electronico, numero_de_cuenta, tipo_de_acceso):
        print("El token de acceso es válido. Procesando el archivo...")
        # Aquí procesas el archivo utilizando el token de acceso
        
        # Verificar si el token de actualización es válido
        if validar_token(token_actualizacion, "actualizacion", correo_electronico, numero_de_cuenta, tipo_de_acceso):
            # Si el token de actualización es válido, generar un nuevo token de acceso
            nuevo_token_acceso = generar_nuevo_token_acceso(correo_electronico,numero_de_cuenta,tipo_de_acceso)
            print("Se generó un nuevo token de acceso:", nuevo_token_acceso)
            return nuevo_token_acceso
        else:
            print("El token de actualización no es válido. No se puede generar un nuevo token de acceso.")
            return False
    else:
        print("El token de acceso no es válido. No se puede procesar el archivo.")
        return False

def validar_token(token=None, tipo=None, correo_electronico=None, numero_de_cuenta=None, tipo_de_acceso=None):
    try:
        # Decodificar el token y verificar la firma
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Verificar la identidad del usuario (correo electrónico)
        if payload["identity"] != correo_electronico:
            print("El token no pertenece al usuario especificado.")
            return False

        # Verificar la cuenta asociada
        if payload.get("numero_de_cuenta") != numero_de_cuenta:
            print("El token no pertenece a la cuenta especificada.")
            return False

        # Verificar el tipo de acceso
        if payload.get("acceso") != tipo_de_acceso:
            print("El token no tiene el tipo de acceso correcto.")
            return False

        # Verificar la fecha de expiración
        exp_timestamp = payload["exp"]
        if exp_timestamp < datetime.now().timestamp():
            print("El token ha expirado.")
            return False

        # Verificar el tipo de token
        if tipo == "acceso":
            if payload.get("typ") != "access":
                print("El token no es del tipo de acceso.")
                return False
        elif tipo == "actualizacion":
            if payload.get("typ") != "refresh":
                print("El token no es del tipo de actualización.")
                return False
        else:
            print("Tipo de token no válido.")
            return False

        # Si todas las verificaciones pasan, el token es válido
        return True
    
    except jwt.ExpiredSignatureError:
        print("El token ha expirado.")
        return False
    except jwt.InvalidTokenError:
        print("El token no es válido.")
        return False







import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError
import datetime

def validar_expiracion_token(access_token):
    try:
        # Validar si el token es especial (por ejemplo, para usuarios anónimos)
        if access_token == 'access_dpi_token_usuario_anonimo':
            print("Token de usuario anónimo válido.")
            return True, None  # El segundo valor puede ser None ya que no hay datos asociados

        # Decodificar el token
        token_info = jwt.decode(
            access_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )

        # Validar la expiración (ya manejada automáticamente por jwt.decode)
        exp_timestamp = token_info.get('exp')
        if exp_timestamp:
            current_time = datetime.datetime.utcnow().timestamp()
            if current_time > exp_timestamp:
                print("El token ha expirado.")
                return False, None

        print("El token es válido y está bien formado.")
        return True, token_info  # Devolver la información del token para comprobaciones posteriores

    except ExpiredSignatureError:
        print("Error: El token ha expirado.")
        return False
    except DecodeError:
        print("Error: El token tiene un formato inválido.")
        return False, None
    except InvalidTokenError:
        print("Error: El token no es válido.")
        return False, None

def generar_nuevo_token_acceso(correo_electronico,numero_de_cuenta,tipo_de_acceso):
    return create_access_token(identity=correo_electronico, numero_de_cuenta=numero_de_cuenta, acceso=tipo_de_acceso, expires_delta=timedelta(minutes=TOKEN_DURATION))

def generar_nuevo_token_acceso_vencido(user_id):
      expiry_timestamp = timedelta(minutes=TOKEN_DURATION)
      return  create_access_token(identity=user_id, expires_delta=expiry_timestamp)
    
def decode_token(token):
    try:
        # Decodificar el token con la clave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        # Devolver el nombre de usuario almacenado en el token
        return payload['sub']

    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        # Si el token es inválido o ha expirado, devolver None
        return None