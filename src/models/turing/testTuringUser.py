from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String, Date

# Inicializar Marshmallow
ma = Marshmallow()

# Declarar el Blueprint
testTuringUser = Blueprint('testTuringUser', __name__)

# Modelo para la tabla testTuringUser
class TestTuringUser(db.Model):
    __tablename__ = 'testTuringUser'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)  # Cambiado a String
    ip_cliente = db.Column(db.String(45), nullable=False)  # Cambiado a String, longitud estándar para IP
    estado = db.Column(db.String(50), nullable=True)
    fecha_registro = db.Column(db.Date, nullable=False)

    # Constructor
    def __init__(self, nombre, ip_cliente,  estado,  fecha_registro):
        self.nombre = nombre
        self.ip_cliente = ip_cliente      
        self.estado = estado     
        self.fecha_registro = fecha_registro

    # Representación en texto
    def __repr__(self):
        return (f"<TestTuringUser(id={self.id}, nombre={self.nombre}, ip_cliente={self.ip_cliente}, "
                f"estado={self.estado}, "
                f"fecha_registro={self.fecha_registro})>")

# Schema para serialización
class TestTuringUserSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "ip_cliente",  "estado","fecha_registro")  # Campos a serializar
