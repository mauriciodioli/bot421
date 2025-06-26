# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
import asyncio
from werkzeug.utils import secure_filename
import os
from models.usuario import Usuario
from models.brokers import Broker
from models.modelMedia.TelegramNotifier import TelegramNotifier

cargarPdf = Blueprint('cargarPdf',__name__)


@cargarPdf.route('/media_cargarPdf/', methods=['POST'])
def media_cargarPdf():
    try:
        # Obtener encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar el formato del token
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token no válido'}), 401

        access_token = parts[1]
        
        # Verificar la expiración del token
        if not Token.validar_expiracion_token(access_token=access_token):  
            return jsonify({'error': 'Token expirado'}), 401

        # Decodificar el token para obtener el usuario
        app = current_app._get_current_object()                    
        decoded_token = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get("sub")

        # Verificar que se haya enviado el archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró ningún archivo en la solicitud"}), 400
        
        file = request.files['file']
        if not file:
            return jsonify({"error": "No se seleccionó un archivo"}), 400
        
        # Validación del archivo (solo PDF)
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Solo se permite subir archivos PDF"}), 400

        # Usar secure_filename para limpiar el nombre del archivo
        file_name = secure_filename(file.filename)
        safe_file_name = os.path.basename(file_name)
        file_path = os.path.join('static', 'uploads', f"{safe_file_name}")  # Ruta temporal para archivo
       
        # Asegurarse de que el directorio 'static/uploads' exista
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))  # Crear el directorio si no existe
        
        # Guardar el archivo en el servidor
        file.save(file_path)
        
       # Retornar la URL del archivo subido
        pdf_url = url_for("static", filename=f"uploads/{safe_file_name}", _external=True)

        return jsonify({"pdf_url": pdf_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cargarPdf.route('/media_visualizarPdf/', methods=['GET'])
def media_visualizarPdf():
    # Obtener los archivos PDF de la carpeta 'static/uploads'
    upload_folder = os.path.join('static', 'uploads')
    pdf_files = [f for f in os.listdir(upload_folder) if f.endswith('.pdf')]
    
    # Crear una lista de rutas relativas para los archivos PDF
    pdf_files_urls = [os.path.join('uploads', f) for f in pdf_files]
    
    return render_template('media/documentos/mostrarPdf.html', pdf_files=pdf_files_urls, layout='layout_muestra_imagenes_dpi')
