#from re import template

from flask import (Flask,Blueprint,render_template,request,redirect,url_for,flash,jsonify)
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_identity)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import DATABASE_CONNECTION_URI
# Importar create_engine y NullPool
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import QueuePool

from models.creaTablas import crea_tablas_DB


from strategies.estrategias import estrategias
from strategies.estrategiaSheetWS import estrategiaSheetWS
from strategies.datoSheet import datoSheet
from strategies.datoSheet import datoSheet
from strategies.Experimental.FuncionesBasicas01 import FuncionesBasicas01
from strategies.arbitraje_001 import arbitraje_001
from strategies.utils.testWS import testWS

from tokens.token import token

 
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
from fichasTokens.fichas import fichas

from usuarios.autenticacion import autenticacion
from usuarios.registrarUsuario import registrarUsuario
from usuarios.usuario import usuario

from social.imagenes.imagenesOperaciones import imagenesOperaciones
from social.media_e_mail import media_e_mail

from panelControlBroker.panelControl import panelControl
from panelControl.pcEstrategiaUs import pcEtrategiaUs

from automatizacion.programar_trigger import programar_trigger 
from automatizacion.shedule_triggers import shedule_triggers
import automatizacion.programar_trigger as trigger
import subprocess
from celery import Celery

from celery.schedules import crontab
from models.usuario import Usuario
from models.triggerEstrategia import triggerEstrategia
from models.orden import orden
from models.ficha import ficha
from models.trazaFicha import trazaFicha
from models.operacion import operacion
from models.operacionHF import operacionHF
from models.logs import logs
from models.creaTablas import creaTabla

from log.logRegister import logRegister

from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
import schedule
import time



# desde aqui se llama la aplicacion al inicio
#app = Flask(__name__)

 # Inicia los workers de Celery
#celery_app.start()
app = Flask(__name__, static_folder='static')

# Configurar el manejo de errores para la aplicación
login_manager = LoginManager(app)

# Configurar CORS
CORS(app)

# Configurar la generación de logs para la aplicación
logging.basicConfig(level=logging.DEBUG)  # Configura el nivel de log a DEBUG

# Configurar el logger de la aplicación Flask
app.logger.setLevel(logging.DEBUG)  # Configura el nivel de log a DEBUG para la aplicación Flask


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
##### BLUEPRINT ES EL ENRUTADOR####

app.register_blueprint(logs)
app.register_blueprint(creaTabla)
app.register_blueprint(token)
app.register_blueprint(instrumentos)
app.register_blueprint(instrumentosGet)
app.register_blueprint(get_login)
app.register_blueprint(cuenta)
app.register_blueprint(cuentas)
app.register_blueprint(orden)
app.register_blueprint(comprar)
app.register_blueprint(operacion)
app.register_blueprint(operaciones)
app.register_blueprint(operacionHF)
app.register_blueprint(validaInstrumentos)
app.register_blueprint(wsocket)
app.register_blueprint(suscripciones)
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


print(DATABASE_CONNECTION_URI)
app.secret_key = '*0984632'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_POOL_SIZE'] = 100
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
engine = create_engine(DATABASE_CONNECTION_URI, poolclass=QueuePool, pool_timeout=60, pool_size=1000, max_overflow=10)

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

# Inicia los workers de Celery
# Programar la tarea para que se ejecute a una hora específica


def log_connection_info(dbapi_connection, connection_record):
    """Log connection events."""
    global connection_count
    connection_count += 1
    print(f"Conexión establecida ({connection_count} veces)")



@app.route("/")
def entrada():  
      # Llama a la tarea Celery
    #trigger.llama_tarea_cada_24_horas_estrategias('1',app)
    #crea_tablas_DB()
    return redirect("index")

@login_manager.user_loader
def load_user(user_id):
    #return Usuario.query.get(int(user_id))
    
     return db.session.query(Usuario).filter_by(id=user_id).first()
# Make sure this we are executing this file
if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=5001, debug=True)
    # Ciclo para ejecutar las tareas programadas
  
   # while True:
   #     schedule.run_pending()
   #     print('__________________________________________________')
   #     print('entra en el planificador')
   #     time.sleep(3)
   
   
   
   
   
