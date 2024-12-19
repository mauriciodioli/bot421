from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from datetime import date

# Inicializar Marshmallow
ma = Marshmallow()

# Blueprint
trivia = Blueprint('trivia', __name__)

# Modelo Trivia
class Trivia(db.Model):
    __tablename__ = 'trivia'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    estado = db.Column(db.String(500), nullable=True)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    porcentaje = db.Column(db.Integer, nullable=True)
    total_respuestas = db.Column(db.Integer, nullable=True)
    total_respuestas_correctas = db.Column(db.Integer, nullable=True)
    total_respuestas_incorrectas = db.Column(db.Integer, nullable=True)
    
    # Constructor
    def __init__(self, user_id, estado=None, porcentaje=None, total_respuestas=0, total_respuestas_correctas=0, total_respuestas_incorrectas=0, fecha=None):
        self.user_id = user_id
        self.estado = estado
        self.porcentaje = porcentaje
        self.total_respuestas = total_respuestas
        self.total_respuestas_correctas = total_respuestas_correctas
        self.total_respuestas_incorrectas = total_respuestas_incorrectas
        self.fecha = fecha or date.today()

    def __repr__(self):
        return f"<Trivia(id={self.id}, user_id={self.user_id}, estado={self.estado}, fecha={self.fecha})>"

# Esquema Trivia
class TriviaSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "estado", "fecha", "porcentaje", "total_respuestas", "total_respuestas_correctas", "total_respuestas_incorrectas")
