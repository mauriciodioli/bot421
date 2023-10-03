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

panelControl = Blueprint('panelControl',__name__)

@panelControl.route("/panel_control/")
def panel_control():
   
     return render_template("/paneles/panelDeControlBroker.html")
   



