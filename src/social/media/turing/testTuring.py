# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort    
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambito_usuario import Ambito_usuario


testTuring = Blueprint('testTuring', __name__)

@testTuring.route('/social-media-turing-testTuring', methods=['GET', 'POST'])
def social_media_turing_testTuring():
    try:
        return render_template('media/turing/testTuring.html')
    except Exception as e:
        return str(e)