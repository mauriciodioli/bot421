<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String

ma = Marshmallow()

newsLetter = Blueprint('newsLetter', __name__)

class NewLetter(db.Model):
    __tablename__ = 'newsLetter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, correo_electronico):
        self.correo_electronico = correo_electronico

    def __repr__(self):
        return f"NewLetter(correo_electronico={self.correo_electronico})"

    @classmethod
    def crear_tabla_newsLetter(cls):
        insp = inspect(db.engine)
        if not insp.has_table("newsLetter"):
            db.create_all()

class NewLetterSchema(ma.Schema):
    class Meta:
        fields = ("id", "correo_electronico")

new_letter_schema = NewLetterSchema()
new_letters_schema = NewLetterSchema(many=True)
=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String

ma = Marshmallow()

newsLetter = Blueprint('newsLetter', __name__)

class NewLetter(db.Model):
    __tablename__ = 'newsLetter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, correo_electronico):
        self.correo_electronico = correo_electronico

    def __repr__(self):
        return f"NewLetter(correo_electronico={self.correo_electronico})"

    @classmethod
    def crear_tabla_newsLetter(cls):
        insp = inspect(db.engine)
        if not insp.has_table("newsLetter"):
            db.create_all()

class NewLetterSchema(ma.Schema):
    class Meta:
        fields = ("id", "correo_electronico")

new_letter_schema = NewLetterSchema()
new_letters_schema = NewLetterSchema(many=True)
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
