from flask import Flask, request, redirect, render_template, send_file
import json
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

DB_FILE = "links.json"

# Cargar datos de forma segura
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            urls = json.load(f)
    except:
        urls = {}
else:
    urls = {}

# Guardar datos
def guardar():
    with open(DB_FILE, "w") as f:
        json.dump(urls, f)

# Página principal
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        opcion = request.form.get("opcion")
        link = request.form.get("url")

        if not link:
            return "Debes ingresar un link"

        # SOLO QR
        if opcion == "qr":
            return render_template("resultado.html", short_url=None, qr="/qr_directo?data=" + link)

        # SOLO ACORTAR
        if opcion == "short":
            alias = request.form.get("alias", "").strip().replace(" ", "_")

            if not alias:
                return "Debes poner un alias"

            if alias in urls:
                return "Ese nombre ya existe"

            urls[alias] = link
            guardar()

            short_url = request.host_url + alias

            return render_template("resultado.html", short_url=short_url, qr=None)

        # AMBAS
        if opcion == "ambas":
            alias = request.form.get("alias", "").strip().replace(" ", "_")

            if not alias:
                return "Debes poner un alias"

            if alias in urls:
                return "Ese nombre ya existe"

            urls[alias] = link
            guardar()

            short_url = request.host_url + alias

            return render_template("resultado.html", short_url=short_url, qr="/qr/" + alias)

    return render_template("index.html")

# Redirección
@app.route("/<alias>")
def redirigir(alias):
    if alias in urls:
        return redirect(urls[alias])
    return "Link no encontrado"

# QR de link corto
@app.route("/qr/<alias>")
def qr_alias(alias):
    if alias not in urls:
        return "No existe"

    short_url = request.host_url + alias
    img = qrcode.make(short_url)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")

# QR directo
@app.route("/qr_directo")
def qr_directo():
    data = request.args.get("data")

    if not data:
        return "No data"

    img = qrcode.make(data)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")

# Ejecutar app (local y producción)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)