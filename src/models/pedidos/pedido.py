from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime


ma = Marshmallow()

pedido = Blueprint('pedido', __name__)

class Pedido(db.Model):
    __tablename__ = 'pedido'
    
    # Atributos del modelo Pedido
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    publicacion_id = db.Column(db.Integer, nullable=False)
   
    ambito = db.Column(String(50), nullable=True)  # Por ejemplo, "nacional" o "internacional"
    estado = db.Column(String(50), nullable=True)  # Por ejemplo, "pendiente", "completado", "cancelado"
    fecha_pedido = db.Column(DateTime, default=datetime.utcnow)  # Fecha del pedido
    fecha_entrega = db.Column(DateTime, nullable=True)  # Fecha estimada de entrega
    fecha_consulta = db.Column(DateTime, nullable=True)  # Fecha de consulta (si aplica)
    fecha_baja = db.Column(DateTime, nullable=True)  # Fecha de baja (si aplica)
    lugar_entrega = db.Column(String(255), nullable=True)  # Dirección de entrega
    
    cantidad = db.Column(Integer, nullable=False, default=1)  # Cantidad pedida
    precio_costo = db.Column(Float, nullable=True)  # Precio de costo
    precio_venta = db.Column(Float, nullable=True)  # Precio de venta
    ganancia = db.Column(Float, nullable=True)  # Ganancia calculada
    diferencia = db.Column(Float, nullable=True)  # Diferencia entre precios
    
    nombre_producto = db.Column(String(255), nullable=True)  # Nombre del producto
    descripcion = db.Column(Text, nullable=True)  # Descripción del pedido
    consulta = db.Column(Text, nullable=True)  # Texto de consulta del cliente
    respuesta = db.Column(Text, nullable=True)  # Respuesta a la consulta
        
    asignado_a = db.Column(String(255), nullable=True)  # Persona o equipo asignado al pedido
    tamaño = db.Column(String(50), nullable=True)  # Tamaño del producto (si aplica)
    pais = db.Column(String(100), nullable=True)  # País de entrega
    provincia = db.Column(String(100), nullable=True)  # Provincia o estado
    region = db.Column(String(100), nullable=True)  # Región (si aplica)
    sexo = db.Column(String(20), nullable=True)  # Información del cliente, si es relevante
    imagen = db.Column(String(255), nullable=True)
    
    nombreCliente = db.Column(String(255), nullable=True)
    apellidoCliente = db.Column(String(255), nullable=True)
    emailCliente = db.Column(String(255), nullable=True)
    telefonoCliente = db.Column(String(255), nullable=True)
    comentarioCliente = db.Column(Text, nullable=True)
    emailCliente = db.Column(String(255), nullable=True)
    cluster_id = db.Column(Integer, nullable=True)
    pagoOnline = db.Column(db.Boolean, default=True)
    
    
    # Constructor
    def __init__(self, user_id, publicacion_id, **kwargs):
        self.user_id = user_id
        self.publicacion_id = publicacion_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Representación para debugging
    def __repr__(self):
        return (
            f"<Pedido(id={self.id}, user_id={self.user_id}, publicacion_id={self.publicacion_id}, "
            f"estado={self.estado}, fecha_pedido={self.fecha_pedido},pagoOnline={self.pagoOnline})>"
        )

# Esquema para serialización
class PedidoSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "user_id", "publicacion_id", "ambito", "estado", "fecha_pedido",
            "fecha_entrega", "lugar_entrega", "cantidad", "precio_costo", "precio_venta",
            "ganancia", "diferencia", "nombre_producto", "descripcion", "consulta", "respuesta",
            "asignado_a", "tamaño", "pais", "provincia", "region", "sexo","imagen","pagoOnline"
        )

# Instancias del esquema
pedido_schema = PedidoSchema()
pedidos_schema = PedidoSchema(many=True)

