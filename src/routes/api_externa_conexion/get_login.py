
from ast import Return
from http.client import UnimplementedFileMode
from flask import current_app,g
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
from models.cuentas import Cuenta
from utils.db import db
from datetime import datetime

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

VariableParaTiemposMDHandler = 0
VariableParaBotonPanico = 0
VariableParaSaldoCta = 0
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

@get_login.route('/home')
def home():
    return render_template('home.html')

@get_login.route("/loginExtAutomatico", methods=['POST'])
def loginExtAutomatico():
    print('loginExtAutomatico ')
    if request.method == 'POST':
        try:
            access_token = request.json.get('access_token')
            refresh_token = request.json.get('refresh_token')
            correo_electronico = request.json.get('correo_electronico')
            user = request.json.get('usuario')
            password = request.json.get('contraseña')
            account = request.json.get('cuenta')
          
            simuladoOproduccion = request.json.get('simuladoOproduccion')
           # print('access_token ',access_token)
           # print('refresh_token ',refresh_token)
           # print('correo_electronico ',correo_electronico)
            
            print('usuario ',user)
            print('selector ',account)
            if access_token:
                    app = current_app._get_current_object()
            
                    user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                    # Add user data to the database
                    print("user_id ",user_id)
                    cuentas = db.session.query(Cuenta).filter(Cuenta.accountCuenta == account).first()
                    db.session.close()
                    print("______............._______",cuentas.userCuenta) 
                  
                    print("cuentas.userCuenta ",cuentas.passwordCuenta)
                    print("cuentas.accountCuenta ",cuentas.accountCuenta)
          
             
            if int(simuladoOproduccion) < 2:
                  # try:
                                pyRofexInicializada.initialize(user=cuentas.userCuenta,
                                                                password=cuentas.passwordCuenta,
                                                                account=cuentas.accountCuenta,
                                                                environment=pyRofexInicializada.Environment.REMARKET)
                               # pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                               #     order_report_handler=order_report_handler,
                               #     error_handler=error_handler,
                               #     exception_handler=exception_handler)
                                print("está logueado en simulado en REMARKET")
                                
                                return jsonify({'redirect': url_for('get_login.home')})

                                #return render_template('home.html', cuenta=[cuentas.accountCuenta,cuentas.userCuenta,simuladoOproduccion])
                  # except:
                     #  print("contraseña o usuario incorrecto")
                     #  flash('Loggin Incorrect')
                     #  return render_template("errorLogueo.html")
            else:
                    pyRofexInicializada.initialize(user=cuentas.userCuenta,
                                                   password=cuentas.passwordCuenta,
                                                   account=cuentas.accountCuenta,
                                                 environment=pyRofexInicializada.Environment.LIVE)
                    #pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                      # order_report_handler=order_report_handler,
                      # error_handler=error_handler,
                      # exception_handler=exception_handler)
                    print("está logueado en produccion en LIVE")
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
            return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except:
           print("contraseña o usuario incorrecto")
           
                  
        return render_template('home.html', cuenta=[account,user,simuladoOproduccion])


@get_login.route("/loginExt", methods=['POST'])
def loginExt():
    if request.method == 'POST':
            selector = request.form['selctorEnvironment']
            try:
                user = request.form['usuario']
                password = request.form['contraseña']
                account = request.form['cuenta']
                access_token = request.form['access_token']
                #print("selctorEnvironment",selector)

                if access_token:
                    app = current_app._get_current_object()

                    try:
                        user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                         # Add user data to the database
                        usuario = Usuario.query.get(user_id)  # Obtener el objeto Usuario con id=1
                        usuario.userCuenta = user  # Modificar la propiedad nombre
                        usuario.passwordCuenta = password
                        usuario.accountCuenta = account
                        
                        db.session.commit()
                        db.session.close()
                        
                    except:
                        print("no posee datos")
                        return render_template("login.html")

                    if int(selector) < 2:
                        try:
                            pyRofexInicializada.initialize(user=user,
                                                           password=password,
                                                           account=account,
                                                           environment=pyRofexInicializada.Environment.REMARKET)
                          #  pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                          #      order_report_handler=order_report_handler,
                          #      error_handler=error_handler,
                          #      exception_handler=exception_handler)
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
                        #pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                        #    order_report_handler=order_report_handler,
                        #    error_handler=error_handler,
                        #    exception_handler=exception_handler)
                        print("está logueado en produccion en LIVE")
                        
                   
                        
            except jwt.ExpiredSignatureError:
                print("El token ha expirado")
                return redirect(url_for('autenticacion.index'))
            except jwt.InvalidTokenError:
                print("El token es inválido")

            return render_template('home.html', cuenta=[account,user,selector])


#def order_report_handler(message):
#  print("Mensaje de OrderRouting: {0}".format(message))
#  reporte_de_ordenes.append(message)
  
#def error_handler(message):
#  print("Mensaje de error: {0}".format(message))

#def exception_handler(e):
#    print("Exception Occurred: {0}".format(e.msg))


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
        
        





 

  
  

  
 
    




