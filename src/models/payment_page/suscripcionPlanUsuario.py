from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import pyRofex
from models.usuario import Usuario
from models.brokers import Broker


ma = Marshmallow()

suscripcionPlanUsuario = Blueprint('suscripcionPlanUsuario', __name__)


class SuscripcionPlanUsuario(db.Model):
    __tablename__ = 'suscripcionPlanUsuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    payer_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    accountCuenta = db.Column(db.String(500))
    status = db.Column(db.String(50))
    reason = db.Column(db.String(255))
    date_created = db.Column(db.String(50))
    preapproval_plan_id = db.Column(db.String(255))
    frequency = db.Column(db.Integer)
    frequency_type = db.Column(db.String(50))
    currency_id = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    billing_day = db.Column(db.Integer)
    quotas = db.Column(db.Integer)
    pending_charge_amount = db.Column(db.Float)
    next_payment_date = db.Column(db.String(50))
    payment_method_id = db.Column(db.String(50))
    card_id = db.Column(db.String(50))
    
    def __init__(self, payer_id, user_id, accountCuenta, status, reason, date_created,
                 preapproval_plan_id, frequency, frequency_type, currency_id, start_date,
                 end_date, billing_day, quotas, pending_charge_amount, next_payment_date,
                 payment_method_id, card_id):
        self.payer_id = payer_id
        self.user_id = user_id
        self.accountCuenta = accountCuenta
        self.status = status
        self.reason = reason
        self.date_created = date_created
        self.preapproval_plan_id = preapproval_plan_id
        self.frequency = frequency
        self.frequency_type = frequency_type
        self.currency_id = currency_id
        self.start_date = start_date
        self.end_date = end_date
        self.billing_day = billing_day
        self.quotas = quotas
        self.pending_charge_amount = pending_charge_amount
        self.next_payment_date = next_payment_date
        self.payment_method_id = payment_method_id
        self.card_id = card_id
    
    def __repr__(self):
        return f"SuscripcionPlanUsuario(id={self.id}, payer_id={self.payer_id}, user_id={self.user_id}, " \
               f"accountCuenta={self.accountCuenta}, status={self.status}, reason={self.reason}, " \
               f"date_created={self.date_created}, preapproval_plan_id={self.preapproval_plan_id}, " \
               f"frequency={self.frequency}, frequency_type={self.frequency_type}, currency_id={self.currency_id}, " \
               f"start_date={self.start_date}, end_date={self.end_date}, billing_day={self.billing_day}, " \
               f"quotas={self.quotas}, pending_charge_amount={self.pending_charge_amount}, " \
               f"next_payment_date={self.next_payment_date}, payment_method_id={self.payment_method_id}, " \
               f"card_id={self.card_id})"
    
    @classmethod
    def crear_tabla_suscripcionPlanUsuario(cls):
        insp = inspect(db.engine)
        if not insp.has_table("suscripcionPlanUsuario"):
            db.create_all() 


class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "payer_id", "user_id", "accountCuenta", "status", "reason", "date_created",
                  "preapproval_plan_id", "frequency", "frequency_type", "currency_id", "start_date",
                  "end_date", "billing_day", "quotas", "pending_charge_amount", "next_payment_date",
                  "payment_method_id", "card_id")


mer_schema = MerShema()
mer_shema = MerShema(many=True)
