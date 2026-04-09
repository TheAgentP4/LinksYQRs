from flask import Flask, request, redirect, render_template, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators
import qrcode
import os
import logging
import re
from io import BytesIO
from datetime import datetime

# Configuración
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de Base de Datos
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), unique=True, nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'alias': self.alias,
            'url': self.url,
            'clicks': self.clicks,
            'created_at': self.created_at.isoformat()
        }

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# Funciones auxiliares
def validar_url(url):
    """Valida que la URL sea correcta"""
    if not url or len(url) > 500:
        return False, "URL inválida o demasiado larga"
    
    if not validators.url(url):
        return False, "URL no válida. Debe comenzar con http:// o https://"
    
    return True, None

def sanitizar_alias(alias):
    """Sanitiza el alias: solo letras, números, guiones y guiones bajos"""
    if not alias:
        return None, "Alias requerido"
    
    # Limitar longitud
    alias = alias.strip()[:30]
    
    # Solo permitir caracteres seguros
    if not re.match(r'^[a-zA-Z0-9_-]+$', alias):
        return None, "Alias solo puede contener letras, números, guiones y guiones bajos"
    
    if len(alias) < 2:
        return None, "Alias debe tener al menos 2 caracteres"
    
    return alias, None

# Rutas
@app.route("/", methods=["GET", "POST"])
@limiter.limit("30 per minute")
def home():
    """Página principal"""
    if request.method == "POST":
        opcion = request.form.get("opcion", "").strip()
        url = request.form.get("url", "").strip()
        
        # Validar URL
        es_valida, error = validar_url(url)
        if not es_valida:
            return render_template("index.html", error=error), 400
        
        # SOLO QR
        if opcion == "qr":
            return render_template("resultado.html", 
                                 short_url=None, 
                                 qr=f"/qr_directo?data={url}")
        
        # SOLO ACORTAR o AMBAS
        if opcion in ["short", "ambas"]:
            alias = request.form.get("alias", "").strip()
            alias_clean, error_alias = sanitizar_alias(alias)
            
            if not alias_clean:
                return render_template("index.html", error=error_alias), 400
            
            # Verificar que el alias no exista
            if Link.query.filter_by(alias=alias_clean).first():
                return render_template("index.html", 
                                     error="Ese alias ya existe"), 409
            
            # Crear nuevo link
            link = Link(alias=alias_clean, url=url)
            db.session.add(link)
            db.session.commit()
            logger.info(f"Alias creado: {alias_clean} -> {url}")
            
            short_url = request.host_url + alias_clean
            
            if opcion == "short":
                return render_template("resultado.html", 
                                     short_url=short_url, 
                                     qr=None)
            else:  # ambas
                return render_template("resultado.html", 
                                     short_url=short_url, 
                                     qr=f"/qr/{alias_clean}")
        
        return render_template("index.html", 
                             error="Opción no válida"), 400
    
    return render_template("index.html")

@app.route("/<alias>")
@limiter.limit("1000 per hour")
def redirigir(alias):
    """Redirección con contador de clics"""
    link = Link.query.filter_by(alias=alias).first()
    
    if not link:
        return render_template("error.html", 
                             mensaje="Alias no encontrado"), 404
    
    # Incrementar contador de clics
    link.clicks += 1
    db.session.commit()
    logger.info(f"Redirección: {alias} -> {link.url}")
    
    return redirect(link.url)

@app.route("/qr/<alias>")
@limiter.limit("60 per minute")
def qr_alias(alias):
    """Genera QR del alias corto"""
    link = Link.query.filter_by(alias=alias).first()
    
    if not link:
        return jsonify({"error": "Alias no encontrado"}), 404
    
    short_url = request.host_url + alias
    img = qrcode.make(short_url)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return send_file(buffer, mimetype="image/png")

@app.route("/qr_directo")
@limiter.limit("60 per minute")
def qr_directo():
    """Genera QR de una URL directa"""
    data = request.args.get("data", "").strip()
    
    if not data:
        return jsonify({"error": "Parámetro 'data' requerido"}), 400
    
    es_valida, error = validar_url(data)
    if not es_valida:
        return jsonify({"error": error}), 400
    
    img = qrcode.make(data)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return send_file(buffer, mimetype="image/png")

@app.route("/api/links")
@limiter.limit("30 per minute")
def api_links():
    """API para obtener todos los links (sin datos sensibles)"""
    links = Link.query.all()
    return jsonify([link.to_dict() for link in links])

@app.errorhandler(404)
def no_encontrado(e):
    """Error 404 personalizado"""
    return render_template("error.html", 
                         mensaje="Página no encontrada"), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Error de limite de rate"""
    return render_template("error.html", 
                         mensaje="Demasiadas solicitudes. Intenta más tarde"), 429

@app.errorhandler(500)
def error_interno(e):
    """Error 500 personalizado"""
    logger.error(f"Error interno: {e}")
    return render_template("error.html", 
                         mensaje="Error interno del servidor"), 500

# Ejecutar app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)