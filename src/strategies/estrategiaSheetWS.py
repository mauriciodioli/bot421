from flask import Blueprint,current_app, render_template,session, request, redirect, url_for, flash,jsonify,g
from utils.db import db
from models.orden import Orden
from models.usuario import Usuario
from models.operacionEstrategia import operacionEstrategia, OperacionEstrategia

import re
import jwt
import csv
import json
import random
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.cuenta as cuenta
import routes.api_externa_conexion.operaciones as operaciones
from strategies.estrategias import estrategias_usuario_nadmin_desde_endingOperacionBot
from routes.api_externa_conexion.operaciones import cargar_ordenes_db
import time
from pytz import timezone as pytz_timezone
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest
from herramientasAdmin.accionesTriggers import control_tiempo_lectura_verifiar_estado

from models.unidadTrader import UnidadTrader

import tokens.token as Token
instrumentos_existentes_arbitrador1=[]


estrategiaSheetWS = Blueprint('estrategiaSheetWS',__name__)

pyRofexInicializada = None
cuentaGlobal = None
VariableParaSaldoCta = None



tiempo_inicial_30s_ms = None
tiempo_inicial_5min_ms = None


diccionario_global_operaciones = {}
diccionario_operaciones_enviadas = {} 


idUser = None




@estrategiaSheetWS.route('/estrategiaSheetWS-001/', methods=['POST'])
def estrategiaSheetWS_001():
    print('00000000000000000000000 estrategiaSheetWS-001 00000000000000000000000000')
    global idUser  # Indica que estás usando la variable global
    if request.method == 'POST':
        try:
            app = current_app._get_current_object()
            #test.entradaTest()
            data = request.get_json()

            # Accede a los datos individualmente
            
            usuario = data['userCuenta']
            #usuario = "apipuntillo22583398"
            
            idTrigger = data['idTrigger']
            access_token = data['access_token']
            idUser = data['idUser']
            correo_electronico = data['correo_electronico']
            
            get.accountLocalStorage = data['cuenta']
            
            
            tiempoInicio = data['tiempoInicio']
            tiempoFin = data['tiempoFin']
            automatico = data['automatico']
            nombre = data['nombre']
            get.VariableParaBotonPanico = 0
            if access_token and Token.validar_expiracion_token(access_token=access_token): 
                for elemento in get.ConexionesBroker:
                    print("Variable agregada:", elemento)
                    accountCuenta = get.ConexionesBroker[elemento]['cuenta']                
                
                    if accountCuenta ==  data['cuenta']:              
                    
                        global pyRofexInicializada,cuentaGlobal
                        cuentaGlobal = data['cuenta']
                        pyRofexInicializada =  get.ConexionesBroker[elemento]['pyRofex']
                        cuentaGlobal = accountCuenta
                    
                        CargOperacionAnterioDiccionarioEnviadas(app,pyRofexInicializada=pyRofexInicializada,account=accountCuenta,user_id=usuario,userCuenta=correo_electronico)
                        carga_operaciones(app,pyRofexInicializada,get.diccionario_global_sheet['argentina'],accountCuenta,usuario,correo_electronico,get.ContenidoSheet_list[1],idTrigger)
                        pyRofexInicializada.order_report_subscription(account=accountCuenta,snapshot=True,handler = order_report_handler,environment=accountCuenta)
                        pyRofexInicializada.add_websocket_market_data_handler(market_data_handler_estrategia,environment=accountCuenta)
                        pyRofexInicializada.add_websocket_order_report_handler(order_report_handler,environment=accountCuenta)
         
        
            
            else:
               return render_template('usuarios/logOutSystem.html')
        except jwt.ExpiredSignatureError:
                print("El token ha expirado")
                get.actualiza_luz_web_socket('', get.accountLocalStorage,'',False)
                return redirect(url_for('autenticacion.index'))
        except jwt.InvalidTokenError:
            print("El token es inválido")
            get.actualiza_luz_web_socket('', get.accountLocalStorage,'',False)
        except:
           print("no pudo conectar el websocket en estrategiaSheetWS.py ")
           get.actualiza_luz_web_socket('', get.accountLocalStorage,'',False)
    return render_template('notificaciones/estrategiaOperando.html')
     
       
def market_data_handler_estrategia(message):
    global tiempo_inicial_30s_ms,tiempo_inicial_5min_ms,VariableParaSaldoCta   
    
    #print(message)
    
  
    # message1 = {'type': 'Md', 'timestamp': 1684504693780, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'WTI/JUL23'}, 'marketData': {'OF': [{'price': 72.44, 'size': 100}], 'BI': [{'price': 72.4, 'size': 100}], 'LA': {'price': 72.44, 'size': 200, 'date': 1684504670967}}}
    # message2 = {'type': 'Md', 'timestamp': timeuno, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'ORO/JUL23'}, 'marketData': {'OF': [{'price': 1960, 'size': 100}], 'BI': [{'price': 1955, 'size': 100}], 'LA': {'price': 1956, 'size': 200, 'date': 1684504670967}}}
    # message = {'type': 'Md', 'timestamp': timeuno, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'WTI/JUL23'}, 'marketData': {'OF': [{'price': 76, 'size': 100}], 'BI': [{'price': 75, 'size': 100}], 'LA': {'price': 75.5, 'size': 3, 'date': 1687786000759}}}    
        ###### BOTON DE PANICO #########        
    response = botonPanicoRH('None') 
   # print("MDH respuesta desde el boton de panico", response)
   
    
    if response != 1: ### si es 1 el boton de panico fue activado
     
      #  print(" FUN: market_data_handler_estrategia: _") 

        # Obtén el timestamp del mensaje
        marca_de_tiempo = int(message["timestamp"])
        marca_de_tiempo_para_leer_sheet = marca_de_tiempo
        Symbol = message["instrumentId"]["symbol"]
       
        if diccionario_global_operaciones or diccionario_operaciones_enviadas:
          if Symbol in diccionario_global_operaciones or Symbol in diccionario_operaciones_enviadas:
  
                # Verifica si han pasado 30 segundos
                han_pasado_30_segundos, tiempo_inicial_30s_ms = control_tiempo_lectura(30000, tiempo_inicial_30s_ms, marca_de_tiempo)

                if han_pasado_30_segundos:
                    print('Pasaron 30 segundos')
                    VariableParaSaldoCta=cuenta.obtenerSaldoCuentaConObjeto(pyRofexInicializada, account=cuentaGlobal )# cada mas de 5 segundos
                    # Reinicia el tiempo_inicial_30s_ms para el próximo intervalo
                    tiempo_inicial_30s_ms = marca_de_tiempo
                
                
                
                    # Verifica si han pasado 5 minutos
                han_pasado_5_minutos, tiempo_inicial_5min_ms = control_tiempo_lectura(300000, tiempo_inicial_5min_ms, marca_de_tiempo)
                banderaLecturaSheet = 1 #La lectura del sheet es solo cada x minutos
                if han_pasado_5_minutos:
                    print('Pasaron 5 minutos')
                    _cancela_orden(0)
                    banderaLecturaSheet = 0 #La lectura del sheet es solo cada x minutos
                    # Reinicia el tiempo_inicial_5min_ms para el próximo intervalo
                    tiempo_inicial_5min_ms = marca_de_tiempo
                
                      
                # Va afuera de la verificacion de periodo de tiempo, porque debe ser llamada inmediatamente
                # para cumplir con el evento de mercado market data



                if message["marketData"]["BI"] is None or len(message["marketData"]["BI"]) == 0:
                    pass
                    #print("FUN market_data_handler_estrategia: message[marketData][BI] es None o está vacío")
                elif message["marketData"]["OF"] is None or len(message["marketData"]["OF"]) == 0:
                    pass
                    #print("FUN market_data_handler_estrategia: message[marketData][OF] es None o está vacío")
                elif message["marketData"]["LA"] is None or len(message["marketData"]["LA"]) == 0:            
                    pass
                    #print("FUN market_data_handler_estrategia: message[marketData][LA] es None o está vacío")
                else:
                    
                    #tiempoAhora = datetime.now()
                    #print('"FUN market_data_handler_estrategia')
                    #pass
                    estrategiaSheetNuevaWS(message, banderaLecturaSheet)
                    
                    #tiempoDespues = datetime.now()
                    #teimporAhoraInt = tiempoDespues - tiempoAhora
                    #tiempomili =  teimporAhoraInt.total_seconds() * 1000
                #  print("FUN_ veta_capital_44593_001 tiempoTotal en microsegundos: ",teimporAhoraInt.microseconds," en milisegundo: ",tiempomili)
            
        
@estrategiaSheetWS.route('/botonPanicoPortfolio/', methods = ['POST']) 
def boton_panico_portfolio():
     if request.method == 'POST':
        try:
            usuario = request.form['usuario_portfolio']
            get.accountLocalStorage = request.form['account']
            access_token = request.form['access_token_portfolio']
            correo_electronico = request.form['correo_electronico_portfolio']
            respuesta = botonPanicoRH('true')
            estadoOperacionAnterioCargaDiccionarioEnviadas(pyRofexInicializada=pyRofexInicializada,account=request.form['account'],user_id=correo_electronico,userCuenta=usuario)
            #get.pyRofexInicializada.close_websocket_connection()
            respuesta = botonPanicoRH('true')
            _cancela_orden(0)
            respuesta = botonPanicoRH('false')
            return  operaciones.estadoOperacion()
        except:
           print("no pudo leer los datos de local storage")
     return operaciones.estadoOperacion()
   
@estrategiaSheetWS.route('/botonPanico/', methods = ['POST']) 
def botonPanico():
    if request.method == 'POST':
      try:           
            account = request.form['account']
            respuesta = botonPanicoRH('true')
            _cancela_orden(9)
            respuesta = botonPanicoRH('false')
            pyRofexInicializada = get.ConexionesBroker[account]['pyRofex']
            
            pyRofexInicializada.close_websocket_connection(environment=account)
            get.actualiza_luz_web_socket('',account,'',False)
            return render_template("utils/bottonPanic.html" ) 
      except:
           print("no pudo leer los datos de local storage")         
           return render_template("utils/bottonPanic.html" ) 

def botonPanicoRH(message):
    # Llamada al método /botonPanico utilizando la referencia a wsConnection
        if message == 'true':
         get.VariableParaBotonPanico = 1
        #print("Se accionó el Boton de Panico ?",get.VariableParaBotonPanico)
        elif message == 'false':
            get.VariableParaBotonPanico = 0
       
        return get.VariableParaBotonPanico
    
def estrategiaSheetNuevaWS(message, banderaLecturaSheet):# **11
    if banderaLecturaSheet == 0:
        print('entra en estrategiaSheetNuevaWS punto de control sheeeet')
        ContenidoSheet = get.diccionario_global_sheet['argentina']
        banderaLecturaSheet = 1
        ContenidoSheet_list = list(ContenidoSheet)
        
        for Symbol,tipo, TradeEnCurso,ut,senial,gan_tot, dias_operado,precioUt in ContenidoSheet_list[2:]:
            if Symbol in diccionario_global_operaciones:
                if senial != '':
                    #aqui entra en caso que tenga que cambiar la señal de trading
                    if senial != diccionario_global_operaciones[Symbol]['senial']:
                        if diccionario_global_operaciones[Symbol]['status'] == "0":
                            diccionario_global_operaciones[Symbol]['senial'] = senial


            mepAl30 = 460 ####Calcula dolar MEP
     # Verificar si el diccionario de operaciones está vacío
    #if not get.diccionario_global_operaciones:
    #    print("El diccionario de operaciones está vacío.")
    #else:
        # Iterar sobre las claves y valores del diccionario
    #    for clave, valor in get.diccionario_global_operaciones.items():
            # Imprimir cada clave y su correspondiente valor
   #         print("El diccionario de operaciones contiene esto")
   #         print(clave)
   #         print(valor)
    
    Symbol = message['instrumentId']['symbol']
    
    if Symbol in diccionario_global_operaciones:
        #print('___________________________________________________________')    
       # print(message['instrumentId']['symbol']) 
        #rutaMDH = 'C:\\Users\\mDioli\\Documents\\tmp\\operacionesMDH_01.csv'
        
        #append_order_report_to_csv(Symbol, rutaMDH)
        tipo_de_activo = diccionario_global_operaciones[Symbol]['tipo_de_activo']
        senial = diccionario_global_operaciones[Symbol]['senial']
        TradeEnCurso =  diccionario_global_operaciones[Symbol]['tradeEnCurso']
        
       # if get.diccionario_global_operaciones[Symbol] == message["instrumentId"]["symbol"]:
        if diccionario_global_operaciones[Symbol]['status'] == "0":
               
                if diccionario_global_operaciones[Symbol]['ut'] !=0: 
                                                 
                    if senial != "":
                        Liquidez_ahora_cedear = 0
                        if TradeEnCurso in ['LONG_', 'SHORT']:
                            if senial == 'OPEN.':
                                Liquidez_ahora_cedear = obtener_liquidez_actual(message, "OF")
                            
                            elif senial == 'closed.':
                                Liquidez_ahora_cedear = obtener_liquidez_actual(message, "BI")                            
                          
                            cantidad_a_usar = min(Liquidez_ahora_cedear, diccionario_global_operaciones[Symbol]['ut'])
                            estrategia = OperacionEstrategia(
                                                                pyRofexInicializada=pyRofexInicializada,
                                                                diccionario_global_operaciones=diccionario_global_operaciones,
                                                                diccionario_operaciones_enviadas=diccionario_operaciones_enviadas,
                                                                Symbol=Symbol,
                                                                tipo_de_activo=tipo_de_activo,
                                                                Liquidez_ahora_cedear=cantidad_a_usar,
                                                                senial=senial,
                                                                message=message
                                                            )
                            
                            estrategia.operar()
                        else:
                            # Manejo de otro tipo de TradeEnCurso si es necesario
                            pass
       
def obtener_liquidez_actual(message, key):
    if message and "marketData" in message and key in message["marketData"]:
        if isinstance(message["marketData"][key][0]["size"], int):
            return message["marketData"][key][0]["size"]
        elif "LA" in message["marketData"] and isinstance(message["marketData"]["LA"]["size"], int):
            return message["marketData"]["LA"]["size"]
    return 0


def simbolo_no_en_diccionario(simbol, diccionarios):    
    for key, diccionario in diccionarios.items():       
        if simbol == diccionario['Symbol']:
            return False
    return True

def cargaUt(UT_unidadTrader, elemento7, elemento3):
    try:
        if elemento7 == -1:
            elemento7 = 1
            console.log('elemento7 = 1: Error de precio desde sheet ')
        # Calcular el trader base
        ut_trader = UT_unidadTrader / elemento7
        ut_trader = abs(int(ut_trader))
        # Reemplazar comas y puntos para manejar el formato numérico
        # LONG -1, LONG -2
        factorNuevo = elemento3.replace("_", "").replace("LONG", "").strip()
       # factorNuevo = re.search(r'[-+]?\d*\.?\d+', factorNuevo)
      #  factorUtnuevo = int(match.group()) if match else None  # Convertir a int si se encuentra un número
        factorUtnuevo = abs(int(factorNuevo))
      
        
        # Filtrar para solo obtener números <= 20
        if factorUtnuevo > 20:
            return ut_trader  # Ignorar valores mayores a 20
         
        # Ajustar el trader base según el factor calculado
        ut_tradert = ut_trader * factorUtnuevo
        return ut_tradert  # Devolver el UT ajustado
    except (ValueError, AttributeError):
        # Si elemento8 no es válido (por ejemplo, #REF!, None, etc.), devolver el UT base
        return UT_unidadTrader

def carga_operaciones(app,pyRofexInicializada,ContenidoSheet_list,account,usuario,correo_electronico,message,idTrigger):#carg
     coincidencias = []
     contador_1=0
     símbolos_vistos = set()
     tiempoLecturaSaldo = datetime.now()
   
   
     usuariodb = db.session.query(Usuario).filter(Usuario.correo_electronico == correo_electronico).first()
     unidadTrader = db.session.query(UnidadTrader).filter(UnidadTrader.trigger_id == idTrigger).first()
    
    # saldo = cuenta.obtenerSaldoCuentaConObjeto(pyRofexInicializada, account=account )

     #filtrar las coincidencias entre las dos listas
     for elemento1 in ContenidoSheet_list:
        if not isinstance(elemento1, list):
            elemento1 = list(elemento1)
        
        if contador_1 >= 2:
            for key, elemento2 in diccionario_operaciones_enviadas.items():
                if elemento1[0] == elemento2['Symbol']:
                    if elemento2['Symbol'] not in símbolos_vistos:
                        if elemento1[4] == 'closed.':
                                print('account: ',account,' elemento1[0] ******************', elemento1[0], 'elemento2[_ut_]:', elemento2['_ut_'], '**** ', elemento1[4], ' tipo:', elemento1[1],' tradeEnCurso: ',elemento1[2])
                                app.logger.info(elemento1)
                                # Paso 1: Eliminar los puntos
                                cadena_sin_puntos = elemento1[7].replace('.', '')
                                # Paso 2: Reemplazar la coma por un punto
                                cadena_correcta = cadena_sin_puntos.replace(',', '.')
                                # Paso 3: Convertir la cadena a float
                                precio = float(cadena_correcta)
                                ut = cargaUt(unidadTrader.ut, precio, elemento1[2])
                                elemento1[3] =  ut 
                                coincidencias.append(elemento1)
                        elif elemento1[2] == 'SHORT_2':
                            if elemento1[4] == '':
                                print('account: ',account,' elemento1[0] ******************', elemento1[0], 'elemento2[_ut_]:', elemento2['_ut_'], '**** ', elemento1[4], ' tipo:', elemento1[1],' tradeEnCurso: ',elemento1[2])
                                app.logger.info(elemento1)
                                elemento1[3] = int(elemento2['_ut_'])
                                coincidencias.append(elemento1)
                        elif elemento1[4] == 'OPEN.':
                            if simbolo_no_en_diccionario(elemento1[0], diccionario_operaciones_enviadas):
                                print('account: ',account,' elemento1[0] ******************', elemento1[0], 'elemento2[_ut_]:', elemento2['_ut_'], '**** ', elemento1[4], ' tipo:', elemento1[1],' tradeEnCurso: ',elemento1[2])
                                app.logger.info(elemento1)
                                elemento1[3] = int(elemento2['_ut_'])
                                coincidencias.append(elemento1)
                        símbolos_vistos.add(elemento2['Symbol'])
                    else:
                        elemento1[3] = 0
                        coincidencias.append(elemento1)
                        símbolos_vistos.add(elemento2['Symbol'])
        contador_1 += 1
     #coincidencias = [elemento2 for elemento1 in message for elemento2 in ContenidoSheet_list if elemento1 == elemento2[0]]
    
     contador = 0
     for elemento1 in ContenidoSheet_list:
        if contador >= 2:
            #print('elemento1 ', elemento1)        
            for elemento2 in message:
             # if elemento1[0] == 'MERV - XMEV - SUPV - 24hs':
              #  print(' elemento1[0] ', elemento1 ,' elemento2 ',elemento2)                
                if elemento1[2].startswith("LONG"):  # Verifica si empieza con "LONG "   
                     if int(elemento1[3]) != 0:                       
                          if elemento1[4] == 'OPEN.':
                               #if simbolo_no_en_diccionario(elemento1[0], diccionario_operaciones_enviadas):
                                if elemento1[0] == elemento2:
                                        # Paso 1: Eliminar los puntos
                                    cadena_sin_puntos = elemento1[7].replace('.', '')
                                    # Paso 2: Reemplazar la coma por un punto
                                    cadena_correcta = cadena_sin_puntos.replace(',', '.')
                                    # Paso 3: Convertir la cadena a float
                                    precio = float(cadena_correcta)
                                    ut = cargaUt(unidadTrader.ut, precio, elemento1[2])
                                    ut = abs(int(ut))
                                    # Paso 6: Agregar a elemento1 y coincidencias
                                    lista_modificable = list(elemento1)

                                    # Modificar el valor en el índice deseado
                                    lista_modificable[3] = str(ut)  # Cambia el valor en el índice 3

                                    # Convertir la lista de nuevo a una tupla si es necesario
                                    tupla_modificada = tuple(lista_modificable)
                                
                                    coincidencias.append(tupla_modificada)
                                # print(' elemento1[] ', elemento1[0])
                                # print(coincidencias)
                            
        contador += 1  
          
       
     for elemento  in coincidencias:  
         # Paso 1: Eliminar los puntos
         cadena_sin_puntos = elemento[7].replace('.', '')
        # Paso 2: Reemplazar la coma por un punto
         cadena_correcta = cadena_sin_puntos.replace(',', '.')
        # Paso 3: Convertir la cadena a float
         precio = float(cadena_correcta)
         if int(elemento[3]) == 0:
            ut = cargaUt(unidadTrader.ut, precio, elemento1[2])
                                      
        
            ut = abs(int(ut))
         else:
            ut = abs(int(elemento[3]))
         if ut > 0:
        #  print("FUN carga_operaciones_ print(elem[0]",elemento[0],"elem[1]",elemento[1],",elem[2]",elemento[2],",elem[3]",elemento[3],",elem[4])",elemento[4])
            #print(elemento[0],elemento[1],elemento[2],elemento[3],elemento[4])
            if elemento1[2].startswith("LONG"):  # Verifica si empieza con "LONG "
                    tradeEnCurso = 'LONG_'
            else:
                    tradeEnCurso = elemento1[2]
            # Cargar los valores del objeto en el diccionario global
            if  elemento[4] == 'closed.': 
                if elemento[2] =='' or elemento[2] != 'LONG_' or elemento[2] != 'SHORT':
                     tradeEnCurso = 'SHORT'
            else:
                 tradeEnCurso =  elemento[2]
            
            if  elemento[2] == 'SHORT':
               senial='closed.'
            else:
               senial = elemento[4] 
            # cargar_ordenes_db(cuentaAcount=usuario,cantidad_a_comprar_abs=ut,signal=senial,clOrdId='', orderStatus='operado', tipo_orden='trigger', symbol=elemento[0], user_id=usuariodb.id, accountCuenta=account)   
            if tradeEnCurso.startswith("LONG"):  # Verifica si empieza con "LONG "
                    tradeEnCurso = 'LONG_'
            if tradeEnCurso.startswith("LONG -"):  # Verifica si empieza con "LONG "
                    tradeEnCurso = 'SHORT'
            nueva_orden_para_dic = {
                'user_id': usuariodb.id,
                'userCuenta': usuario,
                'accountCuenta': account, 
                'idTrigger' : idTrigger,          
                'clOrdId_alta': '',
                'clOrdId_baja': '',
                'orderId': '',
                'wsClOrdId_timestamp': datetime.now(),
                'clOrdId_alta_timestamp': None,
                'clOrdId_baja_timestamp': None,
                'proprietary': True,
                'marketId': '',           
                'symbol': elemento[0],
                'tipo_de_activo': elemento[1],
                'tradeEnCurso': tradeEnCurso,                
                'ut':ut,            
                'senial': senial,
                'status': '0',
                'tiempoSaldo':tiempoLecturaSaldo,
                'saldo':VariableParaSaldoCta
            }
        # Cargar cada objeto Orden en el diccionario global con una clave única
            diccionario_global_operaciones[elemento[0]] = nueva_orden_para_dic
        
            if elemento[0] in diccionario_global_operaciones:
                    contenido = diccionario_global_operaciones[elemento[0]]
                   # print(f"Contenido encontrado para {contenido['symbol']}:")

                    # Seleccionar los campos específicos
                    campos_especificos = [
                        'symbol',
                        'tipo_de_activo',
                        'tradeEnCurso',
                        'ut',
                        'senial',
                        'status'
                    ]

                    # Formatear los campos específicos en una sola línea
                    contenido_linea = ', '.join([f"{campo}: {contenido[campo]}" for campo in campos_especificos])
                    print('c: ',account,' ',contenido_linea)
            else:
                    print(f"No se encontró contenido para {elemento[0]} en diccionario_global_operaciones.")

        
    # Acceder al diccionario global y a los objetos Orden
     
    #     db.session.add(nueva_orden)
    #     db.session.commit() 
     #get.current_session = db.session
     for clave, valor in diccionario_global_operaciones.items():
          print(f'Clave: {clave}, Valor: {valor}')
   
    # db.session.close()
     if len(diccionario_global_operaciones) == 0 or diccionario_global_operaciones == None:
            parametros = {
                    'account': get.ConexionesBroker[account]['cuenta'], 
                    'user_id': idUser, 
                    'symbol': '',
                    'mensaje' : 'No hay operaciones',
                    'status': 'termino'               
                }

            get.estrategias_usuario__endingOperacionBot[idTrigger] = parametros
     app.logger.info('______CARGA_OPERACIONES____') 
    # app.logger.info(diccionario_global_operaciones) 


     
def es_numero(numero):
    try:
          int(numero)
          return True
    except:
        return False
  
def order_report_handler(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']        
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']  
    print(diccionario_global_operaciones[symbol]['accountCuenta'],' ___________ORH_______STATUS__ENTREGADO: ', status, ' symbol: ', symbol)
    timestamp_order_report = order_data['transactTime']  
   
    if es_numero(clOrdId):
        if len(diccionario_operaciones_enviadas) != 0:
            asignarClOrId(order_report)
            if status != 'NEW' and status != 'PENDING_NEW' and status != 'UNKNOWN':  
                _operada(order_report)   

                       
        
def _operada(order_report):
    order_data = order_report['orderReport']
    clOrdId = order_data['clOrdId']
    symbol = order_data['instrumentId']['symbol']
    status = order_data['status']
    stock_para_closed = int(float(obtenerStock(order_data['text'])))

    print(f'Processing order {clOrdId} for {symbol} with status {status}')

    # Verifica si el estado está en la lista de estados relevantes
    if status in ['CANCELLED', 'ERROR', 'REJECTED', 'EXPIRED']:
        actualizar_diccionario_enviadas(order_data, symbol, status)

    # Procesa el estado final
    if status in ['FILLED', 'REJECTED','CANCELLED']:
        procesar_estado_final(symbol, clOrdId)
 
 
 
def procesar_estado_final(symbol, clOrdId):
    global endingGlobal, endingEnviadas

    endingGlobal = False
    endingEnviadas = False
    if diccionario_operaciones_enviadas.get(clOrdId) == 'TERMINADA':
            print(f"[AVISO] La operación {clOrdId} ya estaba en estado TERMINADA, se intentó actualizar nuevamente.")
            # Puedes optar por no actualizarla de nuevo, según la lógica:
            return
    # Actualiza el estado de las operaciones enviadas
    endingEnviadas = actualizar_estado_operaciones( symbol, clOrdId)    
    # Revisa las operaciones globales
    for key, operacionGlobal in diccionario_global_operaciones.items():        
            if operacionGlobal['ut'] == 0:
                # Verifica si ninguna operación relacionada está en estado 'ANTERIOR'
                all_enviadas_validas = all(
                    operacion['status'] == 'TERMINADA'
                    for operacion in diccionario_operaciones_enviadas.values()
                       if operacion["Symbol"] == symbol and operacion['status'] != 'ANTERIOR'
                    )
                any_enviada_anterior = any(
                    operacion['status'] == 'ANTERIOR'
                    for operacion in diccionario_operaciones_enviadas.values()
                     if operacion["Symbol"] == symbol
                )
                if all_enviadas_validas and not any_enviada_anterior:
                    operacionGlobal['status'] = '1'
                    endingGlobal = True
                else:
                    endingGlobal = False
            else:
                endingGlobal = False

    # Asegura que `endingEnviadas` siga siendo 'SI' si corresponde
    if endingGlobal == True and endingEnviadas == True:
        print(f'Final state: endingGlobal={endingGlobal}, endingEnviadas={endingEnviadas}, symbol={symbol}')
        endingOperacionBot(endingGlobal, endingEnviadas, symbol)   
        
def actualizar_estado_operaciones(symbol, clOrdId):
    todas_terminadas = True
    for operacion_enviada in diccionario_operaciones_enviadas.values():
        # Verifica si la operación actual no está terminada
        if operacion_enviada['status'] != 'TERMINADA':
            # Actualiza el estado si coincide con el símbolo y clOrdId proporcionados
            if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId):
                operacion_enviada['status'] = 'TERMINADA'
        
   # Verifica si todas las operaciones están en estado 'TERMINADA'
    for operacion_enviada in diccionario_operaciones_enviadas.values():
        if operacion_enviada["status"] != 'ANTERIOR':
            if operacion_enviada['status'] != 'TERMINADA':
                todas_terminadas = False
                break  # Sale del bucle si encuentra una operación que no está terminada
    return todas_terminadas


def actualizar_diccionario_enviadas(order_data, symbol, status):
    """Actualiza el diccionario de operaciones enviadas según el estado de la orden."""
    
    clOrdId = order_data['clOrdId']
    
    if symbol in diccionario_global_operaciones:
        for key, operacion in diccionario_operaciones_enviadas.items():
            # Si la operación corresponde al símbolo y clOrdId
            if operacion['Symbol'] == symbol and operacion['_cliOrderId'] == int(clOrdId):
                # Si la operación no está 'TERMINADA' ni 'CANCELLED'
                if operacion['status'] not in ['TERMINADA', 'CANCELLED']:
                    # Orden Rechazada ('REJECTED'): Si la orden tiene estado 'REJECTED'
                    if status == 'REJECTED':
                        ut_a_devolver = 0
                    # Otros Estados de la Orden: Si la orden tiene cualquier otro estado
                    else:
                          #se coloca este if para que no se le devuelva un valor negativo si la orden tiene estado 'CANCELLED'
                        #y se le le quita el valor de la orden
                        #se debe quitar este if si se desea que el valor de la orden sea positivo cuando la orden sea 'CANCELLED'
                        #if status == 'CANCELLED':
                        #    ut_a_devolver = 0
                        #else:
                        if status == 'CANCELLED':
                            ut_a_devolver = 0
                        else:
                            ut_a_devolver = operacion['_ut_']
                    # Marca la operación como 'TERMINADA'
                    operacion['status'] = 'TERMINADA'
                    
                    # Llamar a la función para actualizar el diccionario global
                    actualizar_diccionario_global(symbol, ut_a_devolver)
                elif operacion['status'] == 'ANTERIOR' and status == 'REJECTED':
                    operacion['status'] = 'TERMINADA'
                elif operacion['status'] == 'CANCELLED':
                    operacion['status'] = 'TERMINADA'
                    



def actualizar_diccionario_global(symbol, ut_a_devolver):
    """Actualiza el diccionario global de operaciones."""
    operacionGlobal = diccionario_global_operaciones.get(symbol)
    if operacionGlobal:
         if int(ut_a_devolver) > 0:  
            operacionGlobal['ut'] += int(ut_a_devolver)
         else:   
            if operacionGlobal['status'] != '0':
                    operacionGlobal['status'] = '0'
            
 
def convert_datetime(original_datetime_str, desired_timezone_str):
    # Convertir la cadena a un objeto datetime
    original_datetime = datetime.strptime(original_datetime_str, "%Y%m%d-%H:%M:%S.%f")

    # Definir la zona horaria deseada
    desired_timezone = pytz_timezone(desired_timezone_str)

    # Convertir el objeto datetime a la zona horaria deseada
    desired_datetime = original_datetime.astimezone(desired_timezone)

    # Convertir el objeto datetime a una cadena en el formato deseado
    desired_datetime_str = desired_datetime.strftime("%Y%m%d-%H:%M:%S.%f")[:-3] + desired_datetime.strftime("%z")

    return desired_datetime_str

def _cancela_orden(delay):
    
   # clOrdId = order_data['clOrdId']
   # symbol = order_data['instrumentId']['symbol']
   # status = order_data['status']
    
    time = datetime.now()
    timestamp_order_report = time.strftime("%Y%m%d-%H:%M:%S.%f%z")
   # example_datetime_str = "20230724-13:23:12.071198"
    example_timezone_str = 'Etc/GMT+3'
    timestamp_order_report = convert_datetime(timestamp_order_report, example_timezone_str)
     
    timestamp_order_report = str(timestamp_order_report)
    
    # Recorrer los elementos del diccionario_enviados
    
    for key, valor in diccionario_operaciones_enviadas.items():    
           
            tiempo_diccionario = valor["timestamp"]
            # Verificar y ajustar el formato de cadena de fecha si es necesario

            if isinstance(tiempo_diccionario, str):
                tiempo_diccionario = datetime.strptime(tiempo_diccionario, "%Y-%m-%d %H:%M:%S")
           
            # Convertir el timestamp en milisegundos a objeto datetime
            # Convertir las cadenas de texto en objetos datetime
            diferencia_segundos = tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario)
           

          #  print("FUN _cancela_orden: diferencia [seg]",diferencia_segundos)
            
            
            #diferencia = fecha2_obj - tiempo_diccionario
            #print("FUN _c ancela_orden: Diferencia",diferencia)

            
            
            #if diferencia >= 300:
            if diferencia_segundos >= delay:
              # print('diferencia_segundos ',diferencia_segundos,' delay ',delay)
               _cancel_if_orders(valor["Symbol"],valor['_cliOrderId'],valor['statusActualBotonPanico'])       
      
def _cancel_if_orders(symbol,clOrdId,order_status):
    #debe sumar de la lista de orden general
    #eliminar de la ordenes enviadas luedo de confirmacion de cancelacion
    try:
        # Obtener el estado de la orden
        if order_status in ['PENDING_NEW','NEW','PENDING','REJECT','ACTIVE','PARTIALLY_EXECUTED','SENT','ROUTED','ACCEPTED','PARTIALLY_FILLED','PARTIALLY_FILLED_CANCELED','PARTIALLY_FILLED_REPLACED','PENDING_REPLACE']:
            print("FUN _cancel_if_orders: ENVIA Orden DE CANCELAR: order_status:", order_status," symbol: ",symbol," clOrdId: ",clOrdId)
            pyRofexInicializada.cancel_order_via_websocket(client_order_id=clOrdId,proprietary='ISV_PBCP',environment=cuentaGlobal) 
        
            # Aumentar el valor de ut en get.diccionario_global_operaciones        
            for key, operacion_enviada in diccionario_operaciones_enviadas.items(): 
                if operacion_enviada["Symbol"] == symbol and operacion_enviada["_cliOrderId"] == int(clOrdId):
                    if operacion_enviada["status"] != 'PENDING_CANCEL':
                        operacion_enviada["status"] = 'PENDING_CANCEL'  
                        operacion_enviada['statusActualBotonPanico'] = 'PENDING_CANCEL' 
                        print("FUN _cancel_if_orders:  Orden :", clOrdId," symbol ",symbol, " operacion_enviada[statusActualBotonPanico] ",operacion_enviada['statusActualBotonPanico'])      
                        break  # Salir del bucle después de eliminar el elemento encontrado    
               
        else:
            pass
            #print('No se puede cancelar la Orden order_status no corresponde') 
            #print("FUN _cancel_if_orders:  Orden order_status:", order_status," symbol ",symbol," clOrdId ",clOrdId) 
    except Exception as e:
        print("Error en Envio de Cancelacion de orden:", e)
    #    print("FUN _cancel_if_orders: La orden no se puede cancelar en el estado actual:", order_status)
               
def tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario):
     fecha2_obj = datetime.strptime(timestamp_order_report, "%Y%m%d-%H:%M:%S.%f%z")
     fecha_comun_enviada = tiempo_diccionario.strftime("%Y%m%d-%H:%M:%S")
     fecha_comun_orh = fecha2_obj.strftime("%Y%m%d-%H:%M:%S")
     #print("FUN tiempoDeEsperaOperacioncalculaTiempo: fecha_enviada",fecha_comun_enviada)
     #print("FUN tiempoDeEsperaOperacioncalculaTiempo: fecha_ORH",fecha_comun_orh)
     # Restar los dos objetos datetime
     fecha_obj1 = datetime.strptime(fecha_comun_enviada, "%Y%m%d-%H:%M:%S")
     fecha_obj2 = datetime.strptime(fecha_comun_orh, "%Y%m%d-%H:%M:%S")

     diferencia = fecha_obj2 - fecha_obj1
     diferencia_segundos = abs(diferencia.total_seconds())
    
     return diferencia_segundos

def asignarClOrId(order_report):
      order_data = order_report['orderReport']
      clOrdId = order_data['clOrdId']
      symbol = order_data['instrumentId']['symbol']
      status = order_data['status']   
      timestamp_order_report = order_data['transactTime'] 
      
    #  print("FUNC_asignarClOrId  symbol ",symbol, " clOrdId ",clOrdId, " status ",status," timestamp_order_report ",timestamp_order_report)
      #pprint.pprint(g et.diccionario_operaciones_enviadas) 
      for key, valor in diccionario_operaciones_enviadas.items():  
        tiempo_diccionario = valor["timestamp"]  
        if valor["Symbol"] == symbol and valor["_cliOrderId"] == 0:                  
            if valor["status"] == '1':                
                # pasa que llegamos aca y wsOrderClId puede no existir mas
                if status in ['PENDING_NEW','REJECT']: 
                    if 'wsClOrdId' in order_report:                
                        wsClOrdId = order_data['wsClOrdId'] 
                        if  valor["_ws_client_order_id"] == int(wsClOrdId):
                            valor["_cliOrderId"] = int(clOrdId)
                            valor["status"] = "2"  
                            valor["statusActualBotonPanico"] = status                          
                else:
                    valor["_cliOrderId"] = int(clOrdId)

      
      
        cargar_estado_para_B_panico(valor,clOrdId,timestamp_order_report,symbol,status,tiempo_diccionario)
        
def cargar_estado_para_B_panico(valor,clOrdId,timestamp_order_report,symbol,status,tiempo_diccionario): 
        #carga el estado para el boton te panico           
        if valor["Symbol"] == symbol and valor["_cliOrderId"] ==  int(clOrdId):               
            if valor['statusActualBotonPanico'] != 'PENDING_CANCEL': 
                if isinstance(tiempo_diccionario, str):
                   tiempo_diccionario = datetime.strptime(tiempo_diccionario, "%Y-%m-%d %H:%M:%S")         
                diferencia_segundos = tiempoDeEsperaOperacioncalculaTiempo(timestamp_order_report,tiempo_diccionario)   
                print("FUN _asignarClOrId: diferencia [seg]",diferencia_segundos)
                #if diferencia_segundos >= 3:       
                valor["statusActualBotonPanico"] = status
                print("FUN_cargar_estado_para_B_panico status ",status, " clOrdId ",clOrdId)
                   




def CargOperacionAnterioDiccionarioEnviadas(app,pyRofexInicializada=None, account=None, user_id=None, userCuenta=None):
    try:
        global VariableParaSaldoCta
        accountCuenta = account
        tiempoLecturaSaldo = datetime.now()
        
        # Obtener saldo de la cuenta
        VariableParaSaldoCta = cuenta.obtenerSaldoCuentaConObjeto(pyRofexInicializada, account=account)
        
        # Obtener posiciones de la cuenta
        respuesta_operacion = pyRofexInicializada.get_account_position(account=account, environment=account)
        reporte = respuesta_operacion['positions']
        
        # Diccionario para almacenar totales de buySize y sellSize por símbolo
        totales = {}
        
        # Iterar sobre las posiciones para calcular totales por símbolo
        for posicion in reporte:
            symbol = posicion['symbol']
            buySize = abs(int(posicion['buySize']))
            sellSize = abs(int(posicion['sellSize']))
            print("Este esta en cartera de la cuenta: ",accountCuenta," Símbolo:", symbol)
            print("Estan en matriz, Cantidad de stock buySize:", posicion['buySize'])
            print("Estan en matriz, Cantidad de stock sellSize:", posicion['sellSize'])
            print()
            # Si el símbolo no está en totales, inicializarlo
            if symbol not in totales:
                totales[symbol] = {'buySize': 0, 'sellSize': 0}
            
            # Sumar buySize y sellSize
            totales[symbol]['buySize'] += buySize
            totales[symbol]['sellSize'] += sellSize
        
        # Limpiar diccionario global de operaciones enviadas
        diccionario_operaciones_enviadas.clear()
        
        # Iterar sobre totales para determinar qué acciones deben venderse
        for symbol, sizes in totales.items():
            buySize = sizes['buySize']
            sellSize = sizes['sellSize']
            
            # Calcular diferencia de acciones para vender
            if buySize > sellSize:
                acciones_a_vender = buySize - sellSize
                
                # Crear diccionario con la información de la operación
                diccionario = {
                    "Symbol": symbol,
                    "_t_": 'None',
                    "_tr_": 'None',
                    "_s_": 'None',
                    "_ut_": acciones_a_vender,
                    "precio Offer": 'None',
                    "_ws_client_order_id": 'None',
                    "_cliOrderId": 0,
                    "timestamp": datetime.now(),
                    "status": 'ANTERIOR',
                    "statusActualBotonPanico": 'ANTERIOR',
                    "user_id": user_id,
                    "userCuenta": userCuenta,
                    "accountCuenta": accountCuenta,
                    "tiempoSaldo": tiempoLecturaSaldo,
                    "saldo": VariableParaSaldoCta
                }
                
                # Agregar diccionario al diccionario global de operaciones enviadas
                diccionario_operaciones_enviadas[len(diccionario_operaciones_enviadas) + 1] = diccionario
        app.logger.info("________CARGA DICCIONARIO OPERACIONES ENVIADAS___________")  
        app.logger.info(accountCuenta)  # Imprimir cuenta en consola
      
       
        return 'ok'  # Retorna 'ok' si la operación fue exitosa
    
    except Exception as e:
        print(f"Error: {e}")  # Imprimir error en caso de excepción
        get.actualiza_luz_web_socket('', get.accountLocalStorage,'',False)
        return 'error'  # Retorna 'error' si ocurre una excepción








         
def estadoOperacionAnterioCargaDiccionarioEnviadas(pyRofexInicializada=None,account=None,user_id=None,userCuenta=None):
   try:        
        repuesta_operacion = pyRofexInicializada.get_all_orders_status()
        
        datos = repuesta_operacion['orders']
        #print("posicion operacionnnnnnnnnnnnnnnnnnnnn ",datos)
        diccionario = {}
        diccionario_operaciones_enviadas.clear()        
        for dato in datos:
          if dato['orderId'] is not None:
            if es_numero(dato['clOrdId']):  
                orderId = dato['orderId']
                clOrdId = dato['clOrdId']
                proprietary = dato['proprietary']
                execId = dato['execId']
                accountId = dato['accountId']
                Symbol = dato['instrumentId']['symbol']
                price = dato['price']
                orderQty = dato['orderQty']
                ordType = dato['ordType']
                side = dato['side']
                timeInForce = dato['timeInForce']
                transactTime = dato['transactTime']
                avgPx = dato['avgPx']
                #lastPx = dato['lastPx']
                #lastQty = dato['lastQty']
                cumQty = dato['cumQty']
                leavesQty = dato['leavesQty']
                status = dato['status']
                text = dato['text']
                originatingUsername = dato['originatingUsername']

                
                diccionario = {
                            "Symbol": Symbol,
                            "_t_": 'None',
                            "_tr_": 'None',
                            "_s_": 'None',
                            "_ut_": orderQty,
                            "precio Offer": 'None',
                            "_ws_client_order_id": 'None',
                            "_cliOrderId": int(clOrdId),
                            "timestamp": datetime.now(),
                            "status": status,
                            "statusActualBotonPanico":status,
                            "user_id": user_id,
                            "userCuenta": userCuenta,
                            "accountCuenta": account
                                }
                diccionario_operaciones_enviadas[len(diccionario_operaciones_enviadas) + 1] = diccionario
                #pprint.pprint( g et.diccionario_operaciones_enviadas)
            #for key, valor in g et.diccionario_operaciones_enviadas.items():
            #    print(key," : ",valor['_cliOrderId'])
        return 'ok'
   except Exception as e:       
        print("error de carga de diccionario de enviados", e)  
        flash(' error de carga de diccionario de enviados')    
   return 'ok'                   

def obtenerStock(cadena):
# Verificar si la cadena contiene la frase "Stock insuficiente"
    if "Stock insuficiente" in cadena:
        # Buscar el índice del signo "="
        index = cadena.find("=")
        # Extraer el valor después del signo "=" y eliminar los espacios en blanco al principio y al final
        valor_despues_de_igual = cadena[index:].strip()
        
        #print('valor_despues_de_igual ' ,valor_despues_de_igual)
       
        # Buscar el número después del signo "=" utilizando una expresión regular
        match = re.search(r'(?<== )-?\d+\.\d+', valor_despues_de_igual)
       # print('match ' ,match)
        # Verificar si se encontró una coincidencia
        if match:
            valor_despues_de_igual = match.group()
           # print("El primer número después del signo '=' es:", valor_despues_de_igual)
            valor = int(float(valor_despues_de_igual))
           # print(valor)
        
            return valor_despues_de_igual
        else:
           return '0'
    else:
       return '0' 


def endingOperacionBot(endingGlobal, endingEnviadas, symbol,account=None):
    try:
           # Limpiar el diccionario si se cumplen todas las condiciones
           
            print("###############################################") 
            print("###############################################") 
            print("###############################################")  
            print("FELICIDADES, EL BOT TERMINO DE OPERAR CON EXITO") 
            print("###############################################") 
            print("###############################################") 
            print("###############################################") 
            if account is None and symbol is not None:

                account = diccionario_global_operaciones[symbol]['accountCuenta']
                idTrigger = diccionario_global_operaciones[symbol]['idTrigger']
                print('endingGlobal___ ', endingGlobal, ' endingEnviadas', endingEnviadas, 'symbol: ', symbol,'account: ', account, 'idTrigger: ', idTrigger)
           
            pyRofexInicializada = get.ConexionesBroker[account]['pyRofex'] 
            if account is not None:
                diccionario_operaciones_enviadas.clear()
                pyRofexInicializada.remove_websocket_market_data_handler(market_data_handler_estrategia, environment=account)
            parametros = {
                'account': get.ConexionesBroker[account]['cuenta'], 
                'user_id': idUser, 
                'symbol': symbol,
                'mensaje' : 'FELICIDADES, EL BOT TERMINO DE OPERAR CON EXITO !!!',
                'status': 'termino'               
            }

            get.estrategias_usuario__endingOperacionBot[idTrigger] = parametros

         
    except KeyError as e:
        print(f"KeyError: La clave {e} no se encontró en los diccionarios.")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")

@estrategiaSheetWS.route("/strategies_estrategias_detenerMDHtrigger_lanzado", methods=['POST'])
def strategies_estrategias_detenerMDHtrigger_lanzado():
    try:
        if request.method == 'POST':
            # Obtener los datos del POST
            usuario_id = request.form.get('usuario_id')
            trigger_id = request.form.get('trigger_id')
            account = request.form.get('account')

            # Inicializar la conexión pyRofex y eliminar el websocket handler
            pyRofexInicializada = get.ConexionesBroker[account]['pyRofex'] 
            pyRofexInicializada.remove_websocket_market_data_handler(market_data_handler_estrategia, environment=account)

            # Devolver una respuesta exitosa
            return jsonify({"message": "MDH trigger detenido correctamente"}), 200

    except Exception as e:
        print("Error al detener MDH trigger:", str(e))
        # Devolver un mensaje de error
        return jsonify({"error": "Error al detener MDH trigger", "details": str(e)}), 500
@estrategiaSheetWS.route("/estrategiaSheetWS_verificar_estado/", methods=['POST'])
def estrategiaSheetWS_verificar_estado():
    try:
        # Obtén los datos JSON del cuerpo de la solicitud
        data = request.get_json()
         # Verifica si los datos se obtuvieron correctamente
        if not data:
            raise BadRequest('No se recibió ningún dato JSON.')

        # Obtén los valores del JSON
        idTrigger = data.get('idTrigger')
        userId = data.get('userId')
        account = data.get('cuenta')
        nombreEstrategia = data.get('nombreEstrategia')
        
        # Verifica si idTrigger y cuenta están presentes
        if idTrigger is None or account is None:
            raise BadRequest('Faltan parámetros requeridos: idTrigger o cuenta.')

        # Verifica si la cuenta existe en el diccionario
        parametros = get.estrategias_usuario__endingOperacionBot.get(idTrigger)        
        # Verifica si se encontraron parámetros
        if parametros:
            # Desglosar las variables
            account = parametros.get('account')
            user_id = parametros.get('user_id')
            symbol = parametros.get('symbol')
            status = parametros.get('status')
            mensaje = parametros.get('mensaje')
            # Compara el tiempo actual con el tiempo de inicio
            
            if control_tiempo_lectura_verifiar_estado(300000, get.marca_de_tiempo_para_verificar_estado):
                    pyRofexInicializada.remove_websocket_market_data_handler(market_data_handler_estrategia, environment=account)
                    return jsonify({'estado': 'terminado', 'account': account, 'mensaje': 'Operación superó los 5 minutos.'}), 200

            # Verifica el estado y responde apropiadamente
            if status == 'termino':
                 return jsonify({'estado': 'listo', 'account': account, 'mensaje': mensaje}), 200
        
        else:
            # Verifica el tiempo de lectura
            if control_tiempo_lectura_verifiar_estado(300000, get.marca_de_tiempo_para_verificar_estado):
                  # Inicializar la conexión pyRofex y eliminar el websocket handler
                pyRofexInicializada = get.ConexionesBroker[account]['pyRofex'] 
                try:
                    #ordenes_cargadas = db.session.query(Orden).filter_by(user_id=user_id, accountCuenta=account).all()

                    repuesta_operacion = pyRofexInicializada.get_all_orders_status(account=account, environment=account)
                    ordenes = repuesta_operacion.get('orders', [])                   
                    # Verificar si hay órdenes para procesar
                    if ordenes:
                        # Recorrer la lista de órdenes
                        symbols_encontrados = []  # Lista para almacenar los símbolos encontrados
                        sim = ''
                        for orden in ordenes:
                            symbol = orden['instrumentId']['symbol']  # Obtener el symbol
                            accountId = orden['accountId']['id']      # Obtener el accountId
                            # Recorrer el diccionario de operaciones globales
                            
                            
                         
                            for key, operacionGlobal1 in diccionario_global_operaciones.items():
                                if operacionGlobal1['ut'] == 0:  # Asegúrate de que 'ut' está en cada operacionGlobal
                                    # Comparar símbolos entre la operación global y la orden cargada
                                    if operacionGlobal1['symbol'] == symbol:
                                        sim = symbol
                                        symbols_encontrados.append(symbol)  # Agregar símbolo encontrado

                        # Verificar si todos los símbolos de las órdenes están en symbols_encontrados
                        if len(symbols_encontrados) == len(ordenes):
                            # Llamada a la función endingOperacionBot si todos los símbolos están presentes                           
                            
                            diccionario_operaciones_enviadas.clear()
                            pyRofexInicializada.remove_websocket_market_data_handler(market_data_handler_estrategia, environment=account)
        
                            
                            return jsonify({
                                'estado': 'listo',
                                'account': account,
                                'mensaje': 'FELICIDADES, EL BOT TERMINO DE OPERAR CON EXITO !!!',
                                'redirect': url_for('accionesTriggers.terminoEjecutarEstrategia')  # Corregido aquí
                            }), 200
                    else:
                        return jsonify({'estado': 'en_proceso'}), 200               
       
                except BadRequest as e:
                    pass
        
            else:
                return jsonify({'estado': 'en_proceso'}), 200
       
    except BadRequest as e:
        # Maneja los errores de solicitud incorrecta
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Maneja cualquier otro error
        return jsonify({'error': 'Ocurrió un error inesperado.', 'detalle': str(e)}), 500



         




def error_handler(message):
  print("error_handler Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))



    



def append_order_report_to_csv(report, rutaORH):
    with open(rutaORH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Comprobar si el archivo está vacío para escribir las cabeceras
        file.seek(0)
        if file.tell() == 0:
            headers = []
            for key, value in report.items():
                if isinstance(value, dict):
                    for sub_key in value.keys():
                        headers.append(f"{key}_{sub_key}")
                else:
                    headers.append(key)
            writer.writerow(headers)
        
        # Escribir los valores
        values = []
        for key, value in report.items():
            if isinstance(value, dict):
                for sub_value in value.values():
                    values.append(sub_value)
            else:
                values.append(value)
        writer.writerow(values)
        
def control_tiempo_lectura(intervalo_ms, tiempo_inicial, marca_de_tiempo):
    # Inicializa el tiempo_inicial si es la primera vez que se ejecuta
    if tiempo_inicial is None:
        tiempo_inicial = marca_de_tiempo
        return False, tiempo_inicial
    return (marca_de_tiempo - tiempo_inicial) >= intervalo_ms, tiempo_inicial