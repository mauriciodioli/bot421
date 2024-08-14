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
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.modelMedia.image import Image
from models.modelMedia.video import Video
from datetime import datetime
from models.modelMedia.TelegramNotifier import TelegramNotifier

publicaciones = Blueprint('publicaciones',__name__)

@publicaciones.route('/media-publiaciones-mostrar', methods = ['POST'])
def media_publiaciones_mostrar():
    try:
        # Obtener el encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]
        if Token.validar_expiracion_token(access_token=access_token):  
            app = current_app._get_current_object()                    
            decoded_token = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            # Obtener todas las publicaciones del usuario
            publicaciones_user = db.session.query(Publicacion).filter_by(user_id=user_id).all()
           
            # Armar el diccionario con todas las publicaciones, imágenes y videos
            publicaciones_data = armar_publicacion(publicaciones_user)
            # Transformar las rutas al formato almacenado en la base de datos
        # db_image_paths = [os.path.relpath(os.path.join(current_app.root_path, path), current_app.root_path).replace('/', os.sep) for path in image_paths]

           # for publicacion in publicaciones_data:
           #     for imagen in publicacion.get('imagenes', []):
           #         imagen['filepath'] = imagen['filepath'].replace('\\', '/')
           #     for video in publicacion.get('videos', []):
           #         video['filepath'] = video['filepath'].replace('\\', '/')

         
        # Filtrar solo las imágenes (puedes ajustar esto según tus necesidades)
           # imagenes_filtradas = [img for img in publicaciones_data if es_formato_imagen(publicaciones_data.filepath)]

            # Procesar y asignar los paths solo a las imágenes filtradas
           # for img in imagenes_filtradas:
           #     img.filepath = img.filepath.replace('static\\', '').replace('\\', '/')

            #          img.image_paths = [img.filepath.replace('static\\', '').replace('\\', '/') for img in imagenes if es_formato_imagen(img.filepath)]
            
           # for vid in imagenes_filtradas:
           #     vid.filepath = vid.filepath.replace('static\\', '').replace('\\', '/')
            print(publicaciones_data)
            return jsonify(publicaciones_data)


    except Exception as e:
                # Manejo genérico de excepciones, devolver un mensaje de error
                return jsonify({'error': str(e)}), 500
        



# Definir la función para armar las publicaciones con imágenes y videos
def armar_publicacion(publicaciones_user):
    publicaciones_data = []
    
    
    # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]
   
    
    

    for publicacion in publicaciones_user:
        # Obtener todas las imágenes y videos asociados a esta publicación
        imagenes_videos = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()
        
        imagenes = []
        videos = []

        for iv in imagenes_videos:
            # Obtener la información de las imágenes
            if iv.imagen_id:
                imagen = db.session.query(Image).filter_by(id=iv.imagen_id).first()
                if imagen:
                    imagenes.append({
                        'id': imagen.id,
                        'title': imagen.title,
                        'description': imagen.description,
                        'filepath': imagen.filepath,
                        'randomNumber': imagen.randomNumber,                        
                    })

            # Obtener la información de los videos
            if iv.video_id:
                video = db.session.query(Video).filter_by(id=iv.video_id).first()
                if video:
                    videos.append({
                        'id': video.id,
                        'title': video.title,
                        'description': video.description,
                        'filepath': video.filepath
                    })
        # Determinar el separador de ruta según el sistema operativo
        #path_separator = '/' if os.name != 'nt' else '\\'
        path_separator = '/'
        # Ajustar las rutas de archivos según el sistema operativo
        db.session.close()
        for imagen in imagenes:
            imagen['filepath'] = imagen['filepath'].replace('\\', path_separator)
            #imagen['filepath'] = imagen['filepath'].replace('static/', ''),
        for video in videos:
            video['filepath'] = video['filepath'].replace('\\', path_separator)
            #video['filepath'] = video['filepath'].replace('static/', '')
        # Agregar la publicación con sus imágenes y videos al diccionario
        publicaciones_data.append({
            'publicacion_id': publicacion.id,
            'user_id': publicacion.user_id,
            'titulo':publicacion.titulo,
            'texto': publicacion.texto,
            'ambito': publicacion.ambito,
            'correo_electronico': publicacion.correo_electronico,
            'descripcion': publicacion.descripcion,
            'color_texto': publicacion.color_texto,
            'color_titulo': publicacion.color_titulo,
            'fecha_creacion': publicacion.fecha_creacion,            
            'imagenes': imagenes,
            'videos': videos
        })

    return publicaciones_data












@publicaciones.route('/social_imagenes_crear_publicacion', methods=['POST'])
def social_imagenes_crear_publicacion():
    try:
          # Obtener el encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]

        # Validar y decodificar el token
        if Token.validar_expiracion_token(access_token=access_token):  # Asegúrate de que este método acepte el token directamente
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")
            
            # Obtener datos del formulario
            post_title = request.form.get('postTitle_creaPublicacion')
            post_text = request.form.get('postText_creaPublicacion')
            post_description = request.form.get('postDescription_creaPublicacion')
            post_ambito = request.form.get('postAmbito_creaPublicacion')
            post_estado = request.form.get('postLeido_creaPublicacion')
            
            # Procesar archivos multimedia
            media_files = []
            id_publicacion = guardarPublicacion(request, media_files, user_id)
           
            for key in request.files:
                file = request.files[key]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)

                    # Decide si el archivo es una imagen o un video
                    if file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                        # Llama a la función de carga de imagen
                        file_path = cargarImagen_crearPublicacion(request,file, filename, id_publicacion,userid=user_id)
                    elif file.filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}:
                        # Llama a la función de carga de video
                        file_path = cargarVideo_crearPublicacion(request,file, filename, id_publicacion,userid=user_id)

                    if file_path:
                        media_files.append(file_path)
            # Obtén otros datos del formulario
           
            post_title = request.form.get('postTitle_creaPublicacion')
            post_text = request.form.get('postText_creaPublicacion')   
            ambito = request.form.get('ambito')
            correo_electronico = request.form.get('correo_electronico')
            color_texto = request.form.get('color_texto')
            color_titulo = request.form.get('color_titulo')
            
            print("Título de la publicación:", post_title)
            print("Texto de la publicación:", post_text)        
            print("Finalizando social_imagenes_crear_publicacion")
            return jsonify({
                'message': 'Publicación creada exitosamente.',
                'media_files': media_files,
                'post_title': post_title,
                'post_text': post_text,
                'ambito': ambito,
                'correo_electronico': correo_electronico,
                'color_texto': color_texto,
                'color_titulo': color_titulo
            })
    except Exception as e:
            # Manejo genérico de excepciones, devolver un mensaje de error
            return jsonify({'error': str(e)}), 500
        


def cargarImagen_crearPublicacion(request,file, filename, id_publicacion,userid=0):    
    color_texto = request.form.get('color_texto')   
    file_path = os.path.join('static', 'uploads', filename)
    file.save(file_path)
   
    nombre_archivo = filename
    descriptionImagen = 'ambitoSocial'
    randomNumber_ = random.randint(1, 1000000)  # Generar un número aleatorio entre 1 y 1,000,000


  
    nueva_imagen = Image(
        user_id=userid,
        title=nombre_archivo,
        description=descriptionImagen,
        colorDescription=color_texto,
        filepath=file_path,
        randomNumber=randomNumber_
    )
    db.session.add(nueva_imagen)
    db.session.commit()
    cargar_id_publicacion_id_imagen(id_publicacion,nueva_imagen.id)
    return file_path


def cargarVideo_crearPublicacion(request,file, filename,id_publicacion,userid=0):   
    color_texto = request.form.get('color_texto')   
    file_path = os.path.join('static', 'uploads', filename)
    file.save(file_path)

    nombre_archivo = filename
    description_video = 'ambitoSocial'
    randomNumber_ = random.randint(1, 1000000)  # Generar un número aleatorio entre 1 y 1,000,000


    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return jsonify({'error': 'Token de acceso no proporcionado'}), 401
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({'error': 'Formato de token de acceso no válido'}), 401

    access_token = parts[1]
    app = current_app._get_current_object()
    userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']

    nuevo_video = Image(
        user_id=userid,
        title=nombre_archivo,
        description=description_video,
        colorDescription=color_texto,
        filepath=file_path,
        randomNumber=randomNumber_
    )
    db.session.add(nuevo_video)
    db.session.commit()
    cargar_id_publicacion_id_imagen(id_publicacion,nuevo_video.id)
    return file_path


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def es_formato_imagen(filepath):
    # Extensiones de archivo de imagen comunes
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # Verificar si la extensión del archivo está en la lista de extensiones de imagen
    return any(filepath.lower().endswith(ext) for ext in extensiones_imagen)




def guardarPublicacion(request, media_files, user_id):
    post_title = request.form.get('postTitle_creaPublicacion')
    post_text = request.form.get('postText_creaPublicacion')   
    ambito = request.form.get('ambito')
    correo_electronico = request.form.get('correo_electronico')
    color_texto = request.form.get('color_texto')
    color_titulo = request.form.get('color_titulo')
    estado = request.form.get('postEstado_creaPublicacion')
    
    nueva_publicacion = Publicacion(
            user_id=user_id,             
            titulo= post_title,
            texto= post_text,
            ambito= ambito,
            correo_electronico= correo_electronico,
            descripcion= post_text,
            color_texto= color_texto,
            color_titulo= color_titulo,
            fecha_creacion= datetime.now(),
            estado = estado
        )
           
    db.session.add(nueva_publicacion)
    db.session.commit()
    return nueva_publicacion.id

def cargar_id_publicacion_id_imagen(id_publicacion,nueva_imagen_id):
    nuevo_ids= Public_imagen_video(
        publicacion_id=id_publicacion,
        imagen_id=nueva_imagen_id,
        video_id=0,
        fecha_creacion=datetime.now()
    )
    db.session.add(nuevo_ids)
    db.session.commit()
    db.session.close()
    return True

def show_publicacion_galeriaimagenes(request, media_files,id_publicacion):
     return render_template('publicaciones/publicacionesGaleriaImagenes.html', media_files=media_files,id_publicacion=id_publicacion)
     

