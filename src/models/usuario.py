from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect
from sqlalchemy.orm import relationship


ma = Marshmallow()

usuario = Blueprint('usuario',__name__) 



class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activo = db.Column(db.Boolean, nullable=False, default=False)    
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    token = db.Column(db.String(500), nullable=True)
    refresh_token = db.Column(db.String(500), nullable=True)
    cuentas = relationship("Cuenta", back_populates="usuarios")
    orden = relationship("Orden", back_populates="usuarios")
    imagenes = relationship("Image", back_populates="usuarios")
    triggerEstrategia = relationship("TriggerEstrategia", back_populates="usuarios")
   
    
 # constructor
    def __init__(self, id,correo_electronico,token,refresh_token,activo,password):
        self.id = id
        self.correo_electronico = correo_electronico
        self.token = token
        self.refresh_token = refresh_token
        self.activo = activo        
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.activo

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


    def crear_tabla(serlf):
         insp = inspect(db.engine)
         if not insp.has_table("usuarios"):
              db.create_all()
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id",  "correo_electronico","token","refresh_token","activo","password")

mer_schema = MerShema()
mer_shema = MerShema(many=True)