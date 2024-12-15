from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect
from sqlalchemy.orm import relationship

ma = Marshmallow()


ambitos = Blueprint('ambitos', __name__)


class Ambitos(db.Model):
    __tablename__ = 'ambitos'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(500), unique=True, nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    idioma = db.Column(db.String(500), nullable=True)
    valor = db.Column(db.String(500), nullable=True)
    estado = db.Column(db.String(500), nullable=True)
    
    
    # Constructor
    def __init__(self, nombre, descripcion, idioma=None, valor=None, estado=None, user_id=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.idioma = idioma
        self.valor = valor
        self.estado = estado
        self.user_id = user_id
    
    def __repr__(self):
        return f"Ambitos(id={self.id}, nombre={self.nombre}, descripcion={self.descripcion}, idioma={self.idioma}, valor={self.valor}, estado={self.estado}, user_id={self.user_id})"
    
    @classmethod
    def crear_tabla_ambitos(self):
        # Verificar si la tabla 'ambitos' existe antes de crearla
        insp = inspect(db.engine)
        if not insp.has_table("ambitos"):
            db.create_all()

# Schema de Marshmallow para serialización
class MerShema(ma.Schema):
    class Meta:
        model = Ambitos
        fields = ("id", "nombre", "descripcion", "idioma", "valor", "estado", "user_id")  # Campos a serializar

# Crear instancias del esquema para serialización
mer_schema = MerShema()
mer_shema = MerShema(many=True)

