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
    selector =  Column(String(500), nullable=True)
    tipoEndPointApi = Column(String(500), nullable=True)
    tipoEndPointWs = Column(String(500), nullable=True)
    pyRofexConex = None
   
    
    def __init__(self, id_user: str, cuenta: str, userCuentaBroker: str, passwordCuentaBroker: str, api_url: str, ws_url: str, selector, tipoEndPointApi,tipoEndPointWs):
        self.id_user = id_user
        self.cuenta = cuenta
        self.userCuentaBroker = userCuentaBroker
        self.passwordCuentaBroker = passwordCuentaBroker
        self.api_url = api_url
        self.ws_url = ws_url
        self.selector = selector
        self.tipoEndPointApi = tipoEndPointApi
        self.tipoEndPointWs = tipoEndPointWs
        
      #  self.inicializar_pyrofex()  # Llamamos al método para inicializar pyRofex

    def inicializar_pyrofex(self):
        pyRofexInicializada = pyRofex  # Importamos pyRofex aquí
        if self.selector == 'simulado':
            environments = pyRofexInicializada.Environment.REMARKET
        else:
             environments = pyRofexInicializada.Environment.LIVE
      
       
        try:
            if self.tipoEndPointWs == '':
                pyRofexInicializada._set_environment_parameter(self.tipoEndPointApi, self.api_url, environments)
            else:
                pyRofexInicializada._set_environment_parameter(self.tipoEndPointApi, self.api_url, environments)
                pyRofexInicializada._set_environment_parameter(self.tipoEndPointWs, self.ws_url, environments) 
                
            #    pyRofexInicializada._set_environment_parameter('url','https://api.bull.xoms.com.ar/', environments)
            #    pyRofexInicializada._set_environment_parameter('ws','wss://api.bull.xoms.com.ar/', environments) 
            pyRofexInicializada._set_environment_parameter("proprietary", "PBCP", environments)
            pyRofexInicializada.initialize(user=self.userCuentaBroker, password=self.passwordCuentaBroker, account=self.cuenta, environment=environments)
            self.pyRofexConex = pyRofexInicializada
            return pyRofexInicializada
        except Exception as e:
            # Manejar el error de inicialización de PyRofex según tu lógica de aplicación
            print("Error durante la inicialización de PyRofex:", e)
                