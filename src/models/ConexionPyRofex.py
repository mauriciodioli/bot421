from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect,Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import pyRofex
import copy 



class ConexionPyRofex(db.Model):
    
    __tablename__ = 'conexiones_pyrofex'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_url = Column(String(120), unique=True, nullable=True)
    ws_url = Column(String(120), unique=True, nullable=True)
    id_user = Column(String(120), unique=True, nullable=True)
    cuenta = Column(String(500), nullable=True)
    userCuentaBroker = Column(String(500), nullable=True)
    passwordCuentaBroker = Column(String(500), nullable=True)
   
    
    def __init__(self, id_user: str, cuenta: str, userCuentaBroker: str, passwordCuentaBroker: str, api_url: str, ws_url: str):
        self.id_user = id_user
        self.cuenta = cuenta
        self.userCuentaBroker = userCuentaBroker
        self.passwordCuentaBroker = passwordCuentaBroker
        self.api_url = api_url
        self.ws_url = ws_url
        self.inicializar_pyrofex()  # Llamamos al método para inicializar pyRofex

    def inicializar_pyrofex(self):
       
        pyRofexInicializada = pyRofex  # Importamos pyRofex aquí
        environments = pyRofexInicializada.Environment.LIVE
        pyRofexInicializada._set_environment_parameter("url", self.api_url, environments)
        pyRofexInicializada._set_environment_parameter("ws", self.ws_url, environments) 
        pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments)
        pyRofexInicializada.initialize(user=self.userCuentaBroker, password=self.passwordCuentaBroker, account=self.cuenta, environment=environments)
        return pyRofexInicializada
               
                