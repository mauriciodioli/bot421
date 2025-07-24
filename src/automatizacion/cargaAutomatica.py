import os
import sys
# Añadir el directorio actual al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from utils.db import db
import threading
import redis
import mimetypes
from PIL import Image as PILImage  # Renombrar la clase Image de Pillow
import ffmpeg
from utils.db_session import get_db_session 
from flask import Blueprint,current_app
from social.buckets.bucketGoog import upload_to_gcs
from models.modelMedia.image import Image
from models.modelMedia.video import Video
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.publicacion_imagen_video import Public_imagen_video


# Configuración de Redis usando las variables de entorno
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))

# Conexión a Redis
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# Crear el Blueprint para Flask
cargaAutomatica = Blueprint('cargaAutomatica', __name__)

BUCKET_NAME = 'nombre-de-tu-bucket'

def ArrancaSheduleCargaAutomatica(id_publicacion):
    # Asegúrate de que este código esté dentro del contexto de la aplicación
    with current_app.app_context():
        # Usamos la sesión con contexto seguro
        with get_db_session() as session:
            # Paso 1: Buscar asociaciones con la publicación
            imagenes_ids = session.query(Public_imagen_video).filter(
                Public_imagen_video.publicacion_id == id_publicacion
            ).all()

            total_por_publicacion = []

            if imagenes_ids:
                imagen_ids_lista = [img.imagen_id for img in imagenes_ids if img.imagen_id > 0]
                video_ids_lista = [vid.video_id for vid in imagenes_ids if vid.video_id > 0]

                # Paso 2: Recuperar imágenes
                if imagen_ids_lista:
                    imagenes = session.query(Image).filter(Image.id.in_(imagen_ids_lista)).all()
                    for img in imagenes:
                        total_por_publicacion.append({
                            "filepath": img.filepath,
                            "title": img.title
                        })

                # Paso 3: Recuperar videos
                if video_ids_lista:
                    videos = session.query(Video).filter(Video.id.in_(video_ids_lista)).all()
                    for vid in videos:
                        total_por_publicacion.append({
                            "filepath": vid.filepath,
                            "title": vid.title
                        })

        # 👇 A partir de acá, la sesión ya está cerrada, pero tenés todo lo necesario en memoria
        def delayed_execution():
            time.sleep(17)  # Esperar unos segundos

            for item in total_por_publicacion:
                file_path_local = item["filepath"]
                blob_name_gcs = item["title"]

                temp_file_path = os.path.join('static', 'uploads', f"{blob_name_gcs}")
                absolute_file_path = os.path.abspath(temp_file_path)

                comprimir_video_ffmpeg(absolute_file_path, blob_name_gcs, 0.5)
                url = upload_to_gcs(absolute_file_path, blob_name_gcs)

                # Limpiar Redis
                redis_client.hdel(blob_name_gcs, "file_path", "file_data")

                if os.path.exists(absolute_file_path):
                    os.remove(absolute_file_path)
                    print(f"Archivo temporal eliminado: {absolute_file_path}")

            print("✅ Todas las imágenes y videos fueron subidos correctamente.")

        # Iniciar el thread en segundo plano
        hilo = threading.Thread(target=delayed_execution)
        hilo.start()

        
def ArrancaSheduleCargaAutomatica_video_by_name(blob_name_gcs):
    # Asegúrate de que este código esté dentro del contexto de la aplicación
       
        """ Inicia un hilo que, después de 2 minutos, sube los archivos a Google Cloud Storage. """
        def delayed_execution():
            time.sleep(17)  # Esperar 2 minutos
          
            # Obtener la nueva ruta absoluta del archivo comprimido
            temp_file_path = os.path.join('static', 'uploads', f"{blob_name_gcs}")
            absolute_file_path = os.path.abspath(temp_file_path)
            comprimir_video_ffmpeg(absolute_file_path,blob_name_gcs,0.5)
            url = upload_to_gcs(absolute_file_path, blob_name_gcs)                
            # Liberar la memoria de Redis
            redis_client.hdel(blob_name_gcs, "file_path", "file_data")  # Eliminar los datos en Redis
            print(f"Memoria de Redis liberada para la clave ")
            # Eliminar el archivo temporal después de la carga
            if os.path.exists(absolute_file_path):
                os.remove(absolute_file_path)
                print(f"Archivo temporal eliminado: {absolute_file_path}")
            print("Todas las imágenes han sido subidas a Google Cloud Storage.")

        # Crear un thread en segundo plano
        # Crear y arrancar el hilo en segundo plano (sin daemon para que termine antes de finalizar la aplicación)
        hilo = threading.Thread(target=delayed_execution)
        hilo.start()
                


def comprimir_video_ffmpeg(output_path, file_name, compression_ratio=0.7):
    # Verificar si el archivo existe antes de continuar
    if not os.path.exists(output_path):
        print(f"El archivo {output_path} no existe.")
        return False

    # Verificar que el archivo sea un video
    content_type, _ = mimetypes.guess_type(file_name)
    if not content_type or not content_type.startswith('video/'):
        print(f"El archivo {file_name} no es un video.")
        return False

    try:
        # Obtener el tamaño original del archivo
        original_size = os.path.getsize(output_path)
        if original_size == 0:
            print("Error: El archivo original está vacío.")
            return False

        # Obtener el nombre del archivo sin la extensión
        base_name, ext = os.path.splitext(file_name)

        # Crear una ruta temporal con un sufijo para el archivo comprimido
        temp_output_path = os.path.join('static/uploads', f"{base_name}_compressed{ext}")

        # Comprimir el video para redes sociales (manteniendo la relación de aspecto)
        ffmpeg.input(output_path).output(
                temp_output_path, 
                vcodec='libx264', 
                acodec='copy',  # Copia el audio original sin modificarlo
                crf=25,
                preset='medium',
                vf="scale='if(gt(iw/ih,16/9),1280,-2)':'if(gt(iw/ih,16/9),-2,720)', pad=1280:720:(ow-iw)/2:(oh-ih)/2"
            ).run(overwrite_output=True)


        # Verificar el tamaño del archivo comprimido
        compressed_size = os.path.getsize(temp_output_path)
        reduction_percentage = (1 - (compressed_size / original_size)) * 100

        print(f"Tamaño original: {original_size} bytes, Tamaño comprimido: {compressed_size} bytes")
        print(f"Reducción del tamaño: {reduction_percentage:.2f}%")

        if compressed_size < original_size:
            os.replace(temp_output_path, output_path)
            print("Compresión exitosa.")
            return output_path
        else:
            os.remove(temp_output_path)
            print("No se logró comprimir el archivo.")
            return False

    except ffmpeg.Error as e:
        print(f"Error al comprimir el video: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False