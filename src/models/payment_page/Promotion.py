from sqlalchemy import create_engine, inspect,Column, ForeignKey,Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from utils.db import db
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


ma = Marshmallow()

class Promotion(db.Model):
    __tablename__ = 'promocion'

    id = db.Column(db.Integer, primary_key=True)
    idPlan = db.Column(db.String(255), nullable=True)
    reason = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    cluster = db.Column(db.Integer, nullable=True)
    currency_id = db.Column(db.String(255), nullable=False)
    def __init__(self, idPlan, reason, description, price, discount, image_url, state,cluster,currency_id):
        self.idPlan = idPlan
        self.reason = reason
        self.description = description
        self.price = price
        self.discount = discount
        self.image_url = image_url
        self.state = state
        self.cluster = cluster
        self.currency_id = currency_id

    def __repr__(self):
        return f"Promotion(id={self.id}, idPlan={self.idPlan}, description={self.description}, price={self.price}, reason={self.reason}, discount={self.discount}, image_url={self.image_url}, state={self.state},cluster={self.cluster},currency_id={self.currency_id})"

    @classmethod
    def crear_tabla_promocion(cls):
        try:
            insp = inspect(db.engine)
            if not insp.has_table("promocion"):
                db.create_all()
                print("Tabla 'promocion' creada correctamente.")
            else:
                print("La tabla 'promocion' ya existe en la base de datos.")
        except Exception as e:
            print(f"Error al crear la tabla 'promocion': {str(e)}")
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "idPlan", "description", "price", "reason", "discount", "image_url","state","cluster","currency_id")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

    