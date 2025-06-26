<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String

# Inicializar Marshmallow
ma = Marshmallow()

# Declarar el Blueprint
respuestaUsuario = Blueprint('respuestaUsuario', __name__)

# Modelo para la tabla respuestaUsuario
class RespuestaUsuario(db.Model):
    __tablename__ = 'respuestaUsuario'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pregunta_id = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    respuesta_id = db.Column(db.Integer, nullable=False)
    valor_respuesta_usuario = db.Column(db.String(255), nullable=False)
    valor_respuesta_turing = db.Column(db.String(255), nullable=False)
   
    # Constructor
    def __init__(self, pregunta_id, usuario_id, respuesta_id, valor_respuesta_usuario, valor_respuesta_turing):
        self.pregunta_id = pregunta_id
        self.usuario_id = usuario_id
        self.respuesta_id = respuesta_id
        self.valor_respuesta_usuario = valor_respuesta_usuario
        self.valor_respuesta_turing = valor_respuesta_turing
     

    def __repr__(self):
        return (f"<RespuestaUsuario(id={self.id}, pregunta_id={self.pregunta_id}, usuario_id={self.usuario_id}, "
                f"respuesta_id={self.respuesta_id})>")

# Esquema para serialización
class RespuestaUsuarioSchema(ma.Schema):
    class Meta:
        fields = ("id", "pregunta_id", "usuario_id", "respuesta_id", "valor_respuesta_usuario", 
                  "valor_respuesta_turing")
=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String

# Inicializar Marshmallow
ma = Marshmallow()

# Declarar el Blueprint
respuestaUsuario = Blueprint('respuestaUsuario', __name__)

# Modelo para la tabla respuestaUsuario
class RespuestaUsuario(db.Model):
    __tablename__ = 'respuestaUsuario'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pregunta_id = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    respuesta_id = db.Column(db.Integer, nullable=False)
    valor_respuesta_usuario = db.Column(db.String(255), nullable=False)
    valor_respuesta_turing = db.Column(db.String(255), nullable=False)
   
    # Constructor
    def __init__(self, pregunta_id, usuario_id, respuesta_id, valor_respuesta_usuario, valor_respuesta_turing):
        self.pregunta_id = pregunta_id
        self.usuario_id = usuario_id
        self.respuesta_id = respuesta_id
        self.valor_respuesta_usuario = valor_respuesta_usuario
        self.valor_respuesta_turing = valor_respuesta_turing
     

    def __repr__(self):
        return (f"<RespuestaUsuario(id={self.id}, pregunta_id={self.pregunta_id}, usuario_id={self.usuario_id}, "
                f"respuesta_id={self.respuesta_id})>")

# Esquema para serialización
class RespuestaUsuarioSchema(ma.Schema):
    class Meta:
        fields = ("id", "pregunta_id", "usuario_id", "respuesta_id", "valor_respuesta_usuario", 
                  "valor_respuesta_turing")
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
