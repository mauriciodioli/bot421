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
    publicacion_id = Column(Integer, ForeignKey('usuarios.id'))   
    imagen_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))    
    fecha_creacion = db.Column(db.DateTime)
    imagenes = relationship("Image", back_populates="publicaciones")
    usuarios = relationship("Usuario", back_populates="cuentas")
    publicacion = relationship("Public_imagen_video", back_populates="publicaciones")
    
   
   

    # constructor
    def __init__(self,publicacion_id, imagen_id, video_id,fecha_creacion):
        self.publicacion_id = publicacion_id
        self.imagen_id = imagen_id
        self.video_id = video_id        
        self.fecha_creacion = fecha_creacion
        

    def __repr__(self):
        return f"Public_imagen_video(id={self.id}, imagen_id={self.imagen_id}, video_id={self.video_id}, fecha_creacion={self.fecha_creacion})"

    @classmethod
    def crear_tabla_Public_imagen_video(cls):
        insp = inspect(db.engine)
        if not insp.has_table("publicacion_imagen_video"):
            db.create_all()
            
            
  
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "publicacion_id", "imagen_id", "video_id","fecha_creacion")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

