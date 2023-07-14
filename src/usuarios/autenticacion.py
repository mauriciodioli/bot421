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
from models.cuentas import Cuenta
from utils.db import db
import jwt


autenticacion = Blueprint("autenticacion", __name__)

# Clave secreta para generar los tokens
SECRET_KEY = 'supersecreto'

# Duración de los tokens
TOKEN_DURATION =   1440 #  24 hs en minutos

#REFRESH_TOKEN_DURATION = 16  # minutos
REFRESH_TOKEN_DURATION = 43200  # minutos

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
    
#sale del sistema completo
@autenticacion.route("/logOutSystem")   
def logOutSystem():
   
   return render_template('usuarios/logOutSystem.html')

# muestra todos los usuarios
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

 # esta es la autenticacion cuando ingresa por app si en caso ya existe el token##################    

@autenticacion.route("/loginIndex", methods=['POST'])
def loginIndex():
    if request.method == 'POST':
        print("intenta crear tablaaaaaaaaaaaaa_____________________   ")
        
        access_token = request.json.get('token')
        refresh_token  = request.json.get('refresh_token')
        selector =request.json.get('selctorEnvironment')
        account = request.json.get('cuenta')
        print("___________________todken   ",access_token)
        if access_token:
            app = current_app._get_current_object()
            try:
                # Decodificar el token y obtener el id del usuario
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                user = Usuario.query.get(user_id)
                print("user ___________",user.correo_electronico)
                print("userid ________________",user_id)
                print("user ________________",user.cuentas[0].userCuenta)
                # Si el usuario existe, redirigirlo a la página de inicio
                if user:
                   #  return redirect(url_for('get_login.loginApi'))
                    # Crear una respuesta que redirige a la ruta autenticacion.loginBroker y enviar el token como parámetro
                    resp = make_response(render_template('home.html', cuenta=[account,user.cuentas[0].userCuenta,selector]))
                    #resp = make_response(render_template('login.html'))
                    set_access_cookies(resp, access_token)
                    set_refresh_cookies(resp, refresh_token)
                    
                   
                    #return resp
                   #resp = make_response('login.html', tokens=[token,refresh_token])
                    return render_template('home.html', cuenta=[account,user,selector])
                #    return jsonify({'redirect': url_for('get_login.loginApi')})

                 
            except jwt.ExpiredSignatureError:
                # Si el token ha expirado, redirigirlo a la página de inicio de sesión
                print("El token ha expirado")
                return redirect(url_for('autenticacion.index'))
            except jwt.InvalidTokenError:
                # Si hay un error decodificando el token, redirigirlo a la página de inicio de sesión
                print("El token es inválido")

        # Si no hay token o el token no es válido, devolver la dirección a la que se debe redirigir
        return render_template('home.html', cuenta=[account,user,selector])
        #return jsonify({'redirect': url_for('get_login.loginApi')})

##################################################################################################

 

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

#aqui se logea el usuario de manera manual y se genera el token y el refresh token y luego se envia para
# ser almacenado en localStorage y en cookies
@autenticacion.route('/loginUsuario', methods=['POST'])
def loginUsuario():
    if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        password = request.form['password']
        # Buscar el usuario en la base de datos
       # crea_tabla_usuario()
        usuario = Usuario.query.filter_by(correo_electronico=correo_electronico).first()
       # print("Valor de password: ", password," usuario.password ",usuario.password)
        if usuario is None or not bcrypt.checkpw(password if isinstance(password, bytes) else password.encode('utf-8'), usuario.password):
            flash('Correo electrónico o contraseña incorrectos', 'danger')
            return redirect(url_for('autenticacion.index'))
        # Iniciar sesión de usuario
       
        login_user(usuario)
        # Generar el token de acceso
        expiry_timestamp = timedelta(minutes=TOKEN_DURATION)
        access_token = create_access_token(identity=usuario.id, expires_delta=expiry_timestamp)
        refresh_token = create_refresh_token(identity=usuario.id, expires_delta=timedelta(minutes=REFRESH_TOKEN_DURATION))
        # Almacenar el refresh token en la base de datos
        usuario.refresh_token = refresh_token       
        db.session.add(usuario)
        db.session.commit()
        
        # Configurar las cookies de JWT
        resp = make_response(render_template('login.html', tokens=[access_token,refresh_token,usuario.correo_electronico,expiry_timestamp,usuario.roll]))
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        # Guardar tokens en localStorage
        db.session.close()
        return resp
     
    

@autenticacion.route('/loginBroker', methods=['POST'])
def loginBroker():
    access_token = request.form['token']
    resp = make_response(render_template('login.html', tokens=[access_token]))
    set_access_cookies(resp, access_token)
    return resp


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

