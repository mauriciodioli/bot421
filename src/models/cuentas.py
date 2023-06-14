from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

cuentas = Blueprint('cuentas',__name__) 



class Cuenta(db.Model):
    __tablename__ = 'cuentas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))  
    userCuenta = db.Column(db.String(120), unique=True, nullable=False)
    passwordCuenta = db.Column(db.LargeBinary(128), nullable=False)
    accountCuenta = db.Column(db.String(500), nullable=True)
    
    usuarios = relationship("Usuario", back_populates="cuentas")

    
 # constructor
    def __init__(self, id,user_id,userCuenta,passwordCuenta,accountCuenta):
        self.id = id
        self.user_id = user_id
        self.userCuenta = userCuenta
        self.passwordCuenta = passwordCuenta
        self.accountCuenta = accountCuenta
        

   


    def crear_tabla_cuentas(serlf):
         insp = inspect(db.engine)
         if not insp.has_table("cuentas"):
              db.create_all()
             
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id" ,"userCuenta","passwordCuenta","accountCuenta")

mer_schema = MerShema()
mer_shema = MerShema(many=True)