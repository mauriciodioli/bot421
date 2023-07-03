from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

image = Blueprint('image',__name__) 



class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'))      
    
    title  = db.Column(db.String(255), unique=True, nullable=False)
    description  = db.Column(db.String(255), unique=True, nullable=False)
    filepath  = db.Column(db.String(500), nullable=True)
    #created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
    usuarios = relationship("Usuario", back_populates="imagenes")

    
 # constructor
    def __init__(self, id,user_id,title,description,filepath):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.filepath = filepath
        

   


    def crear_tabla_image(self):
         insp = inspect(db.engine)
         if not insp.has_table("image"):
              db.create_all()
             
    
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id" "title","description","filepath")

mer_schema = MerShema()
mer_shema = MerShema(many=True)