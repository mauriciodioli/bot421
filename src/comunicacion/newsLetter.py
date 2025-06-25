# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app


import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
from models.newsLetter.newLetter import NewLetter
from social.media_e_mail import enviar_correo_newSletter
newsLetter = Blueprint('newsLetter',__name__)



@newsLetter.route('/comunicacion_newsLetter_comunica/')
def comunicacion_newsLetter_comunica():
    return render_template('comunicacion/newsLetter.html', layout='layout')
    
@newsLetter.route('/comunicacion_newsLetter_add/', methods=['POST'])
def comunicacion_newsLetter_add():
    if request.method == 'POST':
        try:           
            email = request.form.get('email')
            addEmail = db.session.query(NewLetter).filter_by(correo_electronico=email).first() 
            if addEmail is None:
                new_email = NewLetter(correo_electronico=email)
                db.session.add(new_email)
                db.session.commit()
                db.session.close()
                return jsonify({"message": "Email registered successfully."}), 200
            else:
                db.session.close()
                return jsonify({"message": "Email is already registered."}), 409
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    return render_template('notificaciones/noPoseeDatos.html')

@newsLetter.route('/comunicacion_newsLetter_comunica_a_todos/', methods=['POST'])
def comunicacion_newsLetter_comunica_a_todos():
     if request.method == 'POST':
        try:           
            mensaje = request.form.get('mensaje')
#            emails = db.session.query(NewLetter).filter_by().all()
#            db.session.close() 
#            if emails :
#                for email in emails:
#                    enviar_correo_newSletter(email.correo_electronico,mensaje)
#                return jsonify({"message": "Email registered successfully."}), 200
#            else:
#                return jsonify({"message": "Email is already registered."}), 409
        except Exception as e:
           return jsonify({"message": f"An error occurred: {str(e)}"}), 500
     return render_template('notificaciones/noPoseeDatos.html')


