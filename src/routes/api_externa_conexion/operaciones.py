# Creating  Routes
from pipes import Template
from unittest import result
import requests
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,current_app
from utils.common import Marshmallow, db, get
from models.instrumento import Instrumento
from models.operacion import Operacion
from models.orden import Orden
from models.logs import Logs
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.modelMedia.TelegramNotifier import TelegramNotifier
import routes.api_externa_conexion.validaInstrumentos as val
from utils.db_session import get_db_session 
import time
import os
import routes.api_externa_conexion.wsocket as getWs
import routes.api_externa_conexion.cuenta as cuenta
import routes.instrumentos as inst
import tokens.token as Token
import strategies.datoSheet as datoSheet
from panelControlBroker.panelControl import panel_control
from panelControlBroker.panelControl import procesar_datos
from panelControlBroker.panelControl import forma_datos_para_envio_paneles
import threading
import jwt
import asyncio
from datetime import datetime  # Agrega esta línea para obtener la fecha y hora actual

 




operaciones = Blueprint('operaciones',__name__)


saldo = None  # Variable global para almacenar el saldo
ultima_entrada = 0
@operaciones.route("/operar",methods=["GET"])
def operar():
  try:
     if request.method == 'POST': 
        symbol = request.form.get('symbol')
        
        orderQty = '0'
        symbol = 'x'
        price = '0'
       
        lista =  lista = [{ 'symbol' : symbol, 'price' : price, 'orderQty' : orderQty}]
        return render_template('operaciones/operaciones.html', datos = lista)
  except:        
    return render_template("notificaciones/errorLogueo.html" )

@operaciones.route("/operar-vacio",methods=["POST"])
def operar_vacio():
  try:
     if request.method == 'POST': 
        access_token = request.form.get('token_form_operacion')
        accounCuenta_form_operacion = request.form.get('accounCuenta_form_operacion')
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            orderQty = '0'
            symbol = 'x'
            price = '0'
          
            lista =  lista = [{ 'symbol' : symbol, 'price' : price, 'orderQty' : orderQty}]
            return render_template('operaciones/operaciones.html', datos = lista)
        else:
          return render_template('notificaciones/tokenVencidos.html',layout = 'layout') 
            
  except:        
    return render_template("errorLogueo.html" )
  
   
@operaciones.route("/get_trade_history_by_symbol/",  methods=["POST"])
def get_trade_history_by_symbol():
  try:        
        if request.method == 'POST': 
            symbol = request.form.get('symbol')
            end = datetime.today()
            start = datetime(end.year, 1, 1).date()
            # Convertir a cadena en formato "YYYY-MM-DD"
            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')
            historic_trades = get.pyRofexInicializada.get_trade_history(
                ticker=symbol,
                start_date=start_str,
                end_date=end_str,
                market=get.pyRofexInicializada.Market.ROFEX,
                environment=None
            )
           
            operaciones = historic_trades.get('trades', []) 
            print("historic_trades operacionnnnnnnnnnnnnnnnnnnnneeesss ",symbol)
        return render_template('paneles/tablaOrdenesRealizadas.html', datos = operaciones)
  except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
  return render_template("notificaciones/noPoseeDatos.html" )

@operaciones.route("/estadoOperacion",  methods=["POST"])
def estadoOperacion():
    try:
        account = request.form['accounCuenta_form_estadoOperacion']
        access_token = request.form['form_estadoOperacion_accessToken']
        if access_token and Token.validar_expiracion_token(access_token=access_token):
          pyRofexInicializada = get.ConexionesBroker.get(account)
          if pyRofexInicializada:
              repuesta_operacion = pyRofexInicializada['pyRofex'].get_all_orders_status(account=account,environment=account)
        
        
              operaciones = repuesta_operacion.get('orders', [])  # Usar .get() para manejar si 'orders' no está en la respuesta
              return render_template('paneles/tablaOrdenesRealizadas.html', datos=operaciones)
        else:
          return render_template('usuarios/logOutSystem.html')
    except KeyError as e:
        # Manejar el caso en que 'orders' no está en la respuesta
        print(f"Error: La respuesta no contiene 'orders': {e}")
        flash("La respuesta no contiene datos de operaciones")
    
    except Exception as e:
        # Manejar otras excepciones generales
        print(f"Error inesperado: {e}")
        flash("Ocurrió un error inesperado al obtener los datos de operaciones")

    return render_template("notificaciones/noPoseeDatos.html", layout = 'layoutConexBroker')


@operaciones.route("/envio_notificacion_tlegram_desde_seniales_sin_cuenta/", methods=["POST"]) 
def envio_notificacion_tlegram_desde_seniales_sin_cuenta():
    try:
        
        if request.method == 'POST':
            data = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
            access_token = data.get('access_token')
            ticker = data.get('symbol')
            ut1 = data.get('ut')
            signal = data.get('senial')
            cuentaUser = data.get('correo_electronico')
            pais = data.get('paisSeleccionado')
            chat_id = data.get('idtelegram')
            selector = data.get('selector')
            layouts = 'layout_signal'
            # Validación del token si es necesario
            if access_token and Token.validar_expiracion_token(access_token=access_token):
                # Obtener userId del token (decodificación JWT)
                app = current_app._get_current_object()
                userId = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                
                # Lógica para enviar mensaje asíncrono
                telegram_notifier = TelegramNotifier()      
                asyncio.run(telegram_notifier.enviar_mensaje_async(chat_id, ticker, ut1, signal))
             #   asyncio.run(telegram_notifier.enviar_mensaje_async('-1001285216353', ticker, ut1, signal))
                 # Intentamos encontrar el registro con el symbol específico
                with get_db_session() as session:
                  orden_existente = session.query(Orden).filter_by(symbol=ticker).first()
            
                  if orden_existente:
                      # Si el registro existe, lo actualizamos
                      orden_existente.user_id = userId
                      orden_existente.userCuenta = cuentaUser
                      orden_existente.ut = ut1
                      orden_existente.senial = signal
                      orden_existente.clOrdId_alta_timestamp=datetime.now()
                      orden_existente.status = 'terminado'              
                  else:
                      # Si no existe, creamos un nuevo registro
                      nueva_orden = Orden(
                          user_id=userId,
                          userCuenta=cuentaUser,
                          accountCuenta="sin cuenta broker",
                          clOrdId_alta=random.randint(1,100000),
                          clOrdId_baja='',
                          clientId=0,
                          wsClOrdId_timestamp=datetime.now(),
                          clOrdId_alta_timestamp=datetime.now(),
                          clOrdId_baja_timestamp=None,
                          proprietary=True,
                          marketId='',
                          symbol=ticker,
                          tipo="sin tipo",
                          tradeEnCurso="si",
                          ut=ut1,
                          senial=signal,
                          status='operado'
                      )
                    
                      session.add(nueva_orden)
                  if signal == 'closed.' :                  
                        session.delete(orden_existente)
                  session.commit() 
                      #get.current_session = session
                
                
                  
                  if selector == 'vacio':
                    selector = 'produccion'
                  datos_desempaquetados = procesar_datos(app,pais, None,userId,selector)
                
                  
                
                  return render_template("/paneles/panelSignalSinCuentas.html", datos = datos_desempaquetados)
            else: 
              return render_template('notificaciones/tokenVencidos.html',layout = layouts)       
        else:
            return jsonify({'error': 'Método no permitido'}), 405  # 405 significa Método no permitido
    except Exception as e:
        # Tu código de manejo de excepciones aquí
        return render_template('notificaciones/errorOperacionSinCuenta.html', layout = layouts)           

async def enviar_mensaje_async(idtelegram, ticker, ut1, signal): 
    #https://api.telegram.org/bot7264333617:AAFlrcw9yObB8ksp6k1P--zW6D6uk0gCgqc/getupdates  direccion para conseguir el id del grupo
    # Reemplaza 'YOUR_BOT_TOKEN' con el token de tu bot de Telegram
    token = "7264333617:AAFlrcw9yObB8ksp6k1P--zW6D6uk0gCgqc"
   
    # Reemplaza 'CHAT_ID_DEL_USUARIO' con el chat_id del usuario al que deseas enviar el mensaje   
   # chat_id = "-1001285216353"
    chat_id = idtelegram
    message = f"Ticker: {ticker}\nUT1: {ut1}\nSignal: {signal}"


    # Enviar el mensaje utilizando la API de requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
      
    try:
        response = requests.post(url, data=payload)
        data = response.json()
        print(data)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")


@operaciones.route("/operaciones_desde_seniales_sin_cuenta/", methods=["POST"]) 
def operaciones_desde_seniales_sin_cuenta():
    try:
        
        if request.method == 'POST':
            access_token = request.form['access_token']
            ticker = request.form['symbol']
            ut1 = request.form['ut']
            signal = request.form['senial']           
            cuentaUser = request.form['correo_electronico']
            pais = request.form['paisSeleccionado']
            selector = request.form['selector']
            layouts = 'layout_signal'
            if access_token and Token.validar_expiracion_token(access_token=access_token): 
                app = current_app._get_current_object()  
                userId = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                with get_db_session() as session:
                  # Intentamos encontrar el registro con el symbol específico
                  orden_existente = session.query(Orden).filter_by(symbol=ticker, user_id=userId, accountCuenta="sin cuenta broker").first()
            

                  if orden_existente:
                      # Si el registro existe, lo actualizamos
                      orden_existente.user_id = userId
                      orden_existente.userCuenta = cuentaUser
                      orden_existente.ut = ut1
                      orden_existente.senial = signal
                      orden_existente.clOrdId_alta_timestamp=datetime.now()
                      orden_existente.status = 'terminado'              
                  else:
                      # Si no existe, creamos un nuevo registro
                      nueva_orden = Orden(
                          user_id=userId,
                          userCuenta=cuentaUser,
                          accountCuenta="sin cuenta broker",
                          clOrdId_alta=random.randint(1,100000),
                          clOrdId_baja='',
                          clientId=0,
                          wsClOrdId_timestamp=datetime.now(),
                          clOrdId_alta_timestamp=datetime.now(),
                          clOrdId_baja_timestamp=None,
                          proprietary=True,
                          marketId='',
                          symbol=ticker,
                          tipo="sin tipo",
                          tradeEnCurso="si",
                          ut=ut1,
                          senial=signal,
                          status='operado'
                      )
                    
                      session.add(nueva_orden)
                  if signal == 'closed.' :                  
                        session.delete(orden_existente)
                  session.commit() 
                      #get.current_session = session
                  session
                
                  
                  if selector == 'vacio':
                    selector = 'produccion'
                  datos_desempaquetados = procesar_datos(app,pais, None,userId,selector)
                
                  
                
                  return render_template("/paneles/panelSignalSinCuentas.html", datos = datos_desempaquetados)
            else: 
              return render_template('notificaciones/tokenVencidos.html',layout = layouts)       
        else:
            return jsonify({'error': 'Método no permitido'}), 405  # 405 significa Método no permitido
    except Exception as e:
        # Tu código de manejo de excepciones aquí
        return render_template('notificaciones/errorOperacionSinCuenta.html', layout = layouts)           

    
@operaciones.route("/operaciones_desde_seniales/", methods=["POST"]) 
def operaciones_desde_seniales():
    try:
        if request.method == 'POST':
            access_token = request.form['access_token']
            symbol = request.form['symbol']
            ut = request.form['ut']
            signal = request.form['senial']
            cuentaA = request.form['correo_electronico']
            cuentaAcount = request.form['accountCuenta']
            paisSeleccionado = request.form['paisSeleccionado']
            pyRofexInicializada = get.ConexionesBroker.get(cuentaAcount)
            if pyRofexInicializada:
                #aqui controlo los checkbox y los input del modal de operacion enviado por POST
                if 'CantidadMonto' in request.form:
                  cantidad_monto = request.form['CantidadMonto']
                if 'ValorCantidad' in request.form:
                    valor_cantidad = request.form['ValorCantidad']
                else:
                    valor_cantidad='0' 
                if 'ValorMonto' in request.form:   
                  valor_monto = request.form['ValorMonto']  
                else: 
                  valor_monto='0'            
                if 'Modalidad' in request.form:
                    # El checkbox de modalidad fue seleccionado
                    modalidad_seleccionada = request.form['Modalidad']
                else:
                    modalidad_seleccionada = '2'
              
                  
              
              
              
                #logs_table = Logs()  # Crea una instancia de Logs
                #logs_table.crear_tabla()  # Llama a la función crear_tabla
                if access_token and Token.validar_expiracion_token(access_token=access_token): 
                    app = current_app._get_current_object()  
                    user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                    cuentaBroker = obtenerCuentaBroker(user_id)
                    
                    if 'ValorPrecioLimite' in request.form: 
                        precios = request.form['ValorPrecioLimite']                 
                    else:
                      existencia = inst.instrumentos_existentes_by_symbol(pyRofexInicializada=pyRofexInicializada['pyRofex'],message=symbol,account=cuentaAcount)                   
                      if existencia == True:           
                        precios = inst.instrument_por_symbol(symbol)    
                              
                    if precios != '':
                      
                          resultado = calculaUt(precios,valor_cantidad,valor_monto,signal)
                          
                          if isinstance(resultado, int):
                            price = float(precios)
                            cantidad_a_comprar_abs = resultado
                            if signal == 'closed.':               
                                accion = 'vender'                                                    
                            elif signal == 'OPEN.':
                                accion = 'comprar'                
                              
                          else:
                            cantidad_a_comprar_abs, precio_LA, BI_price, OF_price = resultado
                            if signal == 'closed.':               
                                accion = 'vender' 
                                price = OF_price#envio precio de la oferta                               
                            elif signal == 'OPEN.':
                                accion = 'comprar'                 
                                price = BI_price#envio precio de la demanda
                              # Verificar el saldo y enviar la orden si hay suficiente
                            
                          #se verifica el tipo de orden   
                          if modalidad_seleccionada=='1':
                            tipoOrder = pyRofexInicializada['pyRofex'].OrderType.LIMIT 
                            tipo_orden = 'LIMIT'
                            print("tipoOrder ",tipoOrder)  
                          else:        
                            tipoOrder = pyRofexInicializada['pyRofex'].OrderType.MARKET
                            tipo_orden = 'MARKET'
                            print("tipoOrder ",tipoOrder)
                            
                          #se debe controlar cuando sea mayor a 1 minuto
                          # Inicia el hilo para consultar el saldo después de un minuto
                          if tipo_orden == 'LIMIT' or tipo_orden == 'MARKET':
                              
                              orden_ = Operacion(ticker=symbol, accion=accion, size=cantidad_a_comprar_abs, price=price,order_type=tipoOrder,environment=cuentaAcount)
                             
                              if orden_.enviar_orden(cuenta=cuentaAcount,pyRofexInicializada=pyRofexInicializada['pyRofex']):
                                        print("Orden enviada con éxito.")
                                        flash('Operacion enviada exitosamente')
                                      
                                        repuesta_operacion = pyRofexInicializada['pyRofex'].get_all_orders_status(account=cuentaAcount,environment=cuentaAcount)
                                        operaciones = repuesta_operacion['orders']
                                        print(operaciones)#muestra el listado de todas las operaciones
                                        clOrdId = None
                                        orderStatus = None
                                        timepoTransaccion = None
                                        for orden in operaciones:
                                          if orden['instrumentId']['symbol'] == symbol:
                                            transacTime = datetime.strptime(orden['transactTime'], '%Y%m%d-%H:%M:%S.%f%z')
                                            if timepoTransaccion is None or transacTime > timepoTransaccion:
                                                timepoTransaccion = transacTime

                                                        
                                        for orden in operaciones:
                                            if orden['instrumentId']['symbol'] == symbol:
                                                transacTime = datetime.strptime(orden['transactTime'], '%Y%m%d-%H:%M:%S.%f%z')
                                                if transacTime == timepoTransaccion:                                                                   
                                                    clOrdId = orden['clOrdId'] 
                                                    orderStatus = orden['status']
                                                    break
                                              
                                        if orderStatus != 'REJECTED':  
                                          with get_db_session() as session:   
                                              # Intentamos encontrar el registro con el symbol específico
                                              orden_existente = session.query(Orden).filter_by(symbol=symbol,user_id=user_id,accountCuenta=cuentaAcount).first()

                                              if orden_existente:
                                                  # Si el registro existe, lo actualizamos
                                                  orden_existente.user_id = user_id
                                                  orden_existente.userCuenta = cuentaAcount
                                                  orden_existente.ut = cantidad_a_comprar_abs
                                                  orden_existente.senial = signal
                                                  orden_existente.clOrdId_alta = clOrdId
                                                  orden_existente.clOrdId_alta_timestamp=datetime.now()
                                                  orden_existente.status =  orderStatus
                                              else:
                                                  # Si no existe, creamos un nuevo registro
                                                  nueva_orden = Orden(
                                                      user_id=user_id,
                                                      userCuenta=cuentaA,
                                                      accountCuenta=cuentaAcount,
                                                      clOrdId_alta=clOrdId,
                                                      clOrdId_baja='',
                                                      clientId=0,
                                                      wsClOrdId_timestamp=datetime.now(),
                                                      clOrdId_alta_timestamp=datetime.now(),
                                                      clOrdId_baja_timestamp=None,
                                                      proprietary=True,
                                                      marketId='',
                                                      symbol=symbol,
                                                      tipo=tipo_orden,
                                                      tradeEnCurso="si",
                                                      ut=cantidad_a_comprar_abs,
                                                      senial=signal,
                                                      status= orderStatus
                                                  )
                                                  session.add(nueva_orden)
                                                  
                                              if signal == 'closed.':
                                                session.delete(orden_existente)   
                                              session.commit()  
                                                  #get.current_session = session
                                         
                                        else:  
                                          print("No se pudo enviar la orden debido a REJECTED")
                                          return jsonify({'success': True})

                                        # return jsonify({'redirect': url_for('paneles.panelDeControlBroker')})
                            
                              else:
                                      print("No se pudo enviar la orden debido a saldo insuficiente.")
                                      return jsonify({'redirect': url_for('paneles.panelDeControlBroker')}) 
                              
                              
                              
                            
                        
                                                
                    
                        # repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
                        # operaciones = repuesta_operacion['orders']   
                        # traer datos del portfolio para mostrar cuantas ut se operaron y re enviar esa informacion
                        #  
                          if paisSeleccionado == "argentina":
                              ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')
                          elif paisSeleccionado == "usa":
                                ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'drpibotUSA')
                          else:
                              return "País no válido"
              
              
                          datos_desempaquetados = forma_datos_para_envio_paneles(ContenidoSheet,user_id)
                        
                          return render_template("/paneles/panelSignalConCuentas.html", datos = datos_desempaquetados)
                        # return jsonify({'redirect': url_for('paneles.panelDeControlBroker', datos=datos_desempaquetados)})
            else:
               return None     
    except Exception as e:
      # Si se genera una excepción, crear un registro en Logs
      error_msg = str(e)  # Obtener el mensaje de error

      # Crear un nuevo registro en Logs
      new_log = Logs(user_id=user_id,userCuenta=cuentaA, accountCuenta=cuentaA,fecha_log=datetime.now(), ip=request.remote_addr, funcion='operaciones_desde_seniales', archivo='operaciones',linea=100, error=error_msg )
      session.add(new_log)
      session.commit()
      session
    return render_template('notificaciones/errorOperacion.html')

######## FALTA IMPLEMENTAR LAS OPERACIONES AUTOMATICAS DESDE PANEL CON CUENTA #############
@operaciones.route("/operaciones_automatico_desde_senial_con_cuenta/", methods=["POST "])
def operaciones_automatico_desde_senial_con_cuenta():
  try:
        if request.method == 'POST':
            access_token = request.form['access_token']
            symbol = request.form['symbol']
            ut = request.form['ut']
            signal = request.form['senial']
            cuentaA = request.form['correo_electronico']
       
            return jsonify({'redirect': url_for('paneles.panelDeControlBroker')}) 
  except Exception as e:
      # Si se genera una excepción, crear un registro en Logs
      error_msg = str(e)  # Obtener el mensaje de error

      # Crear un nuevo registro en Logs
    #  new_log = Logs(user_id=user_id,userCuenta=cuentaA, accountCuenta=cuentaA,fecha_log=datetime.now(), ip=request.remote_addr, funcion='operaciones_desde_seniales', archivo='operaciones',linea=100, error=error_msg )
    #  session.add(new_log)
      #session.commit()
      
  return render_template('notificaciones/errorOperacion.html')
def calculaUt(precios,valor_cantidad,valor_monto,signal):
  
  
  if not isinstance(precios, zip):
    precio=precios
    pass
  else:  
      for item in precios:
                      print(item[0])
                      print(item[1])
                      print(item[2])
                      print(item[3])
                      LA = json.loads(item[1].replace("'", "\""))
                      BI = json.loads(item[2].replace("'", "\""))
                      OF = json.loads(item[3].replace("'", "\""))
                        
                        # Acceder a los valores
                      print('LA:', LA['price'], 'size:', LA['size'], 'date:', LA['date'])
                      print('BI:', BI[0]['price'], 'size:', BI[0]['size'])
                      print('OF:', OF[0]['price'], 'size:', OF[0]['size'])
                      
      if signal == 'closed.':
        precio = OF[0]['price']       
      if signal == 'OPEN.':
        precio =  BI[0]['price']    
    
  if valor_monto == '0':
      cantidad_a_comprar =int(valor_cantidad)  # Aseguramos que valor_cantidad sea un entero
  
  else:
      cantidad_a_comprar = int(int(valor_monto) / int(precio))
      
  cantidad_a_comprar_abs = abs(cantidad_a_comprar)  
  if not isinstance(precios, zip):
    return cantidad_a_comprar_abs
  else: 
    return cantidad_a_comprar_abs, LA['price'], BI[0]['price'], OF[0]['price']

def obtenerCuentaBroker(user_id):
   todasLasCuentas = []
   with get_db_session() as session:
      usuario = session.query(Usuario).get(user_id)  
    # Buscar todas las cuentas asociadas a ese usuario
      cuentas = session.query(Cuenta).join(Usuario).filter(Cuenta.user_id == user_id).all()
      session
      if cuentas:
          print("El usuario", usuario.correo_electronico, "tiene las siguientes cuentas asociadas:")
                      
          for cuenta in cuentas:
            todasLasCuentas.append(cuenta.accountCuenta)
            password_cuenta = cuenta.passwordCuenta.decode('utf-8')
            todasLasCuentas.append({'id': cuenta.id, 'accountCuenta': cuenta.accountCuenta,'userCuenta':cuenta.userCuenta,'passwordCuenta':password_cuenta,'selector':cuenta.selector})
        
            print(cuenta.accountCuenta)
      return cuenta.accountCuenta    
 
               	
@operaciones.route("/comprar",  methods=["POST"])
def comprar():
  try:  
   
   if request.method == 'POST':
        symbol = request.form['symbol']
        orderQty = request.form['orderQty']
        price = request.form['price']  
        tipoOrder = request.form.getlist('tipoOrder')[0] 
        tipoTrafico = request.form.getlist('tipoTrafico')[0] 
        print("symbol ",symbol)
        print("orderQty ",orderQty)
        print("price ",price)
        print("tipoOrder ",tipoOrder)
        print("tipoTrafico ",tipoTrafico)
        
        if tipoTrafico == 'REST':
              
              print("tipoOrder ",tipoOrder)
        
              saldo = cuenta.obtenerSaldoCuenta()
              
              
              if saldo >= int(orderQty) * float(price):
                
                print("tipoOrder ",tipoOrder)
                if  tipoOrder == 'LIMIT':
                  #print("saldo cuenta ",saldo)      
                  nuevaOrden = get.pyRofexInicializada.send_order(ticker=symbol,side=get.pyRofexInicializada.Side.BUY,size=orderQty,price=price,order_type=get.pyRofexInicializada.OrderType.LIMIT)
                  orden = nuevaOrden
                  print("Orden de compra enviada ",orden)
                  
                  repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
              
                  operaciones = repuesta_operacion['orders']
                  print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
                  return render_template('tablaOrdenesRealizadas.html', datos = operaciones)
                
              else:
                print("No hay suficiente saldo para enviar la orden de compra")
              #actualizarTablaOR()
              #return format(nuevaOrden)
              estadoOperacion()
              flash('No hay suficiente saldo para enviar la orden de compra')
              return render_template("notificaciones/errorOperacion.html" )
        else:
          
          sendOrderWS()
          flash('Operacion enviada exitosamente')
          repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
          operaciones = repuesta_operacion['orders']
          print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
          return render_template('paneles/tablaOrdenesRealizadas.html', datos = operaciones)
  except:        
    flash('Datos Incorrect')  
    return render_template("operaciones/operaciones.html" )
################# AQUI SE MUESTRAN LOS VALORES QUE SE QUIEREN VENDER#########
@operaciones.route("/mostrarLaVenta/" , methods = ['POST'])
def mostrarLaVenta(): 
  if request.method == 'POST':
     clOrdId = request.form.get('clOrdId') 
     symbol = request.form.get('symbol') 
     price = request.form.get('price') 
     proprietary= request.form.get('proprietary') 
     estado= request.form.get('estado') 
     accountId= request.form.get('accountId') 
     orderQty = request.form.get('orderQty') 
     ordType = request.form.get('ordType')  
     print("clOrdId ", clOrdId)
     print("symbol ", symbol)
     print("price ", price)
     print("proprietary ", proprietary)
     print("estado ", estado)
     print("accountId ", accountId)
     print("orderQty ", orderQty)
     print("ordType ", ordType)
     lista = [{'clOrdId' : clOrdId, 'symbol' : symbol, 'price' : price, 'orderQty' : orderQty,'proprietary' : proprietary, 'estado' : estado, 'accountId' : accountId, 'ordType' : ordType}]
     print("escribiendooooooooooooooooooo la liiiiiiiiiiiiiiiiiistaa /mostrarLaVenta/", lista)
     return render_template('operaciones.html', datos = lista )
    
############# aqui se realiza la operacion de vender ###############################    
@operaciones.route("/vender/" , methods = ['POST'])
def vender(symbol, ut):
  if request.method == 'POST':
     clOrdId = request.form.get('clOrdId') 
     symbol = request.form.get('symbol') 
     price = request.form.get('price') 
     proprietary= request.form.get('proprietary') 
     estado= request.form.get('estado') 
     accountId= request.form.get('accountId') 
     orderQty = request.form.get('orderQty') 
     ordType = request.form.get('ordType') 
     print("clOrdId ", clOrdId)
     print("symbol ", symbol)
     print("price ", price)
     print("proprietary ", proprietary)
     print("estado ", estado)
     print("accountId ", accountId)
     print("orderQty ", orderQty)
     print("ordType ", ordType)
     lista = [{'clOrdId' : clOrdId, 'symbol' : symbol, 'price' : price, 'orderQty' : orderQty,'proprietary' : proprietary, 'estado' : estado, 'accountId' : accountId, 'ordType' : ordType }]
     print("escribiendooooooooooooooooooo la liiiiiiiiiiiiiiiiiistaa en /vender/ ")
    
     
     order_status= get.pyRofexInicializada.get_order_status(clOrdId,proprietary)
     print("order_status operaciones.py /vender/ ",order_status)  
     print("order_status operaciones.py /vender/ ",order_status["order"]["status"])  
     if order_status["order"]["status"] == "FILLED":#aqui debo cambiar el estado
        # aqui debo vender
        saldo = cuenta.obtenerSaldoCuenta()
        print("saldo ",saldo)
        if saldo >= int(orderQty) * float(price):
          print("saldo despues de if ",saldo)
          
          print("<<<-------init_websocket_connection------>>>>> ")
          # 4-Subscribes to receive order report for the default account
       
          print("<<<-------order_report_subscription------>>>>> ")
          # 5-Send an order via websocket message then check that order_report_handler is called
          get.pyConectionWebSocketInicializada.send_order_via_websocket(ticker=symbol, side=get.pyRofexInicializada.Side.SELL, size=orderQty, order_type=get.pyRofexInicializada.OrderType.LIMIT,price=price)  
           # validate correct price
          print("<<<-------send_order_via_websocketttttttttt------>>>>> ")
            # 8-Wait 5 sec then close the connection
          time.sleep(5)
          #estadoOperacion()
          repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
        
          operaciones = repuesta_operacion['orders']
          #print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
          return render_template('tablaOrdenesRealizadas.html', datos = operaciones)
        
        else:
           print("No hay suficiente saldo para enviar la orden de compra")
           return render_template('operaciones.html', datos = lista )
     else:
            flash('No se puede vender la Orden')  
            return render_template('operaciones.html', datos = lista )
   #  instrumento = request.form['instrumento']
   #  cantidad = request.form['cantidad']
   #  tipoOrden = request.form['tipoOrden']
   #  precio = request.form['precio']   
       
   #  saldo = cuenta.obtenerSaldoCuenta()
        
   #  if saldo >= int(cantidad) * float(precio):
   #    if   tipoOrden == 'LIMIT':      
   #          nuevaOrden = get.pyRofexInicializada.send_order(ticker=instrumento,side=get.pyRofexInicializada.Side.SELL,size=cantidad,price=precio,order_type=get.pyRofexInicializada.OrderType.LIMIT)
   #          print("Orden de compra enviada {0}".format(nuevaOrden))
   #  else:
   #       print("No hay suficiente saldo para enviar la orden de compra")
   #     #actualizarTablaOR()
  return render_template('operaciones.html', datos = lista )
 
@operaciones.route("/modificar/", methods = ['POST'])
def modificar():
  if request.method == 'POST':
       clOrdId = request.form.get('clOrdId') 
       symbol = request.form.get('symbol') 
       price = request.form.get('price') 
       proprietary= request.form.get('proprietary') 
       estado= request.form.get('estado') 
       accountId= request.form.get('accountId') 
       orderQty = request.form.get('orderQty') 
       print("clOrdId ", clOrdId)
       print("symbol ", symbol)
       print("price ", price)
       print("proprietary ", proprietary)
       print("estado ", estado)
       print("accountId ", accountId)
       print("orderQty ", orderQty)
        
       
       lista = [{'clOrdId' : clOrdId, 'symbol' : symbol, 'price' : price, 'orderQty' : orderQty,'proprietary' : proprietary, 'estado' : estado, 'accountId' : accountId }]
       print("escribiendooooooooooooooooooo la orden ")       
       order_status= get.pyRofexInicializada.get_order_status(clOrdId,proprietary)
       print("order_status ",order_status)  
       if order_status["order"]["status"] == "NEW":
            # Modifi Order
          
            cancel_order = get.pyRofexInicializada.cancel_order(clOrdId,proprietary)
         
            return render_template('operaciones.html', datos = lista )
       else:
            flash('No se puede modificar la Orden, ya fue OPERADA')  
           
       
        
  return  estadoOperacion()     
      
  
@operaciones.route("/cancelarOrden/" , methods = ['POST'])
def cancelarOrden():
  try:
    if request.method == 'POST':
          #ticker =
          clOrdId = request.form.get('clOrdId') 
          symbol = request.form.get('symbol') 
          price = request.form.get('price') 
          proprietary= request.form.get('proprietary') 
          estado= request.form.get('estado') 
          account= request.form.get('accountId')
         
          print("clOrdId ", clOrdId)
          print("symbol ", symbol)
          print("price ", price)
          print("proprietary ", proprietary)
          print("estado ", estado)
          print("accountId ", account)
         
               
          
          # ojo se comento por compromiso con la homologacion restaurar **66
          pyRofexInicializada = get.ConexionesBroker.get(account)
          if pyRofexInicializada:
              order_status = pyRofexInicializada['pyRofex'].get_order_status(clOrdId,proprietary)
        
            
              #print("order_status ",order_status)          
              if order_status["order"]["status"] == "NEW":
                # Cancel Order
                pyRofexInicializada.cancel_order_via_websocket(client_order_id=clOrdId,proprietary='ISV_PBCP',environment=account) 
            
                #cancel_order = get.pyRofexInicializada.cancel_order(clOrdId,proprietary)
              else:
                flash('No se puede cancelar la Orden, ya fue OPERADA')  
           
       
          #print("cancel_order ")
    return  estadoOperacion()     
   # return render_template('tablaOrdenesRealizadas.html')  
  except:      
    flash('No se puede cancelar la Orden error de datos')    
    return render_template("tablaOrdenesRealizadas.html" )
    
    
@operaciones.route("/sendOrderWS/", methods = ['POST'] )
def sendOrderWS():
  try:
    if request.method == 'POST':
        symbol = request.form['symbol']
        orderQty = request.form['orderQty']
        price = request.form['price']  
        tipoOrder = request.form.getlist('tipoOrder')[0] 
        
        print("tipoOrder WWWWWWWWWWWWWWWWWssssssssssssssssss",tipoOrder)
        
       # saldo = cuenta.obtenerSaldoCuenta()
        
        
        #if saldo >= int(orderQty) * float(price):
          
        print("tipoOrder ",tipoOrder)
        if  tipoOrder == 'LIMIT':
          print("saldo cuenta ",saldo)      
         
              
              
              # 4-Subscribes to receive order report for the default account
            # get.pyConectionWebSocketInicializada.order_report_subscription()

              # 5-Send an order via websocket message then check that order_report_handler is called
          get.pyConectionWebSocketInicializada.send_order_via_websocket(ticker=symbol, side=get.pyRofexInicializada.Side.BUY, size=orderQty, order_type=get.pyRofexInicializada.OrderType.LIMIT,price=price)  
              # validate correct price
              # print("______pasaaaaaa sa send_order_via_websocket")
              # 8-Wait 5 sec then close the connection
          time.sleep(5)
            
              
              
          repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
          operaciones = repuesta_operacion['orders']
          print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
          return render_template('tablaOrdenesRealizadas.html', datos = operaciones)
        else:
            print("No hay suficiente saldo para enviar la orden de compra")
             
            estadoOperacion()
            flash('No hay suficiente saldo para enviar la orden de compra')
            return render_template("notificaciones/errorOperacion.html" )
  except:        
    flash('Datos Incorrect')  
    print('datos incorrectos')
    return render_template("errorOperacion.html" )


def cargar_ordenes_db(cuentaAcount=None, 
                      cantidad_a_comprar_abs=None, 
                      signal=None, 
                      clOrdId=None, 
                      orderStatus=None, 
                      tipo_orden=None, 
                      symbol=None, 
                      user_id=None, 
                      accountCuenta=None):
    try:
        if signal != '':
          with get_db_session() as session:
            # Intentamos encontrar el registro con el symbol específico
            orden_existente = session.query(Orden).filter_by(symbol=symbol, user_id=user_id, accountCuenta=accountCuenta).first()

            if orden_existente:
                  # Si el registro existe, lo actualizamos
                  orden_existente.user_id = user_id
                  orden_existente.userCuenta = cuentaAcount
                  orden_existente.accountCuenta = accountCuenta
                  orden_existente.ut = cantidad_a_comprar_abs
                  orden_existente.senial = signal
                  orden_existente.clOrdId_alta = clOrdId
                  orden_existente.clOrdId_alta_timestamp = datetime.now()
                  orden_existente.status = orderStatus
                
            else:
                # Si no existe, creamos un nuevo registro
                nueva_orden = Orden(
                    user_id=user_id,
                    userCuenta=cuentaAcount,
                    accountCuenta=accountCuenta,
                    clOrdId_alta=clOrdId,
                    clOrdId_baja='',
                    clientId=0,
                    wsClOrdId_timestamp=datetime.now(),
                    clOrdId_alta_timestamp=datetime.now(),
                    clOrdId_baja_timestamp=None,
                    proprietary=True,
                    marketId='',
                    symbol=symbol,
                    tipo=tipo_orden,
                    tradeEnCurso="si",
                    ut=cantidad_a_comprar_abs,
                    senial=signal,
                    status=orderStatus
                )
                session.add(nueva_orden)
      
            # Confirmamos los cambios en la base de datos
            session.commit()
            return True
    
    except Exception as e:
        # En caso de error, hacemos rollback de la sesión y capturamos el error
     
        print(f"Error al cargar la orden en la base de datos: {str(e)}")
        return False



def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic23"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

def order_report_handler(message):
  
  get.reporte_de_ordenes.append(message)
  
 # 2-Defines the handlers that will process the messages and exceptions.
def order_report_handler_cancel(message):
    print("Order Report Message Received: {0}".format(message))
    # 6-Handler will validate if the order is in the correct state (pending_new)
    if message["orderReport"]["status"] == "NEW":
        # 6.1-We cancel the order using the websocket connection
        print("Send to Cancel Order with clOrdID: {0}".format(message["orderReport"]["clOrdId"]))
        get.pyRofexInicializada.cancel_order_via_websocket(message["orderReport"]["clOrdId"])

    # 7-Handler will receive an Order Report indicating that the order is cancelled (will print it)
    if message["orderReport"]["status"] == "CANCELLED":
        print("Order with ClOrdID '{0}' is Cancelled.".format(message["orderReport"]["clOrdId"])) 
  
  ###########tabla de market data
  #Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}

def market_data_handler(message):
  
  
  print("message",message)
  ticker = message["instrumentId"]["symbol"]
  bid = message["marketData"]["BI"] if len(message["marketData"]["BI"]) != 0 else [{'price': "-", 'size': "-"}]
  offer = message["marketData"]["OF"] if len(message["marketData"]["OF"]) != 0 else [{'price': "-", 'size': "-"}]
  last = message["marketData"]["LA"]["price"] if message["marketData"]["LA"] != None else 0
  dateLA = message['marketData']['LA']['date'] if message["marketData"]["LA"] != None else 0

  timestamp = message['timestamp']
  objeto_md = {'ticker':ticker,'bid':bid,'offer':offer,'last':last,'dateLA':dateLA,'timestamp':timestamp}
  get.market_data_recibida.append(objeto_md)
 
  print("Mensaje de MarketData en market_data_handler: {0}".format(message))
  
  
  #{"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic21"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

def order_report_handler(message):
  #print("Mensaje de OrderRouting: {0}".format(message))
  get.reporte_de_ordenes.append(message)
  
def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))
 