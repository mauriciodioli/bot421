from flask import Blueprint, render_template, make_response

legal = Blueprint("legal", __name__)

@legal.get("/devoluciones/")
def devoluciones():
    resp = make_response(render_template("policies/devoluciones.html", layout='layout'))
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp

@legal.get("/envios/")
def envios():
    resp = make_response(render_template("policies/envios.html", layout='layout'))
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp
