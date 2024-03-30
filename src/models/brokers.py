from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

brokers = Blueprint('brokers',__name__) 



class Broker(db.Model):
    __tablename__ = 'brokers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    api_url = db.Column(db.String(120), unique=True, nullable=True)
    ws_url = db.Column(db.String(120), unique=True, nullable=True)
    nombre = db.Column(db.String(500), unique=True, nullable=True)
    descripcion = db.Column(db.String(500), nullable=True) 
    ficha = relationship("Ficha", back_populates="broker")   
    traza_fichas = relationship('TrazaFicha', back_populates='broker')
    #cuentas = relationship("Cuenta", back_populates="broker")  # Corregido el uso de uselist
   # usuarios = relationship("Usuario", back_populates="brokers")

    
 # constructor
    def __init__(self, id,api_url,ws_url,nombre,descripcion):
        self.id = id
        self.api_url = api_url
        self.ws_url = ws_url
        self.nombre = nombre
        self.descripcion = descripcion
      

   
    def __repr__(self):
        return f"Cuenta(id={self.id}, api_url={self.api_url}, ws_url={self.ws_url}, nombre={self.nombre}, descripcion={self.descripcion})"
    @classmethod
    def crear_tabla_cuentas(self):
         insp = inspect(db.engine)
         if not insp.has_table("brokers"):
              db.create_all()
             
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "api_url" ,"ws_url","nombre","descripcion")

mer_schema = MerShema()
mer_shema = MerShema(many=True)

