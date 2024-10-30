from flask import Blueprint, render_template, session, current_app, request, redirect, url_for, flash, jsonify, g
import random
from datetime import datetime
from google.cloud import storage
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()
bucketGoog = Blueprint('bucketGoog', __name__)

# Ruta a las credenciales de Google Cloud (archivo JSON descargado)
if 'EC2' in os.uname().nodename:  # o cualquier otro chequeo que prefieras
    BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL_AWS')
else:
    BUCKET_GOOGLE_CREDENTIAL = os.environ.get('BUCKET_GOOGLE_CREDENTIAL')

# Establecer la variable de entorno para las credenciales
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BUCKET_GOOGLE_CREDENTIAL

# Nombre del bucket
BUCKET_NAME = os.environ.get('BUCKET_NAME')  # Asegúrate de que este nombre coincide con tu bucket

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

        
def delete_from_gcs(blob_name):
    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    # Intentar eliminar el archivo del bucket
    try:
        blob.delete()
        print(f"Archivo {blob_name} eliminado del bucket {BUCKET_NAME}.")
    except Exception as e:
        print(f"No se pudo eliminar el archivo {blob_name} del bucket. Error: {e}")

        
def mostrar_from_gcs(blob_name):
    # Inicializar cliente de Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    try:
        # Construir y retornar la URL pública
        url_publica = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
        return url_publica
    except Exception as e:
        print(f"No se pudo obtener la URL pública del archivo {blob_name}. Error: {e}")
        return None
