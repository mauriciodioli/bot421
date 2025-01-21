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
import redis


muestraPublicacionesEnHome = Blueprint('muestraPublicacionesEnHome',__name__)

# Configurar la conexión a Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@muestraPublicacionesEnHome.route('/media-muestraPublicacionesEnDpi-mostrar/<int:publicacion_id>', methods=['GET'])
def media_publicaciones_detalle_dpi(publicacion_id):
    # Obtener los detalles de la publicación desde la base de datos
    # Aquí deberías hacer una consulta para obtener las imágenes y videos
    post = obtener_publicacion_por_id(publicacion_id)  # Reemplaza con tu lógica de obtención
    if post:
        return render_template('media/publicaciones/muestraPublicacionesEnHome.html', post=post, layout='layout_muestra_imagenes_dpi')
    else:
        return jsonify({'error': 'Publicación no encontrada'}), 404
    





@muestraPublicacionesEnHome.route('/media-muestraPublicacionesEnHome-mostrar/<int:publicacion_id>/<string:layout>', methods=['GET'])
def media_publicaciones_detalle(publicacion_id, layout):
    # Obtener los detalles de la publicación desde la base de datos
    # Aquí deberías hacer una consulta para obtener las imágenes y videos
    post = obtener_publicacion_por_id(publicacion_id)  # Reemplaza con tu lógica de obtención
    if post:
        return render_template('media/publicaciones/muestraPublicacionesEnHome.html', post=post, layout=layout)
    else:
        
        return jsonify({'error': 'Publicación no encontrada'}), 404
    




def obtener_publicacion_por_id(publicacion_id):
    try:
        # Intentar obtener los datos desde Redis
        cache_key = f"publicacion:{publicacion_id}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            print("Recuperando datos desde la caché")
            return json.loads(cached_data)  # Convertir la cadena JSON a un diccionario

        publicacion = db.session.query(Publicacion).filter_by(id=publicacion_id).first()
        if publicacion:
            uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]

            imagenes_videos = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()

            imagenes = []
            videos = []

            for iv in imagenes_videos:
                if iv.imagen_id:
                    imagen = db.session.query(Image).filter_by(id=iv.imagen_id).first()
                    if imagen:
                        imagen_url = mostrar_from_gcs(imagen.filepath.replace('static/uploads/', '').replace('static\\uploads\\', ''))
                        imagenes.append({
                            'id': imagen.id,
                            'title': imagen.title,
                            'description': imagen.description,
                            'filepath': imagen_url,
                            'randomNumber': imagen.randomNumber,
                            'colorDescription': imagen.colorDescription,
                            'size': imagen.size                      
                        })

                if iv.video_id:
                    video = db.session.query(Video).filter_by(id=iv.video_id).first()
                    if video:
                        video_url = mostrar_from_gcs(video.filepath.replace('static/uploads/', '').replace('static\\uploads\\', ''))
                        videos.append({
                            'id': video.id,
                            'title': video.title,
                            'description': video.description,
                            'filepath': video_url,
                            'randomNumber': video.randomNumber,
                            'colorDescription': video.colorDescription,
                            'size': video.size
                        })

            response_data = {
                'publicacion_id': publicacion.id,
                'user_id': publicacion.user_id,
                'titulo': publicacion.titulo,
                'texto': publicacion.texto,
                'ambito': publicacion.ambito,
                'correo_electronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'color_texto': publicacion.color_texto,
                'color_titulo': publicacion.color_titulo,
                'fecha_creacion': str(publicacion.fecha_creacion),
                'estado': publicacion.estado,
                'botonCompra': publicacion.botonCompra,
                'imagenes': imagenes,
                'videos': videos
            }

            # Guardar los datos en Redis con una expiración de 1 hora (3600 segundos)
            redis_client.setex(cache_key, 3600, json.dumps(response_data))

            db.session.close()
            return response_data
        else:
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


