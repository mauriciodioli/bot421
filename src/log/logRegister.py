import os #obtener el directorio de trabajo actual
import sys
import csv
from pipes import Template
from unittest import result
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify






logRegister = Blueprint('logRegister',__name__)

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
    ruta_archivo_csv = os.path.join(ruta_hasta_src, 'log/', 'logs.csv')

    # Escribir el diccionario en el archivo JSON
    with open(ruta_archivo_csv, 'w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
          # Escribir los datos en el archivo CSV fila por fila
        for fila in datos:
            escritor_csv.writerow(fila)

    print(f'Se ha creado el archivo csv en "{ruta_archivo_csv}"')   
