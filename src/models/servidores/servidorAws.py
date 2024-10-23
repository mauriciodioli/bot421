from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, DateTime, Float

ma = Marshmallow()

servidorAws = Blueprint('servidorAws', __name__)

class ServidorAws(db.Model):
    __tablename__ = 'servidorAws'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    url = db.Column(db.String(120), unique=True, nullable=True)
    ws_url = db.Column(db.String(120), unique=True, nullable=True)
    direccion_ingreso = db.Column(db.String(500), nullable=True)
    nombre = db.Column(db.String(500), unique=True, nullable=True)
    descripcion = db.Column(db.String(500), nullable=True)
    comentario = db.Column(db.String(500), nullable=True)
    
    # Nuevos atributos
    ip_address = db.Column(db.String(45), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    instance_type = db.Column(db.String(100), nullable=True)
    operating_system = db.Column(db.String(100), nullable=True)
    instance_state = db.Column(db.String(50), nullable=True)
    instance_id = db.Column(db.String(100), unique=True, nullable=False)
    uptime = db.Column(db.Integer, nullable=True)
    cpu_usage = db.Column(db.Float, nullable=True)
    memory_usage = db.Column(db.Float, nullable=True)
    last_status_check = db.Column(DateTime, nullable=True)

    fecha_generacion = db.Column(DateTime)
    hora_generacion = db.Column(DateTime)
    diferencia_horaria = db.Column(Integer)
    hora_clientes = db.Column(DateTime)
    hora_servidor = db.Column(DateTime)
    hora_invierno = db.Column(DateTime)
    hora_verano = db.Column(DateTime)
    estado = db.Column(db.String(500), nullable=True)

    # Constructor actualizado
    def __init__(self, url, ws_url, nombre, descripcion, instance_id, ip_address=None, 
             region=None, instance_type=None, operating_system=None, 
             instance_state=None, uptime=None, cpu_usage=None, 
             memory_usage=None, last_status_check=None, 
             fecha_generacion=None, diferencia_horaria=None, estado=None):

        self.url = url
        self.ws_url = ws_url
        self.nombre = nombre
        self.descripcion = descripcion
        self.ip_address = ip_address
        self.region = region
        self.instance_type = instance_type
        self.operating_system = operating_system
        self.instance_state = instance_state
        self.instance_id = instance_id
        self.uptime = uptime
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.last_status_check = last_status_check
        self.fecha_generacion = fecha_generacion
        self.diferencia_horaria = diferencia_horaria
        self.estado = estado
 # Métodos set para atributos no inicializados
    def set_fecha_generacion(self, fecha_generacion):
        self.fecha_generacion = fecha_generacion

    def set_hora_generacion(self, hora_generacion):
        self.hora_generacion = hora_generacion

    def set_hora_clientes(self, hora_clientes):
        self.hora_clientes = hora_clientes

    def set_hora_servidor(self, hora_servidor):
        self.hora_servidor = hora_servidor

    def set_hora_invierno(self, hora_invierno):
        self.hora_invierno = hora_invierno

    def set_hora_verano(self, hora_verano):
        self.hora_verano = hora_verano

    def set_estado(self, estado):
        self.estado = estado
    # Método __repr__ actualizado
    def __repr__(self):
        return (f"ServidorAws(id={self.id}, url={self.url}, ws_url={self.ws_url}, nombre={self.nombre}, "
                f"descripcion={self.descripcion}, ip_address={self.ip_address}, region={self.region}, "
                f"instance_type={self.instance_type}, operating_system={self.operating_system}, "
                f"instance_id={self.instance_id}, uptime={self.uptime})")

    @classmethod
    def crear_tabla_servidor_aws(cls):
        insp = inspect(db.engine)
        if not insp.has_table("servidorAws"):
            db.create_all()


# Esquema de Marshmallow actualizado
class ServidorAwsSchema(ma.Schema):
    class Meta:
        fields = (
            "id", 
            "url", 
            "ws_url", 
            "nombre", 
            "descripcion", 
            "ip_address", 
            "region", 
            "instance_type", 
            "operating_system", 
            "instance_state", 
            "instance_id", 
            "uptime", 
            "cpu_usage", 
            "memory_usage", 
            "last_status_check", 
            "estado", 
            "fecha_generacion", 
            "diferencia_horaria"
        )

servidor_aws_schema = ServidorAwsSchema()
servidores_aws_schema = ServidorAwsSchema(many=True)
