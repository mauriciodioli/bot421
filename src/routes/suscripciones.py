from pipes import Template
from unittest import result
import requests
import json
import pyRofex
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as valida
from models.instrumentosSuscriptos import InstrumentoSuscriptos


suscripciones = Blueprint('suscripciones',__name__)




@suscripciones.route("/suscripcion_instrumentos/" )
def suscripcion_instrumentos():
    try:
        
        return render_template("suscripcion.html" )

    except:        
        return render_template("login.html" )

@suscripciones.route("/suscripcionDb/" )
def suscripcionDb():
    try:
         all_ins = db.session.query(InstrumentoSuscriptos).all()
         return render_template("suscripciones_db.html", datos =  all_ins)
    except:        
        return render_template("login.html" )
    
@suscripciones.route("/suscDelete/", methods = ['POST'] )
def suscDelete():
    try:
         if request.method == 'POST':
            id = request.form['id']            
            dato = InstrumentoSuscriptos.query.get(id)
            print(dato)
            db.session.delete(dato)
            db.session.commit()
            flash('Operation Removed successfully')
            all_ins = db.session.query(InstrumentoSuscriptos).all()
            return render_template("suscripciones_db.html", datos =  all_ins)
    except: 
            flash('Operation No Removed')       
            all_ins = db.session.query(InstrumentoSuscriptos).all()
            return render_template("suscripciones_db.html", datos =  all_ins)
    
