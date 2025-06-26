<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey,Time
from sqlalchemy.orm import relationship

ma = Marshmallow()

altaEstrategiaApp = Blueprint('altaEstrategiaApp',__name__) 

class AltaEstrategiaApp(db.Model):
    __tablename__ = 'altaEstrategiaApp'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    accountCuenta = db.Column(db.String(500), nullable=True)   
    nombreEstrategia = db.Column(db.String(500), nullable=True)  
    estado = db.Column(db.String(500), nullable=False)  
    descripcion = db.Column(db.String(500), nullable=False)  
    fecha =  db.Column(db.String(500), nullable=False) 
    
  
    
 # constructor
    def __init__(self, id,accountCuenta,nombreEstrategia,estado,descripcion,fecha):
        self.id = id       
        self.accountCuenta = accountCuenta      
        self.nombreEstrategia = nombreEstrategia
        self.estado = estado
        self.descripcion = descripcion
        self.fecha = fecha

    @classmethod
    def crear_tabla_altaEstrategiaApp(self):
         insp = inspect(db.engine)
         if not insp.has_table("altaEstrategiaApp"):
              db.create_all()
             
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "accountCuenta","nombreEstrategia","estado","descripcion","fecha")

mer_schema = MerShema()
=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey,Time
from sqlalchemy.orm import relationship

ma = Marshmallow()

altaEstrategiaApp = Blueprint('altaEstrategiaApp',__name__) 

class AltaEstrategiaApp(db.Model):
    __tablename__ = 'altaEstrategiaApp'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    accountCuenta = db.Column(db.String(500), nullable=True)   
    nombreEstrategia = db.Column(db.String(500), nullable=True)  
    estado = db.Column(db.String(500), nullable=False)  
    descripcion = db.Column(db.String(500), nullable=False)  
    fecha =  db.Column(db.String(500), nullable=False) 
    
  
    
 # constructor
    def __init__(self, id,accountCuenta,nombreEstrategia,estado,descripcion,fecha):
        self.id = id       
        self.accountCuenta = accountCuenta      
        self.nombreEstrategia = nombreEstrategia
        self.estado = estado
        self.descripcion = descripcion
        self.fecha = fecha

    @classmethod
    def crear_tabla_altaEstrategiaApp(self):
         insp = inspect(db.engine)
         if not insp.has_table("altaEstrategiaApp"):
              db.create_all()
             
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "accountCuenta","nombreEstrategia","estado","descripcion","fecha")

mer_schema = MerShema()
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
mer_shema = MerShema(many=True)