#from re import template

from flask import (Flask,Blueprint,Response,make_response,render_template,request,redirect,url_for,flash,jsonify)
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_identity)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import DATABASE_CONNECTION_URI

# Importar create_engine y NullPool
import logging
import os
from log.logRegister import generate_logs

from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import QueuePool
######################zona de estrategias de usuarios####################
from strategies.estrategiasUsuarios.Remarkets_REM6603_001 import Remarkets_REM6603_001
from strategies.estrategiasUsuarios.Bull_Market_10861_001 import Bull_Market_10861_001
from strategies.estrategiasUsuarios.Bull_Market_351653_001 import Bull_Market_351653_001
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
from productosComerciales.descipcionProductos import descrpcionProductos
from productosComerciales.planes import planes
from productosComerciales.suscripcionPlanUsuario import suscripcionPlanUsuario
from productosComerciales.promociones.promociones import promociones

from herramientasAdmin.accionesSheet import accionesSheet

from strategies.estrategias import estrategias
from strategies.estrategiaSheetWS import estrategiaSheetWS

from strategies.datoSheet import datoSheet
from strategies.Experimental.FuncionesBasicas01 import FuncionesBasicas01
from strategies.arbitraje_001 import arbitraje_001
from strategies.utils.testWS import testWS
from strategies.gestion_estrategias.abm_estrategias import abm_estrategias
from strategies.gestion_estrategias.unidad_trader import unidad_trader

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

from social.imagenes.imagenesOperaciones import imagenesOperaciones
from social.media_e_mail import media_e_mail

from comunicacion.contacto import contacto

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

from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
import schedule
import time

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
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


# Crear un manejador de logs que escriba a `stdout`
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)


app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
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
app.register_blueprint(Remarkets_REM6603_001)
app.register_blueprint(Bull_Market_10861_001)
app.register_blueprint(Bull_Market_351653_001)
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
app.register_blueprint(accionesSheet)


print(DATABASE_CONNECTION_URI)
app.secret_key = '*0984632'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_POOL_SIZE'] = 100
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
engine = create_engine(DATABASE_CONNECTION_URI, poolclass=QueuePool, pool_timeout=60, pool_size=1000, max_overflow=10, pool_recycle=3600)

def log_connection_info(dbapi_connection, connection_record):
    """Log connection events."""
    global connection_count
    connection_count += 1
    print(f"Conexión establecida ({connection_count} veces)")
    app.logger.info(f"Conexión establecida ({connection_count} veces)")

event.listen(engine, 'connect', log_connection_info)
db = SQLAlchemy(app)
# Configurar el pool de conexiones para SQLAlchemy
db.init_app(app)
db.session.configure(bind=engine)

ma = Marshmallow(app)


# Creación de la instancia del objeto LoginManager
#login_manager = LoginManager()
#login_manager.init_app(app)


# Registrar los métodos user_loader y request_loader
#login_manager.user_loader(user_loader)
#login_manager.request_loader(request_loader)
# Función para registrar eventos de conexión
# Contador para la cantidad de conexiones
connection_count = 0

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
    #return Usuario.query.get(int(user_id))
    
     return db.session.query(Usuario).filter_by(id=user_id).first()
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
   
   
   
   
   
