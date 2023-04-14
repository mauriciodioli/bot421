import os
from flask import current_app
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
import bcrypt
from datetime import datetime, timedelta

from flask_login import LoginManager, login_required, login_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies
    
)
from models.usuario import Usuario
from utils.db import db
import jwt


autenticacion = Blueprint("autenticacion", __name__)

# Clave secreta para generar los tokens
SECRET_KEY = 'supersecreto'

# Duración de los tokens
TOKEN_DURATION = 30  # minutos
REFRESH_TOKEN_DURATION = 60  # minutos

# Inicializar el objeto login_manager
login_manager = LoginManager()
login_manager.init_app(autenticacion)

# Crear la tabla usuarios si no existe
def crea_tabla_usuario():
    usuario = Usuario(
        id=1,
        correo_electronico="ejemplo@ejemplo.com",
        token="1234",
        refresh_token="5678",
        activo=True,
        password="12345678"        
    )
    usuario.crear_tabla()
    print("Tabla creada!")


# Crear las rutas
@autenticacion.route("/usuarios-listado")
def usuarios_listado():
    print("_______________lletaaaaaaaaaaaaaaaa______")
    all_usr = Usuario.query.all()
    print("all_mer", all_usr)
    #return True
    return render_template("usuarios.html", datos=all_usr)


@autenticacion.route("/login/google")
def login_google():
    return google.authorize(callback=url_for("autenticacion.authorized", _external=True))


@autenticacion.route("/login/google/authorized")
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return "Acceso denegado: razón=%s error=%s" % (
            request.args["error_reason"],
            request.args["error_description"],
        )
    access_token = resp["access_token"]
    refresh_token = resp["refresh_token"]
    # Aquí podrías obtener más información del usuario de Google
    # utilizando el access token, como su dirección de correo electrónico
    # y verificar que pertenece a tu dominio (si lo deseas)
    # Luego, puedes crear un nuevo usuario en la base de datos
    # utilizando la información de Google.
    user_info = google.get("userinfo").data
    cursor = db.cursor()
    query = "INSERT INTO usuarios (nombre, correo) VALUES (%s, %s)"
    values = (user_info["name"], user_info["email"])
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    # Generar el access token y el refresh token
    access_token = create_access_token(identity=user_info["email"])
    refresh_token = create_refresh_token(identity=user_info["email"])
    # Configurar las cookies de JWT
    resp = jsonify({"login": True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    # Almacenar el refresh token en localStorage
    resp.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=604800,
        secure=True,
        httponly=True,
        samesite="Strict",
    )
    resp.set_cookie(
        "access_token",
        access_token,
        max_age=1800,
        secure=True,
        httponly=True,
        samesite="Strict",
    )
    return resp

@autenticacion.route("/index")
def index(): 
    
    return render_template('index.html')

     
@autenticacion.route("/loginIndex", methods=['POST'])
def loginIndex():
    if request.method == 'POST':
        token = request.json.get('token')
        print("___________________todken   ",token)
        if token:
            app = current_app._get_current_object()
            try:
                # Decodificar el token y obtener el id del usuario
                user_id = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                user = Usuario.query.get(user_id)
                print("user ___________",user)
                print("userid ________________",user_id)
                # Si el usuario existe, redirigirlo a la página de inicio
                if user:                   
                     return redirect(url_for('get_login.loginApi'))
            except jwt.ExpiredSignatureError:
                # Si el token ha expirado, redirigirlo a la página de inicio de sesión
                print("El token ha expirado")
            except jwt.InvalidTokenError:
                # Si hay un error decodificando el token, redirigirlo a la página de inicio de sesión
                print("El token es inválido")

        # Si no hay token o el token no es válido, renderizar la plantilla de inicio de sesión
        return render_template('login.html')



 

# Ruta para actualizar el access token con un refresh token
@autenticacion.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')

    # Decodificar el refresh token
    username = decode_token(refresh_token)

    # Verificar si el usuario existe
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM usuarios WHERE username=%s', (username,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    # Generar el token y actualizar la base de datos con el nuevo token
    token = generate_token(username)
    with db.cursor() as cursor:
        cursor.execute('UPDATE usuarios SET token=%s WHERE username=%s', (token, username))
        db.commit()

    response = make_response(jsonify({'mensaje': 'Token refrescado'}))
    response.set_cookie('token', token, httponly=True)

    return response




# Ruta protegida por autenticación JWT
@autenticacion.route('/api/protegido')
@jwt_required()
def protegido():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@autenticacion.route('/loginUsuario', methods=['GET', 'POST'])
def loginUsuario():
    if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        password = request.form['password']
        # Buscar el usuario en la base de datos
        usuario = Usuario.query.filter_by(correo_electronico=correo_electronico).first()
        print("Valor de password: ", password," usuario.password ",usuario.password)
        if usuario is None or not bcrypt.checkpw(password if isinstance(password, bytes) else password.encode('utf-8'), usuario.password):
            flash('Correo electrónico o contraseña incorrectos', 'danger')
            return redirect(url_for('autenticacion.login'))
        # Iniciar sesión de usuario
        login_user(usuario)
        # Generar el token de acceso
        access_token = create_access_token(identity=usuario.id, expires_delta=timedelta(minutes=TOKEN_DURATION))
        refresh_token = create_refresh_token(identity=usuario.id, expires_delta=timedelta(minutes=REFRESH_TOKEN_DURATION))
        # Almacenar el refresh token en la base de datos
        usuario.refresh_token = refresh_token       
        db.session.add(usuario)
        db.session.commit()
        # Configurar las cookies de JWT
        resp = make_response(render_template('home.html', tokens=[access_token,refresh_token]))
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp
    return render_template('home.html',tokens=[access_token,refresh_token])

@autenticacion.route('/loginBroker', methods=['GET', 'POST'])
def loginBroker():
    
    return render_template('errorLogueo.html')

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


@login_manager.unauthorized_handler
def unauthorized():
    # redirigir al usuario a la página de inicio de sesión
    flash('Debes iniciar sesión para acceder a esta página.')
    return redirect(url_for('login'))
# Funciones de utilidad

def generate_token(username):
    """Genera un token JWT."""
    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=TOKEN_DURATION),
        'iat': datetime.utcnow(),
        'sub': username
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
    return token

def generate_refresh_token(username):
    """Genera un token de refresco JWT."""
    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_DURATION),
        'iat': datetime.utcnow(),
        'sub': username
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
    return token

