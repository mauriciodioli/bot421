from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

strategy = Blueprint('strategy',__name__) 



class Strategy(db.Model):
    __tablename__ = 'strategy'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    api_url = db.Column(db.String(120))
    ws_url = db.Column(db.String(120))
    nombre = db.Column(db.String(500), unique=True, nullable=True)
    descripcion = db.Column(db.String(500), nullable=True) 
   

    
 # constructor
    def __init__(self, id,api_url,ws_url,nombre,descripcion):
        self.id = id
        self.api_url = api_url
        self.ws_url = ws_url
        self.nombre = nombre
        self.descripcion = descripcion
      

   
    def __repr__(self):
        return f"strategy(id={self.id}, api_url={self.api_url}, ws_url={self.ws_url}, nombre={self.nombre}, descripcion={self.descripcion})"
    @classmethod
    def crear_tabla_strategy(self):
         insp = inspect(db.engine)
         if not insp.has_table("strategy"):
              db.create_all()
             