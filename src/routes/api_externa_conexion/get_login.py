
from ast import Return
from http.client import UnimplementedFileMode
import json
from datetime import datetime
from re import template
from socket import socket
import pyRofex
# datetime.date.today()
import websocket
import requests
import re
import routes.api_externa_conexion.validaInstrumentos as valida
import routes.api_externa_conexion.wsocket as ws
import routes.instrumentos as inst
from models.instrumento import Instrumento
import ssl



from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)


get_login = Blueprint('get_login',__name__)

 
user = "{{usuario}}" 
password = "{{contraseña}}" 
account = "{{cuenta}}"  
market_data_recibida = []
reporte_de_ordenes = []

pyRofexInicializada = pyRofex
pyConectionWebSocketInicializada = pyRofex
pyWsSuscriptionInicializada = pyRofex



# Creating  Routes
#@get_login.route("/index")
#def index(): 
  
#   all_mer = Instrumento.query.all()
#   print("all_mer",all_mer)  
#   return render_template('index.html', datos = all_mer)


# Creating simple Routes
@get_login.route("/loginApi")
def loginApi():  
 return render_template("login.html")



 
@get_login.route("/loginExt" , methods=['POST'])
def loginExt():
     
     
     #print('fechaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa en get_login.py hoy = datetime.today().strftime()',hoy)
     if request.method == 'POST':
        selector = request.form['selctorEnvironment']
        
        hoy = datetime.today().strftime('%d-%m-20%y')   
        ####   AQUI TENGO QUE COMPARAR LA FECHA ####
        fecha = request.form['fecha']#aqui traigo dato de localstorage
        #print('fechaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa de localstorage',fecha)
        dia = fecha.split()[0]#saco el dia
        mes = int(fecha.split()[1])+1#saco el mes
        a = re.sub("1","",fecha.split()[2])#saco el año
        fecha =  "20"+str(a)+"-"+ str(mes)+"-"+str(dia)#convierto a string
        #print('fechaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa de ayer',fecha)
       
        
       
        first_date = datetime.strptime(hoy,'%d-%m-%Y')# fecha de hoy        
        #second_date = datetime.strptime(hoy,'%d-%m-%Y')
        print('fechaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa en get_login.py first_date',first_date)
        second_date = datetime.strptime('13-02-2023','%d-%m-%Y')#para probar logeo diario   
        print('fechaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa en get_login.py second_date',second_date)     
        result = first_date > second_date#comparo las fechas si la de hoy es mayor que la de ayer no vuelvo a loguear
        #result = first_date < fecha#comparo las fechas
        print(result)
        if result:#si es false se queda pidiendo el logeo y si es true pasa a mostrar
            try:
                user = request.form['usuario']
                password = request.form['contraseña']
                account = request.form['cuenta']            
                print(user)
                print(password)
                print(result)
            except:  
                    print("no posee datos")      
                    return render_template("login.html" )
            if int(selector) < 2:
               try:
                
                pyRofexInicializada.initialize(user=user, 
                    password=password, 
                    account=account, 
                    environment=pyRofexInicializada.Environment.REMARKET)
                pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(order_report_handler=order_report_handler,
                                                                                                 error_handler=error_handler,
                                                                                                 exception_handler=exception_handler)
               # pyWsSuscriptionInicializada = pyRofexInicializada.market_data_subscription()
                print("está logueado en simulado en REMARKET")
               except:  
                    print("contraseña o usuario incorrecto")  
                    flash('Loggin Incorrect')    
                    return render_template("errorLogueo.html" )          
            else: 
                pyRofexInicializada.initialize(user=user, 
                    password=password, 
                    account=account, 
                    environment=pyRofexInicializada.Environment.LIVE) 
                pyConectionWebSocketInicializada = pyRofexInicializada.init_websocket_connection(order_report_handler=order_report_handler,
                                                                                                 error_handler=error_handler,
                                                                                                 exception_handler=exception_handler)
              #  pyWsSuscriptionInicializada = pyRofexInicializada.market_data_subscription()
              
                print("está logueado en produccion en LIVE")
            
            #ws.activarWebSocketConexion
            
        return render_template('operaciones.html')

def order_report_handler(message):
  print("Mensaje de OrderRouting: {0}".format(message))
  reporte_de_ordenes.append(message)
  
def error_handler(message):
  print("Mensaje de error: {0}".format(message))

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))


       #ws.webSocket() ### AQUI FALTA HACER LA PANTALLA EN DONDE ELIJO LOS INSTRUMENTOS PARA SUSCRIBIRME 
       # repuesta_listado_instrumento = pyRofexInicializada.get_detailed_instruments()
       # listado_instrumentos = repuesta_listado_instrumento['instruments']
       # tickers_existentes = obtener_array_tickers(listado_instrumentos)
        #print(tickers_existentes)
       # mis_instrumentos = ["DLR/NOV22", "SOJ.ROS/MAY22","DLR/JUN22", "MERV - XMEV - TSLA - 48hs"]
       # instrumentos_existentes = valida.validar_existencia_instrumentos(mis_instrumentos,tickers_existentes)
        #print(instrumentos_existentes)
        
        ##aqui se conecta al ws
       # pyRofexInicializada.init_websocket_connection(market_data_handler,order_report_handler,error_handler,exception_error)
        #### aqui define el MarketDataEntry
       # entries = [pyRofexInicializada.MarketDataEntry.BIDS,
       #    pyRofexInicializada.MarketDataEntry.OFFERS,
       #    pyRofexInicializada.MarketDataEntry.LAST]        
        #instrumento_suscriptio =  pyRofexInicializada.market_data_subscription(instrumentos_existentes,entries)
        #print(instrumento_suscriptio)
       # pyRofexInicializada.order_report_subscription(snapshot=True)
       # saldo=obtenerSaldoCuenta()
        #print(saldo)
        ####aqui compro        
       # comprar('DLR/NOV22',25,108.25,pyRofex.OrderType.LIMIT)
        #vender('DLR/NOV22',25,108.25,pyRofex.OrderType.LIMIT)
      # actualizarTablaMD()
        
        





 

  
  

  
 
    




