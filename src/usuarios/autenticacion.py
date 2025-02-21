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
from routes.api_externa_conexion.cuenta import cuenta
from utils.db import db
import jwt
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
from panelControlBroker.panelControl import terminaConexionParaActualizarSheet

autenticacion = Blueprint("autenticacion", __name__)

# Clave secreta para generar los tokens
SECRET_KEY = 'supersecreto'

# Duración de los tokens
#TOKEN_DURATION =   3 #  24 hs en minutos
TOKEN_DURATION =   1440 #  24 hs en minutos

#REFRESH_TOKEN_DURATION = 16  # minutos
REFRESH_TOKEN_DURATION = 43200  # minutos

# Inicializar el objeto login_manager
login_manager = LoginManager()
login_manager.init_app(autenticacion)

    
#sale del sistema completo
@autenticacion.route("/logOutSystem", methods=['POST'])   
def logOutSystem():   
   if request.method == 'POST':
        try:
            access_token = request.form['autenticacion_access_token']
            refreshToken = request.form['autenticacion_refresh_token']
            account = request.form['autenticacion_accounCuenta']
            layouts = request.form['layoutOrigen']

            # Intenta obtener pyRofexInicializada del diccionario
            try:
                pyRofexInicializada = get.ConexionesBroker[account]['pyRofex']
            except KeyError:
                # Si la clave no existe en el diccionario, pyRofexInicializada será None
                pyRofexInicializada = None

            if access_token and Token.validar_expiracion_token(access_token=access_token): 
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
       
            if pyRofexInicializada is not None:
                if access_token and Token.validar_expiracion_token(access_token=access_token):
                    
                    if account == get.CUENTA_ACTUALIZAR_SHEET:
                         terminaConexionParaActualizarSheet(get.CUENTA_ACTUALIZAR_SHEET)
                    else:    
                        pyRofexInicializada.close_websocket_connection(environment=account)
                        del get.ConexionesBroker[account]
                    get.actualiza_luz_web_socket('',account, '',False)
                    return render_template('usuarios/logOutSystem.html')
            else:
                # pyRofexInicializada es None, lo que significa que no se encontró en el diccionario
                return render_template('usuarios/logOutSystem.html')
        except Exception as e:
            # Manejo de otros tipos de excepciones
            return render_template('error.html', message='Ocurrió un error: {}'.format(str(e)))

    # Manejar caso de que el método de la solicitud no sea POST
   return render_template('error.html', message='Método de solicitud no permitido')

       

# muestra todos los usuarios
@autenticacion.route("/usuarios-listado")
def usuarios_listado():   
    all_usr = Usuario.query.all()    
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


@autenticacion.route("/home", methods=['POST'])
def home():
     if request.method == 'POST':
        
        access_token = request.json.get('token')
        refresh_token  = request.json.get('refresh_token')
        selector = request.json.get('selectorEnvironment')
        account = request.json.get('account')
        cuenta = [account,selector,access_token]
        return render_template('home.html', cuenta = cuenta)
    
 # esta es la autenticacion cuando ingresa por app si en caso ya existe el token##################    

@autenticacion.route("/loginIndex", methods=['POST'])
def loginIndex():
    if request.method == 'POST':
       
        
        access_token = request.json.get('token')
        refresh_token  = request.json.get('refresh_token')
        selector = request.json.get('selectorEnvironment')
        account = request.json.get('account')
        #print("___________________token   ", access_token)
        
        
        if access_token:
            app = current_app._get_current_object()             
########################## logica para entrar de nuevo sin tener que logear nuevamente #################################3333             
             #return procesar_login(access_token, refresh_token, selector, account)
            try:
                # Decodificar el token y obtener el id del usuario
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                user = Usuario.query.get(user_id)
                if len(user.cuentas) > 0:
                    user_cuenta = user.cuentas[0].userCuenta
                    # do something with user_cuenta
                else:
                    user_cuenta ='null'
              
                
                # Si el usuario existe, redirigirlo a la página de inicio
                if user:
                    # return render_template('cuentas/panelDeControlBroker.html', cuenta=[account,user,selector])
                    resp = make_response(jsonify({'redirect': 'home', 'cuenta': account, 'userCuenta': user_cuenta, 'selector': selector}))
                    resp.headers['Content-Type'] = 'application/json'
                    set_access_cookies(resp, access_token)
                    set_refresh_cookies(resp, refresh_token)
                    return resp
                    #return render_template('cuentas/panelDeControlBroker.html', cuenta=[account,user,selector])
                    
            except jwt.ExpiredSignatureError:
                # Si el token ha expirado, redirigirlo a la página de inicio de sesión
                print("El token ha expirado")
                return redirect(url_for('autenticacion.index'))
            except jwt.InvalidTokenError:
                # Si hay un error decodificando el token, redirigirlo a la página de inicio de sesión
                print("El token es inválido")
        
        # Si no hay token válido o el usuario no existe, mostrar un mensaje de error o redirigir a otra página
        return render_template('error.html', error_message="Error de autenticación")


##################################################################################################

 

# Ruta para actualizar el access token con un refresh token
@autenticacion.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')

    # Decodificar el refresh token
    username = refresh_token.decode_token(refresh_token)

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
        db.session.commit()
        db.session.close()

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

@contextmanager
def session_scope():
    """Proporciona un alcance de sesión que se maneja automáticamente."""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
#aqui se logea el usuario de manera manual y se genera el token y el refresh token y luego se envia para
# ser almacenado en localStorage y en cookies
@autenticacion.route('/loginUsuario', methods=['POST'])
def loginUsuario():
    if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        password = request.form['password']

        # Consolidar la consulta dentro de un solo contexto de sesión
        with session_scope() as session:
            usuario = session.query(Usuario).filter_by(correo_electronico=correo_electronico).first()
            
            # Validar usuario y contraseña
            if usuario is None or not bcrypt.checkpw(password.encode('utf-8'), usuario.password):
                flash('Correo electrónico o contraseña incorrectos', 'danger')
                return redirect(url_for('autenticacion.index'))

            # Iniciar sesión de usuario
            login_user(usuario)

            # Generar tokens de acceso y refresco
            expiry_timestamp = timedelta(minutes=TOKEN_DURATION)
            access_token = create_access_token(identity=usuario.id, expires_delta=expiry_timestamp)
            refresh_token = create_refresh_token(identity=usuario.id, expires_delta=timedelta(minutes=REFRESH_TOKEN_DURATION))

            # Almacenar el refresh token en la base de datos
            usuario.refresh_token = refresh_token
            session.add(usuario)  # Usa `session.add` en lugar de `db.session.add`
            session.commit()      # Usa `session.commit` en lugar de `db.session.commit`

            # Configurar las cookies de JWT y respuesta
            if access_token:
                app = current_app._get_current_object()
                try:
                    cuenta = ''
                    selector = 'vacio'
                    user = ''
                    
                    resp = make_response(render_template('home.html', tokens=[access_token, refresh_token, usuario.correo_electronico, expiry_timestamp, usuario.roll, cuenta, selector, user, usuario.id]))
                    set_access_cookies(resp, access_token)
                    set_refresh_cookies(resp, refresh_token)
                    return resp

                except Exception as e:
                    session.rollback()  # Hacer rollback de la sesión en caso de error
                    print("Error al generar la respuesta:", str(e))
                    flash('Ocurrió un error, intenta nuevamente', 'danger')
                    return redirect(url_for('autenticacion.index'))

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

