from flask import Flask, request, redirect, render_template_string, send_file
import json
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

DB_FILE = "links.json"

# Cargar datos
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        urls = json.load(f)
else:
    urls = {}

def guardar():
    with open(DB_FILE, "w") as f:
        json.dump(urls, f)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        opcion = request.form["opcion"]
        link = request.form["url"]

        # SOLO QR
        if opcion == "qr":
            return render_template_string("""
                <h2>QR generado:</h2>
                <img src="/qr_directo?data={{link}}">
                <br><br>
                <a href="/">Volver</a>
            """, link=link)

        # SOLO ACORTAR
        if opcion == "short":
            alias = request.form["alias"].strip().replace(" ", "_")

            if alias in urls:
                return "Ese nombre ya existe"

            urls[alias] = link
            guardar()

            short_url = request.host_url + alias

            return f"""
            <h2>Link corto:</h2>
            <a href="{short_url}" target="_blank">{short_url}</a>
            <br><br>
            <a href="/">Volver</a>
            """

        # AMBAS
        if opcion == "ambas":
            alias = request.form["alias"].strip().replace(" ", "_")

            if alias in urls:
                return "Ese nombre ya existe"

            urls[alias] = link
            guardar()

            short_url = request.host_url + alias

            return render_template_string("""
                <h2>Link corto:</h2>
                <a href="{{short_url}}" target="_blank">{{short_url}}</a>
                <br><br>
                <h2>QR generado:</h2>
                <img src="/qr/{{alias}}">
                <br><br>
                <a href="/">Volver</a>
            """, short_url=short_url, alias=alias)

    return '''
    <h2>Herramienta de Links</h2>
    <form method="post">
        <input name="url" placeholder="Link" required><br><br>

        <select name="opcion" required>
            <option value="qr">Solo QR</option>
            <option value="short">Solo acortar</option>
            <option value="ambas">Ambas</option>
        </select><br><br>

        <input name="alias" placeholder="Alias (solo para acortar)"><br><br>

        <button type="submit">Continuar</button>
    </form>
    '''

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

# QR directo (sin acortar)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)