from re import template
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
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import DATABASE_CONNECTION_URI

from routes.instrumentos import instrumentos
from routes.instrumentosGet import instrumentosGet
from routes.api_externa_conexion.get_login import get_login
from routes.api_externa_conexion.comprar import comprar
from routes.api_externa_conexion.operaciones import operaciones
from routes.api_externa_conexion.validaInstrumentos import validaInstrumentos
from routes.api_externa_conexion.cuenta import cuenta
from routes.api_externa_conexion.wsocket import wsocket
from routes.suscripciones import suscripciones
from strategies.estrategias import estrategias



# desde aqui se llama la aplicacion al inicio
app = Flask(__name__)

##### BLUEPRINT ES EL ENRUTADOR####
app.register_blueprint(instrumentos)
app.register_blueprint(instrumentosGet)
app.register_blueprint(get_login)
app.register_blueprint(cuenta)
app.register_blueprint(comprar)
app.register_blueprint(operaciones)
app.register_blueprint(validaInstrumentos)
app.register_blueprint(wsocket)
app.register_blueprint(suscripciones)
app.register_blueprint(estrategias)

print(DATABASE_CONNECTION_URI)
app.secret_key = '*0984632'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.route("/")
def entrada():
  return redirect("loginApi")





# Make sure this we are executing this file
if __name__ == "__main__":
    app.run(debug=True)
