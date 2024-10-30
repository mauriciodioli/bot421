# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
import random  # Importar el módulo random
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
import asyncio
import os
from models.usuario import Usuario
from models.brokers import Broker
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.estado_publi_usu import Estado_publi_usu
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.modelMedia.image import Image
from models.modelMedia.video import Video
from datetime import datetime
from models.modelMedia.TelegramNotifier import TelegramNotifier
from social.buckets.bucketGoog import mostrar_from_gcs


muestraPublicacionesEnHome = Blueprint('muestraPublicacionesEnHome',__name__)

@muestraPublicacionesEnHome.route('/media-muestraPublicacionesEnHome-mostrar/<int:publicacion_id>', methods=['GET'])
def media_publicaciones_detalle(publicacion_id):
    # Obtener los detalles de la publicación desde la base de datos
    # Aquí deberías hacer una consulta para obtener las imágenes y videos
    post = obtener_publicacion_por_id(publicacion_id)  # Reemplaza con tu lógica de obtención
    if post:
        return render_template('media/publicaciones/muestraPublicacionesEnHome.html', post=post, layout='layout')
    else:
        return jsonify({'error': 'Publicación no encontrada'}), 404
    
def obtener_publicacion_por_id(publicacion_id):
    try:
        publicacion = db.session.query(Publicacion).filter_by(id=publicacion_id).first()
        if publicacion:
            publicaciones_data = []
            
            # Obtener la ruta completa de la carpeta 'static/uploads'
            uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

            # Obtener todas las imágenes en la carpeta 'static/uploads'
            image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            # Crear las rutas completas de las imágenes sin codificación de caracteres
            image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]

            # Obtener todas las imágenes y videos asociados a esta publicación
            imagenes_videos = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()
            
            imagenes = []
            videos = []

            for iv in imagenes_videos:
                # Obtener la información de las imágenes
                if iv.imagen_id:
                    imagen = db.session.query(Image).filter_by(id=iv.imagen_id).first()
                    if imagen:
                        # Quitar 'static/' del inicio del filepath si existe
                        filepath = imagen.filepath
                        imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')   
                        imagen_url = mostrar_from_gcs(imagen_url)                      
                        if filepath.startswith('static'):
                            filepath = filepath[len('static/'):]
                        imagenes.append({
                            'id': imagen.id,
                            'title': imagen.title,
                            'description': imagen.description,
                            'filepath': imagen_url,
                            'randomNumber': imagen.randomNumber,
                            'colorDescription': imagen.colorDescription,
                            'size': imagen.size                      
                        })

                # Obtener la información de los videos
                if iv.video_id:
                    video = db.session.query(Video).filter_by(id=iv.video_id).first()
                    if video:
                        filepath = video.filepath
                        video_url = filepath.replace('static\\uploads\\', '').replace('static\\uploads\\', '')     # Asegúrate de que la barra final se mantenga si es necesario
                        video_url = mostrar_from_gcs(video_url)
                        if filepath.startswith('static/'):
                            filepath = filepath[len('static/'):]
                        videos.append({
                            'id': video.id,
                            'title': video.title,
                            'description': video.description,
                            'filepath': video_url,
                            'randomNumber': video.randomNumber,
                            'colorDescription': video.colorDescription,
                            'size': video.size
                        })
            # Ajustar las rutas de archivos según el sistema operativo
            path_separator = '/'
            for imagen in imagenes:
                imagen['filepath'] = imagen['filepath'].replace('\\', path_separator)
            for video in videos:
                video['filepath'] = video['filepath'].replace('\\', path_separator)

            # Agregar la publicación con sus imágenes y videos al diccionario
            db.session.close()
            return {
                'publicacion_id': publicacion.id,
                'user_id': publicacion.user_id,
                'titulo': publicacion.titulo,
                'texto': publicacion.texto,
                'ambito': publicacion.ambito,
                'correo_electronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'color_texto': publicacion.color_texto,
                'color_titulo': publicacion.color_titulo,
                'fecha_creacion': publicacion.fecha_creacion,
                'estado': publicacion.estado,           
                'imagenes': imagenes,
                'videos': videos
            }
            
        else:
            return None
    except Exception as e:
        print(str(e))
        return None

