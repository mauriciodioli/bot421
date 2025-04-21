from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


ma = Marshmallow()

preguntas = Blueprint('preguntas', __name__)

class Pregunta(db.Model):
    __tablename__ = 'preguntas'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    descripcion = db.Column(db.Text, nullable=True)  # Cambié String(500) por Text
    idioma = db.Column(db.String(500), nullable=True)
    valor = db.Column(db.Text, nullable=False)  # Cambié String(500) por Text
    estado = db.Column(db.String(500), nullable=True)
    dificultad = db.Column(db.String(500), nullable=True)  # Corrigiendo el error tipográfico
    categoria = db.Column(db.String(500), nullable=True)
    respuesta_ia =  db.Column(db.Text, nullable=True)
   

    # Constructor
    def __init__(self, descripcion, idioma=None, valor=None, estado=None, dificultad=None, categoria=None, respuesta_ia=None):
        self.descripcion = descripcion
        self.idioma = idioma
        self.valor = valor
        self.estado = estado
        self.dificultad = dificultad
        self.categoria = categoria
        self.respuesta_ia = respuesta_ia
    
    def __repr__(self):
        return f"Pregunta(id={self.id}, descripcion={self.descripcion}, idioma={self.idioma}, valor={self.valor}, estado={self.estado},respuesta_ia={self.respuesta_ia})"
    
 # Método para serializar el modelo
    
# Schema de Marshmallow para serialización
class PreguntaSchema(ma.Schema):
    class Meta:       
        model = Pregunta  # Usar la clase Pregunta como el modelo a serializar
        fields = ("id", "descripcion", "idioma", "valor", "estado", "dificultad", "categoria", "respuesta_ia")  # Campos a serializar
