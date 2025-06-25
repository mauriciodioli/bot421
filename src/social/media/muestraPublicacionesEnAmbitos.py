# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
import re
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
import base64
from models.usuario import Usuario
from models.brokers import Broker
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.estado_publi_usu import Estado_publi_usu
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.modelMedia.image import Image
from models.modelMedia.video import Video
from datetime import datetime
from models.modelMedia.TelegramNotifier import TelegramNotifier
from social.buckets.bucketGoog import mostrar_from_gcs

muestraPublicacionesEnAmbitos = Blueprint('muestraPublicacionesEnAmbitos',__name__)



@muestraPublicacionesEnAmbitos.route('/media-muestraPublicacionesEnAmbitos/', methods=['GET'])
def media_muestraPublicacionesEnAmbitos():
    # Acceder a los parámetros de la URL
    publicacion_id = request.args.get('publicacion_id')
    user_id = request.args.get('user_id')
    ambito = request.args.get('ambito')
    layoutIn = request.args.get('layout')
    categoria = request.args.get('categoria')

     # Aquí manejas los datos recibidos y haces la lógica correspondiente
    # Podrías devolver una página renderizada con los datos correspondientes.
    # Ejemplo de cómo podrías usar los datos:
    return render_template('media/publicaciones/publicacionesEnAmbitos.html', publicacion_id=publicacion_id, user_id=user_id, ambito=ambito, layout=layoutIn, categoria=categoria)


@muestraPublicacionesEnAmbitos.route('/media-muestraPublicacionesEnAmbitos-mostrar/', methods=['POST'])
def mostrar_publicaciones_en_ambitos():
    # Acceder a los datos enviados en la solicitud POST
    data = request.json  # Si los datos se enviaron como JSON
    publicacion_id = data.get('publicacion_id')
    user_id = data.get('user_id')
    ambito = data.get('ambito')
    layout = data.get('layout')
    idioma = data.get('lenguaje')
    categoria = data.get('categoria')
 
    # Ahora puedes usar publicacion_id, user_id, y ambito en tu lógica
    post = armar_publicacion_bucket_para_dpi(user_id,ambito,layout,idioma,categoria)  # Reemplaza con tu lógica de obtención
    
    if post:
       
        for p in post:
            p['estrellas_html'] = generar_estrellas_html(p.get('rating', 4.5), p.get('reviews', 1))
    
        return jsonify(post)

      
    else:
        return jsonify({'error': 'Publicación no encontrada'}), 404
def generar_estrellas_html(rating, reviews):
    estrellas_html = ''
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    estrellas_html += '★' * full_stars
    estrellas_html += '½' * half_star
    estrellas_html += '☆' * empty_stars

    return f'{estrellas_html} <span class="text-muted" style="font-size: 0.9rem;">({reviews})</span>'

def armar_publicacion_bucket_para_dpi(user_id, ambito,layout,idioma, categoria):
      
        # Obtener todas las publicaciones que coincidan con user_id y ambito
        if not isinstance(user_id, int):
            user_id = int(user_id)


        publicaciones = db.session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito, idioma=idioma, categoria_id=int(categoria)).all()
        categoria = db.session.query(AmbitoCategoria).filter_by(id=int(categoria)).first()
        resultados = []

        for publicacion in publicaciones:
            # Obtener solo la primera imagen asociada a la publicación
            imagen_video = (
                db.session.query(Public_imagen_video)
                .filter_by(publicacion_id=publicacion.id)
                .order_by(Public_imagen_video.id.asc())  # Ordena para obtener el primero
                .first()
            )

            # Inicializar listas para imágenes y videos
            imagenes = []
            videos = []

            if imagen_video:
                # Si tiene una imagen asociada
                if imagen_video.imagen_id:
                    imagen = db.session.query(Image).filter_by(id=imagen_video.imagen_id).first()
                    if imagen:
                        # Ajustar la ruta del archivo
                        filepath = imagen.filepath
                        imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')   
                        if publicacion.imagen:
                            file_path = publicacion.imagen
                            file_data = None
                        else:   
                            file_data,file_path = mostrar_from_gcs(imagen_url)  # Asegúrate de definir esta función
                    
                        if file_data:
                            # Convertir la imagen a base64 solo si hemos obtenido datos binarios
                            imagen_base64 = base64.b64encode(file_data).decode('utf-8')
                        else:
                            imagen_base64 = None                   

                        imagenes.append({
                            'id': imagen.id,
                            'title': imagen.title,
                            'description': imagen.description,
                            'imagen': imagen_base64,
                            'filepath': file_path,
                            'randomNumber': imagen.randomNumber,
                            'colorDescription': imagen.colorDescription,
                            'size': imagen.size                      
                        })

                # Si tiene un video asociado
                if imagen_video.video_id:
                    video = db.session.query(Video).filter_by(id=imagen_video.video_id).first()
                    if video:
                        # Ajustar la ruta del archivo
                        filepath = video.filepath
                        video_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')  
                        file_data, file_path  = mostrar_from_gcs(video_url)
                        
                        if file_data:
                            # Convertir la imagen a base64 solo si hemos obtenido datos binarios
                            video_base64 = base64.b64encode(file_data).decode('utf-8')
                        else:
                            video_base64 = None

                        videos.append({
                            'id': video.id,
                            'title': video.title,
                            'description': video.description,
                            'filepath': file_path,  # Usar la URL de GCS o el path procesado
                            'video': video_base64 if file_data else None,  # La imagen en base64
                            'mimetype': video.mimetype,  # Asignar correctamente el tipo MIME
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
 # Calcular descuento aleatorio si hay precio
            precio_actual, descripcion = extraer_precio_y_descripcion(publicacion.texto)
            if precio_actual:
                if random.random() < 0.5:  # 50% de chance de aplicar descuento
                    descuento_porcentaje = random.choice([10, 15, 20, 25, 30, 35, 40])
                    descuento = f"{descuento_porcentaje}% OFF"
                    precio_original = round(precio_actual / (1 - descuento_porcentaje / 100))
                else:
                    descuento = None
                    precio_original = None
            else:
                descuento = None
                precio_original = None
            
            texto = limpiar_texto(publicacion.texto)
            # Agregar la publicación con su imagen y video a la lista de resultados
            resultados.append({
                'publicacion_id': publicacion.id,
                'user_id': publicacion.user_id,
                'titulo': publicacion.titulo,
                'texto': publicacion.texto,
                'ambito': publicacion.ambito,
                'categoria_id': publicacion.categoria_id,
                'categoriaNombre': categoria.valor,
                'correo_electronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'color_texto': publicacion.color_texto,
                'color_titulo': publicacion.color_titulo,
                'fecha_creacion': publicacion.fecha_creacion,
                'estado': publicacion.estado,           
                'imagenes': imagenes,
                'videos': videos,
                'botonCompra': publicacion.botonCompra,
                'rating': round(random.uniform(3.0, 5.0), 1),
                'reviews': random.randint(1, 150),
                'descuento': descuento,
                'precio': precio_actual,
                'precio_original': precio_original,
                'layout':layout
            })

       
        return resultados





def extraer_precio_y_descripcion(texto):
    match = re.match(r"^\$ ?(\d+)(.*)", texto)
    if match:
        precio_actual = int(match.group(1))
        descripcion = match.group(2).strip()
        return precio_actual, descripcion
    else:
        return None, texto


def limpiar_texto(texto):
    # Elimina precios, números y links al comienzo, antes del título
    # Busca el primer bloque de texto que no sea número, precio o link
    texto = texto.strip()

    # Opción 1: cortar directamente desde donde empieza una letra mayúscula seguida de letras (ej: "Mochila")
    match = re.search(r'\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+.*?)$', texto)
    if match:
        return match.group(1).strip()
    
    return texto  # Si no encuentra coincidencia, lo devuelve igual



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
                        imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')   
                        imagen_url = mostrar_from_gcs(imagen_url)                      
                      
                        if filepath.startswith('static'):
                            #filepath = filepath[len('static/'):]
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
                        # Ajustar la ruta del archivo
                        filepath = video.filepath
                        video_url = filepath.replace('static\\uploads\\', '').replace('static\\uploads\\', '')     # Asegúrate de que la barra final se mantenga si es necesario
                        video_url = mostrar_from_gcs(video_url)
                       # if filepath.startswith('static/'):
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








