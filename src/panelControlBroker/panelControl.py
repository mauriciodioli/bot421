# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
import strategies.datoSheet as datoSheet

panelControl = Blueprint('panelControl',__name__)

@panelControl.route("/panel_control/")
def panel_control():
     ContenidoSheet = datoSheet.leerSheet()
     print(ContenidoSheet)
     datos_desempaquetados = list(ContenidoSheet)[2:]  # Desempaqueta los datos y omite las dos primeras filas
     for dato in ContenidoSheet:
          print( dato)
         
     return render_template("/paneles/panelDeControlBroker.html", datos = datos_desempaquetados)




