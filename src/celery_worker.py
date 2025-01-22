from celery import Celery
from flask import Flask
import redis
from google.cloud import storage
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Configuración de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configura Celery para usar Redis como backend y broker
def make_celery(app: Flask) -> Celery:
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/0',  # Aquí usamos Redis para guardar el estado de las tareas
        broker='redis://localhost:6379/0'    # Redis como broker
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Establecer la variable de entorno para las credenciales de Google Cloud
if 'EC2' in os.uname().nodename:
    BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL_AWS')
else:
    BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BUCKET_GOOGLE_CREDENTIAL
BUCKET_NAME = os.environ.get('BUCKET_NAME')

# Tarea Celery
@celery.task
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
        url_publica = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name_gcs}"
        redis_client.set(blob_name_gcs, url_publica, ex=3600)
        print(f"URL de {blob_name_gcs} almacenada en Redis: {url_publica}")
        return url_publica

# Otras funciones (delete_from_gcs, mostrar_from_gcs) también deben ser modificadas para usarse con Celery si es necesario

