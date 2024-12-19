from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date



ma = Marshmallow()

preguntaUsuario = Blueprint('preguntaUsuario', __name__)

class PreguntaUsuario(db.Model):
    __tablename__ = 'preguntaUsuario'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)  # Cambié Integer por BigInteger
    pregunta_id = db.Column(db.Integer, nullable=False)
    dificultad = db.Column(db.String(500), nullable=True)  # Corregí "difcultad" a "dificultad"
    estado = db.Column(db.String(500), nullable=True)
    tiempo = db.Column(db.String(500), nullable=True)
    fecha = db.Column(db.Date(), nullable=False)  # Corregí el error tipográfico en "Fals"
    
        
    
    def __init__(self, user_id, pregunta_id, dificultad, estado, tiempo, fecha):
        self.user_id = user_id
        self.pregunta_id = pregunta_id
        self.dificultad = dificultad
        self.estado = estado
        self.tiempo = tiempo
        self.fecha = fecha
    
    def __repr__(self):
        return f"PreguntaUsuario(id={self.id}, user_id={self.user_id}, pregunta_id={self.pregunta_id}, estado={self.estado}, fecha={self.fecha})"
    

# Schema de Marshmallow para serialización
class PreguntaUsuarioSchema(ma.Schema):
    class Meta:       
        model = PreguntaUsuario  # Usar la clase PreguntaUsuario como el modelo a serializar
        fields = ("id", "user_id", "pregunta_id", "dificultad", "estado", "tiempo", "fecha")  # Campos a serializar
