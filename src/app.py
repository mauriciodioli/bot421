#from re import template

from flask import (Flask,Blueprint,Response,make_response,render_template,request,redirect,url_for,flash,jsonify)
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_identity)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import DATABASE_CONNECTION_URI
from sqlalchemy.exc import OperationalError
# Importar create_engine y NullPool
import logging
import os
from log.logRegister import generate_logs

from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import QueuePool
######################zona de estrategias de usuarios####################
from strategies.estrategiasUsuarios.Bull_Market_351653_001 import Bull_Market_351653_001
from strategies.estrategiasUsuarios.Bull_Market_10861_001 import Bull_Market_10861_001
########################################################################
from models.creaTablas import crea_tablas_DB
from sistemaDePagos.payment_page import payment_page
from sistemaDePagos.success_failure import success_failure
from sistemaDePagos.crearPlanes import crearPlanes
from sistemaDePagos.createOrden import createOrden
from sistemaDePagos.updatePlanes import updatePlanes
from sistemaDePagos.deletePlanes import deletePlanes
from sistemaDePagos.createSuscripcion import createSuscripcion
from sistemaDePagos.tarjetaUsuario import tarjetaUsuario
from sistemaDePagos.deleteSuscripcion import deleteSuscripcion
from sistemaDePagos.carrucelPromocionOfertas import carrucelPromocionOfertas
from sistemaDePagos.carrucelPromocionSuscripciones import carrucelPromocionSuscripciones
from productosComerciales.descipcionProductos import descrpcionProductos
from productosComerciales.planes import planes
from productosComerciales.suscripcionPlanUsuario import suscripcionPlanUsuario
from productosComerciales.promociones.promociones import promociones

from Tests.test_order_report_handler import test_order_report_handler


from social.telegram.telegram import telegram

from herramientasAdmin.accionesSheet import accionesSheet
from herramientasAdmin.runScript import runScript

from strategies.estrategias import estrategias
from strategies.estrategiaSheetWS import estrategiaSheetWS

from strategies.datoSheet import datoSheet
from strategies.Experimental.FuncionesBasicas01 import FuncionesBasicas01
from strategies.arbitraje_001 import arbitraje_001
from strategies.utils.testWS import testWS
from strategies.gestion_estrategias.abm_estrategias import abm_estrategias
from strategies.gestion_estrategias.unidad_trader import unidad_trader
from strategies.caucionador.caucion import caucion

from tokens.token import token
import tokens.token as Token

from routes.instrumentos import instrumentos
from routes.instrumentosGet import instrumentosGet
from routes.api_externa_conexion.get_login import get_login
from routes.api_externa_conexion.comprar import comprar
from routes.api_externa_conexion.operaciones import operaciones
from routes.api_externa_conexion.validaInstrumentos import validaInstrumentos
from routes.api_externa_conexion.cuenta import cuenta

from routes.api_externa_conexion.wsocket import wsocket
from routes.suscripciones import suscripciones

from cuentas.cuentaUsuarioBroker import cuentas
from cuentas.endPointBrokers import endPointBrokers

from fichasTokens.fichas import fichas

from usuarios.autenticacion import autenticacion
from usuarios.registrarUsuario import registrarUsuario
from usuarios.usuario import usuario
from usuarios.cambiarContrasenaUsuarioSistema import cambiarContrasenaUsuarioSistema

from social.imagenes.imagenesOperaciones import imagenesOperaciones
from social.media_e_mail import media_e_mail

from comunicacion.contacto import contacto
from comunicacion.newsLetter import newsLetter

from panelControlBroker.panelControl import panelControl
from panelControl.pcEstrategiaUs import pcEtrategiaUs

from automatizacion.programar_trigger import programar_trigger 
from automatizacion.shedule_triggers import shedule_triggers
import automatizacion.programar_trigger as trigger
import subprocess

from models.usuario import Usuario
from models.triggerEstrategia import triggerEstrategia
from models.strategy import strategy
from models.orden import orden
from models.ficha import ficha
from models.trazaFicha import trazaFicha
from models.operacion import operacion
from models.brokers import brokers
from models.operacionHF import operacionHF
from models.logs import logs
from models.creaTablas import creaTabla
from models.operacionEstrategia import operacionEstrategia

from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
import schedule
import time
from sqlalchemy.pool import Pool

from routes.api_externa_conexion.get_login import CUSTOM_LEVEL

# desde aqui se llama la aplicacion al inicio
#app = Flask(__name__)

 # Inicia los workers de Celery
#celery_app.start()
app = Flask(__name__, static_folder='static')


# Configurar el manejo de errores para la aplicación
login_manager = LoginManager(app)

# Configurar CORS
CORS(app)
# Configurar el nivel de logging de la aplicación Flask
app.logger.setLevel(logging.DEBUG)
# Definir el nuevo nivel de registro
CUSTOM_LEVEL = 25  # Elige un número de nivel adecuado
logging.addLevelName(CUSTOM_LEVEL, "CUSTOM")
# Configurar la generación de logs para la aplicación
logging.basicConfig(level=logging.DEBUG)  # Configura el nivel de log a DEBUG


# Configurar un formateador para los logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Obtener la ruta al directorio 'src' de tu proyecto
src_directory = os.path.dirname(os.path.abspath(__file__))
#if os.path.exists(src_directory):
    # Eliminar el archivo
#    os.remove(src_directory)
# Ruta al archivo de logs dentro del directorio 'src'
logs_file_path = os.path.join(src_directory, 'logs.log')

# Crear un manejador de logs que escriba en el archivo 'logs.log' en el directorio 'src'
file_handler = logging.FileHandler(logs_file_path, encoding='utf-8')
# Crear un manejador de logs que escriba a `stdout`
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)


app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.debug('Debugging message: Configuración de logger completada.')
app.logger.info('Este es un mensaje de info.')
app.logger.warning('Este es un mensaje de advertencia.')
app.logger.error('Este es un mensaje de error.')
app.logger.critical('Este es un mensaje crítico.')
# Configura el manejo de autenticación JWT
app.config['JWT_SECRET_KEY'] = '621289'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/refresh/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
jwt = JWTManager(app)


# Configura el blueprint de Google OAuth
blueprint = make_google_blueprint(client_id='client_id',
                                   client_secret='client_secret',
                                   scope=['profile', 'email'])
app.register_blueprint(blueprint, url_prefix='/login')
#####################zona blueprin de usuarios##############
app.register_blueprint(Bull_Market_351653_001)
app.register_blueprint(Bull_Market_10861_001)
############################################################

app.register_blueprint(logs)
app.register_blueprint(payment_page)
app.register_blueprint(success_failure)
app.register_blueprint(crearPlanes)
app.register_blueprint(createOrden)
app.register_blueprint(createSuscripcion)
app.register_blueprint(updatePlanes)

app.register_blueprint(deletePlanes)
app.register_blueprint(descrpcionProductos)
app.register_blueprint(planes)
app.register_blueprint(suscripcionPlanUsuario)
app.register_blueprint(deleteSuscripcion)
app.register_blueprint(tarjetaUsuario)
app.register_blueprint(creaTabla)
app.register_blueprint(carrucelPromocionSuscripciones)
app.register_blueprint(carrucelPromocionOfertas)
app.register_blueprint(promociones)
app.register_blueprint(token)
app.register_blueprint(instrumentos)
app.register_blueprint(instrumentosGet)
app.register_blueprint(get_login)
app.register_blueprint(cuenta)
app.register_blueprint(cuentas)
app.register_blueprint(endPointBrokers)
app.register_blueprint(brokers)
app.register_blueprint(orden)
app.register_blueprint(comprar)
app.register_blueprint(operacion)
app.register_blueprint(operaciones)
app.register_blueprint(operacionHF)
app.register_blueprint(validaInstrumentos)
app.register_blueprint(wsocket)
app.register_blueprint(suscripciones)
app.register_blueprint(abm_estrategias)
app.register_blueprint(unidad_trader)
app.register_blueprint(strategy)
app.register_blueprint(estrategias)
app.register_blueprint(estrategiaSheetWS)
app.register_blueprint(datoSheet)
app.register_blueprint(autenticacion)
app.register_blueprint(registrarUsuario)
app.register_blueprint(usuario)
app.register_blueprint(cambiarContrasenaUsuarioSistema)
app.register_blueprint(testWS)
app.register_blueprint(imagenesOperaciones)
app.register_blueprint(media_e_mail)
app.register_blueprint(panelControl)
app.register_blueprint(pcEtrategiaUs)
app.register_blueprint(FuncionesBasicas01)
app.register_blueprint(ficha)
app.register_blueprint(trazaFicha)
app.register_blueprint(fichas)
app.register_blueprint(arbitraje_001)
app.register_blueprint(programar_trigger)
app.register_blueprint(shedule_triggers)
app.register_blueprint(contacto)
app.register_blueprint(newsLetter)
app.register_blueprint(accionesSheet)
app.register_blueprint(runScript)
app.register_blueprint(telegram)
app.register_blueprint(operacionEstrategia)
app.register_blueprint(caucion)

app.register_blueprint(test_order_report_handler)


print(DATABASE_CONNECTION_URI)


# Configuración de Flask
app.secret_key = '*0984632'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Parámetros de configuración
app.config['SQLALCHEMY_POOL_SIZE'] = 1000  # Tamaño máximo del pool
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 50  # Conexiones adicionales permitidas

# Configuración inicial
INITIAL_POOL_SIZE = 2
INITIAL_MAX_OVERFLOW = 3
MAX_USERS_INCREMENT = 3
POOL_SIZE_INCREMENT = 2
MAX_USERS_AMPLIFICATION = 5
AMPLIFICATION_INCREMENT = 3
POOL_REDUCTION_THRESHOLD = 0.5  # Reducción del pool cuando el 50% de las conexiones están inactivas
MAX_CONNECTIONS = 2  # Número máximo de conexiones activas permitidas
INACTIVITY_TIMEOUT = 5  # Tiempo máximo de inactividad en segundos

# Crear el motor de SQLAlchemy
engine = create_engine(
    DATABASE_CONNECTION_URI,
    poolclass=QueuePool,
    pool_size=INITIAL_POOL_SIZE,
    max_overflow=INITIAL_MAX_OVERFLOW,
    pool_timeout=30,  # Tiempo máximo en segundos que se esperará por una conexión
    pool_recycle=3600
)



db = SQLAlchemy(app)
db.init_app(app)
db.session.configure(bind=engine)

ma = Marshmallow(app)


# Contadores y estructuras para controlar las conexiones
active_connections = set()
connection_times = {}
user_count = 0
total_connections = 0

def adjust_pool_size():
    """Ajusta el tamaño del pool basado en el número de usuarios y conexiones activas."""
    global total_connections, user_count
    current_pool_size = engine.pool.size()
    current_max_overflow = engine.pool._max_overflow

    # Crear 2 conexiones cada 3 usuarios
    if user_count % MAX_USERS_INCREMENT == 0:
        new_pool_size = current_pool_size + POOL_SIZE_INCREMENT
        engine.pool._set_pool_size(new_pool_size)

    # Ampliar el pool en 3 por cada 5 usuarios
    if user_count % MAX_USERS_AMPLIFICATION == 0:
        new_max_overflow = current_max_overflow + AMPLIFICATION_INCREMENT
        engine.pool._set_max_overflow(new_max_overflow)

    # Reducir el tamaño del pool basado en conexiones inactivas
    if total_connections > 0:
        active_ratio = len(active_connections) / total_connections
        if active_ratio < POOL_REDUCTION_THRESHOLD:
            new_pool_size = max(INITIAL_POOL_SIZE, current_pool_size - POOL_SIZE_INCREMENT)
            engine.pool._set_pool_size(new_pool_size)
            app.logger.info(f"Reduciendo el tamaño del pool a {new_pool_size}. Conexiones activas: {len(active_connections)}")

@event.listens_for(engine, 'connect')
def on_connect(dbapi_connection, connection_record):
    """Incrementar el contador de usuarios y ajustar el pool si es necesario."""
    global user_count, total_connections, active_connections
    user_count += 1
    total_connections += 1
    connection_key = id(connection_record)
    active_connections.add(connection_key)
    connection_times[connection_key] = time.time()
    adjust_pool_size()
    app.logger.info(f"Usuario conectado. Total usuarios: {user_count}")
    print("Evento 'connect' disparado.")
    
@event.listens_for(engine, 'checkin')
def on_checkin(dbapi_connection, connection_record):
    """Asegura que el número de conexiones no exceda el máximo al devolver conexiones al pool."""
    global active_connections, connection_times    
    connection_key = id(connection_record)
    if connection_key in active_connections:
        active_connections.remove(connection_key)
    connection_times[connection_key] = time.time()  # Actualizar tiempo de inactividad
    app.logger.info(f"Conexión verificada. Total conexiones activas: {len(active_connections)}")
    print("Evento 'checkin' disparado.")
    
    
@event.listens_for(engine, 'checkout')
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Decrementar el contador de usuarios cuando una conexión se libera y manejar conexiones inactivas."""
    global user_count, active_connections, connection_times

    # Decrementar el contador de usuarios
    user_count -= 1
    if user_count < 0:
        user_count = 0
    app.logger.info(f"Usuario desconectado. Total usuarios: {user_count}")

    # Cerrar conexiones que han estado inactivas durante un período prolongado
    current_time = time.time()
    connections_to_close = [key for key, last_active in connection_times.items()
                            if current_time - last_active > INACTIVITY_TIMEOUT]

    for conn_key in connections_to_close:
        if conn_key in active_connections:
            # Encontrar la conexión en el conjunto de conexiones activas
            connection = next((conn for conn in active_connections if id(conn) == conn_key), None)
            if connection:
                connection.close()  # Cerrar la conexión
                active_connections.remove(conn_key)  # Eliminar del conjunto de conexiones activas
                connection_times.pop(conn_key, None)  # Eliminar del diccionario de tiempos
                app.logger.info(f"Cerrando conexión inactiva: {conn_key}")

    # Crear una nueva conexión si no hay conexiones activas
    if len(active_connections) == 0:
        app.logger.info("No hay conexiones activas. Creando una nueva conexión...")
        try:
           
            # Crear una nueva sesión y forzar la creación de una nueva conexión
            pass
            #db.session.execute('SELECT 1')  # Consulta trivial para crear una conexión
        except Exception as e:
            app.logger.error(f"Error al crear nueva conexión: {e}")
            # Manejar el error si es necesario
# Registrar el evento de desconexión
    app.logger.info(f"Usuario desconectado. Total usuarios: {user_count}")


@event.listens_for(engine.pool, "connect")
def log_connection_info(dbapi_connection, connection_record):
    """Registra eventos de conexión y asegura que el número máximo de conexiones no se exceda."""
    global active_connections, connection_times
    connection_key = id(connection_record)
    connection_times[connection_key] = time.time()
    active_connections.add(connection_key)
    app.logger.info(f"Conexión establecida. Total conexiones activas: {len(active_connections)}")

    if len(active_connections) > MAX_CONNECTIONS:
        # Cerrar conexiones inactivas si el límite se excede
        current_time = time.time()
        connections_to_close = [key for key, last_active in connection_times.items()
                                if current_time - last_active > INACTIVITY_TIMEOUT]
        
        for conn_key in connections_to_close:
            if len(active_connections) <= MAX_CONNECTIONS:
                break
            if conn_key in active_connections:
                app.logger.info(f"Cerrando conexión inactiva: {conn_key}")
                connection = next((conn for conn in active_connections if id(conn) == conn_key), None)
                if connection:
                    connection.close()  # Cerrar la conexión
                    active_connections.remove(conn_key)  # Eliminar del conjunto de conexiones activas
                    connection_times.pop(conn_key, None)  # Eliminar del diccionario de tiempos

# Registro explícito de los eventos (líneas añadidas)
event.listen(engine, 'connect', on_connect)
event.listen(engine, 'checkin', on_checkin)
event.listen(engine, 'checkout', on_checkout)
event.listen(engine.pool, 'connect', log_connection_info)

# Definir una función de registro personalizada para el nuevo nivel
def custom_log(self, message, *args, **kwargs):
    if self.isEnabledFor(CUSTOM_LEVEL):
        self._log(CUSTOM_LEVEL, message, args, **kwargs)

# Agregar la función de registro personalizada al logger de la aplicación Flask
app.logger.custom = custom_log
# Programar la tarea para que se ejecute a una hora específica
@app.route('/logs')
def logs():
    print("FUNC_ app.py Se está accediendo a la ruta /logs")
    return Response(generate_logs(), mimetype='text/event-stream')



@app.route("/send_local_storage", methods=["POST"])
def send_local_storage():
    data = request.json
    if data:
        ruta_de_logeo = data.get('rutaDeLogeo')
        refresh_token = data.get('refresh_token')
        access_token = data.get('access_token')
        correo_electronico = data.get('correo_electronico')
        cuenta = data.get('cuenta')
        usuario = data.get('usuario')
        simuladoOproduccion = data.get('simuladoOproduccion')
        client_ip = request.remote_addr  # Obtiene la IP del cliente
        data['client_ip'] = client_ip

        if access_token and Token.validar_expiracion_token(access_token=access_token):
            if correo_electronico:
              #  app.logger.info(client_ip)
                app.logger.info(correo_electronico)  
                redirect_route = 'home'
            else:
                app.logger.info('____INTENTO ENTRAR____')  
                app.logger.info(client_ip)
                app.logger.info(correo_electronico)  
                redirect_route = 'index'    
        else:
            app.logger.info('____INTENTO ENTRAR____') 
            app.logger.info(client_ip) 
            app.logger.info(correo_electronico)  
            redirect_route = 'index'
        
        # Devuelve una respuesta JSON con la ruta
        return jsonify(success=True, ruta=redirect_route)
    else:
        return jsonify(success=False, message="No data received")


@app.route("/")
def entrada():  
      # Llama a la tarea Celery
    #trigger.llama_tarea_cada_24_horas_estrategias('1',app)
    #crea_tablas_DB()
    
    return  render_template("entrada.html")

@login_manager.user_loader
def load_user(user_id):
    try:
        # Realiza la consulta para obtener el usuario
        user = db.session.query(Usuario).filter_by(id=user_id).first()
        return user
    
    except OperationalError as e:
        # Manejar el error de conexión y reconfigurar si es necesario
        app.logger.error(f"Error de conexión a la base de datos: {e}")
        
        # Volver a crear la sesión
      
        db.session.execute('SELECT 1')  # Consulta trivial para verificar la conexión   
        # Reintenta la consulta después de reconfigurar
        try:
            # Reintenta la consulta después de reconfigurar
            user = db.session.query(Usuario).filter_by(id=user_id).first()
            return user
        except OperationalError as e:
            app.logger.error(f"Error de conexión a la base de datos tras reintentar: {e}")
            return None
# Make sure this we are executing this file
if __name__ == "__main__":
   # app.run()
    #app.run(host='0.0.0.0', port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=False)
   

    # Ciclo para ejecutar las tareas programadas
  
   # while True:
   #     schedule.run_pending()
   #     print('__________________________________________________')
   #     print('entra en el planificador')
   #     time.sleep(3)
   
   
   
   
   
