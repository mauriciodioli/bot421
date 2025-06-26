<<<<<<< HEAD
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
    url = Column(String(120), unique=True, nullable=True)
    ws = Column(String(120), unique=True, nullable=True)   
    user = Column(String(500), nullable=True)
    password = Column(String(500), nullable=True)
    account = Column(String(500), nullable=True)
   
   
    
    def __init__(self,account,user,password,url,ws ):
       
        self.account = account
        self.user = user,
        self.password = password
        self.url = url
        self.ws = ws
      
        
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
            return pyRofexInicializada,environments
        except Exception as e:
            # Manejar el error de inicialización de PyRofex según tu lógica de aplicación
            print("Error durante la inicialización de PyRofex:", e)
=======
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
    url = Column(String(120), unique=True, nullable=True)
    ws = Column(String(120), unique=True, nullable=True)   
    user = Column(String(500), nullable=True)
    password = Column(String(500), nullable=True)
    account = Column(String(500), nullable=True)
   
   
    
    def __init__(self,account,user,password,url,ws ):
       
        self.account = account
        self.user = user,
        self.password = password
        self.url = url
        self.ws = ws
      
        
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
            return pyRofexInicializada,environments
        except Exception as e:
            # Manejar el error de inicialización de PyRofex según tu lógica de aplicación
            print("Error durante la inicialización de PyRofex:", e)
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
                