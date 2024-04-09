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
        return f"Cuenta(id={self.id}, user_id={self.user_id}, userCuenta={self.userCuenta}, passwordCuenta={self.passwordCuenta}, accountCuenta={self.accountCuenta}, selector={self.selector} broker_id={self.broker_id})"

    @classmethod
    def crear_tabla_cuentas(cls):
        insp = inspect(db.engine)
        if not insp.has_table("cuentas"):
            db.create_all()

    @classmethod
    def getReporteCuenta(cls, user_id, account, selector):
        pyRofexInicializada = pyRofex
        todasLasCuentas = cls.get_cuentas_de_broker(user_id)
        for cuenta in todasLasCuentas:          
             if cuenta['accountCuenta'] == account:
                   userCuenta = cuenta['userCuenta']
                   passwordCuenta = cuenta['passwordCuenta']
                   passwordCuenta_decoded = passwordCuenta.decode('utf-8')
                   if selector == 'simulado':
                       environments = pyRofexInicializada.Environment.REMARKET
                   else:
                        environments = pyRofexInicializada.Environment.LIVE
                       
                
                   pyRofexInicializada.initialize(user=userCuenta, password=passwordCuenta_decoded, account=account, environment=environments)
                   return pyRofexInicializada.get_account_report(account=account)
        return None           

    @staticmethod
    def get_cuentas_de_broker(user_id):
        todasCuentas = []
        from models.cuentas import Cuenta
        try:
            usuario = Usuario.query.get(user_id)
            cuentas = Cuenta.query.filter_by(user_id=user_id).all()
            broker_ids = [cuenta.broker_id for cuenta in cuentas if cuenta.broker_id is not None]
            brokers = Broker.query.filter(Broker.id.in_(broker_ids)).all()
            id_nombre_broker = {broker.id: broker.nombre for broker in brokers}
            if cuentas:
                for cuenta in cuentas:
                    password_cuenta = cuenta.passwordCuenta  # No es necesario decodificar la contraseña aquí
                    nombre_broker = id_nombre_broker.get(cuenta.broker_id)
                    todasCuentas.append({
                        'id': cuenta.id,
                        'accountCuenta': cuenta.accountCuenta,
                        'userCuenta': cuenta.userCuenta,
                        'passwordCuenta': password_cuenta,
                        'selector': cuenta.selector,
                        'broker_id': cuenta.broker_id,
                        'nombre_broker': nombre_broker
                    })
        except Exception as e:
            print("Error al obtener las cuentas del usuario:", e)
        return todasCuentas

class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "userCuenta", "passwordCuenta", "accountCuenta", "selector", "broker_id")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

