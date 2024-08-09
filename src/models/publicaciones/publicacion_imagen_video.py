from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

publicacion_imagen_video = Blueprint('publicacion_imagen_video', __name__)

class Public_imagen_video(db.Model):
    __tablename__ = 'publicacion_imagen_video'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    publicacion_id = db.Column(db.Integer,nullable=False)
    imagen_id = db.Column(db.Integer,nullable=False)
    video_id = db.Column(db.Integer,nullable=False)
    fecha_creacion = db.Column(db.DateTime)
    
    # Relaciones
    #publicacion = relationship("Publicacion", back_populates="publicacion_imagen_video")
    #imagen = relationship("Imagen", back_populates="publicaciones_imagen")
    #video = relationship("Video", back_populates="publicaciones_video")

  

    def __init__(self, publicacion_id, imagen_id, video_id, fecha_creacion):
        self.publicacion_id = publicacion_id
        self.imagen_id = imagen_id
        self.video_id = video_id        
        self.fecha_creacion = fecha_creacion

    def __repr__(self):
        return f"Public_imagen_video(id={self.id}, publicacion_id={self.publicacion_id}, imagen_id={self.imagen_id}, video_id={self.video_id}, fecha_creacion={self.fecha_creacion})"

    @classmethod
    def crear_tabla_Public_imagen_video(cls):
        insp = inspect(db.engine)
        if not insp.has_table("publicacion_imagen_video"):
            cls.__table__.create(db.engine)
            
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "publicacion_id", "imagen_id", "video_id", "fecha_creacion")

mer_schema = MerShema()
mer_shema = MerShema(many=True)
