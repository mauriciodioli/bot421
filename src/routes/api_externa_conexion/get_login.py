from utils.common import Marshmallow, db
from ast import Return
from http.client import UnimplementedFileMode

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
import os
import routes.api_externa_conexion.validaInstrumentos as valida

from routes.api_externa_conexion.wsocket import wsocketConexion as conexion
from fichasTokens.fichas import refrescoValorActualCuentaFichas
import routes.instrumentos as inst
from models.instrumento import Instrumento
import routes.api_externa_conexion.cuenta as cuenta
import ssl
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.brokers import Broker

import automatizacion.programar_trigger as trigger
import automatizacion.shedule_triggers as shedule_triggers
import threading

from utils.db import db
from datetime import datetime
import time
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies
    
)
from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
    g,
    make_response
)


get_login = Blueprint('get_login',__name__)

 
user = "{{usuario}}" 
password = "{{contraseña}}" 
account = "{{cuenta}}"  
market_data_recibida = []
reporte_de_ordenes = []


SPREADSHEET_ID_PRUEBA='1yQeBg8AWinDLaErqjIy6OFn2lp2UM8SRFIcVYyLH4Tg'#drpiBot3 de pruba
SPREADSHEET_ID_PRODUCCION='1GMv6fwa1-4iwhPBZqY6ZNEVppPeyZY0R4JB39Xmkc5s'#drpiBot de produccion
SPREADSHEET_ID_USA='1sxbKe5pjF3BsGgUCUzBDGmI-zV5hWbd6nzJwRFw3yyU'#de produccion USA

VariableParaTiemposMDHandler = 0
accountLocalStorage = ""
VariableParaBotonPanico = 0
VariableParaSaldoCta = 0
pyRofexInicializada = pyRofex
pyConectionWebSocketInicializada = pyRofex
pyWsSuscriptionInicializada = pyRofex
diccionario_global_operaciones = {}
diccionario_operaciones_enviadas = {}
diccionario_global_sheet = {}
diccionario_global_sheet_intercambio = {}
ya_ejecutado_hilo_panelControl = False
hilo_iniciado_panel_control = {}  # Un diccionario para mantener los hilos por país
hilo_iniciado_estrategia_usuario = {}
hilos_iniciados_shedule = []
ultima_entrada = time.time()
CUSTOM_LEVEL = 25  # Elige un número de nivel adecuado
detener_proceso_automatico_triggers = False  # Bucle hasta que la bandera detener_proceso sea True
ContenidoSheet_list = None
api_url = None
ws_url = None

# Calcula la hora de inicio del día siguiente a las 9:00 AM
#hora_inicio_manana = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(9, 0))

# Configurar las URLs de la instancia de BMB
#api_url = "https://api.bull.xoms.com.ar/"
#ws_url = "wss://api.bull.xoms.com.ar/"

#api_url = "https://api.cocos.xoms.com.ar/"
#ws_url = "wss://api.cocos.xoms.com.ar/"
 
#api_url = "https://api.veta.xoms.com.ar/"
#ws_url = "wss://api.veta.xoms.com.ar/"



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

@get_login.route("/panel_control_broker", methods=['GET'])
def panel_control_broker():
     if request.method == 'GET':       
       
        cuenta = []#si va cero entonces no cargar localstorage
        return render_template("/paneles/panelDeControlBroker.html", datos = cuenta)

@get_login.route("/loginExtAutomatico", methods=['POST'])
def loginExtAutomatico():
    print('get_login.loginExtAutomatico ')
    if request.method == 'POST':
        try:
            #selector = request.form.get('environment')
            selector = request.json.get('simuladoOproduccion')
            access_token = request.json.get('access_token')
            rutaDeLogeo =  request.json.get('origin_page')
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
                environment = pyRofexInicializada.Environment.REMARKET if selector == 'simulado' else pyRofexInicializada.Environment.LIVE
                print(f"Está enviando a {environment}")
                if account is not None and account != '':   
                   cuentas = db.session.query(Cuenta).filter(Cuenta.accountCuenta == account).first()
                   db.session.close()
                   passwordCuenta = cuentas.passwordCuenta
                   passwordCuenta = passwordCuenta.decode('utf-8')
                    
                   if  simuladoOproduccion !='':
                        if simuladoOproduccion =='simulado':
                            try:
                                            environment =pyRofexInicializada.Environment.REMARKET
                                            
                                          #  WsEndPoint ='wss://api.remarkets.primary.com.ar/'
                                          #  urlEndPoint= 'https://api.remarkets.primary.com.ar/'
                                          #  pyRofexInicializada._set_environment_parameter("url", urlEndPoint,environment)
                                          #  pyRofexInicializada._set_environment_parameter("ws",WsEndPoint,environment) 
                                          #  pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environment)
                                         
                                            pyRofexInicializada.initialize(user=cuentas.userCuenta,password=passwordCuenta,account=cuentas.accountCuenta,environment=environment )
                                            conexion() 
                                            refrescoValorActualCuentaFichas(user_id)                                    
                                            print("está logueado en simulado en REMARKET")
                                            if rutaDeLogeo == 'Home':  
                                                resp = make_response(jsonify({'redirect': 'home', 'cuenta': account, 'userCuenta': cuentas.userCuenta, 'selector': selector}))
                                                resp.headers['Content-Type'] = 'application/json'
                                                set_access_cookies(resp, access_token)
                                                set_refresh_cookies(resp, refresh_token)
                                                return resp
                                            else:                                          
                                                resp = make_response(jsonify({'redirect': 'panel_control_broker'}))
                                                resp.headers['Content-Type'] = 'application/json'
                                                set_access_cookies(resp, access_token)
                                                set_refresh_cookies(resp, refresh_token)
                                                return resp
                            except:
                                #  print("contraseña o usuario incorrecto")
                              flash('Loggin Incorrect')
                              return render_template("errorLogueo.html")
                        else:
                            exp_date = datetime.utcfromtimestamp(exp_timestamp)
                            fecha_actual =   datetime.utcnow()
                            endPoint = inicializar_variables(cuentas.accountCuenta)
                            global api_url
                            global ws_url
                            api_url = endPoint[0]
                            ws_url = endPoint[1]
                            print('88888888888888888888888888888888 fecha_actual ',fecha_actual,'22222222222 exp_date',exp_date)
                            if fecha_actual > exp_date:#hay que corregir el direccionamiento de esto_________
                              
                                environment = pyRofexInicializada.Environment.LIVE
                                
                                pyRofexInicializada._set_environment_parameter("url", api_url,environment)
                                pyRofexInicializada._set_environment_parameter("ws", ws_url,environment)                                
                                pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environment)                                
                                pyRofexInicializada.initialize(user=cuentas.userCuenta,password=passwordCuenta,account=cuentas.accountCuenta,environment=environment )
                                conexion(app)
                                #trigger.llama_tarea_cada_24_horas_estrategias('1',app)
                                print("está logueado en produccion en LIVE")
                                # Crear un objeto que represente los argumentos que deseas pasar a la función planificar_schedule
                               

                                # Crear el hilo sin llamar directamente a la función planificar_schedule
                                # Supongamos que shedule_triggers es tu objeto Blueprint de Flask
                                #hilo_principal = threading.Thread(target=shedule_triggers.planificar_schedule, 
                                #args=('1', app, "12:00", "17:00"))

                               # hilo_principal.start()
                                #refrescoValorActualCuentaFichas(user_id)
                                print("pasa hilo hilo_principal.start() planificar_schedule")
                                if rutaDeLogeo != 'Home':      
                                    return render_template("/paneles/panelDeControlBroker.html")   
                                else:
                                    
                                    resp = make_response(jsonify({'redirect': 'panel_control_broker'}))
                                    resp.headers['Content-Type'] = 'application/json'
                                    set_access_cookies(resp, access_token)
                                    set_refresh_cookies(resp, refresh_token)
                                    return resp 
                            else:
                                 
                                  # return render_template('paneles/panelDeControlBroker.html', cuenta=[accountCuenta, user, selector])
                                  # Supongamos que `accountCuenta`, `user`, y `selector` son los datos que quieres enviar
                                  cuenta = {
                                        'accountCuenta': account,
                                        'user': user,
                                        'selector': selector
                                  }
                                  # Crear una respuesta JSON con los datos de la cuenta y la redirección
                                  resp_data = {
                                        'redirect': 'panel_control_broker',
                                        'cuenta': cuenta  # Aquí incluimos los datos de la cuenta en el cuerpo de la respuesta
                                  }
                                  # Crear la respuesta utilizando jsonify y make_response
                                  resp = make_response(jsonify(resp_data))
                                  #resp = make_response(jsonify({'redirect': 'panel_control_broker'}))
                                  resp.headers['Content-Type'] = 'application/json'
                                  set_access_cookies(resp, access_token)
                                  set_refresh_cookies(resp, refresh_token)
                                  return resp 
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





@get_login.route("/loginExtCuentaSeleccionadaBroker", methods=['POST'])
def loginExtCuentaSeleccionadaBroker():
     if request.method == 'POST':
        origin_page = request.form.get('origin_page')
        user = request.form.get('usuario')
        password = request.form.get('contraseña')
        accountCuenta = request.form.get('cuenta')
        access_token = request.form.get('access_token')       
        src_directory1 = os.getcwd()#busca directorio raiz src o app 
        logs_file_path = os.path.join(src_directory1, 'logs.log')
       
       # logs_file_path = os.path.join(src_directory, 'logs.log')
       

        # Abrir el archivo en modo de escritura para borrar su contenido
#        with open(logs_file_path, 'w') as f:
#            pass  # No es necesario escribir nada, solo abrir y cerrar el archivo borrará su contenido
#        print("El contenido del archivo logs.log ha sido borrado.")
          # Variable local para mantener un registro de los hilos iniciados aquí
      
        if origin_page == 'login':
            selector = request.form.get('environment')
            print('selector ',selector)
            
        else: 
            selector = request.form.get('selectorEnvironment')
            print('selector ',selector)
        
        
       
        if not selector or not user or not password or not accountCuenta:
            flash('Falta información requerida')
            return redirect(url_for('autenticacion.index'))

        try:
           
            app = current_app._get_current_object() 
            #creaJsonParaConextarseSheetGoogle()
            if selector == 'simulado':
                # Configurar para el entorno de simulación
                environments = pyRofexInicializada.Environment.REMARKET
              #  WsEndPoint ='wss://api.remarkets.primary.com.ar/'
              #  urlEndPoint= 'https://api.remarkets.primary.com.ar/'
              #  pyRofexInicializada._set_environment_parameter("url", urlEndPoint,environments)
              #  pyRofexInicializada._set_environment_parameter("ws",WsEndPoint,environments) 
              #  pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments)
                                         
            else:
                # Configurar para el entorno LIVE
                environments = pyRofexInicializada.Environment.LIVE
                
                endPoint = inicializar_variables(accountCuenta)
                app.logger.info(endPoint)
                global api_url
                global ws_url
                api_url = endPoint[0]
                ws_url = endPoint[1]
                pyRofexInicializada._set_environment_parameter("url", api_url,environments)
                pyRofexInicializada._set_environment_parameter("ws", ws_url,environments) 
                pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments)
               

                    
            print(f"Está enviando a {environments}")
            if access_token:
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                # Aquí puedes realizar operaciones relacionadas con el usuario si es necesario.
          
            pyRofexInicializada.initialize(user=user,password=password,account=accountCuenta,environment=environments )
            conexion(app)
            #trigger.llama_tarea_cada_24_horas_estrategias('1',app)
            
            refrescoValorActualCuentaFichas(user_id)
           
           
            print(f"Está logueado en {selector} en {environments}")
             # Se inicia el programa principal en un hilo separado
           # Supongamos que shedule_triggers es tu objeto Blueprint de Flask
            #hilo_principal = threading.Thread(target=shedule_triggers.planificar_schedule, 
             #                     args=('1', app, "12:00", "17:00"))

            #hilo_principal.start()
            
            
        except jwt.ExpiredSignatureError:
            flash("El token ha expirado")
        except jwt.InvalidTokenError:
            flash("El token es inválido")
        except Exception as e:
            print('Error inesperado:', e)
            flash('No se pudo iniciar sesión')
            return render_template('errorLogueo.html')
            
 # Redirige a la página de origen según el valor de origin_page
        if origin_page == 'login':
            return render_template('home.html', cuenta=[accountCuenta, user, selector])
        elif origin_page == 'cuentasDeUsusario':
            return render_template('paneles/panelDeControlBroker.html', cuenta=[accountCuenta, user, selector])
        else:
            # Si origin_page no coincide con ninguna ruta conocida, redirige a una página por defecto.
            return render_template('registrarCuentaBroker.html')

    

def inicializar_variables(accountCuenta):
    valores = []  # Inicializar la lista
    
        # Buscar la cuenta asociada a la cuentaCuenta proporcionada
    cuenta = db.session.query(Cuenta).filter(Cuenta.accountCuenta == accountCuenta).first()
    
    if cuenta:
        # Si se encontró la cuenta, obtener el objeto Broker asociado usando su broker_id
        broker = db.session.query(Broker).filter(Broker.id == cuenta.broker_id).first()
        
        if broker:
              # Agregar los valores de api_url y ws_url a la lista 'valores'
            valores = [broker.api_url, broker.ws_url]
            # Hacer algo con el objeto Broker encontrado
            print(f"El broker asociado a la cuenta es: {broker.nombre}")
        else:
            print("No se encontró el broker asociado a la cuenta.")
    else:
        print("No se encontró la cuenta.")

        
    return valores
    
    
   

    pyRofexInicializada = pyRofex
    pyConectionWebSocketInicializada = pyRofex
    pyWsSuscriptionInicializada = pyRofex
    
    

def creaJsonParaConextarseSheetGoogle():
  #  directorioCompleto = os.path.dirname(__file__)
  #  partes_ruta_partes = directorioCompleto.split(os.path.sep)
  #  print(f'Ruta hasta "src": {partes_ruta_partes}')
  #  indice_src = partes_ruta_partes.index('Desktop')
  #  print(f'Ruta hasta "src": {indice_src}')

    # Ruta al archivo de texto plano
    #ruta_archivo_texto = 'C:\\Users\\dpuntillovirtual01\\Desktop\\clavesheet.txt'    
    ruta_archivo_texto = 'C:/Users/mdioli/Desktop/clavesheet.txt'    
  
    print(ruta_archivo_texto)
    # Leer el texto plano desde el archivo
    with open(ruta_archivo_texto, 'r') as archivo_texto:
        texto_plano = archivo_texto.read()

    # Parsear el texto plano a un diccionario
    datos = json.loads(texto_plano)

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
    ruta_archivo_json = os.path.join(ruta_hasta_src, 'strategies', 'pruebasheetpython.json')

    # Escribir el diccionario en el archivo JSON
    with open(ruta_archivo_json, 'w') as archivo_json:
        json.dump(datos, archivo_json, indent=2)

    print(f'Se ha creado el archivo JSON en "{ruta_archivo_json}"')


  

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
        
        





 

  
  

  
 
    




