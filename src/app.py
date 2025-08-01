from flask import (Flask,Blueprint,current_app,Response,make_response,render_template,request,redirect,url_for,flash,jsonify)
from flask_jwt_extended import (JWTManager,decode_token, jwt_required, create_access_token,get_jwt_identity)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import DATABASE_CONNECTION_URI
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import SQLAlchemyError

from utils.db_session import get_db_session 
# Importar create_engine y NullPool
import logging
import datetime
import os
import jwt
from datetime import timedelta
from log.logRegister import generate_logs
from log.logRegister import logRegister
from models.logs import Logs
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
from sistemaDePagos.pagoPedidos import pagoPedidos
from sistemaDePagos.carrucelPromocionSuscripciones import carrucelPromocionSuscripciones
from sistemaDePagos.payPal import payPal

from productosComerciales.descipcionProductos import descrpcionProductos
from productosComerciales.planes import planes
from productosComerciales.suscripcionPlanUsuario import suscripcionPlanUsuario
from productosComerciales.promociones.promociones import promociones
from productosComerciales.pedidos.pedidos import pedidos
from productosComerciales.pedidos.ventasProductosComerciales import ventasProductosComerciales



from Tests.test_order_report_handler import test_order_report_handler
from Tests.test_2_order_report_handler import test_2_order_report_handler
from Tests.test_ejecutarHiloPanelControl import test_ejecutarHiloPanelControl




from social.telegram.telegram import telegram
from social.videosYtube.videosYtube import videosYtube
from social.chats.chat import chat
from social.buckets.bucketGoog import bucketGoog

from herramientasAdmin.accionesSheet import accionesSheet
from herramientasAdmin.runScript import runScript
from herramientasAdmin.accionesTriggers import accionesTriggers
from herramientasAdmin.administracion import administracion

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
from usuarios.registrarUsuarioRegion import registrarUsuarioRegion
from usuarios.usuarioUbicacionC import usuarioUbicacionC

from social.imagenes.imagenesOperaciones import imagenesOperaciones
from social.media_e_mail import media_e_mail
from social.media.publicaciones import publicaciones
from social.media.cargarPdf import cargarPdf
from social.media.muestraPublicacionesEnHome import muestraPublicacionesEnHome
from social.media.muestraPublicacionesEnAmbitos import muestraPublicacionesEnAmbitos
from social.media.ambitos.ambito import ambito
from social.media.ambitos.ambitosCategorias import ambitosCategorias
from social.media.consultaPublicaciones import consultaPublicaciones
from social.media.creaPublicacionesPartes import creaPublicacionesPartes
from turing.testTuring import testTuring
from turing.turingUser import turingUser
from turing.turingRespuestas import turingRespuestas
from turing.triviaTuring import triviaTuring
from turing.conectionSheet import conectionSheet

from social.dpis.dpi import dpi

from comunicacion.contacto import contacto
from comunicacion.newsLetter import newsLetter

from panelControlBroker.panelControl import panelControl
from panelControl.pcEstrategiaUs import pcEtrategiaUs

from automatizacion.programar_trigger import programar_trigger 
from automatizacion.shedule_triggers import shedule_triggers
from automatizacion.cargaAutomatica import cargaAutomatica
import automatizacion.programar_trigger as trigger
import subprocess

from models.usuario import Usuario
from models.usuarioRegion import usuarioRegion
from models.usuarioUbicacion import usuarioUbicacion
from models.usuarioPublicacionUbicacion import usuarioPublicacionUbicacion
from models.triggerEstrategia import triggerEstrategia
from models.strategy import strategy
from models.orden import orden
from models.ficha import ficha
from models.trazaFicha import trazaFicha
from models.operacion import operacion
from models.brokers import brokers
from models.codigoPostal import codigoPostal
from models.operacionHF import operacionHF
from models.logs import logs
from models.creaTablas import creaTabla
from models.operacionEstrategia import operacionEstrategia
from models.servidores.servidorAws import servidorAws
from models.publicaciones.ambitos import ambitos
from models.publicaciones.ambito_usuario import ambito_usuario
from models.publicaciones.ambitoCategoria import ambitoCategoria
from models.publicaciones.ambitoCategoriaRelation import ambitoCategoriaRelation
from models.publicaciones.ambito_codigo_postal import ambito_codigo_postal
from models.publicaciones.categoriaPublicacion import categoriaPublicacion
from models.publicaciones.publicacionCodigoPostal import publicacionCodigoPostal
from models.turing.preguntaUsuario import preguntaUsuario
from models.turing.preguntas import preguntas
from models.turing.respuesta import respuesta
from models.turing.respuestaUsuario import respuestaUsuario
from models.turing.trivia import trivia
from models.turing.testTuringUser import testTuringUser
from models.pedidos.pedido import pedido
from models.pedidos.pedidoEntregaPago import pedidoEntregaPago

from aplicaciones.calculadora import calculadora


from Tests.test_procesar_estado_final import test_procesar_estado_final

from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
import schedule
import time
from sqlalchemy.pool import Pool
from tokens.token import generar_nuevo_token_acceso_vencido

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
#app.logger.addHandler(console_handler)
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
app.config['MAX_CONTENT_LENGTH'] =  100 * 1024 * 1024  # 100 MB

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
app.register_blueprint(logRegister)
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
app.register_blueprint(codigoPostal)
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
app.register_blueprint(usuarioRegion)
app.register_blueprint(registrarUsuarioRegion)
app.register_blueprint(usuarioUbicacion)
app.register_blueprint(usuarioUbicacionC)
app.register_blueprint(usuarioPublicacionUbicacion)
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
app.register_blueprint(administracion)
app.register_blueprint(contacto)
app.register_blueprint(newsLetter)
app.register_blueprint(accionesSheet)
app.register_blueprint(runScript)
app.register_blueprint(accionesTriggers)
app.register_blueprint(telegram)
app.register_blueprint(chat)
app.register_blueprint(operacionEstrategia)
app.register_blueprint(caucion)
app.register_blueprint(publicaciones)
app.register_blueprint(cargarPdf)
app.register_blueprint(ambitos)
app.register_blueprint(ambito)
app.register_blueprint(ambito_usuario)
app.register_blueprint(ambitoCategoria)
app.register_blueprint(ambitoCategoriaRelation)
app.register_blueprint(ambito_codigo_postal)
app.register_blueprint(categoriaPublicacion)
app.register_blueprint(ambitosCategorias)
app.register_blueprint(publicacionCodigoPostal)
app.register_blueprint(muestraPublicacionesEnHome)
app.register_blueprint(muestraPublicacionesEnAmbitos)
app.register_blueprint(consultaPublicaciones)
app.register_blueprint(creaPublicacionesPartes)
app.register_blueprint(pedido)
app.register_blueprint(pedidos)
app.register_blueprint(pedidoEntregaPago)
app.register_blueprint(pagoPedidos)
app.register_blueprint(payPal)

app.register_blueprint(ventasProductosComerciales)
app.register_blueprint(servidorAws)
app.register_blueprint(dpi)
app.register_blueprint(videosYtube)
app.register_blueprint(calculadora)
app.register_blueprint(cargaAutomatica)

app.register_blueprint(testTuringUser)
app.register_blueprint(testTuring)
app.register_blueprint(preguntas)
app.register_blueprint(preguntaUsuario)
app.register_blueprint(respuesta)
app.register_blueprint(respuestaUsuario)
app.register_blueprint(trivia)
app.register_blueprint(turingUser)
app.register_blueprint(turingRespuestas)
app.register_blueprint(triviaTuring)
app.register_blueprint(conectionSheet)




app.register_blueprint(test_order_report_handler)
app.register_blueprint(test_2_order_report_handler)
app.register_blueprint(test_ejecutarHiloPanelControl)
app.register_blueprint(bucketGoog)






print(DATABASE_CONNECTION_URI)


# Configuración de Flask
app.secret_key = '*0984632'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 10  # Conexiones adicionales permitidas

# Configuración inicial
INITIAL_POOL_SIZE = 2
INITIAL_MAX_OVERFLOW = 5
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
    max_overflow=INITIAL_MAX_OVERFLOW,
    pool_timeout=0.5,  # Tiempo máximo en segundos que se esperará por una conexión
    pool_recycle=3600,
    pool_pre_ping=True 
    
)
  


db = SQLAlchemy(app)
db.init_app(app)
#session.configure(bind=engine)

ma = Marshmallow(app)


# Contadores y estructuras para controlar las conexiones
active_connections = set()
connection_times = {}
user_count = 0
total_connections = 0



# Escuchar cuando se abre una nueva conexión
@event.listens_for(Pool, "connect")
def connect_listener(dbapi_connection, connection_record):
    connection_key = id(connection_record)
    #print("connect_listener Nueva conexión abierta. Conexión ID:", connection_key)
    
    # Registrar la nueva conexión
    active_connections.add(connection_key)
    connection_times[connection_key] = time.time()
  #  app.logger.info(f"connect_listener Conexión abierta. Total conexiones activas: {len(active_connections)}")
  #  app.logger.info(f"connect_listener Conexión abierta. Total conexiones activas: {len(connection_times)}")

# Escuchar cuando se obtiene una conexión del pool
@event.listens_for(Pool, "checkout")
def checkout_listener(dbapi_connection, connection_record,connection_proxy):
    connection_key = id(connection_record)
    #print("checkout_listener Conexión obtenida del pool. Conexión ID:", connection_key)
    
    # Actualizar el tiempo de última actividad
    if connection_key in connection_times:
        connection_times[connection_key] = time.time()
    else:
        pass
   # app.logger.warning(f"checkout_listener Clave de conexión no encontrada en connection_times: {connection_key}")

@event.listens_for(db.engine, "close")
def close_listener(dbapi_connection, connection_record):
    connection_key = id(connection_record)
      # Cerrar la conexión inmediatamente después de abrirla
  #  print(f"Cerrando la conexión inmediatamente. Conexión ID: {connection_key}")
    dbapi_connection.close()  # Cerrar la conexión en este punto
    if connection_key in active_connections:
        active_connections.remove(connection_key)  # Removerla del conjunto de conexiones activas
        connection_times.pop(connection_key, None)  # Eliminar el tiempo asociado
   #     app.logger.info(f"close_listener Conexión cerrada. ID: {connection_key}. Total conexiones activas: {len(active_connections)}")

@app.teardown_appcontext
def teardown_db(exception):
    with get_db_session() as session:
        # Cierra la sesión de la base de datos y libera recursos
        session.remove()
# Escuchar cuando se devuelve una conexión al pool
@event.listens_for(Pool, "checkin")
def checkin_listener(dbapi_connection, connection_record):
    connection_key = id(connection_record)
    #print("Conexión devuelta al pool. Conexión ID:", connection_key)
    
    # Verificar y eliminar la clave de active_connections si existe
    if connection_key in active_connections:
        active_connections.remove(connection_key)
    else:
        pass
        
    #app.logger.warning(f"Clave de conexión no encontrada en active_connections: {connection_key}")
    
    # Verificar y eliminar la clave de connection_times si existe
    if connection_key in connection_times:
        connection_times.pop(connection_key, None)
    else:
        pass
        #app.logger.warning(f"Clave de conexión no encontrada en connection_times: {connection_key}")
    
    #app.logger.info(f"Conexión devuelta al pool. Total conexiones activas: {len(active_connections)}")
    
    # Manejar el número de conexiones si es necesario
    if len(active_connections) > MAX_CONNECTIONS:
        current_time = time.time()
        connections_to_close = [key for key, last_active in connection_times.items()
                                if current_time - last_active > INACTIVITY_TIMEOUT]
        
        for conn_key in connections_to_close:
            if len(active_connections) <= MAX_CONNECTIONS:
                break
            if conn_key in active_connections:
                app.logger.info(f"Cerrando conexión inactiva: {conn_key}")
                # Aquí simplemente removemos el registro, no la conexión real
                active_connections.remove(conn_key)
                connection_times.pop(conn_key, None)
                pool = engine.pool
                if pool.checkedout() >= pool.size():
                  pass
                  #print(f"Conexiones en uso: {pool.checkedout()} / {pool.size()}")

def log_connection_info(dbapi_connection, connection_record):
    pass
    #print("Registro de conexión. Conexión ID:", id(dbapi_connection))
    
    
event.listen(engine, 'connect', connect_listener)
event.listen(engine, 'checkin', checkin_listener)
event.listen(engine, 'checkout', checkout_listener)
event.listen(engine, 'close',close_listener)
event.listen(engine.pool, 'connect', log_connection_info)

def adjust_pool_size():
    """Ajusta el tamaño del pool basado en el número de usuarios y conexiones activas."""
    global total_connections, user_count, engine

    # Obtener tamaño actual del pool y max_overflow
    current_pool_size = engine.pool.size()
    current_max_overflow = engine.pool._max_overflow

    # Crear 2 conexiones cada 3 usuarios
    if user_count % MAX_USERS_INCREMENT == 0:
        new_pool_size = current_pool_size + POOL_SIZE_INCREMENT
        new_max_overflow = current_max_overflow  # Mantener el max_overflow igual o ajustarlo si es necesario
        engine.dispose()  # Desconectar el motor actual
        engine = create_engine(
            DATABASE_CONNECTION_URI,
            pool_size=new_pool_size,
            max_overflow=new_max_overflow
        )
        app.logger.info(f"Ajustado el tamaño del pool a {new_pool_size}.")

    # Ampliar el pool en 3 por cada 5 usuarios
    if user_count % MAX_USERS_AMPLIFICATION == 0:
        new_max_overflow = current_max_overflow + AMPLIFICATION_INCREMENT
        new_pool_size = engine.pool.size()  # Mantener el pool_size igual o ajustarlo si es necesario
        engine.dispose()  # Desconectar el motor actual
        engine = create_engine(
            DATABASE_CONNECTION_URI,
            pool_size=new_pool_size,
            max_overflow=new_max_overflow
        )
        app.logger.info(f"Ajustado el max_overflow a {new_max_overflow}.")

    # Reducir el tamaño del pool basado en conexiones inactivas
    if total_connections > 0:
        active_ratio = len(active_connections) / total_connections
        if active_ratio < POOL_REDUCTION_THRESHOLD:
            new_pool_size = max(INITIAL_POOL_SIZE, current_pool_size - POOL_SIZE_INCREMENT)
            new_max_overflow = current_max_overflow  # Mantener el max_overflow igual o ajustarlo si es necesario
            engine.dispose()  # Desconectar el motor actual
            engine = create_engine(
                DATABASE_CONNECTION_URI,
                pool_size=new_pool_size,
                max_overflow=new_max_overflow
            )
            app.logger.info(f"Reducido el tamaño del pool a {new_pool_size}. Conexiones activas: {len(active_connections)}.")


@event.listens_for(Pool, "invalidate")
def invalidate_listener(dbapi_connection, connection_record):
    pass
    #print("Conexión invalidada. Conexión ID:", id(dbapi_connection))


def monitor_pool_state(engine):
    pool = engine.pool
    if pool.checkedout() >= pool.size():
        pass
       # print(f"Advertencia: El pool está casi lleno: {pool.checkedout()} / {pool.size()}")
    else:
        pass
       # print(f"Conexiones en uso: {pool.checkedout()} / {pool.size()}")




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








@app.route("/send_local_storage/", methods=["POST"])
def send_local_storage():
    data = request.json
    if not data:
        return jsonify(success=False, message="No data received")

    ruta_de_logeo = data.get('rutaDeLogeo')
    refresh_token = data.get('refresh_token')
    access_token = data.get('access_token')
    correo_electronico = data.get('correo_electronico')
    cuenta = data.get('cuenta')
    user_id = data.get('usuario_id')        
    simuladoOproduccion = data.get('simuladoOproduccion')
    client_ip = request.remote_addr
    data['client_ip'] = client_ip

    Logs.eliminar_logs_antiguos(5)

   
    try:
        if access_token:
            with get_db_session() as session:
                if Token.validar_expiracion_token(access_token=access_token):                     
                    usuario_obj = session.query(Usuario).filter_by(id=user_id).first()
                    registrar_acceso(data, usuario_obj, True)

                    redirect_route = 'home' if correo_electronico else 'index'
                    app.logger.info(correo_electronico or '____INTENTO ENTRAR____')
                    return jsonify(success=True, ruta=redirect_route, dominio=ruta_de_logeo)

                elif refresh_token and Token.validar_expiracion_token(access_token=refresh_token):
                    decoded_token = decode_token(refresh_token)
                    user_id = decoded_token.get("sub")

                    nuevo_access_token = generar_nuevo_token_acceso_vencido(user_id)
                    usuario_obj = session.query(Usuario).filter_by(id=user_id).first()
                    registrar_acceso(data, usuario_obj, True)

                    app.logger.info(f"Nuevo access_token generado para: {correo_electronico}")
                    return jsonify(success=True, ruta='home', access_token=nuevo_access_token)

                else:
                    app.logger.warning("El token ha expirado y no hay refresh_token válido")
                    return jsonify(success=False, ruta='index', message="Requiere autenticación nuevamente")

        else:
            app.logger.info('____INTENTO ENTRAR____') 
            app.logger.info(client_ip) 
            app.logger.info(correo_electronico)  
            return jsonify(success=True, ruta='index', dominio=ruta_de_logeo)

    except Exception as e:
        app.logger.error(f"Error al procesar la solicitud: {e}")
        return jsonify(success=False, message="Hubo un error en la solicitud")

    


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

  

@app.route("/index/<string:dominio>")
def index(dominio):
    return render_template('index.html', dominio=dominio)

@app.route("/home/<string:dominio>")
def home(dominio):
    return render_template('home.html', dominio=dominio)

@app.route("/")
@app.route("/<string:pagina>/")
@app.route("/<string:pagina>/<string:dominio>")
def entrada(dominio=None, pagina=None):
      # Llama a la tarea Celery
    #trigger.llama_tarea_cada_24_horas_estrategias('1',app)
    crea_tablas_DB()
    if not dominio:
        dominio = "inicialDominio"
    if not pagina:
        pagina = "index"
    
    return  render_template("entrada.html", dominio=dominio, pagina=pagina)


@login_manager.user_loader
def load_user(user_id):
    with get_db_session() as session:
        try:
            monitor_pool_state(db.engine)
        
            # Realiza la consulta para obtener el usuario
            user = session.query(Usuario).filter_by(id=user_id).first()
          
            return user
        
        except OperationalError as e:
            # Manejar el error de conexión y reconfigurar si es necesario
            app.logger.error(f"Error de conexión a la base de datos: {e}")
            
            # Volver a crear la sesión
        
            session.execute('SELECT 1')  # Consulta trivial para verificar la conexión   
            # Reintenta la consulta después de reconfigurar
            try:
                # Reintenta la consulta después de reconfigurar
                user = session.query(Usuario).filter_by(id=user_id).first()
             
                return user
            except OperationalError as e:
                app.logger.error(f"Error de conexión a la base de datos tras reintentar: {e}")
              
                return None
            
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Make sure this we are executing this file
if __name__ == "__main__":
   # app.run()
    #app.run(host='0.0.0.0', port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=False)
   

 
   
   
   
