from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect

ma = Marshmallow()

usuario = Blueprint('usuario',__name__) 



class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo_electronico = db.Column(db.String(255), unique=True, nullable=False)
    token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=False)
 # constructor
    def __init__(self, id,correo_electronico,token,refresh_token,activo):
        self.id = id
        self.correo_electronico = correo_electronico
        self.token = token
        self.refresh_token = refresh_token
        self.activo = activo



    def crear_tabla(serlf):
         insp = inspect(db.engine)
         if not insp.has_table("usuarios"):
              db.create_all()
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id",  "correo_electronico","token","refresh_token","activo")

mer_schema = MerShema()
mer_shema = MerShema(many=True)