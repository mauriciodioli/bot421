import os
from flask import current_app
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
import bcrypt
from datetime import datetime, timedelta


from flask_login import LoginManager, login_required, login_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies
    
)
from models.usuario import Usuario
from models.cuentas import Cuenta
from routes.api_externa_conexion.cuenta import cuenta
from utils.db import db
import jwt
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
from flask_mail import Mail, Message
import random
import string

cambiarContrasenaUsuarioSistema = Blueprint("cambiarContrasenaUsuarioSistema", __name__)

app = Flask(__name__)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Tu dirección de correo electrónico de Gmail
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Tu contraseña de aplicación de Gmail
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Almacén temporal para códigos de verificación
verification_codes = {}

@cambiarContrasenaUsuarioSistema.route('/usuarios_recuperar_contrasena_usuario_sistema')
def usuarios_recuperar_contrasena_usuario_sistema():
    return render_template('usuarios/cambiarContrasenaUsuarioSistema.html')

@cambiarContrasenaUsuarioSistema.route('/send_reset_email', methods=['POST'])
def send_reset_email():
    try:
        request_data = request.get_json()
        user_email = request_data['email']
        
        # Imprimir los datos para verificar que son correctos
        current_app.logger.info(f"Datos recibidos para enviar correo de recuperación: {request_data}")
        
        # Generar un código de verificación
        verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        # Guardar el código de verificación y su tiempo de expiración (2 minutos)
        verification_codes[user_email] = {
            'code': verification_code,
            'timestamp': datetime.now(),
            'expiry': timedelta(minutes=2)  # 2 minutos de validez
        }
    
        # Construir y enviar el correo electrónico
        sender_email = app.config['MAIL_USERNAME']
        recipients = [user_email]
        
        msg = Message(
            'Código de recuperación de contraseña',
            sender=sender_email,
            recipients=recipients
        )
        msg.body = f'Tu código de verificación es {verification_code}.'
        
        # Imprimir los detalles del correo electrónico
        current_app.logger.info(f"Correo electrónico enviado de '{sender_email}' a '{recipients}': {msg.body}")
        
        mail.send(msg)
    
        return jsonify({'message': 'Correo de recuperación enviado. Verifica tu correo.'})
    
    except Exception as e:
        # Imprimir el error si ocurre algún problema
        current_app.logger.error(f"Error al enviar correo de recuperación: {str(e)}")
        return jsonify({'error': str(e)})
   
@cambiarContrasenaUsuarioSistema.route('/verify_code', methods=['POST'])
def verify_code():
    try:
        data = request.get_json()
        user_email = data['email']
        verification_code = data['verification_code']
        
        stored_code_info = verification_codes.get(user_email)
        
        if stored_code_info and stored_code_info['code'] == verification_code:
            # Verificar si el código ha expirado
            if datetime.now() - stored_code_info['timestamp'] <= stored_code_info['expiry']:
                # Código válido y dentro del tiempo de expiración
                del verification_codes[user_email]  # Eliminar el código después de usarlo
                return jsonify({'message': 'Código de verificación correcto.'}), 200
            else:
                # Código ha expirado
                del verification_codes[user_email]  # Eliminar el código expirado
                return jsonify({'error': 'El código de verificación ha expirado.'}), 400
        else:
            # Código incorrecto
            return jsonify({'error': 'Código de verificación incorrecto.'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)})


@cambiarContrasenaUsuarioSistema.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    new_password = data['new_password']
    
    # Aquí deberías verificar el código de verificación y cambiar la contraseña en la base de datos
    # Este ejemplo omite esos pasos por simplicidad.
    
    return jsonify({'message': 'Contraseña cambiada exitosamente.'})

