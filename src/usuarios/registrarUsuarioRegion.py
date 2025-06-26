import secrets
from functools import wraps
from flask import (
    Flask,
    Blueprint,
    request,
    redirect,
    jsonify,
    url_for,
    render_template,
    flash,
    make_response
)
from flask import request, make_response, jsonify

from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    set_access_cookies, 
    set_refresh_cookies,
    get_jwt_identity)


import bcrypt
from datetime import datetime, timedelta

from flask_login import LoginManager, login_required, login_user, UserMixin

import jwt
from flask_dance.consumer import oauth_authorized

from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from requests.exceptions import HTTPError
from models.usuario import Usuario
from datetime import datetime, timedelta
from utils.db import db
from usuarios.autenticacion import autenticacion

# Configuración del Blueprint para el registro de usuarios
registrarUsuarioRegion = Blueprint("registrarUsuarioRegion", __name__)

HCAPTCHA_SECRET_KEY = "cc46341e-6f28-419c-b544-5fc8b4deb302"

@registrarUsuarioRegion.route('/usuarios-registrarUsuarioRegion/', methods=['POST'])
def usuarios_registrarUsuarioRegion(): 
    correo_electronico = request.form['correo_electronico']   
    password = request.form['password'] 
    hcaptcha_response = request.form['h-captcha-response']
    if not hcaptcha_response:
        return jsonify({"error": "Captcha no completado"}), 400 
    
    return render_template('usuarios/registrarUsuarioRegion.html', correo_electronico=correo_electronico, password=password,layout='layout_without_navbar')

