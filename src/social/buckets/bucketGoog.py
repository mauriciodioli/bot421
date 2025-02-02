from flask import Blueprint, render_template, session, current_app, request, redirect, url_for, flash, jsonify, g
import random
from datetime import datetime
import redis
from google.cloud import storage
import os
import mimetypes
from dotenv import load_dotenv
from io import BytesIO
import base64
import urllib.parse
from datetime import datetime, timedelta

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


# Inicializar el cliente de GCS
storage_client = storage.Client()

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
    blob.chunk_size = 1 * 1024 * 1024  # 1MB chunks

    # URL pública del archivo en GCS
    url_publica = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name_gcs}"

    # Verificar si el archivo ya existe en GCS
    if blob.exists():
        print(f"El archivo {blob_name_gcs} ya existe en el bucket {BUCKET_NAME}.")
        return url_publica  # Devolver la URL directamente si ya está en GCS

    # Subir el archivo si no existe
    try:
        blob.upload_from_filename(file_path_local, timeout=300)  # 5 minutos
        print(f"Archivo {file_path_local} subido a {blob_name_gcs} exitosamente.")
    except Exception as e:
        print(f"No se pudo subir el archivo {file_path_local} a {blob_name_gcs}. Error: {e}")
        raise

    return url_publica  # Devolver la URL después de subirlo





        
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
    # Primero, verificar si la imagen binaria está en caché
    # Intentar obtener los datos de la imagen desde Redis
    cached_image = redis_client.hgetall(blob_name)

    if cached_image:
        # Obtener la cadena hexadecimal de Redis
        hex_data = cached_image.get("file_data")
        file_path = cached_image.get("file_path")
      
        # Retornar los datos binarios de la imagen
        # Convertir de hexadecimal a binario
        if hex_data == '':
            image_data = None
            if not tiene_https(file_path):
               file_path = '/'+file_path
            return image_data,file_path
        image_data = bytes.fromhex(hex_data)
        return image_data,file_path  # Aquí puedes retornar la imagen o procesarla como desees

    # Si no está en caché, obtener la URL y la imagen desde GCS
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    try:
       
        # Obtener la URL pública de GCS
        url_publica = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
       
        # Verificar si el archivo existe en GCS
        if not blob.exists(client):
            print(f"El archivo {blob_name} no existe en el bucket {BUCKET_NAME}.")
            image_data = ""
            return image_data,url_publica
        # Leer la imagen como binario desde GCS
        image_data = blob.download_as_bytes()

        # Convertir los datos binarios a hexadecimal
        hex_data = image_data.hex()
        
        if es_video(blob_name):
             # Almacenar en Redis la URL y los datos hexadecimales
            redis_client.hset(blob_name, mapping={
                "file_path": url_publica,
                "file_data": ""  # Almacenar los datos como una cadena vacia
            })
        else:
            # Almacenar en Redis la URL y los datos hexadecimales
            redis_client.hset(blob_name, mapping={
                "file_path": url_publica,
                "file_data": hex_data  # Almacenar los datos como una cadena hexadecimal
            })

        # Opcional: establecer un tiempo de expiración (por ejemplo, 1 hora)
        redis_client.expire(blob_name, 300)
 
        print(f"Imagen y URL obtenidas y guardadas en Redis para el archivo: {blob_name}")
        
        return image_data,url_publica # Devolver los datos binarios de la imagen

    except storage.exceptions.NotFound:
        print(f"El archivo {blob_name} no existe en el bucket {BUCKET_NAME}.")
        return None
    except Exception as e:
        print(f"No se pudo obtener la imagen y URL para el archivo {blob_name}. Error: {e}")
        return None
    
def es_video(file_path):
    try:
        mimetype, _ = mimetypes.guess_type(file_path)
        if mimetype and mimetype.startswith("video/"):
            return True
        return False
    except Exception as e:
        print(f"Error al determinar el tipo MIME del archivo: {e}")
        return False
def tiene_https(url):
    return url.lower().startswith("https://")


def generate_signed_url(blob_name, content_type, expiration=timedelta(hours=1)):
    """Genera una URL firmada para subir archivos a GCS"""
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    
    # Generar la URL firmada
    url = blob.generate_signed_url(
        expiration=expiration,
        version="v4",  # Asegúrate de usar la versión correcta de la API
        method="PUT",
        content_type=content_type
    )
    
    return url

@bucketGoog.route('/get_signed_url/', methods=['POST'])
def get_signed_url():
    """Devuelve una URL firmada para subir archivos"""
    data = request.json
    file_name = data.get("file_name")  # Nombre del archivo
    file_type = data.get("file_type")  # MIME type (image/jpeg, video/mp4, etc.)

    if not file_name or not file_type:
        return jsonify({"error": "file_name y file_type son requeridos"}), 400

    signed_url = generate_signed_url(file_name, file_type)
    return jsonify({"signedUrl": signed_url})  # Devolver la URL firmada como respuesta





@bucketGoog.route('/bucketGoog_get_download_url/', methods=['POST'])
def bucketGoog_get_download_url():
    try:
        data = request.json
        file_name = data.get("file_name")

        if not file_name:
            return jsonify({"error": "Falta el nombre del archivo"}), 400

        # Corregir el nombre del bucket para que sea consistente
        bucket_name = "bucket_202404"  # Nombre correcto del bucket
        encoded_file_name = urllib.parse.quote(file_name)

        # Obtener el bucket y el blob
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"uploads/{encoded_file_name}")  # Ajusta la ruta si es necesario

        # Obtener la URL pública del archivo
        public_url = blob.public_url

        # Reemplazar caracteres incorrectos en la URL pública
        # Corrige el nombre del bucket si contiene errores como '%20'
        corrected_url = public_url.replace("bucket%20202404", "bucket_202404")

        # Opcional: corregir espacios (%20) y paréntesis en el nombre del archivo si es necesario
        corrected_url = corrected_url.replace("%20", " ").replace("%28", "(").replace("%29", ")")

        return jsonify({"publicUrl": corrected_url})

    except Exception as e:
        print(f"Error obteniendo la URL pública: {e}")  # Log para depuración
        return jsonify({"error": str(e)}), 500