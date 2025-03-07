from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

ma = Marshmallow()

logs = Blueprint('logs', __name__)

class Logs(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('usuarios.id'))
    userCuenta = db.Column(db.String(120)) 
    accountCuenta = db.Column(db.String(120))    
    fecha_log = db.Column(db.DateTime)  # Corregido a DateTime
    ip = db.Column(db.String(120))   
    funcion = db.Column(db.String(120))   
    archivo = db.Column(db.String(120))   
    linea = db.Column(db.Integer) 
    error = db.Column(db.String(120))   
    codigoPostal = db.Column(db.String(120))
    latitude = db.Column(db.String(120))
    longitude = db.Column(db.String(120))
    language = db.Column(db.String(50))
    
    usuarios = relationship("Usuario", back_populates="logs")

    def __init__(self, user_id, userCuenta, accountCuenta, fecha_log, ip, funcion, archivo, linea, error, codigoPostal, latitude, longitude, language):
        self.user_id = user_id
        self.userCuenta = userCuenta
        self.accountCuenta = accountCuenta
        self.fecha_log = fecha_log
        self.ip = ip
        self.funcion = funcion
        self.archivo = archivo
        self.linea = linea
        self.error = error
        self.codigoPostal = codigoPostal
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
    
    @classmethod
    def crear_tabla_logs(self):
        insp = inspect(db.engine)
        if not insp.has_table("logs"):
            db.create_all()

    @classmethod
    def eliminar_logs_antiguos(cls, dias):
        """Elimina logs de ingreso que sean más viejos que 'dias' días."""
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        logs_antiguos = Logs.query.filter(Logs.fecha_log < fecha_limite).all()
        
        for log in logs_antiguos:
            db.session.delete(log)
        
        db.session.commit()

class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "userCuenta", "accountCuenta", "fecha_log", "ip", "funcion", "archivo", "linea", "error", "codigoPostal", "latitude", "longitude", "language")

mer_schema = MerShema()
mer_shema = MerShema(many=True)
