<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

plan = Blueprint('plan', __name__)


class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    idPlan = db.Column(db.String(120), unique=True, nullable=True) 
    frequency = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(120), nullable=False)
    frequency_type = db.Column(db.String(50), nullable=False) 
    repetitions = db.Column(db.Integer, nullable=False)  
    currency_id = db.Column(db.String(50), nullable=False)      
    billing_day = db.Column(db.Integer, nullable=False)


    # constructor
    def __init__(self, idPlan, frequency, amount, reason, frequency_type, repetitions,currency_id,billing_day):        
        self.idPlan = idPlan
        self.frequency = frequency
        self.amount = amount
        self.reason = reason
        self.frequency_type = frequency_type
        self.repetitions = repetitions
        self.currency_id = currency_id
        self.billing_day = billing_day

    def __repr__(self):
        return f"Cuenta(id={self.id}, idPlan={self.idPlan}, frequency={self.frequency}, amount={self.amount}, reason={self.reason}, frequency_type={self.frequency_type}, repetitions={self.repetitions},currency_id={self.currency_id}, billing_day={self.billing_day})"

    @classmethod
    def crear_tabla_plan(cls):
        insp = inspect(db.engine)
        if not insp.has_table("plan"):
            db.create_all()
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "idPlan", "frequency", "amount", "reason", "frequency_type", "repetitions","currency_id","billing_day")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

=======
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

plan = Blueprint('plan', __name__)


class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    idPlan = db.Column(db.String(120), unique=True, nullable=True) 
    frequency = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(120), nullable=False)
    frequency_type = db.Column(db.String(50), nullable=False) 
    repetitions = db.Column(db.Integer, nullable=False)  
    currency_id = db.Column(db.String(50), nullable=False)      
    billing_day = db.Column(db.Integer, nullable=False)


    # constructor
    def __init__(self, idPlan, frequency, amount, reason, frequency_type, repetitions,currency_id,billing_day):        
        self.idPlan = idPlan
        self.frequency = frequency
        self.amount = amount
        self.reason = reason
        self.frequency_type = frequency_type
        self.repetitions = repetitions
        self.currency_id = currency_id
        self.billing_day = billing_day

    def __repr__(self):
        return f"Cuenta(id={self.id}, idPlan={self.idPlan}, frequency={self.frequency}, amount={self.amount}, reason={self.reason}, frequency_type={self.frequency_type}, repetitions={self.repetitions},currency_id={self.currency_id}, billing_day={self.billing_day})"

    @classmethod
    def crear_tabla_plan(cls):
        insp = inspect(db.engine)
        if not insp.has_table("plan"):
            db.create_all()
        
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "idPlan", "frequency", "amount", "reason", "frequency_type", "repetitions","currency_id","billing_day")


mer_schema = MerShema()
mer_shema = MerShema(many=True)

>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
    