# Librerías estándar
import os
import random
import json
from datetime import datetime

import io
import mimetypes
# Librerías externas
import requests
import jwt
from PIL import Image as PILImage  # Renombrar la clase Image de Pillow
import ffmpeg

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
)
from werkzeug.utils import secure_filename
from sqlalchemy import func
from sqlalchemy.orm.exc import StaleDataError

# Importaciones del proyecto
from models.instrumento import Instrumento
from models.usuario import Usuario
from models.brokers import Broker
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.estado_publi_usu import Estado_publi_usu
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.usuarioRegion import UsuarioRegion
from models.usuarioUbicacion import UsuarioUbicacion
from models.usuarioPublicacionUbicacion import UsuarioPublicacionUbicacion
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.ambitoCategoriaRelation import AmbitoCategoriaRelation
from models.publicaciones.categoriaPublicacion import CategoriaPublicacion

from models.modelMedia.image import Image
from models.modelMedia.video import Video
from models.modelMedia.TelegramNotifier import TelegramNotifier
from utils.db import db
import sys
import os
# Añadir el directorio actual al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.db_session import get_db_session 
from publicaciones import armar_publicacion_bucket_para_dpi
from social.media.publicaciones import cargarImagen_crearPublicacion
from social.media.publicaciones import cargarVideo_crearPublicacion
import redis
import re
import logging
from google.cloud import storage
from datetime import datetime, timedelta
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
from social.buckets.bucketGoog import (
    upload_to_gcs, delete_from_gcs, mostrar_from_gcs,upload_chunk_to_gcs_with_redis
)
from automatizacion.cargaAutomatica import ArrancaSheduleCargaAutomatica

#import boto3
#from botocore.exceptions import NoCredentialsError


creaPublicacionesPartes = Blueprint('creaPublicacionesPartes',__name__)



# Configura el cliente de S3
#s3 = boto3.client('s3', aws_access_key_id='TU_ACCESS_KEY', aws_secret_access_key='TU_SECRET_KEY', region_name='tu-region')
# Nombre del bucket
BUCKET_NAME = os.environ.get('BUCKET_NAME')  # Asegúrate de que este nombre coincide con tu bucket




# Configuración de Redis usando las variables de entorno
redis_host = os.getenv('REDIS_HOST', 'localhost')  # Valor por defecto 'localhost' si no se encuentra la variable
redis_port = os.getenv('REDIS_PORT', 6379)        # Valor por defecto 6379
redis_db = os.getenv('REDIS_DB', 0)                # Valor por defecto 0
# Conexión a Redis
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)


# Probar la conexión a Redis (opcional)
try:
    redis_client.ping()  # Verifica si Redis está accesible
    print("Conexión a Redis exitosa")
except redis.ConnectionError:
    print("No se pudo conectar a Redis")





@creaPublicacionesPartes.route('/creaPublicacionesPartes_testCgs/')
def creaPublicacionesPartes_testCgs():
    return render_template('administracion/testCGS.html', layout='layout_administracion')


































def armar_publicacion_bucket(publicaciones):
    publicaciones_data = []
    with get_db_session() as session:
        for publicacion in publicaciones:
            # Obtener todas las imágenes y videos asociados a esta publicación
            imagenes_videos = session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()

            imagenes = []
            videos = []

            for iv in imagenes_videos:
                # Obtener la información de las imágenes
                if iv.imagen_id:
                    try:
                        imagen = session.query(Image).filter_by(id=iv.imagen_id).first()
                        
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
                        video = session.query(Video).filter_by(id=iv.video_id).first()
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











@creaPublicacionesPartes.route('/social_publicaciones_handle_upload_chunkn/', methods=['POST'])
def social_publicaciones_handle_upload_chunkn():
    try:
        # Validar encabezado de autorización
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401

        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401

        # Obtener el token de acceso
        access_token = parts[1]
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token de acceso inválido o expirado'}), 403

        # Decodificar el token para obtener el usuario
        decoded_token = jwt.decode(
            access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256']
        )
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Usuario no autorizado'}), 403

        # Procesar los datos del archivo
        chunk = request.files.get('chunk')
        filename = request.form.get('fileName')
        chunk_start = request.form.get('chunkStart')
        is_last_chunk = request.form.get('isLastChunk', 'false').lower() == 'true'
      
        if not chunk or not filename or chunk_start is None:
            return jsonify({'error': 'Datos incompletos en la solicitud'}), 400
        # Asegúrate de usar un nombre de archivo seguro
        file_name = secure_filename(filename_pre).replace("_", "")

        # Convertir chunk_start a entero
        try:
            chunk_start = int(chunk_start)
        except ValueError:
            return jsonify({'error': 'chunkStart debe ser un número entero'}), 400

        # Almacenar el fragmento
        safe_file_name = os.path.basename(file_name)
        file_path = os.path.join('static', 'uploads', f"{safe_file_name}")  # Ruta temporal para archivo
        
        with open(file_path, 'ab') as f:
            f.seek(chunk_start)
            f.write(chunk.read())
            
      

        # Si es el último fragmento, realizar acciones finales
        if is_last_chunk:
            # Verificar tamaño del archivo completo
            received_size = os.path.getsize(file_path)
            expected_size = int(request.form.get('fileSize', received_size))
            
            print(f"received_size: {received_size}, expected_size: {expected_size}")  # Depuración
           
            if received_size != expected_size:
                return jsonify({'error': 'Tamaño del archivo incompleto'}), 400

            # Mover el archivo a su ubicación final
            final_path = os.path.join('static', 'uploads', f"{safe_file_name}")  # Ruta final del archivo
            os.rename(file_path, final_path)
            
            if es_video(file_path):
                with open(final_path, "rb") as f:
                    redis_client.hset(safe_file_name, mapping={
                            "file_path": final_path,
                            "file_data": "" # Guardar binario como string hexadecimal
                        })
              
            else:
                comprimir_imagen(file_path,safe_file_name, 85)
            # comprimir_video_ffmpeg(file_path,safe_file_name,0.5)
            
                # Guardar el archivo en Redis con expiración de 2 minutos
                with open(final_path, "rb") as f:
                    redis_client.hset(safe_file_name, mapping={
                            "file_path": final_path,
                            "file_data": f.read().hex()  # Guardar binario como string hexadecimal
                        })
                    
            # Configurar expiración de 2 minutos (120 segundos) para ambos tipos de archivo
            redis_client.expire(safe_file_name, 120)
            print(f"URL de {safe_file_name} almacenada en Redis: {final_path}")
                
        
            return jsonify({'message': 'Archivo recibido completamente', 'path': final_path})

        return jsonify({'message': 'Fragmento recibido con éxito'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@creaPublicacionesPartes.route('/social_publicaciones_crear_publicacion_partes/', methods=['POST'])
def social_publicaciones_crear_publicacion_partes():
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
            layout = request.form.get('layout')
            ambito = request.form.get('ambito')  
               
            with get_db_session() as session:
                total_publicaciones = session.query(Publicacion).filter_by(user_id=user_id).count()
                #if total_publicaciones >= 20:
                #    return jsonify({'error': 'El usuario ha alcanzado el límite de publicaciones'}), 400
            
            
            # Recibir los metadatos de los archivos
                uploaded_files_metadata = request.form.getlist('uploadedFilesMetadata')  # Obtiene todos los valores de este campo
                
                # Parsear los metadatos JSON de cada archivo
                file_metadata_list = [json.loads(file_metadata) for file_metadata in uploaded_files_metadata]

                # Ahora `file_metadata_list` contiene los metadatos de los archivos
                print(file_metadata_list)
            
            
                # Guardar la publicación en la base de datos
                id_publicacion = guardarPublicacion(request, user_id)
                # Procesar archivos multimedia
                if id_publicacion is True:
                    return jsonify({'message': 'Publicación no creada, ya existe ese nombre'}), 400
            
                
                for index, file in enumerate(file_metadata_list):
                    filename_pre = file.get("fileName")
                    size = file.get("fileSize")               
                    content_type = file.get("content_type")  # Tipo de contenido MIME
                    print(f"Índice: {index}, Archivo: {filename_pre}, Tamaño: {size} bytes, Content-Type: {content_type}")
                    # Verifica si el archivo tiene un nombre
                    if filename_pre == '':
                        continue

                    # Asegúrate de usar un nombre de archivo seguro
                    filename =  secure_filename(filename_pre).replace("_", "")
                    # Decide si el archivo es una imagen o un video
                    file_ext = filename.rsplit('.', 1)[-1].lower()
                    if file_ext in {'png', 'jpg', 'jpeg', 'gif'}:
                        # Llama a la función de carga de imagen
                        color_texto = request.form.get('color_texto')
                        titulo_publicacion = request.form.get('postTitle_creaPublicacion')
                        file_path = cargarImagen_crearPublicacion(
                                                        app, 
                                                        request, 
                                                        filename, 
                                                        id_publicacion, 
                                                        color_texto, 
                                                        titulo_publicacion, 
                                                        content_type,
                                                        userid=user_id, 
                                                        index=index,
                                                        size=size)


                        app.logger.info(f'Se cargó una imagen: {filename}, índice: {index}')
                    elif file_ext in {'mp4', 'avi', 'mov'}:
                        # Llama a la función de carga de video
                        color_texto = request.form.get('color_texto')   
                        titulo_publicacion = request.form.get('postTitle_creaPublicacion')
                        file_path = cargarVideo_crearPublicacion(
                                                            app,
                                                            '',                                                         
                                                            filename, 
                                                            id_publicacion,
                                                            color_texto, 
                                                            titulo_publicacion,
                                                            content_type,
                                                            user_id,
                                                            index,
                                                            size
                                                            )
                    

                # Obtener todas las publicaciones del usuario
                publicaciones_user = session.query(Publicacion).filter_by(user_id=user_id,ambito=ambito).all()
            
                # Armar el diccionario con todas las publicaciones, imágenes y videos
                publicaciones_data = armar_publicacion_bucket_para_dpi(publicaciones_user,layout)
               
            # ArrancaSheduleCargaAutomatica(id_publicacion)  # Inicia el hilo para subir archivos a GCS
    
                #print(publicaciones_data)
                return jsonify(publicaciones_data)
    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500
        



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
        post_descripcion = request.form.get('postDescription_creaPublicacion')
        ambito = request.form.get('postAmbito_creaPublicacion')
        categoria_id =  request.form.get('postAmbitoCategorias_creaPublicacion')
        correo_electronico = request.form.get('correo_electronico')
        color_texto = request.form.get('color_texto')
        color_titulo = request.form.get('color_titulo')
        estado = request.form.get('postEstado_creaPublicacion')
        botonCompra = request.form.get('postBotonCompra_creaPublicacion')
        idioma = request.form.get('lenguaje')
        codigoPostal = request.form.get('codigoPostal')
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud') 
        pagoOnline = False
        with get_db_session() as session:
            # Verificar si ya existe una publicación con el mismo título para el mismo usuario
            publicacion_existente = session.query(Publicacion).filter_by(titulo=post_title, user_id=user_id).first()
            
            if publicacion_existente:
                # Si existe, devolver un mensaje sugiriendo cambiar el nombre
                return True
            if botonCompra == 'True':
                botonCompra = True
            else:
                botonCompra = False
        
            # Crear una nueva publicación si no existe una con el mismo nombre
            nueva_publicacion = Publicacion(
                user_id=user_id,             
                titulo=post_title,
                texto=post_text,
                ambito=ambito,
                categoria_id=int(categoria_id),
                correo_electronico=correo_electronico,
                descripcion=post_descripcion,
                color_texto=color_texto,
                color_titulo=color_titulo,
                fecha_creacion=datetime.now(),
                estado=estado,
                botonCompra=botonCompra,
                idioma=idioma,
                codigoPostal=codigoPostal,            
                pagoOnline=pagoOnline
            )
            
            session.add(nueva_publicacion)
            session.commit()
            #guardar la ubicacion publicacion
            publicacion_id = publicacionUbicacion(session,nueva_publicacion.id,codigoPostal,user_id)
            print("publicacion_id",nueva_publicacion.id)
            publicacionCategoriaPublicacion(session, categoria_id,nueva_publicacion.id)
            #guardar 
            return nueva_publicacion.id
        
    except Exception as e:
        print(str(e))
     
        return jsonify({'error': 'Ocurrió un error al guardar la publicación.'}), 500
   

def cargar_id_publicacion_id_imagen_video(id_publicacion,nueva_imagen_id,nuevo_video_id,media_type,size=0):
    with get_db_session() as session:
        nuevo_ids= Public_imagen_video(
            publicacion_id=id_publicacion,
            imagen_id=nueva_imagen_id,
            video_id=nuevo_video_id,
            fecha_creacion=datetime.now(),
            media_type=media_type,
            size=float(size)
        )
        session.add(nuevo_ids)
        session.commit()
       
        return True

def show_publicacion_galeriaimagenes(request, media_files,id_publicacion):
     return render_template('publicaciones/publicacionesGaleriaImagenes.html', media_files=media_files,id_publicacion=id_publicacion)
     



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

def comprimir_imagen(output_path,file_name, quality=85):
    # Detectar el tipo de archivo automáticamente
    content_type, _ = mimetypes.guess_type(file_name)
   
    # Si es un video, devolver el archivo sin cambios
    if content_type and content_type.startswith('video/'):
       return False

    # Procesar la imagen si no es JPEG (convertir a JPEG y comprimir)
    with PILImage.open(output_path) as img:
        img = img.convert("RGB")  # Asegurar que esté en formato RGB
        img.thumbnail((800, 800))  # Redimensionar (por ejemplo, máximo 800x800 px)
        img.save(output_path, format="JPEG", quality=quality)  # Guardar comprimida con calidad especificada
    
    return output_path


def es_video(file_path):
    mimetype, _ = mimetypes.guess_type(file_path)
    return mimetype is not None and mimetype.startswith("video/")




def publicacionCategoriaPublicacion(session,categoria_id,publicacion_id):
    try:
      
            new_categoria_publicacion = CategoriaPublicacion(
                categoria_id=int(categoria_id),
                publicacion_id=publicacion_id,
                estado='activo'
            )
            session.add(new_categoria_publicacion)
            session.commit()
            
            return True
    except Exception as e:
        print(str(e))
      
        return False
    


def publicacionUbicacion(session, nueva_publicacion_id,codigoPostal,user_id):
    try:
        # Buscar si el usuario ya tiene una ubicación guardada
        
            usuarioRegion = session.query(UsuarioRegion).filter_by(user_id=user_id).first()
            usuario_ubicacion = session.query(UsuarioUbicacion).filter_by(user_id=user_id).first() # Suponiendo que existe un modelo UsuarioUbicacion
            publicacion_ubicacion = session.query(UsuarioPublicacionUbicacion).filter_by(id=nueva_publicacion_id).first() # Suponiendo que existe un modelo UsuarioUbicacion
            if publicacion_ubicacion:
                return True
            else:
                
                if usuario_ubicacion:
                    id_ubicaion = usuario_ubicacion.id
                else:
                    # Si no existe, creamos un nuevo registro de ubicación
                    id_ubicaion = 0
                    
                new_publicacion_ubicacion = UsuarioPublicacionUbicacion(
                            user_id = user_id,
                            id_region = usuarioRegion.id,
                            id_publicacion = nueva_publicacion_id,
                            id_ubicacion = id_ubicaion,
                            codigoPostal = codigoPostal,
                        )
                session.add(new_publicacion_ubicacion)

            session.commit()
            
            return True
    except Exception as e:
        print(str(e))
       
        return False
            