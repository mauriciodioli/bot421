from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship






ma = Marshmallow()
codigoPostal = Blueprint('codigoPostal', __name__)

class CodigoPostal(db.Model):
    __tablename__ = 'codigo_postal'
    id = db.Column(db.Integer, primary_key=True)
    codigoPostal = db.Column(db.String(20), unique=True, nullable=False)
    ciudad = db.Column(db.String(100), nullable=True)
    pais = db.Column(db.String(100), nullable=True)
    # RELACIÓN con la tabla intermedia
    relaciones_ambito = db.relationship("AmbitoCodigoPostal", backref="codigo_postal", lazy=True)
   

    def __init__(self, codigoPostal, ciudad=None, pais=None):
        self.codigoPostal = codigoPostal
        self.ciudad = ciudad
        self.pais = pais

    def __repr__(self):
        return f"<CodigoPostal id={self.id}, codigoPostal={self.codigoPostal}, ciudad={self.ciudad}, pais={self.pais}>"

    @classmethod
    def crear_tabla_codigo_postal(self):
         insp = inspect(db.engine)
         if not insp.has_table("codigo_postal"):
              db.create_all()

class CodigoPostalSchema(ma.Schema):
    class Meta:       
        fields =("id", "codigoPostal", "ciudad", "pais")# Campos a serializar

codigo_postal_schema = CodigoPostalSchema()
codigos_postales_schema = CodigoPostalSchema(many=True)

from models.publicaciones.ambito_codigo_postal import AmbitoCodigoPostal  # import directo
from models.publicaciones.categoriaCodigoPostal import CategoriaCodigoPostal

