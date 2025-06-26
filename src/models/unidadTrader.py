<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect
from sqlalchemy.orm import relationship


ma = Marshmallow()

unidad_trader = Blueprint('unidad_trader',__name__) 
class UnidadTrader(db.Model):
    __tablename__ = 'unidadTrader'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    accountCuenta = db.Column(db.String(500), nullable=True)
    usuario_id = db.Column(db.Integer)
    trigger_id = db.Column(db.Integer)   
    ut = db.Column(db.Integer)  

    def __init__(self, accountCuenta, usuario_id, trigger_id, ut):
        self.accountCuenta = accountCuenta
        self.usuario_id = usuario_id
        self.trigger_id = trigger_id
        self.ut = ut

    def __repr__(self):
        return f"UnidadTrader(id={self.id}, cuenta_id={self.accountCuenta}, usuario_id={self.usuario_id}, trigger_id={self.trigger_id}, ut={self.ut})"
    @classmethod
    def crear_tabla_ut(cls):
        insp = inspect(db.engine)
        if not insp.has_table("unidadTrader"):
            db.create_all()

             
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id",  "accountCuenta","usuario_id","trigger_id","ut")

mer_schema = MerShema()
=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect
from sqlalchemy.orm import relationship


ma = Marshmallow()

unidad_trader = Blueprint('unidad_trader',__name__) 
class UnidadTrader(db.Model):
    __tablename__ = 'unidadTrader'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    accountCuenta = db.Column(db.String(500), nullable=True)
    usuario_id = db.Column(db.Integer)
    trigger_id = db.Column(db.Integer)   
    ut = db.Column(db.Integer)  

    def __init__(self, accountCuenta, usuario_id, trigger_id, ut):
        self.accountCuenta = accountCuenta
        self.usuario_id = usuario_id
        self.trigger_id = trigger_id
        self.ut = ut

    def __repr__(self):
        return f"UnidadTrader(id={self.id}, cuenta_id={self.accountCuenta}, usuario_id={self.usuario_id}, trigger_id={self.trigger_id}, ut={self.ut})"
    @classmethod
    def crear_tabla_ut(cls):
        insp = inspect(db.engine)
        if not insp.has_table("unidadTrader"):
            db.create_all()

             
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id",  "accountCuenta","usuario_id","trigger_id","ut")

mer_schema = MerShema()
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
mer_shema = MerShema(many=True)