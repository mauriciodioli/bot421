<<<<<<< HEAD
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
import tokens.token as Token
import jwt
import asyncio
from models.usuario import Usuario
from models.brokers import Broker
from models.modelMedia.TelegramNotifier import TelegramNotifier
from collections import defaultdict



dpi = Blueprint('dpi',__name__)


@dpi.route('/dpi-in')
def dpi_in():
=======
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
import tokens.token as Token
import jwt
import asyncio
from models.usuario import Usuario
from models.brokers import Broker
from models.modelMedia.TelegramNotifier import TelegramNotifier
from collections import defaultdict



dpi = Blueprint('dpi',__name__)


@dpi.route('/dpi-in')
def dpi_in():
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
    return render_template('dpis/dpi.html')