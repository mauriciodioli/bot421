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
  try:
   repuesta_listado_instrumento = get.pyRofexInicializada.get_account_position()
   return render_template('operaciones.html')
  except:        
    return render_template("errorLogueo.html" )
  
    
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
        return print("No hay suficiente saldo para enviar la orden de compra")
  except:        
    flash('Datos Incorrect')  
    return render_template("operaciones.html" )
 
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
        #actualizarTablaOR()
        return render_template('operaciones.html')
 
@operaciones.route("/modificar", methods = ['POST'])
def modificar():
  if request.method == 'POST':
        instrumento = request.form['instrumento']
        cantidad = request.form['cantidad']
        tipoOrden = request.form['tipoOrden']
        precio = request.form['precio'] 
        return render_template('operaciones.html')  
  
@operaciones.route("/cancelarOrden" , methods = ['POST'])
def cancelarOrden():
  if request.method == 'POST':
        clientId = request.form['clientId']
        print(clientId)
        cancel_order = get.pyRofexInicializada.cancel_order(clientId)
  print(cancel_order)
  return render_template('tablaOrdenesRealizadas.html')  
 
    
#el proprietary se debe configuarar de acuerdo al ambiente del broker que entre en produccion
#{'type': 'or', 'timestamp': 1631140826238, 'orderReport': {'orderId': '220805706', 'clOrdId': 'eMSofNm4oXL92V_s', 'proprietary': 'PBCP', 'execId': '210908063630-fix1-2229680', 'accountId': {'id': 'REM2747'}, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'GGAL/DIC21'}, 'price': 192.0, 'orderQty': 10, 'ordType': 'LIMIT', 'side': 'BUY', 'timeInForce': 'DAY', 'transactTime': '20210908-13:11:04.214-0300', 'avgPx': 0, 'lastPx': 0, 'lastQty': 0, 'cumQty': 0, 'leavesQty': 10, 'status': 'NEW', 'text': 'Aceptada '}}


 