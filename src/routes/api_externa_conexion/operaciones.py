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
import routes.api_externa_conexion.validaInstrumentos as val
import pandas as pd
import time
import routes.api_externa_conexion.wsocket as getWs
import routes.api_externa_conexion.cuenta as cuenta
import routes.instrumentos as inst
import strategies.datoSheet as datoSheet
from panelControlBroker.panelControl import panel_control
from panelControlBroker.panelControl import forma_datos_para_envio_paneles
import threading
import jwt
from datetime import datetime  # Agrega esta línea para obtener la fecha y hora actual

 




operaciones = Blueprint('operaciones',__name__)


saldo = None  # Variable global para almacenar el saldo
ultima_entrada = 0
@operaciones.route("/operar",methods=["GET"])
def operar():
  try:
   orderQty = '0'
   symbol = 'x'
   price = '0'
   repuesta_listado_instrumento = get.pyRofexInicializada.get_account_position()
   lista =  lista = [{ 'symbol' : symbol, 'price' : price, 'orderQty' : orderQty}]
   return render_template('operaciones.html', datos = lista)
  except:        
    return render_template("errorLogueo.html" )
  
    
@operaciones.route("/get_trade_history_by_symbol",  methods=["POST"])
def get_trade_history_by_symbol():
  try:        
        if request.method == 'POST': 
            symbol = request.form.get('symbol')
           # end = datetime.date.today()
           # start = datetime.date(year=end.year, month=1, day=1)
           # historic_trades = get.pyRofexInicializada.get_trade_history(ticker=symbol, start_date=start, end_date=end)
           # operaciones = historic_trades
            print("historic_trades operacionnnnnnnnnnnnnnnnnnnnneeesss ",symbol)
        return render_template('tablaOrdenesRealizadas.html', datos = operaciones)
  except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
  return render_template("login.html" )

@operaciones.route("/estadoOperacion")
def estadoOperacion():
    try:
        print(get.pyRofexInicializada)
        repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
       
        operaciones = repuesta_operacion.get('orders', [])  # Usar .get() para manejar si 'orders' no está en la respuesta
        return render_template('tablaOrdenesRealizadas.html', datos=operaciones)
    
    except KeyError as e:
        # Manejar el caso en que 'orders' no está en la respuesta
        print(f"Error: La respuesta no contiene 'orders': {e}")
        flash("La respuesta no contiene datos de operaciones")
    
    except Exception as e:
        # Manejar otras excepciones generales
        print(f"Error inesperado: {e}")
        flash("Ocurrió un error inesperado al obtener los datos de operaciones")

    return render_template("login.html")

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
            if access_token:
                app = current_app._get_current_object()  
                userId = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                
            # Intentamos encontrar el registro con el symbol específico
            orden_existente = Orden.query.filter_by(symbol=ticker).first()

            if orden_existente:
                # Si el registro existe, lo actualizamos
                orden_existente.user_id = userId
                orden_existente.userCuenta = cuentaUser
                orden_existente.ut = ut1
                orden_existente.senial = signal
                orden_existente.clOrdId_alta_timestamp=datetime.now()
                orden_existente.status = 'operado'
            else:
                # Si no existe, creamos un nuevo registro
                nueva_orden = Orden(
                    user_id=userId,
                    userCuenta=cuentaUser,
                    accountCuenta="sin cuenta broker",
                    clOrdId_alta=random.randint(1,100000),
                    clOrdId_baja='',
                    clientId='',
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
                db.session.add(nueva_orden)
                #get.current_session = db.session
            db.session.close()
          
            
            if pais == "argentina":
               ContenidoSheet = datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')
            elif pais == "usa":
                ContenidoSheet =  datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'drpibotUSA')
            else:
              return "País no válido"
          
          
            datos_desempaquetados = forma_datos_para_envio_paneles(ContenidoSheet)
          
            return render_template("/paneles/panelSignalSinCuentas.html", datos = datos_desempaquetados)
        else:
            return jsonify({'error': 'Método no permitido'}), 405  # 405 significa Método no permitido
    except Exception as e:
        # Tu código de manejo de excepciones aquí
        return render_template('notificaciones/errorOperacionSinCuenta.html')           

    
@operaciones.route("/operaciones_desde_seniales/", methods=["POST"]) 
def operaciones_desde_seniales():
    try:
        if request.method == 'POST':
            access_token = request.form['access_token']
            symbol = request.form['symbol']
            ut = request.form['ut']
            signal = request.form['senial']
            cuentaA = request.form['cuentaEnvioAjax']
            logs_table = Logs()  # Crea una instancia de Logs
            logs_table.crear_tabla()  # Llama a la función crear_tabla
            if access_token:
                app = current_app._get_current_object()  
                user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
          
            existencia = inst.instrumentos_existentes_by_symbol(symbol) 
            if existencia == True:           
              precios = inst.instrument_por_symbol(symbol)               
              if precios != '':
                precios = list(precios)
                if signal == 'closed.':               
                    accion = 'vender' 
                    price = precios[0][3]#envio precio de la oferta                               
                elif signal == 'OPEN.':
                    accion = 'comprar'                 
                    price = precios[0][2]#envio precio de la demanda
                   # Verificar el saldo y enviar la orden si hay suficiente
                tipoOrder = 'LIMIT'        
                print("tipoOrder ",tipoOrder)
                #se debe controlar cuando sea mayor a 1 minuto
                 # Inicia el hilo para consultar el saldo después de un minuto
                if  tipoOrder == 'LIMIT':
                    
                    orden_ = Operacion(ticker=symbol, accion=accion, size=ut, price=price,order_type=get.pyRofexInicializada.OrderType.LIMIT)
                     
                    if orden_.enviar_orden(cuenta=cuentaA):
                         print("Orden enviada con éxito.")
                         flash('Operacion enviada exitosamente')
                         repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
                         operaciones = repuesta_operacion['orders']
                         print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
                    else:
                        print("No se pudo enviar la orden debido a saldo insuficiente.")
                  
                    
                    
                   
              
                                      
           
               # repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
               # operaciones = repuesta_operacion['orders']   
               # traer datos del portfolio para mostrar cuantas ut se operaron y re enviar esa informacion
               # 
                return jsonify({'redirect': url_for('paneles.panelDeControlBroker')}) 
    except Exception as e:
         # Si se genera una excepción, crear un registro en Logs
        error_msg = str(e)  # Obtener el mensaje de error

        # Crear un nuevo registro en Logs
        new_log = Logs(user_id=user_id,userCuenta=cuentaA, accountCuenta=cuentaA,fecha_log=datetime.now(), ip=request.remote_addr, funcion='operaciones_desde_seniales', archivo='operaciones',linea=100, error=error_msg )
        db.session.add(new_log)
        db.session.commit()

        return render_template('errorOperacion.html')




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
              return render_template("errorOperacion.html" )
        else:
          sendOrderWS()
          flash('Operacion enviada exitosamente')
          repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
          operaciones = repuesta_operacion['orders']
          print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
          return render_template('tablaOrdenesRealizadas.html', datos = operaciones)
  except:        
    flash('Datos Incorrect')  
    return render_template("operaciones.html" )
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
          accountId= request.form.get('accountId')
         
          print("clOrdId ", clOrdId)
          print("symbol ", symbol)
          print("price ", price)
          print("proprietary ", proprietary)
          print("estado ", estado)
          print("accountId ", accountId)
         
         
          
          # 3-Initialize Websocket Connection with the handlers
          #get.pyRofexInicializada.init_websocket_connection(order_report_handler=getFunction.order_report_handler_cancel,
          #                       error_handler=getFunction.error_handler,
          #                       exception_handler=getFunction.exception_handler)
        
          
          # ojo se comento por compromiso con la homologacion restaurar **66
          
          order_status= get.pyRofexInicializada.get_order_status(clOrdId,proprietary)
          #print("order_status ",order_status)          
          if order_status["order"]["status"] == "NEW":
            # Cancel Order
            get.pyConectionWebSocketInicializada.cancel_order_via_websocket(client_order_id=clOrdId)
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
   #try:
    if request.method == 'POST':
        symbol = request.form['symbol']
        orderQty = request.form['orderQty']
        price = request.form['price']  
        tipoOrder = request.form.getlist('tipoOrder')[0] 
        
        print("tipoOrder WWWWWWWWWWWWWWWWWssssssssssssssssss",tipoOrder)
        
        saldo = cuenta.obtenerSaldoCuenta()
        
        
        if saldo >= int(orderQty) * float(price):
          
          print("tipoOrder ",tipoOrder)
          if  tipoOrder == 'LIMIT':
            print("saldo cuenta ",saldo)      
         
            
            
            # 4-Subscribes to receive order report for the default account
            get.pyConectionWebSocketInicializada.order_report_subscription()

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
            return render_template("errorOperacion.html" )
   #except:        
   # flash('Datos Incorrect')  
   # print('datos incorrectos')
   # return render_template("errorOperacion.html" )

def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic23"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}

def order_report_handler(message):
  
  
  
  
  #print("Mensaje de OrderRouting: {0}".format(message))
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
 