from pipes import Template
from unittest import result
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumentoGet import InstrumentoGet
from models.instrumento import Instrumento
from models.instrumentosSuscriptos import InstrumentoSuscriptos
from utils.db import db
from datetime import datetime
from utils.db_session import get_db_session 


instrumentosGet = Blueprint('instrumentosGet',__name__)



# Creating simple Routes
@instrumentosGet.route("/guarda_instrumento", methods=['POST'])
def guarda_instrumento():   
    if request.method == 'POST':
        especie = request.form['symbol']
        c_compra = request.form['lowLimitPrice']
        p_compra = request.form['highLimitPrice']
        p_venta = request.form['minPriceIncrement']   
        c_venta = request.form['contractMultiplier']
        ultimo = request.form['symbol']
        var = request.form['tickSize']
        apertura = request.form['roundLot']
        minimo = request.form['priceConvertionFactor']
        maximo = request.form['symbol']
        cierre_anterior = request.form['symbol']
        volumen = request.form['minTradeVol']
        vol_monto = request.form['maturityDate']
        vwap = request.form['currency']
        idsegmento = request.form['orderTypes']
        idmarket = request.form['marketId']
        print(especie)
        print(c_compra)
        print(p_compra)
        with get_db_session() as session:
            new_mer = InstrumentoGet(especie,c_compra,p_compra,p_venta,c_venta,ultimo,var,apertura,minimo,maximo,cierre_anterior,volumen,vol_monto,vwap,idsegmento,idmarket)
            session.add(new_mer)
            session.commit()
           
    # jsonify puede devolver datos en lista, dict y otros formatos
    # print json content
    
    flash('Operation Added successfully')
    return redirect('/index')

def guarda_instrumento_para_suscripcion_ws(message):
     with get_db_session() as session:
        ob = session.query(InstrumentoSuscriptos).filter_by(symbol=message).first()
        
        print("salida query",ob)   
        if ob is None:
            symbol = message     
            tiempo =  datetime.now()
            timestamp = tiempo.microsecond        
            new_ins = InstrumentoSuscriptos(symbol,timestamp)
            print(new_ins)
            session.add(new_ins)
            session.commit()
          
      
  
def get_instrumento_para_suscripcion_ws():
     
     susc = []
     with get_db_session() as session:
        all_ins = session.query(InstrumentoSuscriptos).all()
        for instrumentoSuscriptos in all_ins:
            susc.append(instrumentoSuscriptos.symbol)	
         
    # for datos in susc:
     #  print(datos)
     #mis_instrumentos = ["DLR/NOV22", "SOJ.ROS/MAY22","DLR/JUN22", "MERV - XMEV - TSLA - 48hs"]
     return susc