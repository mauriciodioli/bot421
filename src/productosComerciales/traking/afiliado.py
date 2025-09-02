# routes/afiliado.py
from datetime import datetime
from flask import Blueprint, request, redirect, abort, jsonify
from models.tracking import db, ImpresionAfiliado, ClickAfiliado
from tracking_utils import append_params, price_bucket_of, discount_pct_of

bp_afiliado = Blueprint("afiliado", __name__)

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

def snapshot_from_publicacion(pub, imagenes, videos):
    # Calcula derivados
    titulo = (pub.titulo or "").strip()
    texto  = (pub.texto or "").strip()
    precio = pub.precio
    p0     = getattr(pub, "precio_original", None)

    imagenes_count = len(imagenes or [])
    videos_count   = len(videos or [])
    has_video      = bool(videos_count > 0)

    discount_pct = discount_pct_of(precio, p0)
    pbucket      = price_bucket_of(precio)

    return dict(
        ambito           = getattr(pub, "ambito", None),
        categoria_id     = getattr(pub, "categoria_id", None),
        categoria_nombre = getattr(pub, "categoriaNombre", None),
        layout           = getattr(pub, "layout", None),
        color_titulo     = getattr(pub, "color_titulo", None),
        color_texto      = getattr(pub, "color_texto", None),
        titulo_len       = len(titulo),
        texto_len        = len(texto),
        imagenes_count   = imagenes_count,
        videos_count     = videos_count,
        has_video        = has_video,
        precio           = precio,
        precio_original  = p0,
        discount_pct     = discount_pct,
        price_bucket     = pbucket,
        rating           = getattr(pub, "rating", None),
        reviews          = getattr(pub, "reviews", None),
    )



@bp_afiliado.route("/afiliado/impresion", methods=["POST", "GET"])
def afiliado_impresion():
    pub_id    = request.args.get("pub_id", type=int)
    visitor_id= request.args.get("vid")
    if not pub_id:
        abort(400, "pub_id requerido")

    # >>>> Traé la publicación desde tu ORM/repo actual <<<<
    # Acá asumo que tenés un método para obtenerla por id:
    pub = obtener_publicacion(pub_id)  # IMPLEMENTA: devuelve objeto con campos usados
    if not pub:
        abort(404, "Publicación no encontrada")

    # Construí snapshot (pasale arrays reales si los tenés aquí, si no [] )
    snap = snapshot_from_publicacion(pub, imagenes=[], videos=[])

    imp = ImpresionAfiliado(
        publicacion_id = pub_id,
        visitor_id     = visitor_id,
        user_id        = getattr(request, "user_id", None),
        idioma         = get_lang(),
        ip             = get_client_ip(),
        user_agent     = request.headers.get("User-Agent"),
        referer        = request.referrer,
        creado_en      = datetime.utcnow(),
        **snap
    )
    db.session.add(imp)
    db.session.commit()
    return ("", 204)



@bp_afiliado.route("/r/ali")
def redirect_ali():
    pub_id     = request.args.get("pub_id", type=int)
    visitor_id = request.args.get("vid")
    lang       = get_lang()
    if not pub_id:
        abort(400, "pub_id requerido")

    pub = obtener_publicacion(pub_id)  # IMPLEMENTA
    if not pub or not getattr(pub, "afiliado_link", None):
        abort(404, "Publicación sin afiliado_link")

    user_id = getattr(request, "user_id", None)
    # agrega subIDs
    sub_params = build_sub_params(pub, user_id, lang, visitor_id)
    final_url  = append_params(pub.afiliado_link, sub_params)

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
        creado_en      = datetime.utcnow(),
        **snap
    )
    db.session.add(click)
    db.session.commit()

    return redirect(final_url, code=302)
