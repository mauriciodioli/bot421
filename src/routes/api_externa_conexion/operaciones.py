# Creating  Routes
from pipes import Template
from unittest import result
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import pandas as pd
import time

import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.cuenta as cuenta

import routes.api_externa_conexion as getFunction


operaciones = Blueprint('operaciones',__name__)

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
        repuesta_operacion = get.pyRofexInicializada.get_all_orders_status()
        
        operaciones = repuesta_operacion['orders']
        print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",operaciones)
        return render_template('tablaOrdenesRealizadas.html', datos = operaciones)
   except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
   return render_template("login.html" )
  
@operaciones.route("/comprar",  methods=["POST"])
def comprar():
  try:  
   if request.method == 'POST':
        instrumento = request.form['instrumento']
        cantidad = request.form['cantidad']
        precio = request.form['precio']  
        tipoOrder = request.form.getlist('tipoOrder')[0] 
        
        print("tipoOrder ",tipoOrder)
        
        saldo = cuenta.obtenerSaldoCuenta()
        
        
        if saldo >= int(cantidad) * float(precio):
          
          print("tipoOrder ",tipoOrder)
          if  tipoOrder == 'LIMIT':
            print("saldo cuenta ",saldo)      
            nuevaOrden = get.pyRofexInicializada.send_order(ticker=instrumento,side=get.pyRofexInicializada.Side.BUY,size=cantidad,price=precio,order_type=get.pyRofexInicializada.OrderType.LIMIT)
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
  except:        
    flash('Datos Incorrect')  
    return render_template("operaciones.html" )
 
@operaciones.route("/vender/" , methods = ['POST'])
def vender():
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
     print("escribiendooooooooooooooooooo la liiiiiiiiiiiiiiiiiistaa ")
     
     order_status= get.pyRofexInicializada.get_order_status(clOrdId,proprietary)
     print("order_status ",order_status)  
     if order_status["order"]["status"] == "Operada":
        # aqui debo vender
        
        return render_template('operaciones.html', datos = lista )
     else:
            flash('No se puede vender la Orden')  
           
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
        #actualizarTablaOR()
  return render_template('operaciones.html')
 
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
       print("escribiendooooooooooooooooooo la liiiiiiiiiiiiiiiiiistaa ")
       cancelarOrden()
       order_status= get.pyRofexInicializada.get_order_status(clOrdId,proprietary)
       print("order_status ",order_status)  
       if order_status["order"]["status"] == "NEW":
            # Modifi Order
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
        
          order_status= get.pyRofexInicializada.get_order_status(clOrdId,proprietary)
          print("order_status ",order_status)          
          if order_status["order"]["status"] == "NEW":
            # Cancel Order
            cancel_order = get.pyRofexInicializada.cancel_order(clOrdId,proprietary)
          else:
            flash('No se puede cancelar la Orden, ya fue OPERADA')  
           
       
          #print("cancel_order ")
    return  estadoOperacion()     
   # return render_template('tablaOrdenesRealizadas.html')  
  except:        
    return render_template("tablaOrdenesRealizadas.html" )
 

 