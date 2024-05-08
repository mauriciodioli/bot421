import jwt
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from datetime import datetime, timedelta
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


token = Blueprint('token',__name__)

SECRET_KEY = 'supersecreto'
# Duración de los tokens
TOKEN_DURATION = 30  # minutos
REFRESH_TOKEN_DURATION = 60  # minutos

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

def permiso_para_procesar_logica(token_acceso,token_actualizacion,correo_electronico):
    
    if validar_token(token_acceso, "acceso",correo_electronico):
        print("El token de acceso es válido. Procesando el archivo...")
        # Aquí procesas el archivo utilizando el token de acceso
        
        # Verificar si el token de actualización es válido
        if validar_token(token_actualizacion, "actualizacion"):
            # Si el token de actualización es válido, generar un nuevo token de acceso
            nuevo_token_acceso = generar_nuevo_token_acceso(correo_electronico)
            print("Se generó un nuevo token de acceso:", nuevo_token_acceso)
            return nuevo_token_acceso
        else:
            print("El token de actualización no es válido. No se puede generar un nuevo token de acceso.")
            return False
    else:
        print("El token de acceso no es válido. No se puede procesar el archivo.")
        return False
    
def validar_token(token=None, tipo=None,correo_electronico=None):
    try:
        # Decodificar el token y verificar la firma
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decode_token(token)
        # Verificar la fecha de expiración
        exp_timestamp = payload["exp"]
        if exp_timestamp < datetime.now().timestamp():
            print("El token ha expirado.")
            return False
        #usuario_nombre = db.session.query(Usuario).filter_by(user_id=user_id, accountCuenta=account).first()
        #if username == 
        # Verificar el tipo de token
        if tipo == "acceso":
            # Agregar cualquier otra verificación específica para el token de acceso, si es necesario
            if payload.get("typ") != "access":
                print("El token no es del tipo de acceso.")
                return False
        elif tipo == "actualizacion":
            # Agregar cualquier otra verificación específica para el token de actualización, si es necesario
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

def generar_nuevo_token_acceso(correo_electronico):
    return create_access_token(identity=correo_electronico, expires_delta=timedelta(minutes=TOKEN_DURATION))

def decode_token(token):
    try:
        # Decodificar el token con la clave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        # Devolver el nombre de usuario almacenado en el token
        return payload['sub']

    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        # Si el token es inválido o ha expirado, devolver None
        return None