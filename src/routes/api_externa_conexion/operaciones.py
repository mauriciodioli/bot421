# Creating  Routes
from pipes import Template
from unittest import result
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import pandas as pd

import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.cuenta as cuenta



operaciones = Blueprint('operaciones',__name__)

@operaciones.route("/operar",methods=["GET"])
def operar():
   return render_template('operaciones.html')

@operaciones.route("/comprar",  methods=["POST"])
def comprar():
   if request.method == 'POST':
        instrumento = request.form['instrumento']
        cantidad = request.form['cantidad']
        tipoOrden = request.form['tipoOrden']
        precio = request.form['precio']   
       
        
        saldo = cuenta.obtenerSaldoCuenta()
        
        
        if saldo >= int(cantidad) * float(precio):
          
          print("tipoOrden ",tipoOrden)
          if   tipoOrden == 'LIMIT':
            print("saldo cuenta ",saldo)      
            nuevaOrden = get.pyRofexInicializada.send_order(ticker=instrumento,side=get.pyRofexInicializada.Side.BUY,size=cantidad,price=precio,order_type=get.pyRofexInicializada.OrderType.LIMIT)
            print("Orden de compra enviada {0}".format(nuevaOrden))
        else:
          print("No hay suficiente saldo para enviar la orden de compra")
        actualizarTablaOR()
        #return format(nuevaOrden)
        return render_template('tablaOrdenesRealizadas.html')
 
@operaciones.route("/vender" , methods = ['POST'])
def vender():
  if request.method == 'POST':
        instrumento = request.form['instrumento']
        cantidad = request.form['cantidad']
        tipoOrden = request.form['tipoOrden']
        precio = request.form['precio']   
       
        
        saldo = cuenta.obtenerSaldoCuenta()
        
        if saldo >= int(cantidad) * float(precio):
          if   tipoOrden == 'LIMIT':      
             nuevaOrden = get.pyRofexInicializada.send_order(ticker=instrumento,side=get.pyRofexInicializada.Side.SELL,size=cantidad,price=precio,order_type=get.pyRofexInicializada.OrderType.LIMIT)
             print("Orden de compra enviada {0}".format(nuevaOrden))
        else:
          print("No hay suficiente saldo para enviar la orden de compra")
        actualizarTablaOR()
        return render_template('operaciones.html')
 
######cancelacion de cuenta
@operaciones.route("/cancelarOrden" , methods = ['POST'])
def cancelarOrden():
  if request.method == 'POST':
        clientId = request.form['clientId']
        print(clientId)
        cancel_order = get.pyRofexInicializada.cancel_order(clientId)
  print(cancel_order)
  return render_template('tablaOrdenesRealizadas.html')  
   
@operaciones.route("/estadoOperacion")
def estadoOperacion():
   try:        
        repuesta_operacion = get.pyRofexInicializada.get_order_status()
        print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",repuesta_operacion)
   except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
   return render_template("login.html" )
    
#el proprietary se debe configuarar de acuerdo al ambiente del broker que entre en produccion
#{'type': 'or', 'timestamp': 1631140826238, 'orderReport': {'orderId': '220805706', 'clOrdId': 'eMSofNm4oXL92V_s', 'proprietary': 'PBCP', 'execId': '210908063630-fix1-2229680', 'accountId': {'id': 'REM2747'}, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'GGAL/DIC21'}, 'price': 192.0, 'orderQty': 10, 'ordType': 'LIMIT', 'side': 'BUY', 'timeInForce': 'DAY', 'transactTime': '20210908-13:11:04.214-0300', 'avgPx': 0, 'lastPx': 0, 'lastQty': 0, 'cumQty': 0, 'leavesQty': 10, 'status': 'NEW', 'text': 'Aceptada '}}
@operaciones.route("/actualizarTablaOR")
def actualizarTablaOR():

  df = pd.DataFrame(columns=pd.Index(['Timestamp', 'ID Orden', 'Estado', 'Ticker', 'Precio', 'Cantidad', 'Tipo Orden', 'TIF', 'Cuenta', 'Precio Promedio', 'Cantidad Operada', 'Cantidad Remanente', 'TextoAPI']))
  for order in get.reporte_de_ordenes:
    print(order['orderReport']['orderId'])
    if order['orderReport']['status'] != "PENDING_NEW" and order['orderReport']['status'] != "PENDING_CANCEL" :
      df = df.append(
          {
              'Timestamp': get.datetime.fromtimestamp(int(order['timestamp'])/1000),
              'ID Orden':order['orderReport']['orderId'], 
              'Estado':order['orderReport']['status'], 
              'Ticker':order['orderReport']['instrumentId']['symbol'], 
              'Precio':order['orderReport']['price'],
              'Cantidad':order['orderReport']['orderQty'], 
              'Tipo Orden':order['orderReport']['ordType'], 
              'TIF': order['orderReport']['timeInForce'],
              'Cuenta': order['orderReport']['accountId']['id'],
              'Precio Promedio': order['orderReport']['avgPx'],
              'Cantidad Operada': order['orderReport']['cumQty'],
              'Cantidad Remanente': order['orderReport']['leavesQty'],
              'TextoAPI': order['orderReport']['text']}, ignore_index=True)
    else:
        df = df.append(
          {
              'Timestamp': get.datetime.fromtimestamp(int(order['timestamp'])/1000),
              'ID Orden':order['orderReport']['orderId'], 
              'Estado':order['orderReport']['status'], 
              'Ticker':order['orderReport']['instrumentId']['symbol'], 
              'Precio':order['orderReport']['price'],
              'Cantidad':order['orderReport']['orderQty'], 
              'Tipo Orden':order['orderReport']['ordType'], 
              'TIF': order['orderReport']['timeInForce'],
              'Cuenta': order['orderReport']['accountId']['id'],
              'Precio Promedio': "-",
              'Cantidad Operada': "-",
              'Cantidad Remanente': "-",
              'TextoAPI': order['orderReport']['text']}, ignore_index=True)
  
  df = df.sort_values(by=['Timestamp'],ascending=False)
  
  df.to_html('templates/tablaOrdenesRealizadas.html') 
  return render_template('tablaOrdenesRealizadas.html')  

 
def actualizarTablaMD():
  
  
  df = pd.DataFrame(columns=pd.Index(['Ticker','Timestamp','Vol. Compra','Precio Compra', 'Precio Venta', 'Vol. Venta', 'Ult. Precio Operado']))
  for md in get.market_data_recibida:    
    df = df.append(
        {
          'Ticker': md['ticker'],
          'Timestamp':get.datetime.fromtimestamp(int(md['timestamp'])/1000),
          'Vol. Compra':md['bid'][0]['size'],
          'Precio Compra':md['bid'][0]['price'],
          'Precio Venta': md['offer'][0]['price'],
          'Vol. Venta': md['offer'][0]['size'],
          'Ult. Precio Operado': md['last']}, 
          ignore_index=True)
   # result = df.to_json(orient="split")
    df.style.set_table_styles(
      [{'selector': 'tr:hover',
        'props': [('background-color', 'yellow'),('color', 'black')]},
      {'selector': 'thead',
        'props': [('font-size', '16px'),('padding', '8px'),('background-color','brown')]}]
      )
    
  return df.to_html('templates/about.html') 