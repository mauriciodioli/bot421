from flask import Blueprint, render_template,current_app ,session,request, redirect, url_for, flash,jsonify


import routes.api_externa_conexion.cuenta as cuenta
from models.operacion import Operacion
import routes.api_externa_conexion.get_login as get
import tokens.token as Token


caucion = Blueprint('caucion',__name__)




@caucion.route('/caucionador_caucionar', methods=['POST'])
def caucionador_caucionar():
    try:
        if request.method == 'POST':
            account_cuenta = request.form.get('accounCuenta_form_caucionar')
            access_token = request.form.get('form_caucionar_accessToken')
            layout = request.form.get('form_caucionar_layout')
            if access_token and Token.validar_expiracion_token(access_token=access_token): 
                if layout == 'layoutConexBroker':
                    pyRofexInicializada = get.ConexionesBroker.get(account_cuenta)['pyRofex']  
                    if len(get.precios_data_caucion) > 0:
                        for Symbol, data in get.precios_data_caucion.items():
                            if data['recibido_pesos']:
                                saldo = cuenta.obtenerSaldoCuentaConObjeto(pyRofexInicializada, account=account_cuenta)
                                size = int(saldo / data['price'])

                                return render_template('caucionador/caucionar.html', layout='layoutConexBroker', size=size, saldo=saldo, price=data['price'], Symbol=Symbol)
                    else:
                        return render_template('notificaciones/logeePrimero.html', layout=layout)
                    
                else:
                    if len(get.precios_data_caucion) > 0:
                     for Symbol, data in get.precios_data_caucion.items():
                        if data['recibido_pesos']:
                            return render_template('caucionador/caucionSinCuenta.html', layout=layout, size=0, saldo=0, price=data['price'], Symbol=Symbol)
                    else:
                        return render_template('notificaciones/logeePrimero.html', layout=layout)
                    
    except Exception as e:
       flash(f"Error al procesar la caución: {str(e)}", "danger")
       return render_template("notificaciones/errorLogueo.html")



@caucion.route('/caucionador_caucionar_post', methods=['POST'])
def caucionador_caucionar_post():
    try:
        data = request.json  # Recibe los datos JSON
        if not data:
            raise ValueError("No se recibieron datos")
        
        account_cuenta = data.get('accounCuenta_form_caucionar')
        Symbol = data.get('form_caucionar_Symbol')
        price = data.get('form_caucionar_price')
        size = data.get('form_caucionar_size')
        saldo = data.get('form_caucionar_saldo')
        access_token = data.get('form_caucionar_accessToken')
        layout = data.get('form_caucionar_layout')
        
        
        if access_token and Token.validar_expiracion_token(access_token=access_token):
            if layout == 'layoutConexBroker':
                # Realiza aquí las acciones necesarias con los datos recibidos
                # Por ejemplo, guardar en la base de datos, etc.
                caucionar_desde_cuenta(account_cuenta,Symbol,price,size,saldo)
                # Si todo está bien, devuelve una respuesta JSON de éxito
                return jsonify({"status": "success", "message": "Operación realizada correctamente"}), 200
            else:
                raise ValueError("Layout no válido")
        else:
            raise ValueError("Token de acceso no válido o expirado")
    
    except Exception as e:
        flash(f"Error al procesar la caución: {str(e)}", "danger")
        return render_template("notificaciones/errorLogueo.html"), 500

def determinar_caucion(message):
    # Variables básicas
    Symbol = message["instrumentId"]["symbol"]
    market_data = float(message["marketData"]["OF"][0]["price"])

    if "PESOS" in Symbol:
        price = float(message["marketData"]["LA"]["price"])  # Precio "last" para 24hs
        
        if Symbol not in get.precios_data_caucion:
            get.precios_data_caucion[Symbol] = {
                'price': None,
                'recibido_pesos': False,
            }

        # Actualizar precios y estado según el día
        if any(day in Symbol for day in ["- 1D", "- 2D", "- 3D", "- 4D", "- 5D", "- 6D"]):
            get.precios_data_caucion[Symbol]['price'] = market_data
            get.precios_data_caucion[Symbol]['recibido_pesos'] = True

# ******************************
#   FIN                 CAUCION
# ******************************

def caucionar(account):
    # Verifica cada símbolo en get.precios_data_caucion
    for Symbol, data in get.precios_data_caucion.items():
        if data['recibido_pesos']:
            size = calcular_size(account,data['price'])
            nueva_operacion = Operacion(
                ticker=Symbol,
                accion='vender',
                size=size,
                price=data['price'],
                order_type='MARKET'
            )
            resultado = nueva_operacion.enviar_orden_sin_validar_saldo(cuenta=account, pyRofexInicializada=get.ConexionesBroker['cuenta'].get('pyRofex'))
            if resultado:
                print("Orden de caucion enviada con éxito.")
            else:
                print("No se pudo enviar la orden.")
def  caucionar_desde_cuenta(account_cuenta,Symbol,price,size,saldo):
    # Verifica cada símbolo en get.precios_data_caucion
    for Symbol, data in get.precios_data_caucion.items():       
          if saldo >= int(size) * float(price): 
            nueva_operacion = Operacion(
                ticker=Symbol,
                accion='vender',
                size=size,
                price=price,
                order_type='MARKET'
            )
            resultado = nueva_operacion.enviar_orden_sin_validar_saldo(cuenta=account_cuenta, pyRofexInicializada=get.ConexionesBroker['cuenta'].get('pyRofex'))
            if resultado:
                print("Orden de caucion enviada con éxito.")
            else:
                print("No se pudo enviar la orden.")
                                
                
def calcular_size(account, data):
      pyRofexInicializada = get.ConexionesBroker.get(account)['pyRofex']  
      saldo=cuenta.obtenerSaldoCuentaConObjeto(pyRofexInicializada, account=account )# cada mas de 5 segundos
      size = int(saldo / data['price'])
      return size        
                