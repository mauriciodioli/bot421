<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String

# Inicializar Marshmallow
ma = Marshmallow()

# Declarar el Blueprint
respuesta = Blueprint('respuesta', __name__)

# Modelo para la tabla Respuesta
class Respuesta(db.Model):
    __tablename__ = 'respuesta'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    pregunta_id = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    idioma = db.Column(db.String(500), nullable=True)
    valor = db.Column(db.String(500), nullable=False)
    estado = db.Column(db.String(500), nullable=True)
    dificultad = db.Column(db.String(500), nullable=True)
    categoria = db.Column(db.String(500), nullable=True)
    respuesta = db.Column(db.String(1000), nullable=True)

    # Constructor
    def __init__(self, pregunta_id, usuario_id, idioma=None, valor=None, estado=None, dificultad=None, categoria=None, respuesta=None):
        self.pregunta_id = pregunta_id
        self.usuario_id = usuario_id
        self.idioma = idioma
        self.valor = valor
        self.estado = estado
        self.dificultad = dificultad
        self.categoria = categoria
        self.respuesta = respuesta

    def __repr__(self):
        return (f"<Respuesta(id={self.id}, pregunta_id={self.pregunta_id}, usuario_id={self.usuario_id}, "
                f"idioma={self.idioma}, valor={self.valor}, estado={self.estado}, "
                f"dificultad={self.dificultad}, categoria={self.categoria}, respuesta={self.respuesta})>")

# Esquema de Marshmallow para serialización
class RespuestaSchema(ma.Schema):
    class Meta:       
        fields = ("id", "pregunta_id", "usuario_id", "idioma", "valor", "estado", "dificultad", "categoria", "respuesta")
=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String

# Inicializar Marshmallow
ma = Marshmallow()

# Declarar el Blueprint
respuesta = Blueprint('respuesta', __name__)

# Modelo para la tabla Respuesta
class Respuesta(db.Model):
    __tablename__ = 'respuesta'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    pregunta_id = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    idioma = db.Column(db.String(500), nullable=True)
    valor = db.Column(db.String(500), nullable=False)
    estado = db.Column(db.String(500), nullable=True)
    dificultad = db.Column(db.String(500), nullable=True)
    categoria = db.Column(db.String(500), nullable=True)
    respuesta = db.Column(db.String(1000), nullable=True)

    # Constructor
    def __init__(self, pregunta_id, usuario_id, idioma=None, valor=None, estado=None, dificultad=None, categoria=None, respuesta=None):
        self.pregunta_id = pregunta_id
        self.usuario_id = usuario_id
        self.idioma = idioma
        self.valor = valor
        self.estado = estado
        self.dificultad = dificultad
        self.categoria = categoria
        self.respuesta = respuesta

    def __repr__(self):
        return (f"<Respuesta(id={self.id}, pregunta_id={self.pregunta_id}, usuario_id={self.usuario_id}, "
                f"idioma={self.idioma}, valor={self.valor}, estado={self.estado}, "
                f"dificultad={self.dificultad}, categoria={self.categoria}, respuesta={self.respuesta})>")

# Esquema de Marshmallow para serialización
class RespuestaSchema(ma.Schema):
    class Meta:       
        fields = ("id", "pregunta_id", "usuario_id", "idioma", "valor", "estado", "dificultad", "categoria", "respuesta")
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
