from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import pyRofex
from models.usuario import Usuario
from models.brokers import Broker


ma = Marshmallow()

cuentas = Blueprint('cuentas', __name__)


class Cuenta(db.Model):
    __tablename__ = 'cuentas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    broker_id = db.Column(db.Integer, db.ForeignKey('brokers.id'), nullable=True)

    userCuenta = db.Column(db.String(120), unique=True, nullable=False)
    passwordCuenta = db.Column(db.LargeBinary(128), nullable=False)
    accountCuenta = db.Column(db.String(500), nullable=True)
    selector = db.Column(db.String(500), nullable=True)
    ficha = relationship("Ficha", back_populates="cuentas")
    trazaFichas = relationship('TrazaFicha', backref='cuenta')
    usuarios = relationship("Usuario", back_populates="cuentas")
    
   
   

    # constructor
    def __init__(self, id, user_id, userCuenta, passwordCuenta, accountCuenta, selector, broker_id):
        self.id = id
        self.user_id = user_id
        self.userCuenta = userCuenta
        self.passwordCuenta = passwordCuenta
        self.accountCuenta = accountCuenta
        self.selector = selector
        self.broker_id = broker_id

    def __repr__(self):
        return f"Cuenta(id={self.id}, user_id={self.user_id}, userCuenta={self.userCuenta}, passwordCuenta={self.passwordCuenta}, accountCuenta={self.accountCuenta}, selector={self.selector}, broker_id={self.broker_id})"

    @classmethod
    def crear_tabla_cuentas(cls):
        insp = inspect(db.engine)
        if not insp.has_table("cuentas"):
            db.create_all()
            
            
    def inicializar_variables(accountCuenta):
        valores = []  # Inicializar la lista
        
            # Buscar la cuenta asociada a la cuentaCuenta proporcionada
        cuenta = db.session.query(Cuenta).filter(Cuenta.accountCuenta == accountCuenta).first()
        
        if cuenta:
            # Si se encontró la cuenta, obtener el objeto Broker asociado usando su broker_id
            broker = db.session.query(Broker).filter(Broker.id == cuenta.broker_id).first()
            db.session.close()
            if broker:
                # Agregar los valores de api_url y ws_url a la lista 'valores'
                valores = [broker.api_url, broker.ws_url]
                # Hacer algo con el objeto Broker encontrado
                print(f"El broker asociado a la cuenta es: {broker.nombre}")
            else:
                print("No se encontró el broker asociado a la cuenta.")
        else:
            db.session.close()
            print("No se encontró la cuenta.")

            
        return valores
    
    @classmethod
    def getReporteCuenta(cls, userCuenta, passwordCuenta_decoded,account,selector):      
        pyRofexInicializada = pyRofex
        endPoint = cls.inicializar_variables(account)
        api_url = endPoint[0]
               
        if selector == 'simulado':
                environments =pyRofexInicializada.Environment.REMARKET
        else:
               environments = pyRofexInicializada.Environment.LIVE
        pyRofexInicializada._set_environment_parameter("url",api_url,environments) 
        pyRofexInicializada.initialize(user=userCuenta, password=passwordCuenta_decoded, account=account, environment=environments)
        return pyRofexInicializada.get_account_report(account=account,environment=account)
                  

    def getDetalleCuenta(cls, userCuenta, passwordCuenta_decoded,account,selector):
        pyRofexInicializada = pyRofex
        endPoint = cls.inicializar_variables(account)
        api_url = endPoint[0]
               
        if selector == 'simulado':
                environments =pyRofexInicializada.Environment.REMARKET
        else:
               environments = pyRofexInicializada.Environment.LIVE
        pyRofexInicializada._set_environment_parameter("url",api_url,environments) 
        pyRofexInicializada.initialize(user=userCuenta, password=passwordCuenta_decoded, account=account, environment=environments)
        return pyRofexInicializada.get_detailed_position(account=account, environment=environments)
          
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "userCuenta", "passwordCuenta", "accountCuenta", "selector", "broker_id")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

