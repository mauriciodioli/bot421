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

muestraPublicacionesEnAmbitos = Blueprint('muestraPublicacionesEnAmbitos',__name__)



@muestraPublicacionesEnAmbitos.route('/media-muestraPublicacionesEnAmbitos', methods=['GET'])
def media_muestraPublicacionesEnAmbitos():
    # Acceder a los parámetros de la URL
    publicacion_id = request.args.get('publicacion_id')
    user_id = request.args.get('user_id')
    ambito = request.args.get('ambito')

     # Aquí manejas los datos recibidos y haces la lógica correspondiente
    # Podrías devolver una página renderizada con los datos correspondientes.
    # Ejemplo de cómo podrías usar los datos:
    return render_template('media/publicaciones/publicacionesEnAmbitos.html', publicacion_id=publicacion_id, user_id=user_id, ambito=ambito, layout='layout')


@muestraPublicacionesEnAmbitos.route('/media-muestraPublicacionesEnAmbitos-mostrar', methods=['POST'])
def mostrar_publicaciones_en_ambitos():
    # Acceder a los datos enviados en la solicitud POST
    data = request.json  # Si los datos se enviaron como JSON
    publicacion_id = data.get('publicacion_id')
    user_id = data.get('user_id')
    ambito = data.get('ambito')
    
    # Ahora puedes usar publicacion_id, user_id, y ambito en tu lógica
    post = obtener_publicaciones_por_usuario_y_ambito(user_id,ambito)  # Reemplaza con tu lógica de obtención
    
    if post:
        # Aquí puedes usar los parámetros adicionales si es necesario
       return jsonify(post)

    else:
        return jsonify({'error': 'Publicación no encontrada'}), 404
def obtener_publicaciones_por_usuario_y_ambito(user_id, ambito):
    try:
        # Obtener todas las publicaciones que coincidan con user_id y ambito
        publicaciones = db.session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito).all()

        # Lista para almacenar todas las publicaciones con imágenes y videos
        resultados = []

        for publicacion in publicaciones:
            # Obtener las imágenes y videos asociados a esta publicación
            imagenes_videos = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()

            imagenes = []
            videos = []

            for iv in imagenes_videos:
                # Obtener la información de las imágenes
                if iv.imagen_id:
                    imagen = db.session.query(Image).filter_by(id=iv.imagen_id).first()
                    if imagen:
                        # Ajustar la ruta del archivo
                        filepath = imagen.filepath
                        if filepath.startswith('static'):
                            #filepath = filepath[len('static/'):]
                         imagenes.append({
                            'id': imagen.id,
                            'title': imagen.title,
                            'description': imagen.description,
                            'filepath': filepath,
                            'randomNumber': imagen.randomNumber,
                            'colorDescription': imagen.colorDescription,
                            'size': imagen.size                      
                        })

                # Obtener la información de los videos
                if iv.video_id:
                    video = db.session.query(Video).filter_by(id=iv.video_id).first()
                    if video:
                        # Ajustar la ruta del archivo
                        filepath = video.filepath
                       # if filepath.startswith('static/'):
                        filepath = filepath[len('static/'):]
                        videos.append({
                            'id': video.id,
                            'title': video.title,
                            'description': video.description,
                            'filepath': filepath,
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

            # Agregar la publicación con sus imágenes y videos a la lista de resultados
            resultados.append({
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
            })

        db.session.close()
        return resultados

    except Exception as e:
        print(str(e))
        return None


