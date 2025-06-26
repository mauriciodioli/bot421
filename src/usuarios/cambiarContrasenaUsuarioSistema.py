import os
import smtplib
import secrets
import string
import bcrypt
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Creating  Routes
from pipes import Template
from unittest import result
import requests
import json
from flask import current_app,Flask,Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta

# Configurar la aplicación Flask
app = Flask(__name__)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Usar el puerto adecuado para TLS
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Obtener usuario de variables de entorno
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Obtener contraseña de variables de entorno
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


# Almacén temporal para códigos de verificación
verification_codes = {}

# Blueprint para cambiar contraseña de usuario en el sistema
cambiarContrasenaUsuarioSistema = Blueprint("cambiarContrasenaUsuarioSistema", __name__)

@cambiarContrasenaUsuarioSistema.route('/usuarios_recuperar_contrasena_usuario_sistema')
def usuarios_recuperar_contrasena_usuario_sistema():
    return render_template('usuarios/cambiarContrasenaUsuarioSistema.html')

@cambiarContrasenaUsuarioSistema.route('/send_reset_email', methods=['POST'])
def send_reset_email():
    try:
        print("Entering send_reset_email function")
        data = request.get_json()
        email = data['email']

        # Generar un código de verificación aleatorio
        verification_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        verification_codes[email] = {
            'code': verification_code,
            'timestamp': datetime.now(),
            'expiry': timedelta(minutes=2)
        }
        print(f"Generated verification code: {verification_code}")

        
        time = datetime.now()
     
        # Configurar las variables para enviar el correo electrónico   
        sender_email = app.config['MAIL_USERNAME']
        password = app.config['MAIL_PASSWORD']  # Obtener la contraseña del archivo de configuración
        receiver_email = email        
        smtp_server = app.config['MAIL_SERVER']
        smtp_port = app.config['MAIL_PORT'] 
        
        # URL donde el usuario puede colocar el código de verificación
      #  verification_url = url_for('http://127.0.0.1:5001/usuarios_recuperar_contrasena_usuario_sistema', _external=True)  # Reemplaza 'ruta_para_colocar_codigo' con la ruta real en tu aplicación


        # Crear el mensaje de correo electrónico
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = f'Codigos de verificación DPI - {email}'

        # Crear el cuerpo del mensaje con todos los parámetros
        nota = 'ESTE CODIGO TIENE UNA DURACION DE 2 MINUTOS'
        body = email + '\n'
        body += '\n'
        body += '\n'
        body += f'Atencion: {nota}\n'
        body += '\n'
        body += '\n'
        body += f'Verification_code: {verification_code}\n'       
        body += '\n'
        body += '\n'
        body += f'Hora de envio: {str(time)}\n'
        
        message.attach(MIMEText(body, 'plain'))

        

        # Mostrar el mensaje completo antes de enviarlo
        print(f"Email content:\nFrom: {sender_email}\nTo: {receiver_email}\nSubject: {message['Subject']}\nBody:\n{body}")

        # Establecer una conexión con el servidor SMTP y enviar el correo electrónico      
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return 'OK'  # Devolver una respuesta exitosa al cliente

    except KeyError as e:
        print(f"KeyError encountered: {str(e)}")
        return jsonify({'error': f'Campo requerido faltante: {str(e)}'}), 400

    except smtplib.SMTPException as e:
        print(f"SMTPException encountered: {str(e)}")
        return jsonify({'error': f'Error al enviar el correo electrónico: {str(e)}'}), 500

    except Exception as e:
        print(f"Unexpected error encountered: {str(e)}")
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500



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
    try:
        data = request.get_json()
        email = data.get('correo_electronico')
        new_password = data.get('new_password')

        # Validar que se hayan proporcionado el correo electrónico y la nueva contraseña
        if not email or not new_password:
            return jsonify({'error': 'Correo electrónico y nueva contraseña son requeridos.'}), 400

        # Verificar si existe un código de verificación válido para el correo electrónico
        if email not in verification_codes:
            return jsonify({'error': 'No se encontró ningún código de verificación para este correo electrónico.'}), 400
        
        # Obtener el código de verificación y su información
        verification_info = verification_codes[email]
        verification_code = verification_info['code']
        timestamp = verification_info['timestamp']
        expiry = verification_info['expiry']

        # Verificar si el código de verificación ha expirado
        current_time = datetime.now()
        if current_time > timestamp + expiry:
            return jsonify({'error': 'El código de verificación ha expirado. Solicite uno nuevo.'}), 400

       
        # Obtener al usuario y verificar si la nueva contraseña es igual a la anterior
        usuario = db.session.query(Usuario).filter_by(correo_electronico=email).first()
        if usuario:
            if bcrypt.checkpw(new_password.encode('utf-8'), usuario.password):
                return jsonify({'error': 'La nueva contraseña no puede ser igual a la anterior.'}), 400

            # Cambiar la contraseña
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            usuario.password = hashed_password
            db.session.commit()
            db.session.close()
            flash('Contraseña cambiada exitosamente.')
            return jsonify({'message': 'Contraseña cambiada exitosamente.'})
        else:
            return jsonify({'error': 'No se encontró ningún usuario con el correo electrónico proporcionado.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500



