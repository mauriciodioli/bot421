from pipes import Template
from unittest import result
import requests
import json
import pyRofex
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
import routes.instrumentos as inst
import routes.instrumentosGet as instrumentosGet
from utils.db import db
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
from models.instrumentosSuscriptos import InstrumentoSuscriptos

import asyncio
import websockets
import websocket
import json
# Importar la clase base de la biblioteca de websockets
from websockets import WebSocketServerProtocol








# Crea la conexión WebSocket
ws = None
global datos


suscripciones = Blueprint('suscripciones',__name__)

reporte_de_instrumentos = []


@suscripciones.route("/suscripcion_instrumentos/" )
def suscripcion_instrumentos():
    try:
        
        return render_template("suscripcion.html" )

    except:        
        return render_template("notificaciones/noPoseeDatos.html" )

@suscripciones.route("/suscripcionDb/" )
def suscripcionDb():
    try:
       
         all_ins = db.session.query(InstrumentoSuscriptos).all()
         db.session.close()
         return render_template("instrumentos/suscripciones_db.html", datos =  all_ins)
    except:        
        return render_template("errorLogueo.html" )
    
@suscripciones.route("/suscDelete/", methods = ['POST'] )
def suscDelete():
    try:
         if request.method == 'POST':
            id = request.form['id']            
            dato = InstrumentoSuscriptos.query.get(id)
            print(dato)
            db.session.delete(dato)
            db.session.commit()
            
            flash('Operation Removed successfully')
            all_ins = db.session.query(InstrumentoSuscriptos).all()
            db.session.close()
            return render_template("instrumentos/suscripciones_db.html", datos =  all_ins)
    except: 
            flash('Operation No Removed')       
            all_ins = db.session.query(InstrumentoSuscriptos).all()
            db.session.close()
            return render_template("instrumentos/suscripciones_db.html", datos =  all_ins)

@suscripciones.route('/ajax', methods=['POST'])
def ajax():

    if request.method == "POST":
        datos = request.get_json()['datos']  # Acc
       
        print(datos)
        return render_template("instrumentos/suscripcion.html", datos_modificados=datos)
    
# Función async para enviar datos al WebSocket
async def send_data_to_websocket(data):
    async with websockets.connect('ws://localhost:8765') as websocket:
        await websocket.send(data)

# Función para iniciar el servidor WebSocket
async def start_websocket_server():
    # Establecer la conexión WebSocket
    websocket = await websockets.connect("ws://localhost:8765")
    websocket.datos = [get.market_data_recibida,longitudLista]
    
    # Ejecutar el servidor WebSocket
    start_server = await websockets.serve(websocket_handler, "localhost", 8765)
    await start_server



async def websocket_handler(websocket, path):
   # Obtener los datos del contexto de la conexión
    datos = websocket.extra['datos']
    market_data_recibida = datos[0]
    longitudLista = datos[1]
    
    # Enviar los datos al cliente
    await websocket.send(json.dumps({'market_data': market_data_recibida, 'longitud_lista': longitudLista}))



@suscripciones.route("/SuscripcionPorWebSocket/")      
async def SuscripcionPorWebSocket():
    try:
        # Trae los instrumentos para suscribirte
        mis_instrumentos = instrumentosGet.get_instrumento_para_suscripcion_ws()
        longitudLista = len(mis_instrumentos)
        print(len(mis_instrumentos),"<<<<<---------------------mis_instrumentos --------------------------->>>>>> ",mis_instrumentos)
        
        # Obtener la conexión PyRofex desde el diccionario
        pyRofexInicializada = get.ConexionesBroker.get(account)['pyRofex']
        
        # Obtener los instrumentos detallados
        repuesta_listado_instrumento = pyRofexInicializada.get_detailed_instruments(environment=account)
        listado_instrumentos = repuesta_listado_instrumento['instruments']
        
        # Validar existencia de los instrumentos
        tickers_existentes = inst.obtener_array_tickers(listado_instrumentos) 
        instrumentos_existentes = val.validar_existencia_instrumentos(mis_instrumentos, tickers_existentes)
        instrumentos_existentes_arbitrador1 = instrumentos_existentes.copy()

        ##aqui se conecta al ws
        print("<<<-----------pasoooo conexiooooonnnn wsocket.py--------->>>>>")
          
        #### aqui define el MarketDataEntry
        entries = [pyRofexInicializada.MarketDataEntry.BIDS,
                   pyRofexInicializada.MarketDataEntry.OFFERS,
                   pyRofexInicializada.MarketDataEntry.LAST]
          
        #### aqui se subscribe   
        mensaje = pyRofexInicializada.market_data_subscription(tickers=instrumentos_existentes, entries=entries)
        print("instrumento_suscriptio", mensaje)
        datos = [get.market_data_recibida, longitudLista]

        return render_template('suscripcion.html', datos=[get.market_data_recibida, longitudLista])
    except Exception as e:
        # Manejar la excepción, podrías imprimir un mensaje de error o realizar otra acción
        print("Se produjo un error:", e)
        # Redirigir a una página de error o mostrar un mensaje de error en la plantilla
        return render_template('notificaciones/noPoseeDatos.html', error_message="Se produjo un error durante la suscripción a los instrumentos.")



    