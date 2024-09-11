from utils.common import Marshmallow, db
from ast import Return
from http.client import UnimplementedFileMode
import websockets
import json
import copy
from pyRofex.components.exceptions import ApiException

from re import template
from socket import socket
import pyRofex

import importlib
# datetime.date.today()
import websocket
import requests
import jwt
import re
import os
import routes.api_externa_conexion.validaInstrumentos as valida
import asyncio

from routes.api_externa_conexion.wsocket import wsocketConexion as conexion
from routes.api_externa_conexion.wsocket import websocketConexionShedule as conexionShedule
from routes.api_externa_conexion.wsocket import SuscripcionDeSheet
from fichasTokens.fichas import refrescoValorActualCuentaFichas
import tokens.token as Token
import routes.instrumentos as inst
from models.instrumento import Instrumento
import routes.api_externa_conexion.cuenta as cuenta
import ssl
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.brokers import Broker
from models.ConexionPyRofex import ConexionPyRofex
from pyRofex.clients.rest_rfx import RestClient
from pyRofex.clients.websocket_rfx import WebSocketClient
from pyRofex.components.globals import environment_config

import automatizacion.programar_trigger as trigger
import automatizacion.shedule_triggers as shedule_triggers
import threading

from utils.db import db
from datetime import datetime, timezone
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
    session,
    make_response
)


get_login = Blueprint('get_login',__name__)

 
user = "{{usuario}}" 
password = "{{contraseña}}" 
account = "{{cuenta}}"  
market_data_recibida = []
reporte_de_ordenes = []


SPREADSHEET_ID_PRUEBA = os.environ.get('SPREADSHEET_ID_PRUEBA')
SPREADSHEET_ID_PRODUCCION = os.environ.get('SPREADSHEET_ID_PRODUCCION')  #drpiBot de produccion
SPREADSHEET_ID_USA= os.environ.get('SPREADSHEET_ID_USA') #de produccion USA
VARIABLE_ACTUALIZAR_SHEET = os.environ.get('VARIABLE_ACTUALIZAR_SHEET') 

#CUENTA_ACTUALIZAR_SHEET = os.environ.get('CUENTA_ACTUALIZAR_SHEET')
#CORREO_E_ACTUALIZAR_SHEET = os.environ.get('CORREO_E_ACTUALIZAR_SHEET')
#ID_USER_ACTUALIZAR_SHEET = 1

CUENTA_ACTUALIZAR_SHEET = os.environ.get('CUENTA_ACTUALIZAR_SHEET_PRODUCCION')
CORREO_E_ACTUALIZAR_SHEET = os.environ.get('CORREO_E_ACTUALIZAR_SHEET_PRODUCCION')
ID_USER_ACTUALIZAR_SHEET = 2
# Días de la semana a los que debe ejecutar la función

DIAS_EJECUCION = ["lunes", "martes", "miercoles", "jueves", "viernes"]

# Diccionario para convertir el nombre del día a su valor numérico
DIAS_SEMANA = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "domingo": 6
}
precios_data = {} #para mdh 0
precios_data_caucion ={}#para caucion
symbols_sheet_valores = []
sheet = None
accountLocalStorage = ""
VariableParaBotonPanico = 0
VariableParaSaldoCta = 0
pyWsSuscriptionInicializada = pyRofex
pyRofexInicializada = pyRofex
ConexionesBroker = {}
luzMDH_funcionando = False
luzThred_funcionando = {'luz': False, 'hora': 0, 'minuto': 0, 'segundo': 0}
sheet_manager = None
valores_mep = {
    'AL30': {'compra': None, 'venta': None},
    'GD30': {'compra': None, 'venta': None}
}

indice_cuentas = {}
autenticado_sheet = False
diccionario_global_sheet = {}
diccionario_global_sheet_intercambio = {}
ya_ejecutado_hilo_panelControl = False
hilo_iniciado_panel_control = {}  # Un diccionario para mantener los hilos por país
hilo_iniciado_estrategia_usuario = {}
estrategias_usuario__endingOperacionBot = {}
hilos_iniciados_shedule = []
ultima_entrada = time.time()
CUSTOM_LEVEL = 25  # Elige un número de nivel adecuado
detener_proceso_automatico_triggers = False  # Bucle hasta que la bandera detener_proceso sea True


marca_de_tiempo_para_leer_sheet = int(datetime.now().timestamp()) * 1000  # Tiempo inicial
VariableParaTiempoLeerSheet = 0  # Variable para guardar el tiempo transcurrido

ContenidoSheet_list = None
api_url = None
ws_url = None
api_url_veta = None
ws_url_veta = None
REMARKET ={"url": "https://api.remarkets.primary.com.ar/",
        "ws": "wss://api.remarkets.primary.com.ar/",
        "ssl": True,
        "proxies": None,
        "rest_client": None,
        "ws_client": None,
        "token": None,
        "user": None,
        "password": None,
        "account": None,
        "initialized": False,
        "proprietary": "PBCP",
        "heartbeat": 30,
        "ssl_opt": None}
envNuevo =  {"url": "https://api.primary.com.ar/",
        "ws": "wss://api.primary.com.ar/",
        "ssl": True,
        "proxies": None,
        "rest_client": None,
        "ws_client": None,
        "user": None,
        "password": None,
        "account": None,
        "initialized": False,
        "proprietary": "api",
        "heartbeat": 30,
        "ssl_opt": None }


  
    # Si la cuenta no existe en el diccionario o si ninguna entrada tiene la cuenta accountCuenta, entra en el if
          

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
            accountCuenta = request.json.get('cuenta')
            simuladoOproduccion = request.json.get('simuladoOproduccion')
            session['selector'] = selector
            session['access_token'] = access_token
            session['rutaDeLogeo'] = rutaDeLogeo
            session['refresh_token'] = refresh_token
            session['correo_electronico'] = correo_electronico
            session['user'] = user
            session['account'] = accountCuenta
            session['simuladoOproduccion'] = simuladoOproduccion
           # print('access_token ',access_token)
           # print('refresh_token ',refresh_token)
           # print('correo_electronico ',correo_electronico)
           
            sobreEscituraPyRofex = True
            if access_token and Token.validar_expiracion_token(access_token=access_token): 
                app = current_app._get_current_object()                    
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                exp_timestamp = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['exp']
          
                if accountCuenta is not None and accountCuenta != '':   
                   cuentas = db.session.query(Cuenta).filter(Cuenta.accountCuenta == accountCuenta).first()
                 
                 
                   passwordCuenta = cuentas.passwordCuenta
                   passwordCuenta = passwordCuenta.decode('utf-8')
                    
                   if  simuladoOproduccion !='':
                        if simuladoOproduccion =='smulado':
                            try:
                                            environment =pyRofexInicializada.Environment.REMARKET
                                            
                                          #  WsEndPoint ='wss://api.remarkets.primary.com.ar/'
                                          #  urlEndPoint= 'https://api.remarkets.primary.com.ar/'
                                          #  pyRofexInicializada._set_environment_parameter("url", urlEndPoint,environment)
                                          #  pyRofexInicializada._set_environment_parameter("ws",WsEndPoint,environment) 
                                          #  pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environment)
                                         
                                            pyRofexInicializada.initialize(user=cuentas.userCuenta,password=passwordCuenta,account=cuentas.accountCuenta,environment=environment )
                                            conexion(app,pyRofexInicializada,selector) 
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
                            exp_date = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                            fecha_actual =   datetime.now()
                            fecha_actual_utc = fecha_actual.astimezone(timezone.utc)
                            endPoint = inicializar_variables(cuentas.accountCuenta)
                            global api_url, ws_url                          
                            api_url = endPoint[0]
                            ws_url = endPoint[1]
                            session['api_url']=endPoint[0]
                            session['ws_url']=endPoint[1]
                            print('###########################################################################')
                            print('#####################LOGEO AUTOMATICO######################################')
                            print('###########################################################################')
                          #  print('88888888888888888888888888888888 fecha_actual ',fecha_actual,'22222222222 exp_date',exp_date)
                            if fecha_actual_utc < exp_date:#hay que corregir el direccionamiento de esto_____
                                
                                
                                if (len(ConexionesBroker) > 0 and accountCuenta in ConexionesBroker):                                    
                                        #if  ConexionesBroker[accountCuenta].get('identificador') == True:
                                            pyRofexInicializada = ConexionesBroker.get(accountCuenta)['pyRofex']
                                            repuesta_operacion = pyRofexInicializada.get_account_report(account=accountCuenta, environment=accountCuenta)
                                            SuscripcionDeSheet(app,pyRofexInicializada,accountCuenta,user_id,selector)
                                     
                                            if repuesta_operacion:
                                                pass
                                else:
                                                                              
                                        conexionShedule(app,Cuenta=Cuenta, account=accountCuenta, idUser=user_id, correo_electronico=correo_electronico, selector=selector)           
                                        pyRofexInicializada = ConexionesBroker[accountCuenta]['pyRofex']
                                        accountCuenta1 = ConexionesBroker[accountCuenta]['cuenta']
                                        refrescoValorActualCuentaFichas(user_id,pyRofexInicializada,accountCuenta1)
                                        ConexionesBroker[accountCuenta]['identificador'] = True
                                        resp = make_response(jsonify({'redirect': 'panel_control_broker'}))
                                        resp.headers['Content-Type'] = 'application/json'
                                        set_access_cookies(resp, access_token)
                                        set_refresh_cookies(resp, refresh_token)
                                        return resp
                                      
                                if rutaDeLogeo != 'Home':  
                                        pyRofexInicializada = ConexionesBroker[accountCuenta]['pyRofex']
                                        accountCuenta1 = ConexionesBroker[accountCuenta]['cuenta']
                                        ####### TEMPORALMENTE COMPROBAR SI SE DESSUCRIBE POR ERROR DE WS#####
                                       # SuscripcionDeSheet(app,pyRofexInicializada,accountCuenta1,user_id)
                                        refrescoValorActualCuentaFichas(user_id,pyRofexInicializada,accountCuenta1)
                                        resp = make_response(jsonify({'redirect': 'panel_control_broker'}))
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
                            else:
                                 
                                  # return render_template('paneles/panelDeControlBroker.html', cuenta=[accountCuenta, user, selector])
                                  # Supongamos que accountCuenta, user, y selector son los datos que quieres enviar
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
                    return render_template('home.html', cuenta=[accountCuenta,user,simuladoOproduccion]) 
            else:
                  return jsonify({'redirect': url_for('panelControl.panel_control')}) 
        finally:
            db.session.close()  # Asegura que la sesión de la base de datos se cierre, incluso si ocurre un error.           
      



@get_login.route("/loginExtCuentaSeleccionadaBroker", methods=['POST'])
def loginExtCuentaSeleccionadaBroker():
   
    try:
      if request.method == 'POST':
        origin_page = request.form.get('origin_page')
        user = request.form.get('usuario')
        password = request.form.get('contraseña')
        accountCuenta = request.form.get('cuenta')
        access_token = request.form.get('access_token')       
        src_directory1 = os.getcwd()#busca directorio raiz src o app 
        logs_file_path = os.path.join(src_directory1, 'logs.log')
        
        global ConexionesBroker,api_url, ws_url  
       
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
       
                if origin_page == 'login':
                    selector = request.form.get('environment')
                    print('selector ',selector)
                    
                else: 
                    selector = request.form.get('selectorEnvironment')
                    print('selector ',selector)
                
                
            
                if not selector or not user or not password or not accountCuenta:
                    flash('Falta información requerida')
                    return redirect(url_for('autenticacion.index'))

            
            
                app = current_app._get_current_object() 
                #creaJsonParaConextarseSheetGoogle()
                if selector == 'simulado':
                    ambiente = copy.deepcopy(REMARKET)
                    pyRofexInicializada._add_environment_config(enumCuenta=accountCuenta,env=ambiente)
                    environments = accountCuenta                                        
                    pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments) 
                    try:   
                        
                        pyRofexInicializada.initialize(user=user, password=password, account=accountCuenta, environment=environments)                       
                    except ApiException as e:
                        print(f"ApiException occurred: {e}")
                        flash("Cuenta incorrecta: password o usuario incorrecto. Quite la cuenta")
                        return render_template("cuentas/registrarCuentaBroker.html") 
                    ConexionesBroker[accountCuenta] = {'pyRofex': pyRofexInicializada, 'cuenta': accountCuenta, 'identificador': False}
                                            
                else:
                    
                        # Configurar para el entorno LIVE              
                        endPoint = inicializar_variables(accountCuenta)
                    # app.logger.info(endPoint)
                    
                        api_url = endPoint[0]
                        ws_url = endPoint[1]
                        
                        
                    
                        sobreEscituraPyRofex = True
                            
                    
                    # Verificar si la cuenta con el valor accountCuenta no existe en el diccionario
                        if (not ConexionesBroker or 
                            all(entry['cuenta'] != accountCuenta for entry in ConexionesBroker.values()) or 
                            (accountCuenta in ConexionesBroker and ConexionesBroker[accountCuenta].get('identificador') == False)):
    
    
                                #pyRofexInicializada = pyRofex
                                if sobreEscituraPyRofex == True:
                                    ambiente = copy.deepcopy(envNuevo)
                                    pyRofexInicializada._add_environment_config(enumCuenta=accountCuenta,env=ambiente)
                                    environments = accountCuenta
                                else:    
                                    if selector == 'simulado':
                                        environments = pyRofexInicializada.Environment.REMARKET
                                    else:                                    
                                        environments = pyRofexInicializada.Environment.LIVE
                                
                                pyRofexInicializada._set_environment_parameter("url", api_url, environments)                          
                                pyRofexInicializada._set_environment_parameter("ws", ws_url, environments)                            
                                pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments)    
                                pyRofexInicializada.initialize(user=user, password=password, account=accountCuenta, environment=environments)                       
                            #  restClientEnv = RestClient(environments)
                            #  wsClientEnv = WebSocketClient(environments)
                            
                                ConexionesBroker[accountCuenta] = {'pyRofex': pyRofexInicializada, 'cuenta': accountCuenta, 'identificador': False}
                                #ConexionesBroker[accountCuenta]['identificador'] = True
                
                            
                while True:
                            try:  
                                for elemento in ConexionesBroker:
                                    print("Variable agregada:", elemento)
                                    cuenta = ConexionesBroker[elemento]['cuenta']
                            
                                    if accountCuenta ==  cuenta and ConexionesBroker[elemento]['identificador'] == False:
                                    
                    
                                        conexion(app,ConexionesBroker[elemento]['pyRofex'], ConexionesBroker[elemento]['cuenta'],user_id,selector)
                        
                                        refrescoValorActualCuentaFichas(user_id,ConexionesBroker[elemento]['pyRofex'], ConexionesBroker[elemento]['cuenta'])
                        
                        
                                        print(f"Está logueado en {selector} en {environments}")
                                        ConexionesBroker[accountCuenta]['identificador'] = True
                                        break  # Salir del bucle for si se completa correctamente
                                    else:               
                                        pass
                                    
                            except RuntimeError:
                                    # Manejar la excepción aquí
                                    print("Se produjo un RuntimeError durante la iteración. Reiniciando el bucle...")
                                    continue  # Volver al inicio del bucle while para intentar de nuevo    
                                # Si llegamos aquí, significa que el bucle for se completó sin excepciones
                            break  # Salir del bucle while ya que se completó correctamente
    # Redirige a la página de origen según el valor de origin_page
                if origin_page == 'login':
                    return render_template('home.html', cuenta=[accountCuenta, user, selector])
                elif origin_page == 'cuentasDeUsusario':
                        return render_template('paneles/panelDeControlBroker.html', cuenta=[accountCuenta, user, selector])
                else:
                        # Si origin_page no coincide con ninguna ruta conocida, redirige a una página por defecto.
                        return render_template('registrarCuentaBroker.html')

    except jwt.ExpiredSignatureError:
        flash("El token ha expirado")
    except jwt.InvalidTokenError:
        flash("El token es inválido")
    except Exception as e:
         print('Error inesperado:', e)
         flash('No se pudo iniciar sesión')
         return render_template('notificaciones/errorLogueo.html')




def conexion_existente(app,accountCuenta,correo_electronico,selector,user_id):
    if len(precios_data)> 0:       
        return False
    else:        
        with app.app_context():
            conexionShedule(current_app, Cuenta=Cuenta, account=accountCuenta, idUser=user_id, correo_electronico=correo_electronico, selector=selector)           
        return True 
        
def buscar_conexion(client_id, cuenta):
    for key, websocket in ConexionesBroker.items():
        print(f"Comparando clave: (client_id={key[0]}, cuenta={key[1]})")  # Print para mostrar la clave que está siendo comparada
        if key[:2] == (client_id, cuenta):
            print(f"Comparando clave: (client_id={key[0]}, cuenta={key[1]})")
            resumenCuenta = websocket.get_account_report(account=cuenta)
            return websocket  # Retorna la conexión si se encuentra

    return None  # Retorna None si no se encuentra ninguna conexión

def inicializar_variables(accountCuenta):
    valores = []  # Inicializar la lista
    
        # Buscar la cuenta asociada a la cuentaCuenta proporcionada
    cuenta = db.session.query(Cuenta).filter(Cuenta.accountCuenta == accountCuenta).first()
    
    if cuenta:
        # Si se encontró la cuenta, obtener el objeto Broker asociado usando su broker_id
        broker = db.session.query(Broker).filter(Broker.id == cuenta.broker_id).first()
        db.session.close()
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
        
        





 

  
  

  
 
    




