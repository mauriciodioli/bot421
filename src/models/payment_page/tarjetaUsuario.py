from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
import pyRofex
from models.usuario import Usuario
from models.brokers import Broker


ma = Marshmallow()

tarjetaUsuario = Blueprint('tarjetaUsuario', __name__)


class TarjetaUsuario(db.Model):
    __tablename__ = 'tarjetaUsuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Cambiado a 'Usuario' en lugar de 'usuarios'
    numeroTarjeta = db.Column(db.String(120), unique=True, nullable=True)  # Corregido el nombre de la columna
    fecha_vencimiento = db.Column(db.String(120), nullable=False)
    cvv = db.Column(db.String(120), nullable=False)  # Eliminado unique=True porque es poco probable que sea único
    nombreApellidoTarjeta = db.Column(db.String(120), nullable=False)  # Eliminado unique=True porque es poco probable que sea único
    correo_electronico = db.Column(db.String(120), nullable=False)  # Eliminado unique=True porque es poco probable que sea único
    accountCuenta = db.Column(db.String(500), nullable=True)
  
    __table_args__ = (
         UniqueConstraint('user_id', 'numeroTarjeta', name='_user_tarjeta_uc'),
     )

    # constructor
    def __init__(self, user_id, numeroTarjeta, fecha_vencimiento, cvv, nombreApellidoTarjeta, correo_electronico,
                 accountCuenta):
        self.user_id = user_id
        self.numeroTarjeta = numeroTarjeta
        self.fecha_vencimiento = fecha_vencimiento
        self.cvv = cvv
        self.nombreApellidoTarjeta = nombreApellidoTarjeta
        self.correo_electronico = correo_electronico
        self.accountCuenta = accountCuenta

    def __repr__(self):
        return f"TarjetaUsuario(id={self.id}, user_id={self.user_id}, mumeroTarjeta={self.numeroTarjeta}, " \
               f"fecha_vencimiento={self.fecha_vencimiento}, cvv={self.cvv}, " \
               f"nombreApellidoTarjeta={self.nombreApellidoTarjeta}, " \
               f"correo_electronico={self.correo_electronico}, accountCuenta={self.accountCuenta})"

    @classmethod
    def crear_tabla_tarjetaUsuario(cls):
        insp = inspect(db.engine)
        if not insp.has_table("tarjetaUsuario"):
            db.create_all() 


class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "numeroTarjeta", "fecha_vencimiento", "cvv", "nombreApellidoTarjeta",
                  "correo_electronico", "accountCuenta")


mer_schema = MerShema()
mer_shema = MerShema(many=True)
