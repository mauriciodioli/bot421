# afiliado.py
from datetime import datetime,timezone
from flask import Blueprint, request, redirect, abort, jsonify,current_app
from models.tracking.impresion_afiliado import ImpresionAfiliado
from models.tracking.click_afiliado import ClickAfiliado
import os

from productosComerciales.traking.tracking_utils import append_params, price_bucket_of, discount_pct_of


from utils.db_session import get_db_session
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.usuarioPublicacionUbicacion import UsuarioPublicacionUbicacion
from models.modelMedia.image import Image
from models.modelMedia.video import Video
afiliado = Blueprint("afiliado", __name__)

# Config simple para subIDs (podés mover a ENV)
USE_AE_PORTALS = True  # si False, usa subid/subid1/...
SUB_KEYS_AE    = ["aff_sub", "aff_sub2", "aff_sub3", "aff_sub4", "aff_sub5", "aff_fcid"]
SUB_KEYS_GEN   = ["subid", "subid1", "subid2", "subid3", "subid4", "subid5"]

def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

def get_lang():
    # usa ?lang=xx o header Accept-Language
    return request.args.get("lang") or (request.accept_languages.best or "es")

def build_sub_params(pub, user_id, lang, visitor_id):
    values = [
        getattr(pub, "id", None),      # 0: publicación
        user_id,                       # 1: user_id si existe
        lang,                          # 2: idioma
        getattr(pub, "categoria_id", None),  # 3
        getattr(pub, "ambito", None),        # 4
        visitor_id                     # 5: visitor id
    ]
    params = {}
    keys = SUB_KEYS_AE if USE_AE_PORTALS else SUB_KEYS_GEN
    for i, k in enumerate(keys):
        if i < len(values):
            params[k] = values[i]
    return params

def val(pub, name):
    return pub.get(name) if isinstance(pub, dict) else getattr(pub, name, None)

def snapshot_from_publicacion(pub, imagenes=None, videos=None):
    imagenes = imagenes or []
    videos   = videos or []

    titulo = (val(pub, "titulo") or "").strip()
    texto  = (val(pub, "texto")  or "").strip()
    precio = val(pub, "precio")
    p0     = val(pub, "precio_original")

    return dict(
        ambito           = val(pub, "ambito"),
        categoria_id     = val(pub, "categoria_id"),
        categoria_nombre = val(pub, "categoriaNombre"),
        layout           = val(pub, "layout"),
        color_titulo     = val(pub, "color_titulo"),
        color_texto      = val(pub, "color_texto"),
        titulo_len       = len(titulo),
        texto_len        = len(texto),
        imagenes_count   = len(imagenes),
        videos_count     = len(videos),
        has_video        = len(videos) > 0,
        precio           = precio,
        precio_original  = p0,
        discount_pct     = discount_pct_of(precio, p0),
        price_bucket     = price_bucket_of(precio),
        rating           = val(pub, "rating"),
        reviews          = val(pub, "reviews"),
    )

@afiliado.route("/productosComerciales/traking/afiliado/impresion/", methods=["POST", "GET"])
def afiliado_impresion():
    pub_id    = request.args.get("pub_id", type=int)
    visitor_id= request.args.get("vid")
    user_id= request.args.get("user_id", type=int)
    if not pub_id:
        abort(400, "pub_id requerido")
    try:
        with get_db_session() as session:
            # >>>> Traé la publicación desde tu ORM/repo actual <<<<
            # Acá asumo que tenés un método para obtenerla por id:
            pub = obtener_publicacion(session,pub_id)  # IMPLEMENTA: devuelve objeto con campos usados
            if not pub:
                abort(404, "Publicación no encontrada")

            # Construí snapshot (pasale arrays reales si los tenés aquí, si no [] )
            snap = snapshot_from_publicacion(pub, imagenes=[], videos=[])

            imp = ImpresionAfiliado(
                publicacion_id = pub_id,
                visitor_id     = visitor_id,
                user_id        = user_id,
                idioma         = get_lang(),
                ip             = get_client_ip(),
                user_agent     = request.headers.get("User-Agent"),
                referer        = request.referrer,
                creado_en      = datetime.now(timezone.utc),
                **snap
            )
            session.add(imp)
            return ("", 204)       # <--- **siempre** devolver algo
    except Exception as e:
       
        # loguea el error
        current_app.logger.error(f"Error en afiliado_impresion: {e}", exc_info=True)
        abort(500, "Error interno en servidor")
    finally:
        # si usás get_db_session() como context manager,
        # el `close()` debería ocurrir automáticamente.
        # Pero lo podés reforzar aquí si tu implementación lo requiere.
        pass

@afiliado.route("/productosComerciales/traking/r/ali")
def redirect_ali():
    pub_id     = request.args.get("pub_id", type=int)
    visitor_id = request.args.get("vid")
    user_id    = request.args.get("user_id", type=int)
    lang = request.args.get("lang")
    if not pub_id:
        abort(400, "pub_id requerido")
    with get_db_session() as session:
        pub = obtener_publicacion(session,pub_id)  # IMPLEMENTA
        af_link = pub.get("afiliado_link") if isinstance(pub, dict) else getattr(pub, "afiliado_link", None)
        if not pub or not af_link:
            abort(404, "Publicación sin afiliado_link")

       
        # agrega subIDs
        sub_params = build_sub_params(pub, user_id, lang, visitor_id)
        final_url  = append_params(af_link, sub_params)

        # snapshot
        snap = snapshot_from_publicacion(pub, imagenes=[], videos=[])

        click = ClickAfiliado(
            publicacion_id = pub_id,
            visitor_id     = visitor_id,
            user_id        = user_id,
            idioma         = lang,
            ip             = get_client_ip(),
            user_agent     = request.headers.get("User-Agent"),
            referer        = request.referrer,
            destino        = final_url,
            creado_en = datetime.now(timezone.utc),
            **snap
        )
        session.add(click)
        
    return redirect(final_url, code=302)



def obtener_publicacion(session, pub_id):
    publicacion = session.query(Publicacion).filter_by(id=pub_id).first()
    if publicacion:
        pubs = armar_publicacion(session, [publicacion])  # pasás una lista

        return pubs[0] if pubs else None
    return None


def armar_publicacion(session,publicaciones):
    publicaciones_data = []
    
    # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]
    
    for publicacion in publicaciones:
        # Obtener todas las imágenes y videos asociados a esta publicación
        imagenes_videos = session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()
        
        imagenes = []
        videos = []

        for iv in imagenes_videos:
            # Obtener la información de las imágenes
            if iv.imagen_id:
                imagen = session.query(Image).filter_by(id=iv.imagen_id).first()
                if imagen:
                    imagenes.append({
                        'id': imagen.id,
                        'title': imagen.title,
                        'description': imagen.description,
                        'filepath': imagen.filepath,
                        'randomNumber': imagen.randomNumber,  
                        'size': imagen.size                      
                    })

            # Obtener la información de los videos
            if iv.video_id:
                video = session.query(Video).filter_by(id=iv.video_id).first()
                if video:
                    videos.append({
                        'id': video.id,
                        'title': video.title,
                        'description': video.description,
                        'filepath': video.filepath,
                        'size': video.size
                    })

        # Ajustar las rutas de archivos según el sistema operativo
        path_separator = '/'
        for imagen in imagenes:
            imagen['filepath'] = imagen['filepath'].replace('\\', path_separator)
        
        for video in videos:
            video['filepath'] = video['filepath'].replace('\\', path_separator)

        # Agregar la publicación con sus imágenes y videos al diccionario
        publicaciones_data.append({
            'publicacion_id': publicacion.id,
            'user_id': publicacion.user_id,
            'titulo': publicacion.titulo,
            'texto': publicacion.texto,
            'ambito': publicacion.ambito,
            'correo_electronico': publicacion.correo_electronico,
            'descripcion': publicacion.descripcion,
            'color_texto': publicacion.color_texto,
            'color_titulo': publicacion.color_titulo,
            'fecha_creacion': publicacion.fecha_creacion, 
            'estado': publicacion.estado, 
            'afiliado_link': publicacion.afiliado_link,   
            'idioma':publicacion.idioma,       
            'imagenes': imagenes,
            'videos': videos
        })

        return publicaciones_data