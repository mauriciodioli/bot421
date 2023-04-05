import os
import secrets
from flask import Flask, Blueprint,request, redirect, jsonify, url_for,render_template,flash
from flask_dance.contrib.google import make_google_blueprint, google
from functools import wraps
from flask_login import login_required,LoginManager,login_user,UserMixin
from models.usuario import Usuario
from utils.db import db



autenticacion = Blueprint('autenticacion',__name__)


# Inicializar el objeto login_manager
login_manager = LoginManager()
login_manager.init_app(autenticacion)

def creaTablaUsuario():
    usuario = Usuario(id=1, correo_electronico='ejemplo@ejemplo.com', token='1234', refresh_token='5678', activo=True)
    
    # crear la tabla usuarios si no existe
    usuario.crear_tabla()
    return print('Tabla creada!')
    
   

 #Creating  Routes
@autenticacion.route("/usuarios-listado")
def usuarios_listado(): 
  
   all_usr = usuario.query.all()
   print("all_mer",all_usr)  
   return render_template('usuarios.html', datos = all_usr)

# Ruta para el registro con autenticación de Google
@autenticacion.route('/registro-google')
@login_required
def registro_google():
    creaTablaUsuario()
    return True
   

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not google.authorized:
            return redirect(url_for("google.login"))
        return f(*args, **kwargs)
    return decorated_function


@autenticacion.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

# Creamos una clase de usuario que hereda de UserMixin
class User(UserMixin):
    def __init__(self, id, email, token, refresh_token, active=True):
        self.id = id
        self.email = email
        self.token = token
        self.refresh_token = refresh_token
        self.active = active

# Creamos la función de carga de usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    # redirigir al usuario a la página de inicio de sesión
    flash('Debes iniciar sesión para acceder a esta página.')
    return redirect(url_for('login'))