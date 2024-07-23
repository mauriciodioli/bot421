# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from flask import Flask,Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from datetime import datetime
import smtplib
import os

# Configurar la aplicación Flask
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')  # Necesario para usar mensajes flash
# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Usar el puerto adecuado para TLS
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Obtener usuario de variables de entorno
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Obtener contraseña de variables de entorno
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False



media_e_mail = Blueprint('media_e_mail',__name__)

@media_e_mail.route('/save-ip', methods=['POST'])
def save_ip():
    if request.method == 'POST':
        try:
            access_token = request.json.get('accesstoken')
            correo_electronico = request.json.get('correo_electronico')
            usuario = request.json.get('usuario1')
            ip = request.json.get('ip') 
            time = datetime.now()
            print('usario',usuario,'correo_electronico:', correo_electronico, 'ip:', ip, 'time:', time)

            # Configurar las variables para enviar el correo electrónico
            sender_email = 'mauriciodioli@gmail.com'
            receiver_email = app.config['MAIL_USERNAME'] 
            password = app.config['MAIL_PASSWORD']
            smtp_server = app.config['MAIL_SERVER']
            smtp_port = app.config['MAIL_PORT']  # Usar el puerto adecuado para TLS

        

            # Crear el mensaje de correo electrónico
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = f'IP Address - {correo_electronico}'

            # Crear el cuerpo del mensaje con todos los parámetros
           
            body = f'Correo Electrónico: {correo_electronico}\n'
            body += f'Usuario: {usuario}\n'
            body += f'IP Address: {ip}\n'
            body += f'Time: {time}\n'
            
            message.attach(MIMEText(body, 'plain'))

            # Establecer una conexión con el servidor SMTP y enviar el correo electrónico
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())

            return 'OK'  # Devolver una respuesta exitosa al cliente
        except smtplib.SMTPException as e:
            # Manejar errores relacionados con el envío del correo electrónico
            print('Error al enviar el correo electrónico:', str(e))
            return 'Error al enviar el correo electrónico', 500  # Devolver una respuesta de error al cliente
        except Exception as e:
            # Manejar otros errores no esperados
            print('Error inesperado:', str(e))
            return 'Error inesperado', 500  # Devolver una respuesta de error al cliente


@media_e_mail.route('/enviar-email-de-contacto', methods=['POST'])
def enviar_email_de_contacto():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            mensaje = request.form.get('mensaje')
            ip = request.remote_addr
            time = datetime.now()

            #print('Nombre:', nombre, 'Correo Electrónico:', email, 'Mensaje:', mensaje, 'IP:', ip, 'Hora:', time)
            
            # Llamar a la función para enviar el correo electrónico
            resultado_envio = enviar_correo(nombre, email, mensaje, ip, time)
            
            if resultado_envio == 'OK':
                flash('Mensaje enviado correctamente.')
            else:
                flash(f'Error: {resultado_envio}', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

        return render_template('comunicacion/contacto.html')
def enviar_correo(nombre, email, mensaje,ip,time):
    try:
        # Configurar las variables para enviar el correo electrónico
        sender_email = email
        receiver_email = app.config['MAIL_USERNAME'] 
        password = app.config['MAIL_PASSWORD']
        smtp_server = app.config['MAIL_SERVER']
        smtp_port = app.config['MAIL_PORT']  # Usar el puerto adecuado para TLS


        # Crear el mensaje de correo electrónico
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = f'Desde - {nombre}'

        # Crear el cuerpo del mensaje con todos los parámetros
        body = f'Correo Electrónico: {email}\n'
        body += f'Usuario: {nombre}\n'
        body += f'Ip: {ip}\n'
        body += f'Time: {time}\n'
        body += f'Mensaje: {mensaje}\n'

        message.attach(MIMEText(body, 'plain'))

        # Establecer una conexión con el servidor SMTP y enviar el correo electrónico
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return 'OK'  # Devolver una respuesta exitosa al cliente
    except smtplib.SMTPException as e:
        # Manejar errores relacionados con el envío del correo electrónico
        print('Error al enviar el correo electrónico:', str(e))
        return 'Error al enviar el correo electrónico'
    except Exception as e:
        # Manejar otros errores no esperados
        print('Error inesperado:', str(e))
        return 'Error inesperado'



def enviar_correo_newSletter( email, mensaje):
    try:
        # Configurar las variables para enviar el correo electrónico
        sender_email = email
        receiver_email = app.config['MAIL_USERNAME'] 
        password = app.config['MAIL_PASSWORD']
        smtp_server = app.config['MAIL_SERVER']
        smtp_port = app.config['MAIL_PORT']  # Usar el puerto adecuado para TLS
        subjet = 'newsLetter DPI bot'

        # Crear el mensaje de correo electrónico
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = f'Desde - {subjet}'

       

        message.attach(MIMEText(mensaje, 'plain'))

        # Establecer una conexión con el servidor SMTP y enviar el correo electrónico
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return 'OK'  # Devolver una respuesta exitosa al cliente
    except smtplib.SMTPException as e:
        # Manejar errores relacionados con el envío del correo electrónico
        print('Error al enviar el correo electrónico:', str(e))
        return 'Error al enviar el correo electrónico'
    except Exception as e:
        # Manejar otros errores no esperados
        print('Error inesperado:', str(e))
        return 'Error inesperado'
    
    
