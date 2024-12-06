from flask_login import login_required
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
import re
from flask import Blueprint, render_template, request, jsonify
from models.newsLetter.newLetter import NewLetter
from utils.db import db
from social.media_e_mail import enviar_correo_newSletter

# Blueprint and security setup
newsLetter = Blueprint('newsLetter', __name__)
csrf = CSRFProtect(newsLetter)
limiter = Limiter(newsLetter)

def sanitize_message(message):
    """Sanitize message to prevent XSS or malicious content"""
    return re.sub(r'<.*?>', '', message)

@newsLetter.route('/comunicacion_newsLetter_comunica/', methods=['GET'])
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
                return jsonify({"message": "Email registered successfully."}), 200
            else:
                return jsonify({"message": "Email is already registered."}), 409
        except Exception as e:
            app.logger.error(f"Error: {str(e)}")
            return jsonify({"message": "An error occurred. Please try again later."}), 500

@newsLetter.route('/comunicacion_newsLetter_comunica_a_todos/', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def comunicacion_newsLetter_comunica_a_todos():
    if request.method == 'POST':
        try:
            mensaje = sanitize_message(request.form.get('mensaje'))
            emails = db.session.query(NewLetter).filter_by().all()
            if emails:
                for email in emails:
                    enviar_correo_newSletter(email.correo_electronico, mensaje)
                return jsonify({"message": "Email sent successfully."}), 200
            else:
                return jsonify({"message": "No subscribers found."}), 404
        except Exception as e:
            app.logger.error(f"Error: {str(e)}")
            return jsonify({"message": "An error occurred. Please try again later."}), 500
    return render_template('notificaciones/noPoseeDatos.html')
