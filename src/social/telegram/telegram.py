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
import asyncio
from models.usuario import Usuario
from models.brokers import Broker
from models.modelMedia.TelegramNotifier import TelegramNotifier

telegram = Blueprint('telegram',__name__)




@telegram.route('/telegram-envia-mensaje/')
def telegram_envia_mensaje():       
    return render_template('media/telegram/telegramEnviaMensaje.html', layout = 'layout')

@telegram.route('/telegram-envia-mensaje-grupo', methods=['POST'])
def telegram_envia_mensaje_grupo():
    try:
        if request.method == 'POST':
            data = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
            access_token = data.get('access_token')          
            mensaje = data.get('message')
            
            chat_id = "-1001285216353"
          
            # Asumiendo que TelegramNotifier está correctamente definido en otro lugar
            telegram_notifier = TelegramNotifier()
            asyncio.run(telegram_notifier.enviar_mensaje_grupo(chat_id,mensaje))

            return render_template('media/telegam/telegramEnviaMensaje.html', layout='layout')
    except Exception as e:
        # Tu código de manejo de excepciones aquí
        return render_template('notificaciones/errorOperacionSinCuenta.html', layout='layouts')

    return render_template('media/telegam/telegramEnviaMensaje.html', layout='layout')


@telegram.route('/emoticons', methods=['GET'])
def get_emoticons():
    # Lista completa de emoticonos y símbolos
    emoticons_and_symbols = [
        # Emoticones
        "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉",
        "😊", "😇", "😍", "😘", "😗", "😙", "😚", "🤗", "🤔",
        "🤐", "🤨", "🤩", "🤪", "🤫", "🤭", "🤯", "🤠", "🤡",
        "🤥", "🤧", "😷", "🤒", "🤕", "🤢", "🤮", "😵", "😴",
        "😪", "😰", "😥", "😢", "😭", "😓", "😩", "😫", "😤",
        "😡", "😠", "🤬", "😳", "😶", "😑", "😬", "🙄", "😯",
        "😲", "🥺", "🤤", "🤢", "🤮", "🤧",
        "🧑‍⚕️", "👨‍⚕️", "👩‍⚕️", "🧑‍🎓", "👨‍🎓", "👩‍🎓", "🧑‍🏫", "👨‍🏫", 
        "👩‍🏫", "🧑‍⚖️", "👨‍⚖️", "👩‍⚖️", "🧑‍🌾", "👨‍🌾", "👩‍🌾", "🧑‍🍳",
        "👨‍🍳", "👩‍🍳", "🧑‍🔧", "👨‍🔧", "👩‍🔧", "🧑‍🏭", "👨‍🏭", "👩‍🏭", 
        "🧑‍💼", "👨‍💼", "👩‍💼", "🧑‍🔬", "👨‍🔬", "👩‍🔬", "🧑‍💻", "👨‍💻",
        "👩‍💻", "🧑‍🎤", "👨‍🎤", "👩‍🎤", "🧑‍🎨", "👨‍🎨", "👩‍🎨", "🧑‍✈️", 
        "👨‍✈️", "👩‍✈️", "🧑‍🚀", "👨‍🚀", "👩‍🚀", "🧑‍🚒", "👨‍🚒", "👩‍🚒", "👮", 
        "👮‍♂️", "👮‍♀️", "🕵️", "🕵️‍♂️", "🕵️‍♀️", "💂", "💂‍♂️", "💂‍♀️", "🥷", "👷", 
        "👷‍♂️", "👷‍♀️", "🫅", "🤴", "👸", "👳", "👳‍♂️", "👳‍♀️", "👲", 
        "🧕", "🤵", "🤵‍♂️", "🤵‍♀️", "👰", "👰‍♂️", "👰‍♀️", "🤰", 
        "🫃", "🫄", "🤱", "👩‍🍼", "👨‍🍼", "🧑‍🍼", "💁", "💁‍♂️", "💁‍♀️", 
        "🧑‍💻", "👨‍💻", "👩‍💻", "🗣️", "👪", "🏠", "🏡", "🔊", "🎙️",
        "🎧", "📱", "📲", "☎️", "📞", "📠", "💻", "🖥️", "⌨️",
        "🖱️", "📹", "📔", "📖", "📚", "📓", "📃", "🔖", "✏️", 
        "🖋️", "🖊️", "📎", "🖇️",  "🏳️", "🏴", "🏁", "🚩","🇦🇷", "🇧🇷",
        "🇨🇦", "🇨🇱", "🇨🇳", "🇫🇷","🇩🇪", "🇮🇳", "🇯🇵", "🇲🇽", "🇷🇺", "🇪🇸", "🇬🇧", 
        "🇺🇸", "🇦🇮", "🇦🇱", "🇦🇲", "🇦🇴", "🇦🇶","🇦🇸", "🇦🇹", "🇦🇺", 
        "🇦🇼", "🇦🇽","🇦🇿", "🇧🇦", "🇧🇧", "🇧🇩", "🇧🇪", "🇧🇫", "🇧🇬", "🇧🇭", "🇧🇮",
        "🇧🇯","🇧🇱", "🇧🇲", "🇧🇳", "🇧🇴", "🇧🇶", "🇧🇷", "🇧🇸", "🇧🇹", "🇧🇻", "🇧🇼", 
        "🇧🇾", "🇧🇿", "🇨🇦", "🇨🇨", "🇨🇩", "🇨🇫", "🇨🇬", "🇨🇭", "🇨🇮", "🇨🇰", 
        "🇨🇱", "🇨🇲", "🇨🇳", "🇨🇴", "🇨🇵", "🇨🇷", "🇨🇺", "🇨🇻", "🇨🇼", "🇨🇽",        
        "🇵🇳", "🇵🇷", "🇵🇸", "🇵🇹", "🇵🇼", "🇵🇾", "🇶🇦", "🇷🇪", "🇷🇴", "🇷🇸", 
        "🇷🇺", "🇷🇼", "🇸🇦", "🇸🇧", "🇸🇨", "🇸🇩", "🇸🇪", "🇸🇬", "🇸🇭", "🇸🇮", 
        "🇸🇯", "🇸🇰", "🇸🇱", "🇸🇲", "🇸🇳", "🇸🇴", "🇸🇷", "🇸🇸", "🇸🇹", "🇸🇻", "🇸🇽", 
        "🇸🇾", "🇸🇿", "🇹🇦", "🇹🇨", "🇹🇩", "🇹🇫", "🇹🇬", "🇹🇭", "🇹🇯", "🇹🇰", "🇹🇱", 
        "🇹🇲", "🇹🇳", "🇹🇴", "🇹🇷", "🇹🇹", "🇹🇻", "🇹🇼", "🇹🇿", "🇺🇦", "🇺🇬",        

        # Símbolos de dinero y negocios
        "💰", "💸", "💵", "💴", "💶", "💷", "🪙", "🤑", "💳",
        "🏦", "🏧", "💹", "💲", "📈", "📉", "🔝", "🔝", "💼",
        "📊", "📋", "📁", "📂", "🗂", "🗃", "🗄", "🗑", "🔒",
        "🔓", "🔏", "🔐", "🔑", "💡", 
        # Símbolos de colores y amor
        "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎",
        "💔", "❤️‍🔥", "❤️‍🩹",
        "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💌",
        # Animales
        "🐱", "🐶", "🐭", "🐹", "🐰", "🦊", "🐸", "🦄",
        # Estrellas y clima
        "🌟", "💫", "💥", "💨", "💦", "🌈", "☀️", "🌤", "⛅️",
        "🌧", "🌨", "🌩", "⚡️", "☔️", "🌪", "🌫", "🌬",
        "🌈", "🌤", "🌥", "☀️", "🌜", "🌛", "🌝", "🌞",
        # Celebraciones
        "🎉", "🎊", "🎈", "🎂", "🎁", "🎏", "🎀", "🎊",
            # Celulares y tecnología
        "📱", "📲", "📞", "📟", "📠", "💻", "🖥", "🖨", "🖱",
        "⌨️", "🖲", "📡", "🔌", "🔋", "🔍", "🔎",
        # Personas
        "👤", "👥", "🧑", "🧑‍🦰", "🧑‍🦱", "🧑‍🦲", "🧑‍🦳",
        "👩", "👩‍🦰", "👩‍🦱", "👩‍🦲", "👩‍🦳", "👨", "👨‍🦰",
        "👨‍🦱", "👨‍🦲", "👨‍🦳", "🧓", "👴", "👵", "👶",
        "👦", "👧", "👧‍🦱","🤵", "👰", "👸",
        "🤴", "🦸", "🦹", "🧚", "🧜", "🧝", "🧞", "🧟", "🧓",
        "🤶", "🧑‍🎄", "🏢", "🏣","🏟️", "🏛️", "🏗️", "🧱", "🪨",
        "🪵", "🛖", "🏘️", "🏚️", "🏠", "🏡", "🏢", "🏣", "🏤", 
        "🏥", "🏦", "🏨", "🏩", "🏪", "🏫", "🏬", "🏭", "🏯", 
        "🏰", "💒", "🗼", "🗽"

    ]
    return jsonify(emoticons_and_symbols)