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
from social.buckets.bucketGoog import upload_to_gcs
from social.buckets.bucketGoog import delete_from_gcs
from social.buckets.bucketGoog import mostrar_from_gcs

from datetime import datetime
from models.modelMedia.TelegramNotifier import TelegramNotifier
from sqlalchemy import func
from sqlalchemy.orm.exc import StaleDataError



#import boto3
#from botocore.exceptions import NoCredentialsError


publicaciones = Blueprint('publicaciones',__name__)



# Configura el cliente de S3
#s3 = boto3.client('s3', aws_access_key_id='TU_ACCESS_KEY', aws_secret_access_key='TU_SECRET_KEY', region_name='tu-region')

BUCKET_NAME = 'nombre-de-tu-bucket'


@publicaciones.route('/media-publicaciones-mostrar', methods=['POST'])
def media_publicaciones_mostrar():
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
            publicaciones_data = armar_publicacion_bucket(publicaciones_user)
            db.session.close()
            #print(publicaciones_data)
            return jsonify(publicaciones_data)

    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500

    # Respuesta por defecto en caso de que algo falle sin lanzar una excepción
    return jsonify({'error': 'No se pudo procesar la solicitud'}), 500

@publicaciones.route('/media-publicaciones-mostrar-home', methods=['POST'])
def media_publicaciones_mostrar_home():
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

            # Inicializar la lista de publicaciones
            publicaciones = []

           # Obtener todas las publicaciones del usuario
            publicacion_estados = db.session.query(Estado_publi_usu).filter_by(user_id=user_id).all()

            if publicacion_estados:
                # Iterar sobre cada estado de publicación
                for estado_publicacion in publicacion_estados:
                    # Comparar la fecha de hoy con la fecha de eliminación
                    fecha_eliminado = estado_publicacion.fecha_eliminado
                    if fecha_eliminado:
                        dias_diferencia = (datetime.today().date() - fecha_eliminado).days
                        if dias_diferencia > 30:
                            publicacion = db.session.query(Publicacion).filter_by(id=estado_publicacion.publicacion_id, user_id=user_id).first()
                            if publicacion:
                                # Agrega la publicación a la lista de publicaciones
                                publicaciones.append(publicacion)
                    
                    # Si el estado no es "eliminado", obtén la publicación correspondiente
                    if estado_publicacion.estado != 'eliminado':
                        publicacion = db.session.query(Publicacion).filter_by(id=estado_publicacion.publicacion_id, user_id=user_id).first()
                        if publicacion:
                            # Agrega la publicación a la lista de publicaciones
                            publicaciones.append(publicacion)

            else:
                # Si no hay estados publicaciones, obtén todas las publicaciones del usuario
                publicaciones = db.session.query(Publicacion).filter_by(estado='activo').all()
            # Armar el diccionario con todas las publicaciones, imágenes y videos
            publicaciones_data = armar_publicacion_bucket(publicaciones)
            db.session.close()
            return jsonify(publicaciones_data)

    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500

    # Respuesta por defecto en caso de que algo falle sin lanzar una excepción
    return jsonify({'error': 'No se pudo procesar la solicitud'}), 500

# Definir la función para armar las publicaciones con imágenes y videos



import logging

def armar_publicacion_bucket(publicaciones):
    publicaciones_data = []

    for publicacion in publicaciones:
        # Obtener todas las imágenes y videos asociados a esta publicación
        imagenes_videos = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()

        imagenes = []
        videos = []

        for iv in imagenes_videos:
            # Obtener la información de las imágenes
            if iv.imagen_id:
                try:
                    imagen = db.session.query(Image).filter_by(id=iv.imagen_id).first()
                    
                    if imagen:
                        # Generar la URL pública desde GCS
                        filepath = imagen.filepath
                        imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')   
                        imagen_url = mostrar_from_gcs(imagen_url)
                        if imagen_url:                         
                            imagenes.append({
                                'id': imagen.id,
                                'title': imagen.title,
                                'description': imagen.description,
                                'filepath': imagen_url,  # Usar la URL de GCS
                                'randomNumber': imagen.randomNumber,
                                'size': imagen.size
                            })
                except Exception as e:
                    logging.error(f"Error al obtener información de la imagen {iv.imagen_id}: {e}")

            # Obtener la información de los videos
            if iv.video_id:
                try:
                    video = db.session.query(Video).filter_by(id=iv.video_id).first()
                    if video:
                        filepath = video.filepath
                        video_url = filepath.replace('static\\uploads\\', '').replace('static\\uploads\\', '')     # Asegúrate de que la barra final se mantenga si es necesario
                        video_url = mostrar_from_gcs(video_url)
                        if video_url:
                            videos.append({
                                'id': video.id,
                                'title': video.title,
                                'description': video.description,
                                'filepath': video_url,
                                'size': video.size
                            })
                except Exception as e:
                    logging.error(f"Error al obtener información del video {iv.video_id}: {e}")

        # Agregar la publicación con sus imágenes y videos al diccionario
        publicaciones_data.append({
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

    return publicaciones_data









def armar_publicacion(publicaciones):
    publicaciones_data = []
    
    # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]

    for publicacion in publicaciones:
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
                        'size': imagen.size                      
                    })

            # Obtener la información de los videos
            if iv.video_id:
                video = db.session.query(Video).filter_by(id=iv.video_id).first()
                if video:
                    videos.append({
                        'id': video.id,
                        'title': video.title,
                        'description': video.description,
                        'filepath': video.filepath,
                        'size': video.size
                    })

        # Ajustar las rutas de archivos según el sistema operativo
        path_separator = '/'
        for imagen in imagenes:
            imagen['filepath'] = imagen['filepath'].replace('\\', path_separator)
        
        for video in videos:
            video['filepath'] = video['filepath'].replace('\\', path_separator)

        # Agregar la publicación con sus imágenes y videos al diccionario
        publicaciones_data.append({
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

    return publicaciones_data

@publicaciones.route('/media-publicaciones-cambiar-estado', methods=['POST'])
def media_publicaciones_cambiar_estado():
    data = request.form
    publicacion_id = data.get('id')
    nuevo_estado = data.get('nuevoEstado')
    
    # Validar los datos
    if not publicacion_id or not nuevo_estado:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    # Buscar la publicación en la base de datos
    publicacion = db.session.query(Publicacion).filter_by(id=publicacion_id).first()    
    if not publicacion:
        return jsonify({'error': 'Publicación no encontrada'}), 404
    
    # Refrescar para asegurar que la instancia esté actualizada
    db.session.refresh(publicacion)
    
    # Actualizar el estado de la publicación
    publicacion.estado = nuevo_estado
    try:
        db.session.commit()
    except sqlalchemy.orm.exc.StaleDataError:
        db.session.rollback()  # Revertir en caso de error
        return jsonify({'error': 'No se pudo actualizar el estado, verifique si los datos cambiaron'}), 409
    finally:
        db.session.close()
    
    return jsonify({'success': True, 'nuevoEstado': nuevo_estado}), 200







@publicaciones.route('/social_imagenes_crear_publicacion', methods=['POST'])
def social_imagenes_crear_publicacion():
    try:
          # Obtener el encabezado Authorization
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
            app = current_app._get_current_object() 
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")
            
            # Obtener datos del formulario
            post_title = request.form.get('postTitle_creaPublicacion')
            post_text = request.form.get('postText_creaPublicacion')
            post_description = request.form.get('postDescription_creaPublicacion')
            post_ambito = request.form.get('postAmbito_creaPublicacion')
            post_estado = request.form.get('postEstado_creaPublicacion')        
            correo_electronico = request.form.get('correo_electronico')
            color_texto = request.form.get('color_texto')
            color_titulo = request.form.get('color_titulo')
            
            print("Título de la publicación:", post_title)
            print("Texto de la publicación:", post_text)        
            print("Finalizando social_imagenes_crear_publicacion")
            id_publicacion = guardarPublicacion(request, user_id)
            # Procesar archivos multimedia
       # Inicializa una lista para almacenar los datos de los archivos
            media_files = []
           
            for key in request.files:
                file = request.files[key]

                # Obtén el índice del archivo del formulario
                index = request.form.get(f'mediaFileIndex_{key.split("_")[-1]}')

                # Verifica si el índice es None o 'None'
                if index is None or index == 'None':
                    continue  # Salta el archivo si el índice es None

                # Verifica si el archivo tiene un nombre
                if file.filename == '':
                    continue

                # Asegúrate de usar un nombre de archivo seguro
                filename = secure_filename(file.filename)

                # Decide si el archivo es una imagen o un video
                file_ext = filename.rsplit('.', 1)[-1].lower()
                if file_ext in {'png', 'jpg', 'jpeg', 'gif'}:
                    # Llama a la función de carga de imagen
                    file_path = cargarImagen_crearPublicacion(app,request, file, filename, id_publicacion, userid=user_id, index=index, size=request.form.get(f'mediaFileSize_{index}'))
                    app.logger.info(f'Se cargó una imagen: {filename}, índice: {index}')
                elif file_ext in {'mp4', 'avi', 'mov'}:
                    # Llama a la función de carga de video
                    file_path = cargarVideo_crearPublicacion(request, file, filename, id_publicacion, userid=user_id, index=index, size=request.form.get(f'mediaFileSize_{index}'))

                if file_path:
                    # Crea el diccionario del archivo solo si la carga fue exitosa
                    file_data = {
                        'filename': filename,
                        'content_type': file.content_type,
                        'size': request.form.get(f'mediaFileSize_{index}'),
                        'last_modified': request.form.get(f'mediaFileLastModified_{index}'),
                        'type': request.form.get(f'mediaFileType_{index}'),
                        'name': request.form.get(f'mediaFileName_{index}'),
                        'webkit_relative_path': request.form.get(f'mediaFileWebkitRelativePath_{index}'),
                        'index': index,
                        'filepath': file_path  # Agrega la ruta del archivo cargado
                    }
                    media_files.append(file_data)

            # Crear un diccionario para la publicación
            post_data = {
                'publicacion_id': 1,  # Aquí deberías asignar un ID real de la publicación
                'imagenes': [{'filepath': data['filepath']} for data in media_files if data['filepath'].endswith(('jpg', 'jpeg', 'png', 'gif'))],  # Filtra solo imágenes
                'videos': [{'filepath': data['filepath']} for data in media_files if data['filepath'].endswith(('mp4', 'mov', 'avi'))],  # Filtra solo videos
                'titulo': post_title,
                'texto': post_text,
                'descripcion': post_description,
                'ambito': post_ambito,
                'estado': post_estado,
                'correo_electronico': correo_electronico,
                'fecha_creacion': '2024-08-21',  # Aquí deberías usar la fecha de creación real
                'color_texto': color_texto,
                'color_titulo': color_titulo
            }

            # Devuelve los datos de la publicación dentro de un array
            return jsonify([post_data]), 200
    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500
        

def cargarImagen_crearPublicacion(app, request, file, filename, id_publicacion, userid=0, index=None, size=0):   
    color_texto = request.form.get('color_texto')   
    titulo_publicacion = request.form.get('postTitle_creaPublicacion')
    size = size  # Obtener tamaño del archivo usando el índice  
 
     # Construir la ruta del archivo de manera multiplataforma
    file_path = os.path.join('static', 'uploads', filename)
    app.logger.info(f'Se cargó direccion imagen: {filename}, path: {file_path}')
    # Asegurarse de que funcione tanto en Windows como en Linux
  
    #file_path = file_path.replace('\\', '/')
    file.save(file_path)    
     # Subir el archivo a GCS
    try:
        absolute_file_path = os.path.abspath(file_path)  # Obtener la ruta absoluta 
        upload_to_gcs(absolute_file_path, filename)  # `file_path` es el path local, `filename` es el nombre en GCS
        eliminar_desde_archivo(filename, None)
    except Exception as e:
        print(f"No se pudo subir el archivo {filename} a GCS. Error: {e}")
    else:
        print(f"Archivo {filename} subido a GCS con éxito.")
    
    nombre_archivo = filename
    descriptionImagen = titulo_publicacion
    randomNumber_ = random.randint(1, 1000000)  # Generar un número aleatorio entre 1 y 1,000,000
  # Sube la imagen a S3
    #file_path_s3 = upload_to_s3(file, BUCKET_NAME, f"imagenes/{filename}")

    #if file_path_s3:
# Verificar si la imagen ya existe
    imagen_existente = db.session.query(Image).filter_by(filepath=file_path).first()

    if imagen_existente:
        # Si la imagen ya existe, solo guarda la relación en publicacion_media
        cargar_id_publicacion_id_imagen_video(id_publicacion,imagen_existente.id,0,'imagen',size=size)
        return file_path
    else:
  
        nueva_imagen = Image(
            user_id=userid,
            title=nombre_archivo,
            description=descriptionImagen,
            colorDescription=color_texto,
            filepath=file_path,
            randomNumber=randomNumber_,
            size=float(size)
        )
        db.session.add(nueva_imagen)
        db.session.commit()
        cargar_id_publicacion_id_imagen_video(id_publicacion,nueva_imagen.id,0,'imagen',size=size)
        db.session.close()
        return file_path


def cargarVideo_crearPublicacion(request,file, filename,id_publicacion,userid=0, index=None, size=0):   
    print(f"Entering cargarVideo_crearPublicacion with filename: {filename}, userid: {userid}, index: {index}, size: {size}")
    color_texto = request.form.get('color_texto')   
    file_path = os.path.join('static', 'uploads', filename)
    
    #file_path = file_path.replace('\\', '/')
   
    size = size  # Obtener tamaño del archivo usando el índice
    file.save(file_path)
    # Subir el archivo a GCS
    try:
        absolute_file_path = os.path.abspath(file_path)  # Obtener la ruta absoluta 
        upload_to_gcs(absolute_file_path, filename)  # `file_path` es el path local, `filename` es el nombre en GCS
        eliminar_desde_archivo(filename, None)
    except Exception as e:
        print(f"No se pudo subir el archivo {filename} a GCS. Error: {e}")
    else:
        print(f"Archivo {filename} subido a GCS con éxito.")
    nombre_archivo = filename
    description_video = 'ambitoSocial'
    randomNumber_ = random.randint(1, 1000000)  # Generar un número aleatorio entre 1 y 1,000,000

    print(f"Authorization header: {request.headers.get('Authorization')}")

    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        print("Authorization header is empty")
        return jsonify({'error': 'Token de acceso no proporcionado'}), 401
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        print("Invalid authorization header format")
        return jsonify({'error': 'Formato de token de acceso no válido'}), 401

    access_token = parts[1]
    app = current_app._get_current_object()
    userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
    
    print(f"Decoded user ID: {userid}")
    
    # Sube el video a S3
    #file_path_s3 = upload_to_s3(file, BUCKET_NAME, f"videos/{filename}")
    #if file_path_s3:
    video_existente = db.session.query(Video).filter_by(filepath=file_path,size=size).first()

    if video_existente:
        print("Video already exists, saving relation to publicacion_media")
        # Si la imagen ya existe, solo guarda la relación en publicacion_media
        cargar_id_publicacion_id_imagen_video(id_publicacion,0,video_existente.id,'video',size=size)
        return file_path
    else:
        print("Creating new video")
        nuevo_video = Image(
            user_id=userid,
            title=nombre_archivo,
            description=description_video,
            colorDescription=color_texto,
            filepath=file_path,
            randomNumber=randomNumber_,
            size=float(size)
        )
        db.session.add(nuevo_video)
        db.session.commit()
        print("Saving relation to publicacion_media")
        cargar_id_publicacion_id_imagen_video(id_publicacion,0,nuevo_video.id,'video',size=size)
    return file_path


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def es_formato_imagen(filepath):
    # Extensiones de archivo de imagen comunes
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # Verificar si la extensión del archivo está en la lista de extensiones de imagen
    return any(filepath.lower().endswith(ext) for ext in extensiones_imagen)




def guardarPublicacion(request, user_id):
    try:
        post_title = request.form.get('postTitle_creaPublicacion')
        post_text = request.form.get('postText_creaPublicacion')   
        ambito = request.form.get('postAmbito_creaPublicacion')
        correo_electronico = request.form.get('correo_electronico')
        color_texto = request.form.get('color_texto')
        color_titulo = request.form.get('color_titulo')
        estado = request.form.get('postEstado_creaPublicacion')
        
        # Verificar si ya existe una publicación con el mismo título para el mismo usuario
        publicacion_existente = db.session.query(Publicacion).filter_by(titulo=post_title, user_id=user_id).first()
        
        if publicacion_existente:
            # Si existe, devolver un mensaje sugiriendo cambiar el nombre
             return None
        
        # Crear una nueva publicación si no existe una con el mismo nombre
        nueva_publicacion = Publicacion(
            user_id=user_id,             
            titulo=post_title,
            texto=post_text,
            ambito=ambito,
            correo_electronico=correo_electronico,
            descripcion=post_text,
            color_texto=color_texto,
            color_titulo=color_titulo,
            fecha_creacion=datetime.now(),
            estado=estado
        )
        
        db.session.add(nueva_publicacion)
        db.session.commit()
        return nueva_publicacion.id
        
    except Exception as e:
        print(str(e))
        db.session.rollback()  # Asegúrate de hacer rollback en caso de error
        return jsonify({'error': 'Ocurrió un error al guardar la publicación.'}), 500
   

def cargar_id_publicacion_id_imagen_video(id_publicacion,nueva_imagen_id,nuevo_video_id,media_type,size=0):
    nuevo_ids= Public_imagen_video(
        publicacion_id=id_publicacion,
        imagen_id=nueva_imagen_id,
        video_id=nuevo_video_id,
        fecha_creacion=datetime.now(),
        media_type=media_type,
        size=float(size)
    )
    db.session.add(nuevo_ids)
    db.session.commit()
    db.session.close()
    return True

def show_publicacion_galeriaimagenes(request, media_files,id_publicacion):
     return render_template('publicaciones/publicacionesGaleriaImagenes.html', media_files=media_files,id_publicacion=id_publicacion)
     

@publicaciones.route('/social_imagenes_eliminar_publicacion', methods=['POST'])
def social_imagenes_eliminar_publicacion():
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
    if Token.validar_expiracion_token(access_token=access_token):
        app = current_app._get_current_object()
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get("sub")
        
        # Obtener el ID de la publicación a eliminar
        publicacion_id = request.form.get('publicacion_id')
        correo_electronico = request.form.get('correo_electronico')

        # Aquí deberías añadir la lógica para eliminar la publicación, imágenes y videos
        try:
            # Ejemplo de eliminación (ajustar según tu implementación)
            with app.app_context():
                eliminar_publicacion_y_medios(publicacion_id, user_id)

            return jsonify({'success': True}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Token de acceso no válido o expirado'}), 401

def eliminar_publicacion_y_medios(publicacion_id, user_id):
    try:
        publicacion = db.session.query(Publicacion).filter_by(id=publicacion_id, user_id=user_id).first()
        if publicacion:
            # Obtener los registros de medios relacionados en la tabla intermedia
            publicacion_imagen_video = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion_id).all()
            
            # Eliminar la publicación
            db.session.delete(publicacion)          
          
            for p in publicacion_imagen_video:
                # Verificar si la imagen está asociada a más de una publicación
                imagen_en_multiples_publicaciones = (
                    db.session.query(func.count(Public_imagen_video.publicacion_id))
                    .filter_by(imagen_id=p.imagen_id)
                    .scalar() > 1
                )
                if not imagen_en_multiples_publicaciones:
                    # Eliminar la imagen asociada, si no está en otras publicaciones
                    imagen = db.session.query(Image).filter_by(id=p.imagen_id, user_id=user_id, size=float(p.size)).first()
                    if imagen:
                        db.session.delete(imagen)
                      #  eliminar_desde_archivo(imagen.title, user_id)
                        delete_from_gcs(imagen.title)
                
                # Verificar si el video está asociado a más de una publicación
                video_en_multiples_publicaciones = (
                    db.session.query(func.count(Public_imagen_video.publicacion_id))
                    .filter_by(video_id=p.video_id)
                    .scalar() > 1
                )
                if not video_en_multiples_publicaciones:
                    # Eliminar el video asociado, si no está en otras publicaciones
                    video = db.session.query(Video).filter_by(id=p.video_id, user_id=user_id, size=float(p.size)).first()
                    if video:
                        db.session.delete(video)
                        #eliminar_desde_archivo(video.title, user_id)
                        delete_from_gcs(video.title)
                    
                # Eliminar el registro de la tabla intermedia
                db.session.delete(p)
            
            # Commit de todas las eliminaciones en una sola transacción
            db.session.commit()
            return True

    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        print(f"Error al eliminar la publicación y medios: {e}")
        return False


def  eliminar_desde_archivo(title,user_id):
    try:
        # Reemplazar barras diagonales hacia adelante ("/") por barras diagonales hacia atrás ("\")
        
        #ruta_base_datos = title.replace('/', '\\')
        file_path = os.path.join('static', 'uploads', title)
      
        #file_path = file_path.replace('\\', '/')
        # Agregar "static" al inicio de la ruta
        #ruta_base_datos = os.path.normpath('static\\' + file_path)
        ruta_ = os.path.join(file_path)
        ruta_ = ruta_.replace('\\', '/')
        absolute_file_path = os.path.abspath(ruta_)  # Obtener la ruta absoluta 
        os.remove(absolute_file_path)
        return True
    except OSError as e:
        print(f"Error al eliminar el archivo: {e}")
        return False

@publicaciones.route('/social_media_publicaciones_borrado_logico_publicaciones', methods=['POST'])
def social_media_publicaciones_borrado_logico_publicaciones(): 
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
            app = current_app._get_current_object()
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            # Obtener el ID de la publicación del cuerpo de la solicitud
            data = request.form
            publicacion_id = data.get('id')
            estado = data.get('estado')
            
            if not publicacion_id:
                return jsonify({'error': 'ID de publicación no proporcionado'}), 400
            
            # Llamar a la función para el borrado lógico
            borrado_logicopublicacion(int(publicacion_id), user_id,estado)

            return jsonify({'success': True}), 200

        return jsonify({'error': 'Token de acceso expirado o no válido'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def borrado_logicopublicacion(publicacion_id, user_id, estado):
    try:
        # Inicializa una lista vacía para almacenar las publicaciones
        publicaciones = []

        # Obtén todos los estados de la publicación con el publicacion_id y user_id dados
        publicacion_estados = db.session.query(Estado_publi_usu).filter_by(publicacion_id=publicacion_id, user_id=user_id).all()

        nuevo_estado = Estado_publi_usu(
            publicacion_id=publicacion_id,
            user_id=user_id,
            estado=estado,
            visto=False,  # Puedes cambiar esto según tus necesidades
            gusto='',  # Puedes cambiar esto según tus necesidades
            tiempo_visto='',  # Puedes cambiar esto según tus necesidades
            fecha_visto=datetime.now(),  # Puedes cambiar esto según tus necesidades
            fecha_eliminado=datetime.now(),  # Puedes cambiar esto según tus necesidades
            fecha_gustado=datetime.now()  # Puedes cambiar esto según tus necesidades
        )
        
        # Agregar el nuevo estado a la base de datos
        db.session.add(nuevo_estado)
        db.session.commit()
        
        publicaciones.append(nuevo_estado)  
                    
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        db.session.close()



@publicaciones.route('/social_media_publicaciones_modificar_publicaciones', methods=['POST'])
def publicaciones_modificar_publicaciones():
    try:
        # Obtener los datos del formulario
        post_id = request.form.get('postId_modificaPublicacion')
        titulo = request.form.get('postTitle_modificaPublicacion')
        texto = request.form.get('postText_modificaPublicacion')
        descripcion = request.form.get('postDescription_modificaPublicacion')
        estado = request.form.get('postEstado_modificaPublicacion')
        ambito = request.form.get('postAmbito_modificaPublicacion')

        # Obtener archivos subidos si es necesario
        archivos = request.files.getlist('mediaFile_modificaPublicacion')

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
        if Token.validar_expiracion_token(access_token=access_token):  
            app = current_app._get_current_object()
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")
        else:
            return jsonify({'error': 'Token de acceso expirado o inválido'}), 401

        # Verificar si la publicación existe y pertenece al usuario
        publicacion = db.session.query(Publicacion).filter_by(id=post_id, user_id=user_id).first()
        if not publicacion:
            return jsonify({'error': 'Publicación no encontrada o no autorizada'}), 404
        
        # Actualizar la publicación
        publicacion.titulo = titulo
        publicacion.texto = texto
        publicacion.descripcion = descripcion
        publicacion.estado = estado
        publicacion.ambito = ambito
        publicacion.fecha_modificacion = datetime.now()  # Asignar la fecha de modificación si es necesario

        db.session.commit()
        db.session.close()
        return jsonify({"mensaje": "Publicación modificada con éxito!"})

    except Exception as e:
        print(str(e))
        db.session.rollback()
        return jsonify({'error': 'Ocurrió un error al modificar la publicación.'}), 500

            
   
@publicaciones.route('/social_imagenes_eliminar_Imagenes_Publicaciones', methods=['POST'])
def social_imagenes_eliminar_Imagenes_Publicaciones():
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
            app = current_app._get_current_object()
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            # Obtener el ID de la publicación del cuerpo de la solicitud
            data = request.form
            publicacion_id = data.get('publicacion_id')
            
            if not publicacion_id:
                return jsonify({'error': 'ID de publicación no proporcionado'}), 400
            
            eliminar_desde_db_imagen_video(data, user_id)

            return jsonify({'success': True}), 200

        return jsonify({'error': 'Token de acceso expirado o no válido'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def eliminar_desde_db_imagen_video(data, user_id):    
    try:
        publicacion_id = data.get('publicacion_id')
        multimedia_id = data.get('id_imagen')
        size_imagen = data.get('size_imagen')

        # Obtener los registros de medios relacionados en la tabla intermedia
        publicacion_imagen_video = db.session.query(Public_imagen_video).filter_by(publicacion_id=publicacion_id, imagen_id=multimedia_id, size=float(size_imagen)).all()
        
        if len(publicacion_imagen_video) < 2:    
            # Eliminar la imagen asociada, si no está en otras publicaciones
            imagen = db.session.query(Image).filter_by(id=multimedia_id, user_id=user_id, size=float(size_imagen)).first()
            if imagen:
                db.session.delete(imagen)
                #eliminar_desde_archivo(imagen.title, user_id)
                delete_from_gcs(imagen.title)
                
        
            # Eliminar el video asociado, si no está en otras publicaciones
            video = db.session.query(Video).filter_by(id=multimedia_id, user_id=user_id, size=float(imagen.size)).first()
            if video:
                db.session.delete(video)
                #eliminar_desde_archivo(video.title, user_id)
                delete_from_gcs(video.title)
        
        # Eliminar el registro de la tabla intermedia
        for item in publicacion_imagen_video:
            db.session.delete(item)
        
        # Commit de todas las eliminaciones en una sola transacción
        db.session.commit()
        db.session.close()
        return True

    except Exception as e:
        db.session.rollback()
        raise e