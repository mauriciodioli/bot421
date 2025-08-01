import os #obtener el directorio de trabajo actual
import sys
from flask import current_app as app  # Importa `current_app`
import csv
from pipes import Template
from unittest import result
import requests
import json
from utils.db import db
from utils.db_session import get_db_session
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from utils.db_session import get_db_session 
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
import datetime
from models.logs import Logs
from contextlib import contextmanager



logRegister = Blueprint('logRegister',__name__)


@contextmanager
def session_scope():
    """Proporciona un contexto para una sesión de base de datos."""
    with get_db_session() as session:
        session = session()
        try:
            yield session
            session.commit()  # Se hace commit al final del contexto
        except Exception:
            session.rollback()  # Si hay un error, se hace rollback
            raise
        finally:
            session.close()  # Se cierra la sesión al finalizar el contexto



def registrar_acceso(request, usuario, exito, motivo_fallo=None):
    """Registra los intentos de acceso en la base de datos."""
    ip = request.get('client_ip')
    codigoPostal = request.get('codigoPostal')
    latitude = request.get('latitude')
    longitude = request.get('longitude')
    language = request.get('language')
    usuario_id = request.get('usuario_id')
    correo_electronico = request.get('correo_electronico')
    fecha = datetime.datetime.utcnow()

    try:
        with get_db_session() as session:
            log = Logs(
                user_id=usuario_id,
                userCuenta=correo_electronico,
                accountCuenta=correo_electronico,
                fecha_log=fecha,
                ip=ip,
                funcion='log_acceso',
                archivo='logRegister.py',
                linea=608,
                error='No hubo error' if exito else motivo_fallo,
                codigoPostal=codigoPostal,
                latitude=latitude,
                longitude=longitude,
                language=language
            )

            session.add(log)
            session.commit()
       

    except SQLAlchemyError as e:       
        app.logger.error(f"Error registrando acceso: {e}")

 

 







@logRegister.route('/log_acceso/', methods=['POST'])
def log_acceso():
    data = request.get_json()
    if data:
        usuario_obj = 'none'
        # Aquí podrías también verificar si los datos son correctos (por ejemplo, si el token es válido)
        exito = True  # Suponiendo que el login es exitoso. Cambia esto si es necesario.
        registrar_acceso(data, usuario_obj, exito)
        return jsonify({'status': 'ok'})
        
    else:
        return jsonify({'status': 'error', 'message': 'Datos no recibidos'}), 400



def registroLogs(datos):
    
 
    # Obtener el directorio actual del script
    directorio_actual = os.path.dirname(__file__)


    # Dividir la ruta en partes
    partes_ruta = directorio_actual.split(os.path.sep)

    # Encontrar la posición de "src" en las partes de la ruta
    indice_src = partes_ruta.index('src')

    # Construir la ruta hasta "src"
    ruta_hasta_src = os.path.sep.join(partes_ruta[:indice_src + 1])

    print(f'Ruta hasta "src": {ruta_hasta_src}')


    # Ruta relativa para guardar el archivo JSON en el subdirectorio "strategies"
    ruta_archivo_csv = os.path.join(ruta_hasta_src, 'log/', 'logs.log')

    # Escribir el diccionario en el archivo JSON
    with open(ruta_archivo_csv, 'w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
          # Escribir los datos en el archivo CSV fila por fila
        for fila in datos:
            escritor_csv.writerow(fila)

    print(f'Se ha creado el archivo csv en "{ruta_archivo_csv}"')   
    


def generate_logs():
    directorio_actual = os.path.dirname(__file__)
    partes_ruta = directorio_actual.split(os.path.sep)
    indice_src = partes_ruta.index('src')
    ruta_hasta_src = os.path.sep.join(partes_ruta[:indice_src + 1])

    ruta_archivo_csv = os.path.join(ruta_hasta_src, 'logs.log')

    encodings = ['utf-8', 'latin-1', 'iso-8859-1']  # Lista de encodings a intentar

    # Iterar sobre los encodings y abrir el archivo
    for encoding in encodings:
        try:
            with open(ruta_archivo_csv, 'r', encoding=encoding) as f:
                for line_number, log in enumerate(f, start=1):  # Contar las líneas para rastrear el número de línea
                    try:
                        yield f"data: {log}\n\n"
                    except UnicodeDecodeError as e:
                        # Imprimir el número de línea y la línea problemática
                        print(f"Error de decodificación Unicode en la línea {line_number}: {str(e)}")
                        print(f"Línea problemática: {log}")
                break  # Salir del bucle si se abre el archivo correctamente
        except UnicodeDecodeError as e:
            # Obtener el mensaje de error y los bytes problemáticos
            error_message = str(e)
            problem_bytes = e.object[e.start:e.end]
            print(f"Error de decodificación Unicode: {error_message}")
            print(f"Bytes problemáticos: {problem_bytes}")
            continue  # Continuar con el siguiente encoding si hay un error de decodificación

    # Esperar antes de leer los registros nuevamente
    time.sleep(1)


