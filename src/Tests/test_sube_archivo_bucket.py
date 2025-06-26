<<<<<<< HEAD
from flask import Blueprint, render_template,session, current_app,request, redirect, url_for, flash,jsonify,g
#from utils.db import db

import random
from datetime import datetime
from google.cloud import storage
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()
test_sube_archivo_bucket = Blueprint('test_sube_archivo_bucket',__name__)


# Ruta a las credenciales de Google Cloud (archivo JSON descargado)


BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL')
# Establecer la variable de entorno para las credenciales
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('BUCKET_GOOGLE_CREDENTIAL')

# Nombre del bucket
BUCKET_NAME = 'bucket_202404'  # Asegúrate de que este nombre coincide con tu bucket

def upload_to_gcs(file_name, destination_blob_name):
    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Sube el archivo al bucket
    blob.upload_from_filename(file_name)

    print(f"Archivo {file_name} subido a {destination_blob_name}.")

# Ejemplo de uso
file_path = 'ruta/a/tu/imagen.jpg'  # Cambia a la ruta de tu archivo
upload_to_gcs(file_path, 'carpeta_en_gcs/imagen.jpg')
=======
from flask import Blueprint, render_template,session, current_app,request, redirect, url_for, flash,jsonify,g
#from utils.db import db

import random
from datetime import datetime
from google.cloud import storage
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()
test_sube_archivo_bucket = Blueprint('test_sube_archivo_bucket',__name__)


# Ruta a las credenciales de Google Cloud (archivo JSON descargado)


BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL')
# Establecer la variable de entorno para las credenciales
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('BUCKET_GOOGLE_CREDENTIAL')

# Nombre del bucket
BUCKET_NAME = 'bucket_202404'  # Asegúrate de que este nombre coincide con tu bucket

def upload_to_gcs(file_name, destination_blob_name):
    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Sube el archivo al bucket
    blob.upload_from_filename(file_name)

    print(f"Archivo {file_name} subido a {destination_blob_name}.")

# Ejemplo de uso
file_path = 'ruta/a/tu/imagen.jpg'  # Cambia a la ruta de tu archivo
upload_to_gcs(file_path, 'carpeta_en_gcs/imagen.jpg')
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
