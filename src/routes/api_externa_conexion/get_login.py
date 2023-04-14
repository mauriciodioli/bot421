
from ast import Return
from http.client import UnimplementedFileMode
from flask import current_app
import json
from datetime import datetime
from re import template
from socket import socket
import pyRofex
# datetime.date.today()
import websocket
import requests
import jwt
import re
import routes.api_externa_conexion.validaInstrumentos as valida
import routes.api_externa_conexion.wsocket as ws
import routes.instrumentos as inst
from models.instrumento import Instrumento
import ssl
from models.usuario import Usuario
from utils.db import db


from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)


get_login = Blueprint('get_login',__name__)

 
user = "{{usuario}}" 
password = "{{contraseña}}" 
account = "{{cuenta}}"  
market_data_recibida = []
reporte_de_ordenes = []

pyRofexInicializada = pyRofex
pyConectionWebSocketInicializada = pyRofex
pyWsSuscriptionInicializada = pyRofex



# Creating  Routes
#@get_login.route("/index")
#def index(): 
  
#   all_mer = Instrumento.query.all()
#   print("all_mer",all_mer)  
#   return render_template('index.html', datos = all_mer)


# Creating simple Routes
@get_login.route("/loginApi")
def loginApi():  
 return render_template("login.html")



 
from flask import request, render_template, redirect, url_for, flash
from datetime import datetime
from app import get_login, db, pyRofexInicializada, order_report_handler, error_handler, exception_handler
from app.models import Usuario

@get_login.route("/loginExt", methods=['POST'])
def loginExt():
    if request.method == 'POST':
        selector = request.form['selctorEnvironment']
        hoy = datetime.today().strftime('%d-%m-20%y')
        fecha = request.form['fecha']  # aquí traigo dato de localstorage
        dia = fecha.split()[0]
        mes = int(fecha.split()[1]) + 1
        a = re.sub("1", "", fecha.split()[2])
        fecha = "20" + str(a) + "-" + str(mes) + "-" + str(dia)

        first_date = datetime.strptime(hoy, '%d-%m-%Y')
        second_date = datetime.strptime('13-02-2023', '%d-%m-%Y')
        result = first_date > second_date

        if result:
            try:
                user = request.form['usuario']
                password = request.form['contraseña']
                account = request.form['cuenta']
                token = request.json.get('token')

                if token:
                    app = current_app._get_current_object()

                    try:
                        user_id = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                         # Add user data to the database
                        usuario = Usuario.query.get(user_id)  # Obtener el objeto Usuario con id=1
                        usuario.userCuenta = user  # Modificar la propiedad nombre
                        usuario.passwordCuenta = password
                        usuario.accountCuenta = account
                        
                        db.session.commit()
                    except:
                        print("no posee datos")
                        return render_template("login.html")

                    if int(selector) < 2:
                        try:
                            pyRofexInicializada.initialize(user=user,
                                                           password=password,
                                                           account=account,
                                                           environment=pyRofexInicializada.Environment.REMARKET)
                            pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                                order_report_handler=order_report_handler,
                                error_handler=error_handler,
                                exception_handler=exception_handler)
                            print("está logueado en simulado en REMARKET")
                        except:
                            print("contraseña o usuario incorrecto")
                            flash('Loggin Incorrect')
                            return render_template("errorLogueo.html")
                    else:
                        pyRofexInicializada.initialize(user=user,
                                                       password=password,
                                                       account=account,
                                                       environment=pyRofexInicializada.Environment.LIVE)
                        pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                            order_report_handler=order_report_handler,
                            error_handler=error_handler,
                            exception_handler=exception_handler)
                        print("está logueado en produccion en LIVE")
                        
                   
                        
            except jwt.ExpiredSignatureError:
                print("El token ha expirado")
                return redirect(url_for('autenticacion.index'))
            except jwt.InvalidTokenError:
                print("El token es inválido")

        return render_template('operaciones.html')


def order_report_handler(message):
  print("Mensaje de OrderRouting: {0}".format(message))
  reporte_de_ordenes.append(message)
  
def error_handler(message):
  print("Mensaje de error: {0}".format(message))

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))


       #ws.webSocket() ### AQUI FALTA HACER LA PANTALLA EN DONDE ELIJO LOS INSTRUMENTOS PARA SUSCRIBIRME 
       # repuesta_listado_instrumento = pyRofexInicializada.get_detailed_instruments()
       # listado_instrumentos = repuesta_listado_instrumento['instruments']
       # tickers_existentes = obtener_array_tickers(listado_instrumentos)
        #print(tickers_existentes)
       # mis_instrumentos = ["DLR/NOV22", "SOJ.ROS/MAY22","DLR/JUN22", "MERV - XMEV - TSLA - 48hs"]
       # instrumentos_existentes = valida.validar_existencia_instrumentos(mis_instrumentos,tickers_existentes)
        #print(instrumentos_existentes)
        
        ##aqui se conecta al ws
       # pyRofexInicializada.init_websocket_connection(market_data_handler,order_report_handler,error_handler,exception_error)
        #### aqui define el MarketDataEntry
       # entries = [pyRofexInicializada.MarketDataEntry.BIDS,
       #    pyRofexInicializada.MarketDataEntry.OFFERS,
       #    pyRofexInicializada.MarketDataEntry.LAST]        
        #instrumento_suscriptio =  pyRofexInicializada.market_data_subscription(instrumentos_existentes,entries)
        #print(instrumento_suscriptio)
       # pyRofexInicializada.order_report_subscription(snapshot=True)
       # saldo=obtenerSaldoCuenta()
        #print(saldo)
        ####aqui compro        
       # comprar('DLR/NOV22',25,108.25,pyRofex.OrderType.LIMIT)
        #vender('DLR/NOV22',25,108.25,pyRofex.OrderType.LIMIT)
      # actualizarTablaMD()
        
        





 

  
  

  
 
    




