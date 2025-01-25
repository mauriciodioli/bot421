from flask import Blueprint, render_template, session, current_app, request, redirect, url_for, flash, jsonify, g
import random
from datetime import datetime
import redis
from google.cloud import storage
import os
from dotenv import load_dotenv
from io import BytesIO



# Cargar las variables del archivo .env
load_dotenv()
bucketGoog = Blueprint('bucketGoog', __name__)

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

# Ruta a las credenciales de Google Cloud (archivo JSON descargado)
if 'EC2' in os.uname().nodename:  # o cualquier otro chequeo que prefieras
    BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL_AWS')
else:
    BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL')

# Establecer la variable de entorno para las credenciales
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BUCKET_GOOGLE_CREDENTIAL

# Nombre del bucket
BUCKET_NAME = os.environ.get('BUCKET_NAME')  # Asegúrate de que este nombre coincide con tu bucket




# Función para subir el fragmento a GCS

def upload_chunk_to_gcs_with_redis(chunk, blob_name_gcs, blob_name, start_byte, is_last_chunk, file_id, content_type):
    """
    Sube fragmentos de archivo a Google Cloud Storage utilizando Redis para el control de estado.
    """
    # Verificar si el fragmento ya fue subido (usando Redis)
    if redis_client.get(f"{file_id}_chunk_{start_byte}"):
        print(f"Fragmento {start_byte} ya subido, saltando.")
        return

    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    # Subir el fragmento directamente a GCS
    try:
        # Asegurarte de que `chunk` es un objeto de tipo FileStorage y convertirlo a bytes
        byte_stream = BytesIO(chunk.read())  # Lee los datos del archivo y crea un objeto BytesIO

        # Subir el fragmento al GCS
        if start_byte == 0:
            # Si es el primer fragmento, sube el archivo completo
            blob.upload_from_file(byte_stream, content_type=content_type)
        else:
            # Si es un fragmento intermedio, realiza un reemplazo o carga incremental
            byte_stream.seek(0)
            blob.upload_from_file(byte_stream, content_type=content_type)  # Recarga el fragmento

        print(f"Fragmento {start_byte} subido a {blob_name}.")

        # Marcar este fragmento como subido en Redis
        redis_client.set(f"{file_id}_chunk_{start_byte}", "uploaded")

        # Si es el último fragmento, puedes realizar alguna acción adicional (por ejemplo, finalizar la carga)
        if is_last_chunk:
            print(f"Último fragmento recibido. La carga de {blob_name} ha finalizado.")

    except Exception as e:
        print(f"No se pudo subir el fragmento a {blob_name}. Error: {e}")
        raise







def upload_to_gcs(file_path_local, blob_name_gcs):
    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name_gcs)

    # Intentar subir el archivo al bucket
    try:
        blob.upload_from_filename(file_path_local)
    except Exception as e:
        print(f"No se pudo subir el archivo {file_path_local} a {blob_name_gcs}. Error: {e}")
        raise
    else:
        print(f"Archivo {file_path_local} subido a {blob_name_gcs} exitosamente.")

        # Generar la URL pública del archivo
        url_publica = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name_gcs}"

        # Guardar la URL pública en Redis con un tiempo de expiración (por ejemplo, 1 hora)
        redis_client.set(blob_name_gcs, url_publica, ex=3600)
        print(f"URL de {blob_name_gcs} almacenada en Redis: {url_publica}")

        return url_publica


        
def delete_from_gcs(blob_name):
    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    # Intentar eliminar el archivo del bucket
    try:
        blob.delete()
        print(f"Archivo {blob_name} eliminado del bucket {BUCKET_NAME}.")

        # Eliminar la entrada en caché de Redis si existe
        if redis_client.exists(blob_name):
            redis_client.delete(blob_name)
            print(f"Entrada {blob_name} eliminada de Redis.")
        else:
            print(f"El archivo {blob_name} no estaba en caché.")

    except Exception as e:
        print(f"No se pudo eliminar el archivo {blob_name} del bucket. Error: {e}")

        
def mostrar_from_gcs(blob_name):
    # Verificar si la URL ya está en caché
    cached_url = redis_client.get(blob_name)
    print(f"Obteniendo URL desde Redis para el archivo: {blob_name}")
       

    # Si no está en caché, obtener desde GCS
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    try:
        url_publica = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
        
        # Guardar la URL en Redis con un tiempo de expiración (por ejemplo, 1 hora)
        redis_client.setex(blob_name, 3600, url_publica)
        
        print(f"URL obtenida y guardada en Redis para el archivo: {blob_name}")
        return url_publica
    except storage.exceptions.NotFound:
        print(f"El archivo {blob_name} no existe en el bucket {BUCKET_NAME}.")
        return None
    except Exception as e:
        print(f"No se pudo obtener la URL pública del archivo {blob_name}. Error: {e}")
        return None

