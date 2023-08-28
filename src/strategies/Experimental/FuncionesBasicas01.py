from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,  make_response
import routes.instrumentos as instrumentos
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
import routes.instrumentos as inst
from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
import socket
import requests
import time
import json
from models.orden import Orden
import random
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#import routes.api_externa_conexion.cuenta as cuenta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import os #obtener el directorio de trabajo actual
#import drive
#drive.mount('/content/gdrive')



FuncionesBasicas01 = Blueprint('FuncionesBasicas01',__name__)


@FuncionesBasicas01.route('/basicas/', methods = ['POST'])
def basicas():
 if request.method == 'POST':
        try:
            # Obtén los datos enviados en la solicitud AJAX
            data = request.get_json()

            # Accede a los datos individualmente
            userCuenta = data['userCuenta']
            idTrigger = data['idTrigger']
            access_token = data['access_token']
            idUser = data['idUser']
            correo_electronico = data['correo_electronico']
            cuenta = data['cuenta']
            tiempoInicio = data['tiempoInicio']
            tiempoFin = data['tiempoFin']
            automatico = data['automatico']
            nombre = data['nombre']

            # Ahora puedes procesar estos datos como desees
            # ...

            # Devuelve una respuesta (opcional)
           # resp = {'redirect': '/paginaDePrueba/'}
            #resp = make_response(jsonify({'redirect': 'test'}))
           # resp.headers['Content-Type'] = 'application/json'
            #return jsonify({'redirect': url_for('strategies.Experimental.paginaDePrueba')}) 
            return ''
        except Exception as e:
            # Maneja cualquier excepción que pueda ocurrir
            return str(e), 400  # Devuelve un código de estado 400 en caso de error


       # print('llegamos a basicas ')
@FuncionesBasicas01.route('/paginaDePrueba/')
def paginaDePrueba():  
  return render_template('test.html')  


# calculo del mep AL30 con websoket
def MepAl30WS(message):
     
     
  #  resultado = instrument_by_symbol_para_CalculoMep(message)    
  #  resultado2 = instrument_by_symbol_para_CalculoMep(message) 
    
    
    #if isinstance(message["marketData"]["OF"][0]["price"],float):
    #precio = message["marketData"]["OF"][0]["price"]
    #if isinstance(message["marketData"]["OF"][0]["size"],int):
    #Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]


    #if len( message['marketData']['OF']) == 0:
    if not isinstance(message["marketData"]["OF"][0]["size"],int):# entra si el offer esta vacio
        # entra si el offer esta vacio
        print(" FUN calcularMepAl30WS: La clave 'OF' está vacía.")
    else:

        al30_ci = message['marketData']['OF'][0]['price'] #vendedora OF
        al30D_ci =message['marketData']['BI'][0]['price'] #compradora BI
        #print("__________al30_ci____________",al30_ci)
        #print("__________al30D_ci____________",al30D_ci)
        
        # simulo compra de bono      
        #print("____simulo compra de bono ")  
        # al30ci_unitaria = al30_ci/100
        #cantidad_al30ci=int(10000/al30ci_unitaria)
        #print("__________cantidad_al30ci_________",cantidad_al30ci)
        
        # ahora simulo la venta de los bonos D
        #print("ahora simulo la venta de los bonos D")
        #al30D_ci_unitaria = al30D_ci/100
        #dolaresmep = al30D_ci_unitaria * cantidad_al30ci
        #mep = 10000 / dolaresmep
    mep = 380
    #print(" FUN calcularMepAl30WS: .")
    return mep
