# models/impresion_afiliado.py
from datetime import datetime
from flask_marshmallow import Marshmallow
from utils.db import db
from sqlalchemy import Numeric
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional


ma = Marshmallow()


impresion_afiliado = Blueprint('impresion_afiliado', __name__)

class ImpresionAfiliado(db.Model):
    __tablename__ = "impresion_afiliado"

    id = db.Column(db.Integer, primary_key=True)

    # Claves / refs (agregá ForeignKey si tenés esas tablas)
    publicacion_id = db.Column(db.Integer, index=True, nullable=False)  # db.ForeignKey("publicacion.id")
    visitor_id     = db.Column(db.String(64), index=True)               # anónimo (localStorage)
    user_id        = db.Column(db.Integer, index=True, nullable=True)   # db.ForeignKey("usuario.id")

    # Contexto request
    idioma     = db.Column(db.String(8), index=True)
    ip         = db.Column(db.String(64))
    user_agent = db.Column(db.Text)
    referer    = db.Column(db.Text)
    creado_en  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Snapshot publicación (denormalizado)
    ambito           = db.Column(db.String(64), index=True)
    categoria_id     = db.Column(db.Integer, index=True)
    categoria_nombre = db.Column(db.String(128), index=True)
    layout           = db.Column(db.String(64), index=True)
    color_titulo     = db.Column(db.String(16))
    color_texto      = db.Column(db.String(16))
    titulo_len       = db.Column(db.Integer)
    texto_len        = db.Column(db.Integer)
    imagenes_count   = db.Column(db.Integer)
    videos_count     = db.Column(db.Integer)
    has_video        = db.Column(db.Boolean, index=True)

    # Métricas precio / rating
    precio          = db.Column(Numeric(10, 2))
    precio_original = db.Column(Numeric(10, 2))
    discount_pct    = db.Column(db.Float)
    price_bucket    = db.Column(db.String(16), index=True)
    rating          = db.Column(db.Float)
    reviews         = db.Column(db.Integer)

    def __init__(
            self,
            publicacion_id: int,
            visitor_id: Optional[str] = None,
            user_id: Optional[int] = None,
            **snapshot_kwargs,
        ):
        """
        Permite pasar campos snapshot como kwargs (ambito, categoria_id, etc.).
        """
        self.publicacion_id = publicacion_id
        self.visitor_id = visitor_id
        self.user_id = user_id

        # Cargar opcionales si vienen
        for k, v in snapshot_kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def __repr__(self):
        return (
            f"<ImpresionAfiliado id={self.id} pub={self.publicacion_id} "
            f"user={self.user_id} visitor={self.visitor_id} ts={self.creado_en}>"
        )

    @classmethod
    def crear_tabla_impresion_afiliado(self):
        # Verificar si la tabla 'click_afiliado' existe antes de crearla
        insp = inspect(db.engine)
        if not insp.has_table("impresion_afiliado"):
            db.create_all()

# ---- Marshmallow ----
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class ImpresionAfiliadoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ImpresionAfiliado
        load_instance = True
        include_fk = True
        ordered = True
