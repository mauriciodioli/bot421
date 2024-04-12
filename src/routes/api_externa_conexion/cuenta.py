# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app,session

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.brokers import Broker




cuenta = Blueprint('cuenta',__name__)

# Crear la tabla cuenta si no existe
def crea_tabla_cuenta():
    cuenta = Cuenta(    
        id=1,
        user_id = "1",
        userCuenta="mauriciodioli6603",
        passwordCuenta="zbwitW5#",
        accountCuenta="REM6603",
        selector="simulado"                
    )
    cuenta.crear_tabla_cuentas()
    print("Tabla creada!")



@cuenta.route("/cuentas",  methods=["GET"])
def cuentas():
   
   
   try:
      if request.method == 'GET': 
   ####   AQUI TENGO QUE COMPARA LA FECHA ####     
      
         infoCuenta = obtenerCuenta()
         print(infoCuenta)
         
         return render_template("cuenta.html",datos = infoCuenta)
   except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
        return render_template("errorLogueo.html" ) 
     ##~######datos de la cuenta

def obtenerSaldoCuenta(objetoCuentaConexion):
  # print("_______________obtenerSaldoCuenta__________________")
   objetoCuentaConexion.tipoEndPointWs = ''
   pyRofex_inicializado = objetoCuentaConexion.inicializar_pyrofex()
   resumenCuenta = pyRofex_inicializado.get_account_report(account=cuenta.cuenta)
   return resumenCuenta["accountData"]["availableToCollateral"]
##################obtenerSaldoCuenta#######VIEJO QUEDARA OBSOLETO########
def obtenerSaldoCuenta(cuenta):  
   resumenCuenta = get.pyRofexInicializada.get_account_report(account=cuenta)
   return resumenCuenta["accountData"]["availableToCollateral"]

def obtenerCuenta(cuenta=None):
   
           
   resumenCuenta = get.pyRofexInicializada.get_account_report(account=cuenta)
   return resumenCuenta

@cuenta.route("/cuenta_posicion_cuenta", methods=['POST'])
def cuenta_posicion_cuenta():
     try:
                 
        access_token = request.form['access_token_form_posicionCuenta'] 
        layouts = request.form['layoutOrigen']  
        cuenta = request.form['accounCuenta_form_posicionCuenta']
        selector = request.form['selector_form_posicionCuenta']      
            
        if access_token:
            user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
      
            for key, conexion_pyrofex in get.ConexionesBroker.items():
   
               id_usuario, accountCuenta, environments = key
             #  print(f"id_user: {id_usuario}, cuenta: {accountCuenta}, environments: {environments}")
               if id_usuario == user_id and accountCuenta == cuenta:
               
                  print(f" dentro del if id_user: {id_usuario}, cuenta: {accountCuenta}")
              
                  pyRofex_inicializado = conexion_pyrofex.inicializar_pyrofex()
                  respuesta_cuenta = pyRofex_inicializado.get_account_position(account=conexion_pyrofex.cuenta, environment=environments)
                  reporte = respuesta_cuenta['positions']  
                  if reporte!=None:                       
                        return render_template("cuentas/cuentaPosicion.html",datos = reporte)
        else:
          return render_template("notificaciones/noPoseeDatos.html")
     except:  
        print("contraseña o usuario incorrecto")  
        flash('No registra posicion')    
          
     return render_template("notificaciones/noPoseeDatos.html" )

@cuenta.route("/cuenta_detalle_cuenta", methods=['POST'])
def cuenta_detalle_cuenta():
   try:          
        access_token = request.form['access_token_form_detalleCuenta'] 
        layouts = request.form['layoutOrigen']  
        cuenta = request.form['accounCuenta_form_detalleCuenta']
        selector = request.form['selector_form_detalleCuenta']      
            
        if access_token:
            user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
      
            for key, conexion_pyrofex in get.ConexionesBroker.items():
   
               id_usuario, accountCuenta, environments = key
             #  print(f"id_user: {id_usuario}, cuenta: {accountCuenta}, environments: {environments}")
               if id_usuario == user_id and accountCuenta == cuenta:
               
                  print(f" dentro del if id_user: {id_usuario}, cuenta: {accountCuenta}")
              
                  pyRofex_inicializado = conexion_pyrofex.inicializar_pyrofex()
                 # respuesta_cuenta = conexion_pyrofex.pyRofexConex.get_account_report(account=conexion_pyrofex.cuenta, environment=environments)
                  respuesta_cuenta = pyRofex_inicializado.get_account_report(account=conexion_pyrofex.cuenta, environment=environments)
                  reporte = respuesta_cuenta['accountData']
                  if reporte!=None:
                     available_to_collateral = reporte['availableToCollateral']
                     portfolio = reporte['portfolio']
        
        return render_template("cuentas/cuentaDetalles.html",datos = reporte)
     
   except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
          
   return render_template("notificaciones/noPoseeDatos.html" )


@cuenta.route("/reporteCuenta")
def reporteCuenta():
   try:        
        #repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        #reporte = repuesta_cuenta['accountData']
        
        #print("detalle cuentaaaaaaaaaaaaaaaaaaaaaa ",reporte)
        #return render_template("cuentas/cuenta.html",datos = reporte)
        return render_template("notificaciones/noPoseeDatos.html" )
   except:  
      print("contraseña o usuario incorrecto")  
      flash('Loggin Incorrect')    
      return render_template("login.html" )
   
@cuenta.route("/registrar_cuenta_broker")
def registrar_cuenta_broker():
   
   return render_template("cuentas/registrarCuentaBroker.html")

@cuenta.route("/cuentas_de_broker_usuario_")
def cuentas_de_broker_usuario_():
     todasLasCuentas =  get_cuentas_de_broker_usuario()
     return render_template('cuentasDeUsuario.html', datos=todasLasCuentas)
    
@cuenta.route("/registrar_cuenta",  methods=["POST"])
def registrar_cuenta():
   if request.method == 'POST':
         todasLasCuentas = []
       
         access_token = request.form['access_token']
         correo_electronico  = request.form['correo_electronico']
         
         userCuenta = request.form['usuario']
         passwordCuenta = request.form['contraseña']
         accountCuenta = request.form['cuenta']
         selector = request.form['environment']
         
          # Aquí recibimos los campos broker_id y broker_nombre
         broker_id = request.form['broker_id']
         broker_nombre = request.form['broker_nombre']
        
         # Codificar las cadenas usando UTF-8
         userCuenta_encoded = userCuenta.encode('utf-8')
         passwordCuenta_encoded = passwordCuenta.encode('utf-8')
         accountCuenta_encoded = accountCuenta.encode('utf-8')

         if access_token:
            app = current_app._get_current_object()
            
            try:
               user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
               #crea_tabla_cuenta()
               
               usuario = Usuario.query.get(user_id)  # Obtener el objeto Usuario correspondiente al user_id
              
               if selector == '1':
                  selectorStr = 'simulado'
               else: 
                  selectorStr = 'produccion'
               
               cuenta = Cuenta( 
                     id=None,   
                     user_id=user_id,
                     userCuenta=userCuenta_encoded,
                     passwordCuenta=passwordCuenta_encoded,
                     accountCuenta=accountCuenta_encoded,
                     broker_id=broker_id,
                     selector=selectorStr              
                     )
               cuenta.user = usuario  # Asignar el objeto Usuario a la propiedad user de la instancia de Cuenta
               db.session.add(cuenta)  # Agregar la instancia de Cuenta a la sesión
               db.session.commit()  # Confirmar los cambios
               db.session.close()
              
               todasLasCuentas = get_cuentas_de_broker(user_id)
               print("Cuenta registrada exitosamente!")
               print("Cuenta registrada usuario id !",user_id)
               for cuenta in todasLasCuentas:
                  print(cuenta['accountCuenta'])
                  passwordCuenta = cuenta['passwordCuenta']
                  passwordCuenta_decoded = passwordCuenta.decode('utf-8')
                  print(passwordCuenta_decoded)

            except Exception as e:               
                db.session.rollback()  # Hacer rollback de la sesión
                db.session.close()
                flash('"No se pudo registrar la cuenta, la cuenta ya tiene usuario asignado.')
                print("No se pudo registrar la cuenta, la cuenta ya tiene usuario asignado.",e)
                
    
   return render_template('cuentas/registrarCuentaBroker.html')

@cuenta.route("/registro-Cuenta-administracion/",  methods=["POST"])
def registrar_cuenta_administracion():
   if request.method == 'POST':
         todasLasCuentas = []
         correo_electronico = request.form['userSistema']
         userCuenta = request.form['userCuentaBroker']
         passwordCuenta = request.form['passwordCuentaBroker']
         accountCuenta = request.form['accountCuentaBroker']
         print("___________cuentas___________userCuenta",userCuenta)
        
         print("___________cuentas___________accountCuenta",accountCuenta)
         print("___________cuentas___________correo_electronico",correo_electronico)
         # Codificar las cadenas usando UTF-8
         userCuenta_encoded = userCuenta.encode('utf-8')
         passwordCuenta_encoded = passwordCuenta.encode('utf-8')
         accountCuenta_encoded = accountCuenta.encode('utf-8')

         crea_tabla_cuenta()
         try:     
            usuario = Usuario.query.filter_by(correo_electronico=correo_electronico).first()  # Obtener el objeto Usuario correspondiente al user_id

            cuenta = Cuenta( 
                        id=None,   
                        user_id=usuario.id,
                        userCuenta=userCuenta_encoded,
                        passwordCuenta=passwordCuenta_encoded,
                        accountCuenta=accountCuenta_encoded                
                        )
          
            db.session.add(cuenta)  # Agregar la instancia de Cuenta a la sesión
            db.session.commit()  # Confirmar los cambios
            db.session.refresh(cuenta)  # Actualizar la instancia desde la base de datos para obtener el ID generado
            cuenta_id = cuenta.id  # Obtener el ID generado
           
            print("Auomatico registrada exitosamente!")
            print("automatico registrada usuario id !",cuenta_id)
         #   todasLasCuentas = get_cuentas_de_broker(user_id)
            
            cuentasBroker = db.session.query(Cuenta).all()
            
            db.session.close()
            print("Cuenta registrada exitosamente!")            

            return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentasBroker)
             
         except:               
                db.session.rollback()  # Hacer rollback de la sesión
                db.session.close()
                print("No se pudo registrar la cuenta.")
                return 'problemas con la base de datos'
  

def get_cuentas_de_broker(user_id):
    
    todasCuentas = []
    try:
        # Obtener el objeto Usuario correspondiente al user_id
        usuario = Usuario.query.get(user_id)         
        # Buscar todas las cuentas asociadas a ese usuario       
        cuentas = db.session.query(Cuenta).filter(Cuenta.user_id == user_id).all()

        # Obtener todos los IDs de los brokers asociados a las cuentas
        broker_ids = [cuenta.broker_id for cuenta in cuentas if cuenta.broker_id is not None]

        # Obtener todos los brokers correspondientes a los IDs obtenidos
        brokers = db.session.query(Broker).filter(Broker.id.in_(broker_ids)).all()

       # Crear un diccionario que mapee IDs de broker a nombres de broker
        id_nombre_broker = {broker.id: broker.nombre for broker in brokers}
     
        
        if cuentas:
         print("El usuario", usuario.correo_electronico, "tiene las siguientes cuentas asociadas:")
         for cuenta in cuentas:
            password_cuenta = cuenta.passwordCuenta.decode('utf-8')
            
            # Obtener el nombre del broker asociado a esta cuenta (si existe)
            nombre_broker = id_nombre_broker.get(cuenta.broker_id)
            
            todasCuentas.append({
                  'id': cuenta.id,
                  'accountCuenta': cuenta.accountCuenta,
                  'userCuenta': cuenta.userCuenta,
                  'passwordCuenta': password_cuenta,
                  'selector': cuenta.selector,
                  'broker_id': cuenta.broker_id,
                  'nombre_broker': nombre_broker  # Agregar el nombre del broker
            })
            
            print(cuenta.accountCuenta)  
        else:
            print("El usuario", usuario.nombre, "no tiene ninguna cuenta asociada.")
    except:
        print("No se pudo obtener las cuentas del usuario.")
    db.session.close()
    return todasCuentas




@cuenta.route("/get_cuentas_de_broker_usuario",  methods=["POST"])   
def get_cuentas_de_broker_usuario():
     if request.method == 'POST':
         
         access_token = request.form['access_token']
         todasLasCuentas = []
         if access_token:
            app = current_app._get_current_object()
            
            try:
               user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']

              # user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                # Obtener el objeto Usuario correspondiente al user_id
               usuario = Usuario.query.get(user_id)         
              # Buscar todas las cuentas asociadas a ese usuario
               cuentas = db.session.query(Cuenta).join(Usuario).filter(Cuenta.user_id == user_id).all()
               # Obtener el objeto Usuario correspondiente al user_id     

               # Obtener todos los IDs de los brokers asociados a las cuentas
               broker_ids = [cuenta.broker_id for cuenta in cuentas if cuenta.broker_id is not None]

               # Obtener todos los brokers correspondientes a los IDs obtenidos
               brokers = db.session.query(Broker).filter(Broker.id.in_(broker_ids)).all()

               # Crear un diccionario que mapee IDs de broker a nombres de broker
               id_nombre_broker = {broker.id: broker.nombre for broker in brokers}
     
        
               if cuentas:
                  print("El usuario", usuario.correo_electronico, "tiene las siguientes cuentas asociadas:")
                  for cuenta in cuentas:
                     password_cuenta = cuenta.passwordCuenta.decode('utf-8')
                     
                     # Obtener el nombre del broker asociado a esta cuenta (si existe)
                     nombre_broker = id_nombre_broker.get(cuenta.broker_id)
                     
                     todasLasCuentas.append({
                           'id': cuenta.id,
                           'accountCuenta': cuenta.accountCuenta,
                           'userCuenta': cuenta.userCuenta,
                           'passwordCuenta': password_cuenta,
                           'selector': cuenta.selector,
                           'broker_id': cuenta.broker_id,
                           'nombre_broker': nombre_broker  # Agregar el nombre del broker
                     })
                     
                     print(cuenta.accountCuenta)  
               else:
                  print("El usuario", usuario.nombre, "no tiene ninguna cuenta asociada.")
                  flash('No registra cuenta para el usuario: ',usuario.nombre)
                  return render_template("cuentas/registrarCuentaBroker.html")
                  
         
    
       
            except Exception as e:
                     print("Error:", str(e))
                     print("No se pudo registrar la cuenta.")
                     db.session.rollback()  # Hacer rollback de la sesión
                     return render_template("errorLogueo.html")
     db.session.close()
     return render_template('cuentas/cuentasDeUsuario.html', datos=todasLasCuentas)
  
@cuenta.route("/get_cuentas_de_broker_usuario_Abm",  methods=["POST"])   
def get_cuentas_de_broker_usuario_Abm():
     if request.method == 'POST':
       
         access_token = request.form['access_token_form_Abm']
         todasLasCuentas = []
         if access_token:
            app = current_app._get_current_object()
            
            try:
               user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']

              # user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                # Obtener el objeto Usuario correspondiente al user_id
               usuario = Usuario.query.get(user_id)         
              # Buscar todas las cuentas asociadas a ese usuario
               cuentas = db.session.query(Cuenta).join(Usuario).filter(Cuenta.user_id == user_id).all()

               if cuentas:
                  print("El usuario", usuario.correo_electronico, "tiene las siguientes cuentas asociadas:")
                  
                  for cuenta in cuentas:
                   todasLasCuentas.append(cuenta.accountCuenta)
                   password_cuenta = cuenta.passwordCuenta.decode('utf-8')
                   todasLasCuentas.append({'id': cuenta.id, 'accountCuenta': cuenta.accountCuenta,'userCuenta':cuenta.userCuenta,'passwordCuenta':password_cuenta})
     
                   print(cuenta.accountCuenta)	
                  
                
               else:
                  print("El usuario", usuario.nombre, "no tiene ninguna cuenta asociada.")
                  flash('No registra cuenta para el usuario: ',usuario.nombre)
                  return render_template("cuentas/registrarCuentaBroker.html")
                  
         
    
       
            except:
                     print("No se pudo registrar la cuenta.")
                     db.session.rollback()  # Hacer rollback de la sesión
                     return render_template("errorLogueo.html")
     db.session.close()
     return render_template('cuentas/cuentasDeUsuarioAbm.html', datos=todasLasCuentas)
  
@cuenta.route("/delete_cuenta_usuario_broker",  methods=["POST"])   
def delete_cuenta_usuario_broker():
    try:
         if request.method == 'POST':
            id = request.form['id']            
            dato = Cuenta.query.get(id)
            print(dato)
            db.session.delete(dato)
            db.session.commit()
            flash('Operation Removed successfully')
            all_cuenta = db.session.query(Cuenta).all()
            db.session.close()
            return render_template("cuentas/cuentasDeUsuario.html", datos =  all_cuenta)
    except: 
            flash('Operation No Removed')       
            all_ins = db.session.query(Cuenta).all()
            db.session.close()
            
            return render_template('cuentas/cuentasDeUsuario.html', datos=all_cuenta) 
         
@cuenta.route("/logOutAccount")   
def logOutAccount():   
   get.diccionario_global_operaciones = {}
   get.diccionario_operaciones_enviadas = {}
   return render_template('cuentas/logOutAccount.html')

def get_pass_cuenta_de_broker(user_id,account):
        todasCuentas = []
        from models.cuentas import Cuenta
        try:
            
            todasLasCuentas = Cuenta.query.filter_by(user_id=user_id).all()
            broker_ids = [todasLasCuentas.broker_id for todasLasCuentas in todasLasCuentas if todasLasCuentas.broker_id is not None]
            brokers = Broker.query.filter(Broker.id.in_(broker_ids)).all()
            id_nombre_broker = {broker.id: broker.nombre for broker in brokers}
            if todasLasCuentas:
                for cuenta in todasLasCuentas:
                    password_cuenta = cuenta.passwordCuenta  # No es necesario decodificar la contraseña aquí
                    nombre_broker = id_nombre_broker.get(cuenta.broker_id)
                    todasCuentas.append({
                        'id': cuenta.id,
                        'accountCuenta': cuenta.accountCuenta,
                        'userCuenta': cuenta.userCuenta,
                        'passwordCuenta': password_cuenta,
                        'selector': cuenta.selector,
                        'broker_id': cuenta.broker_id,
                        'nombre_broker': nombre_broker
                    })
            
                for cuentas in todasCuentas:          
                        if cuentas['accountCuenta'] == account:
                              userCuenta = cuentas['userCuenta']
                              passwordCuenta = cuentas['passwordCuenta']
                              passwordCuenta_decoded = passwordCuenta.decode('utf-8')                             
                              return cuentas
        except Exception as e:
            print("Error al obtener las cuentas del usuario:", e)
            
   

