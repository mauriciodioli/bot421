
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
accountLocalStorage = ""
VariableParaBotonPanico = 0
VariableParaSaldoCta = 0
pyRofexInicializada = pyRofex
pyConectionWebSocketInicializada = pyRofex
pyWsSuscriptionInicializada = pyRofex
diccionario_global_operaciones = {}
diccionario_operaciones_enviadas = {}




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
    print('get_login.loginExtAutomatico ')
    if request.method == 'POST':
        try:
           
            access_token = request.json.get('access_token')
            rutaDeLogeo =  request.json.get('rutaDeLogeo')
            refresh_token = request.json.get('refresh_token')
            correo_electronico = request.json.get('correo_electronico')
            user = request.json.get('usuario')
            account = request.json.get('cuenta')
            simuladoOproduccion = request.json.get('simuladoOproduccion')
           # print('access_token ',access_token)
           # print('refresh_token ',refresh_token)
           # print('correo_electronico ',correo_electronico)
           
            if access_token:
                app = current_app._get_current_object()                    
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                exp_timestamp = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['exp']
                if account is not None and account != '':   
                   cuentas = db.session.query(Cuenta).filter(Cuenta.accountCuenta == account).first()
                   db.session.close()
                   passwordCuenta = cuentas.passwordCuenta
                   passwordCuenta = passwordCuenta.decode('utf-8')
                    
                   if  simuladoOproduccion !='':
                        if simuladoOproduccion =='simulado':
                            try:
                                            pyRofexInicializada.initialize(user=cuentas.userCuenta,
                                                                            password=passwordCuenta,
                                                                            account=cuentas.accountCuenta,
                                                                            environment=pyRofexInicializada.Environment.REMARKET)
                                        # pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                                        #     order_report_handler=order_report_handler,
                                        #     error_handler=error_handler,
                                        #     exception_handler=exception_handler)
                                            print("está logueado en simulado en REMARKET")
                                            if rutaDeLogeo == 'Home':  
                                                return render_template('home.html', cuenta=[account,user,simuladoOproduccion])
                                                #return jsonify({'redirect': url_for('get_login.home')})
                                            else:
                                                return jsonify({'redirect': url_for('panelControl.panel_control')})
                                            #return render_template('home.html', cuenta=[cuentas.accountCuenta,cuentas.userCuenta,simuladoOproduccion])
                            except:
                                #  print("contraseña o usuario incorrecto")
                              flash('Loggin Incorrect')
                              return render_template("errorLogueo.html")
                        else:
                            exp_date = datetime.utcfromtimestamp(exp_timestamp)
                            fecha_actual =   datetime.utcnow()
                            if fecha_actual > exp_date:
                                pyRofexInicializada.initialize(user=cuentas.userCuenta,
                                                            password=passwordCuenta,
                                                            account=cuentas.accountCuenta,
                                                            environment=pyRofexInicializada.Environment.LIVE)
                                #pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(
                                # order_report_handler=order_report_handler,
                                # error_handler=error_handler,
                                # exception_handler=exception_handler)
                                print("está logueado en produccion en LIVE")
                                if rutaDeLogeo != 'Home':      
                                 return render_template("/cuentas/panelDeControlBroker.html")   
                                else:
                                    return render_template('home.html', cuenta=[account,user,simuladoOproduccion]) 
                            else:
                                  return jsonify({'redirect': url_for('panelControl.panel_control')}) 
                else: 
                    return render_template('home.html', cuenta=[account,user,simuladoOproduccion]) 
            else:
                  return jsonify({'redirect': url_for('panelControl.panel_control')}) 
                    
        except jwt.InvalidTokenError:
            print("El token es inválido")
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
        except Exception as e:
            print("Otro error:", str(e))
        return render_template("cuentas/registrarCuentaBroker.html")


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

                   # try:
                    user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                       # Add user data to the database
                    usuario = Usuario.query.get(user_id)  # Obtener el objeto Usuario con id=1
                    usuario.userCuenta = user  # Modificar la propiedad nombre
                    usuario.passwordCuenta = password
                    usuario.accountCuenta = account
                        
                    db.session.commit()
                    db.session.close()
                    
                   # except jwt.ExpiredSignatureError:
                   #     print("El token ha expirado.")
                   # except jwt.InvalidTokenError:
                   #     print("El token es inválido.")
                   # except Exception as e:
                   #     print("Ocurrió un error no esperado:", e)    
                   # except:
                   #     print("no posee datos")
                   #     return render_template("login.html")
                    VariableParaTiemposMDHandler = 0
                    accountLocalStorage = ""
                    VariableParaBotonPanico = 0
                    VariableParaSaldoCta = 0
                    pyRofexInicializada = None
                    pyConectionWebSocketInicializada = None
                    pyWsSuscriptionInicializada = None
                    diccionario_global_operaciones = {}
                    diccionario_operaciones_enviadas = {}
                    VariableParaTiemposMDHandler = 0
                    accountLocalStorage = ""
                    VariableParaBotonPanico = 0
                    VariableParaSaldoCta = 0
                    pyRofexInicializada = pyRofex
                    pyConectionWebSocketInicializada = pyRofex
                    pyWsSuscriptionInicializada = pyRofex
                    diccionario_global_operaciones = {}
                    diccionario_operaciones_enviadas = {}

                    if selector == 'simulado':
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
            except Exception as e:
                # Manejas la excepción aquí
                print(f"Se produjo una excepción: {e}")
                print('No se puede logear contraseña incorrecta')
                flash('No se puede logear contraseña incorrecta')
                return render_template("login.html")
            return render_template('home.html', cuenta=[account,user,selector])

@get_login.route("/loginExtCuentaSeleccionadaBroker", methods=['POST'])
def loginExtCuentaSeleccionadaBroker():
    if request.method == 'POST':
            selector = request.form['selectorEnvironment']
            try:
                user = request.form['usuario']
                password = request.form['contraseña']              
                account = request.form['cuenta']
                access_token = request.form['access_token']
                #print("selctorEnvironment",selector)

                if access_token:
                    app = current_app._get_current_object()

                   # try:
                    user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                       # Add user data to the database
                  #  usuario = Usuario.query.get(user_id)  # Obtener el objeto Usuario con id=1
                  #  usuario.userCuenta = user  # Modificar la propiedad nombre
                  #  usuario.passwordCuenta = password
                  #  usuario.accountCuenta = account
                        
                  #  db.session.commit()
                  #  db.session.close()
                    
                   # except jwt.ExpiredSignatureError:
                   #     print("El token ha expirado.")
                   # except jwt.InvalidTokenError:
                   #     print("El token es inválido.")
                   # except Exception as e:
                   #     print("Ocurrió un error no esperado:", e)    
                   # except:
                   #     print("no posee datos")
                   #     return render_template("login.html")
                    
                    VariableParaTiemposMDHandler = 0
                    accountLocalStorage = ""
                    VariableParaBotonPanico = 0
                    VariableParaSaldoCta = 0
                    pyRofexInicializada = None
                    pyConectionWebSocketInicializada = None
                    pyWsSuscriptionInicializada = None
                    diccionario_global_operaciones = {}
                    diccionario_operaciones_enviadas = {}
                    VariableParaTiemposMDHandler = 0
                    accountLocalStorage = ""
                    VariableParaBotonPanico = 0
                    VariableParaSaldoCta = 0
                    pyRofexInicializada = pyRofex
                    pyConectionWebSocketInicializada = pyRofex
                    pyWsSuscriptionInicializada = pyRofex
                    diccionario_global_operaciones = {}
                    diccionario_operaciones_enviadas = {}

                    if selector == 'simulado':
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
            except Exception as e:
                print('No se puede logear en route/get_login linea 294')
                flash('No se puede logear en route/get_login linea 294')
                return render_template("login.html")
                # Puedes manejar este error de la manera que desees, por ejemplo, redirigir a una página de error.
               
            return render_template('cuentas/panelDeControlBroker.html', cuenta=[account, user, selector])

def order_report_handler(message):
  print("Mensaje de OrderRouting: {0}".format(message))
#  reporte_de_ordenes.append(message)
  
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
        
        





 

  
  

  
 
    




