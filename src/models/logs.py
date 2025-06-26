<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

ma = Marshmallow()

logs = Blueprint('logs', __name__)

class Logs(db.Model):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    userCuenta = Column(String(120)) 
    accountCuenta = Column(String(120))    
    fecha_log = Column(DateTime)  # ✅ Corrección en el tipo de dato
    ip = Column(String(120))   
    funcion = Column(String(120))   
    archivo = Column(String(120))   
    linea = Column(Integer) 
    error = Column(String(120))   
    codigoPostal = Column(String(120))
    latitude = Column(String(120))
    longitude = Column(String(120))
    language = Column(String(50))
    
    usuarios = relationship("Usuario", back_populates="logs")

    def __init__(self, user_id, userCuenta, accountCuenta, fecha_log, ip, funcion, archivo, linea, error, codigoPostal, latitude, longitude, language):
        self.user_id = user_id
        self.userCuenta = userCuenta
        self.accountCuenta = accountCuenta
        self.fecha_log = fecha_log
        self.ip = ip
        self.funcion = funcion
        self.archivo = archivo
        self.linea = linea
        self.error = error
        self.codigoPostal = codigoPostal
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
    
    @classmethod
    def crear_tabla_logs(cls):
        insp = inspect(db.engine)
        if not insp.has_table("logs"):
            db.create_all()

    @classmethod
    def eliminar_logs_antiguos(cls, dias):
        """Elimina logs de ingreso que sean más viejos que 'dias' días."""
        fecha_limite = datetime.now() - timedelta(days=dias)

        try:
            logs_antiguos = db.session.query(cls).filter(cls.fecha_log < fecha_limite).all()

            if logs_antiguos:  # Solo eliminar si hay registros
                for log in logs_antiguos:
                    db.session.delete(log)
                
                db.session.commit()
                print(f"{len(logs_antiguos)} logs eliminados con éxito.")

        except SQLAlchemyError as e:
            db.session.rollback()  # Revierte en caso de error
            print(f"Error eliminando logs antiguos: {e}")

        finally:
            db.session.close()  # Asegura que la sesión se cierre siempre

class MerSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "userCuenta", "accountCuenta", "fecha_log", "ip", "funcion", "archivo", "linea", "error", "codigoPostal", "latitude", "longitude", "language")

mer_schema = MerSchema()
mer_schema_many = MerSchema(many=True)  # ✅ Nombre corregido
=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

ma = Marshmallow()

logs = Blueprint('logs', __name__)

class Logs(db.Model):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    userCuenta = Column(String(120)) 
    accountCuenta = Column(String(120))    
    fecha_log = Column(DateTime)  # ✅ Corrección en el tipo de dato
    ip = Column(String(120))   
    funcion = Column(String(120))   
    archivo = Column(String(120))   
    linea = Column(Integer) 
    error = Column(String(120))   
    codigoPostal = Column(String(120))
    latitude = Column(String(120))
    longitude = Column(String(120))
    language = Column(String(50))
    
    usuarios = relationship("Usuario", back_populates="logs")

    def __init__(self, user_id, userCuenta, accountCuenta, fecha_log, ip, funcion, archivo, linea, error, codigoPostal, latitude, longitude, language):
        self.user_id = user_id
        self.userCuenta = userCuenta
        self.accountCuenta = accountCuenta
        self.fecha_log = fecha_log
        self.ip = ip
        self.funcion = funcion
        self.archivo = archivo
        self.linea = linea
        self.error = error
        self.codigoPostal = codigoPostal
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
    
    @classmethod
    def crear_tabla_logs(cls):
        insp = inspect(db.engine)
        if not insp.has_table("logs"):
            db.create_all()

    @classmethod
    def eliminar_logs_antiguos(cls, dias):
        """Elimina logs de ingreso que sean más viejos que 'dias' días."""
        fecha_limite = datetime.now() - timedelta(days=dias)

        try:
            logs_antiguos = db.session.query(cls).filter(cls.fecha_log < fecha_limite).all()

            if logs_antiguos:  # Solo eliminar si hay registros
                for log in logs_antiguos:
                    db.session.delete(log)
                
                db.session.commit()
                print(f"{len(logs_antiguos)} logs eliminados con éxito.")

        except SQLAlchemyError as e:
            db.session.rollback()  # Revierte en caso de error
            print(f"Error eliminando logs antiguos: {e}")

        finally:
            db.session.close()  # Asegura que la sesión se cierre siempre

class MerSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "userCuenta", "accountCuenta", "fecha_log", "ip", "funcion", "archivo", "linea", "error", "codigoPostal", "latitude", "longitude", "language")

mer_schema = MerSchema()
mer_schema_many = MerSchema(many=True)  # ✅ Nombre corregido
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
