# Creating  Routes
from pipes import Template
from unittest import result
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get



cuenta = Blueprint('cuenta',__name__)

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
def obtenerSaldoCuenta(cuenta=None):
   print("_______________obtenerSaldoCuenta__________________")
   resumenCuenta = get.pyRofexInicializada.get_account_report(account=cuenta)
   return resumenCuenta["accountData"]["availableToCollateral"]

def obtenerCuenta(cuenta=None):
   resumenCuenta = get.pyRofexInicializada.get_account_report(account=cuenta)
   return resumenCuenta

@cuenta.route("/posicionCuenta")
def posicionCuenta():
     try:
        
        repuesta_cuenta = get.pyRofexInicializada.get_account_position()
        reporte = repuesta_cuenta['positions']
        print("posicion cuentaaaaaaaaaaaaaaaaaaaaaa ",reporte)
        return render_template("cuentaPosicion.html",datos = reporte)
     except:  
        print("contraseña o usuario incorrecto")  
        flash('No registra posicion')    
          
     return render_template("login.html" )

@cuenta.route("/detalleCuenta")
def detalleCuenta():
   try:        
        repuesta_cuenta = get.pyRofexInicializada.get_detailed_position()
        reporte = repuesta_cuenta['detailedPosition']
        
        print("detalle cuentaaaaaaaaaaaaaaaaaaaaaa ",reporte)
        
        return render_template("cuentaDetalles.html",datos = reporte)
     
   except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
          
   return render_template("login.html" )

@cuenta.route("/reporteCuenta")
def reporteCuenta():
   try:        
        repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        reporte = repuesta_cuenta['accountData']
        
        print("detalle cuentaaaaaaaaaaaaaaaaaaaaaa ",reporte)
        return render_template("cuenta.html",datos = reporte)
   except:  
      print("contraseña o usuario incorrecto")  
      flash('Loggin Incorrect')    
      return render_template("login.html" )