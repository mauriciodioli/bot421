# main.py
import numpy as np
from flask import Blueprint, render_template, session,request, redirect, url_for, flash,jsonify
from utils.common import Marshmallow, db, get
import routes.instrumentosGet as instrumentosGet
import routes.api_externa_conexion.validaInstrumentos as val
from models.cuentas import Cuenta

import strategies.datoSheet as datoSheet
import routes.instrumentos as inst
from panelControlBroker.panelControl import enviar_leer_sheet
from strategies.datoSheet import update_precios
from strategies.datoSheet import calculo_dolar_mep
from strategies.caucionador.caucion import determinar_caucion
from datetime import datetime

import pandas as pd
import pyRofex #lo utilizo para test
import time    #lo utilizo para test
import asyncio
import websockets
import websocket
from flask_paginate import Pagination, get_page_parameter

import json
import os
import copy

from sqlalchemy.exc import OperationalError
import pymysql

import yfinance as yf



dolares = Blueprint('dolares',__name__)
# Obtener datos históricos del activo subyacente (por ejemplo, Apple)
data = yf.download('USDARS', start='2020-01-01', end='2023-01-01')

@dolares.route('/api/dolar')
def obtener_dolar():
    # Obtiene el valor del dólar
    dolar = yf.Ticker("USDARS=X")
    datos = dolar.history(period="1d")
    valor = datos["Close"].iloc[0]
    return jsonify({"valor_dolar": valor})