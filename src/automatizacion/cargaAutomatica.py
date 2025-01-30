import os
import sys
# Añadir el directorio actual al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from utils.db import db
import threading
import redis
from flask import Blueprint,current_app
from social.buckets.bucketGoog import upload_to_gcs
from models.modelMedia.image import Image
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
        # Obtén la primera publicación de la lista de publicaciones
       

        # Asegúrate de que 'publicacion_id' existe en el diccionario
        imagenes_ids = db.session.query(Public_imagen_video).filter(Public_imagen_video.publicacion_id == id_publicacion).all()

        # Paso 2: Extraer solo los ids de la consulta, ya que .all() devuelve una lista de tuplas
        imagen_ids_lista = [imagen.imagen_id for imagen in imagenes_ids]
        # Paso 3: Recuperar todas las imágenes con esos ids en una sola consulta
        total_imagenes_por_publicacion = db.session.query(Image).filter(Image.id.in_(imagen_ids_lista)).all()

    
       
        """ Inicia un hilo que, después de 2 minutos, sube los archivos a Google Cloud Storage. """
        def delayed_execution():
            time.sleep(17)  # Esperar 2 minutos
          
            for img in total_imagenes_por_publicacion:
                # Asegúrate de acceder a los atributos del objeto 'img' correctamente
                file_path_local = img.filepath  # Accede al atributo 'filepath' directamente
                blob_name_gcs = img.title      # Accede al atributo 'title' directamente  
                # Obtener la nueva ruta absoluta del archivo comprimido
                temp_file_path = os.path.join('static', 'uploads', f"{blob_name_gcs}")
                absolute_file_path = os.path.abspath(temp_file_path)
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
