from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import inspect

ma = Marshmallow()

image = Blueprint('image', __name__)

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)   
    colorDescription = db.Column(db.String(255), nullable=False) 
    filepath = db.Column(db.String(500), nullable=True)
    randomNumber = db.Column(db.Integer)
    size = db.Column(db.Float)
    mimetype = db.Column(db.String(255), nullable=True)
    
    # Relación con Public_imagen_video
    #publicaciones_imagen = relationship("Public_imagen_video", back_populates="imagen")
    usuarios = relationship("Usuario", back_populates="imagenes")

    def __init__(self, user_id, title, description, filepath, randomNumber, colorDescription, size,mimetype):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.filepath = filepath
        self.randomNumber = randomNumber
        self.colorDescription = colorDescription
        self.size = size   
        self.mimetype = mimetype 

   
    def __repr__(self):
        return f"Imagen(id={self.id}, user_id={self.user_id}, title={self.title}, description={self.description}, filepath={self.filepath}, randomNumber={self.randomNumber}, colorDescription={self.colorDescription}, size={self.size}, mimetype={self.mimetype})"

    @classmethod
    def crear_tabla_image(cls):
        insp = inspect(db.engine)
        if not insp.has_table("image"):
            cls.__table__.create(db.engine)

class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "title", "description", "filepath", "randomNumber", "colorDescription", "size", "mimetype")

mer_schema = MerShema()
mer_shema = MerShema(many=True)
