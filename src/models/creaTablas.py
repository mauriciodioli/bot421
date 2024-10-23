from models.usuario import Usuario
from models.cuentas import Cuenta
from models.ficha import Ficha
from models.logs import Logs
from models.orden import Orden
from models.modelMedia.image import Image
from models.instrumento import Instrumento
from models.instrumentoGet import InstrumentoGet
from models.instrumentosSuscriptos import InstrumentoSuscriptos
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
from models.trades import Trade
from models.trazaFicha import TrazaFicha
from models.brokers import Broker
from models.triggerEstrategia import TriggerEstrategia
from models.strategy import Strategy
from models.unidadTrader import UnidadTrader
from models.administracion.altaEstrategiaApp import AltaEstrategiaApp
from models.payment_page.tarjetaUsuario import TarjetaUsuario
from models.payment_page.suscripcionPlanUsuario import SuscripcionPlanUsuario
from models.payment_page.Promotion import Promotion
from models.newsLetter.newLetter import NewLetter
from models.modelMedia.video import Video
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.publicaciones.estado_publi_usu import Estado_publi_usu
from models.servidores.servidorAws import ServidorAws
from datetime import datetime
from flask import Blueprint,flash

creaTabla = Blueprint('creaTabla',__name__)

def crea_tablas_DB():
    Usuario.crear_tabla_usuarios()
    Cuenta.crear_tabla_cuentas()
    Ficha.crear_tabla_ficha()
    Logs.crear_tabla_logs()
    Image.crear_tabla_image()
    Trade.crear_tabla_trades()
    TrazaFicha.crear_tabla_trazaFichas()
    TriggerEstrategia.crear_tabla_triggerEstrategia()
    Orden.crear_tabla_orden()   
    Instrumento.crear_tabla_instrumento()
    InstrumentoGet.crear_tabla_instrumentoGet()
    InstrumentoSuscriptos.crear_tabla_instrumentoSuscriptos()
    InstrumentoEstrategiaUno.crear_tabla_instrumentoEstrategiaUno()
    Broker.crear_tabla_brokers()
    Strategy.crear_tabla_strategy()
    UnidadTrader.crear_tabla_ut()
    AltaEstrategiaApp.crear_tabla_altaEstrategiaApp()
    TarjetaUsuario.crear_tabla_tarjetaUsuario()
    SuscripcionPlanUsuario.crear_tabla_suscripcionPlanUsuario()
    Promotion.crear_tabla_promocion()
    NewLetter.crear_tabla_newsLetter()
    Video.crear_tabla_video()
    Publicacion.crear_tabla_publicacion()
    Public_imagen_video.crear_tabla_Public_imagen_video()
    Estado_publi_usu.crear_tabla_estado_publi_usu()
    ServidorAws.crear_tabla_servidor_aws()
    flash('Tablas creadas exitosamente', 'success')
    print('tablas creadas exitosamente')
    
    
    
    
    
    
    
   
    