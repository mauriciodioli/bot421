from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

Base = declarative_base()

class Promotion(Base):
    __tablename__ = 'promotions'
    id = db.Column(db.Integer, primary_key=True)
    idPlan = db.Column(db.Integer, nullable=True)
    reason = db.Column(db.String(255), nullable=False) 
    description = db.Column(db.String(255), nullable=False) 
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False) 

   # constructor
    def __init__(self, idPlan, reason, description, price, discount, image_url):        
        self.idPlan = idPlan
        self.description = description
        self.price = price
        self.reason = reason
        self.discount = discount
        self.image_url = image_url
       

    def __repr__(self):
        return f"Cuenta(id={self.id}, idPlan={self.idPlan}, description={self.description}, price={self.price}, reason={self.reason}, discount={self.discount}, image_url={self.image_url})"

    @classmethod
    def crear_tabla_promocion(cls):
        insp = inspect(db.engine)
        if not insp.has_table("promocion"):
            db.create_all()
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "idPlan", "description", "price", "reason", "discount", "image_url")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

    