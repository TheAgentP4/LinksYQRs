import pytest
import json
from app import app, db, Link, validar_url, sanitizar_alias

@pytest.fixture
def client():
    """Fixture para el cliente de pruebas"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def app_context():
    """Fixture para el contexto de la aplicación"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

class TestValidacionURLs:
    """Pruebas para validación de URLs"""

    def test_url_valida(self):
        """Valida que URL correcta sea aceptada"""
        es_valida, error = validar_url("https://ejemplo.com")
        assert es_valida is True
        assert error is None

    def test_url_http(self):
        """Valida que URL con http sea aceptada"""
        es_valida, error = validar_url("http://ejemplo.com")
        assert es_valida is True
        assert error is None

    def test_url_vacia(self):
        """Rechaza URL vacía"""
        es_valida, error = validar_url("")
        assert es_valida is False
        assert error is not None

    def test_url_sin_protocolo(self):
        """Rechaza URL sin protocolo"""
        es_valida, error = validar_url("ejemplo.com")
        assert es_valida is False
        assert error is not None

    def test_url_muy_larga(self):
        """Rechaza URL demasiado larga"""
        url_larga = "https://ejemplo.com/" + "a" * 600
        es_valida, error = validar_url(url_larga)
        assert es_valida is False
        assert error is not None

    def test_url_invalida(self):
        """Rechaza URL inválida"""
        es_valida, error = validar_url("no es una url")
        assert es_valida is False
        assert error is not None

class TestSanitizacionAlias:
    """Pruebas para sanitización de alias"""

    def test_alias_valido(self):
        """Valida alias correcto"""
        alias, error = sanitizar_alias("mi-proyecto")
        assert alias == "mi-proyecto"
        assert error is None

    def test_alias_con_numero(self):
        """Valida alias con números"""
        alias, error = sanitizar_alias("proyecto123")
        assert alias == "proyecto123"
        assert error is None

    def test_alias_con_guion_bajo(self):
        """Valida alias con guión bajo"""
        alias, error = sanitizar_alias("mi_proyecto")
        assert alias == "mi_proyecto"
        assert error is None

    def test_alias_vacio(self):
        """Rechaza alias vacío"""
        alias, error = sanitizar_alias("")
        assert alias is None
        assert error is not None

    def test_alias_demasiado_corto(self):
        """Rechaza alias muy corto"""
        alias, error = sanitizar_alias("a")
        assert alias is None
        assert error is not None

    def test_alias_caracteres_especiales(self):
        """Rechaza alias con caracteres especiales"""
        alias, error = sanitizar_alias("mi@proyecto")
        assert alias is None
        assert error is not None

    def test_alias_espacios(self):
        """Rechaza alias con espacios"""
        alias, error = sanitizar_alias("mi proyecto")
        assert alias is None
        assert error is not None

    def test_alias_longitud_maxima(self):
        """Valida que alias se corte a 30 caracteres"""
        alias_largo = "a" * 50
        alias, error = sanitizar_alias(alias_largo)
        assert len(alias) == 30

class TestRutaHome:
    """Pruebas para ruta principal"""

    def test_get_home(self, client):
        """GET en home retorna 200"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Acortador" in response.data

    def test_post_sin_url(self, client):
        """POST sin URL retorna error"""
        response = client.post("/", data={
            "opcion": "qr",
            "url": ""
        })
        assert response.status_code == 400

    def test_post_url_invalida(self, client):
        """POST con URL inválida retorna error"""
        response = client.post("/", data={
            "opcion": "qr",
            "url": "no es valida"
        })
        assert response.status_code == 400

    def test_solo_qr(self, client):
        """Genera QR sin acortar URL"""
        response = client.post("/", data={
            "opcion": "qr",
            "url": "https://ejemplo.com"
        })
        assert response.status_code == 200
        assert b"Resultado" in response.data

    def test_solo_acortar(self, client, app_context):
        """Acorta URL sin generar QR"""
        response = client.post("/", data={
            "opcion": "short",
            "url": "https://ejemplo.com/pagina-larga",
            "alias": "mi-link"
        })
        assert response.status_code == 200
        assert b"URL Corta" in response.data

        # Verificar que se guardó en BD
        link = Link.query.filter_by(alias="mi-link").first()
        assert link is not None
        assert link.url == "https://ejemplo.com/pagina-larga"

    def test_ambas_opciones(self, client, app_context):
        """Genera QR y acorta URL"""
        response = client.post("/", data={
            "opcion": "ambas",
            "url": "https://ejemplo.com",
            "alias": "test"
        })
        assert response.status_code == 200

        link = Link.query.filter_by(alias="test").first()
        assert link is not None

    def test_alias_duplicado(self, client, app_context):
        """Rechaza alias duplicado"""
        # Crear primer enlace
        client.post("/", data={
            "opcion": "ambas",
            "url": "https://ejemplo.com",
            "alias": "test"
        })

        # Intentar crear con mismo alias
        response = client.post("/", data={
            "opcion": "ambas",
            "url": "https://otra.com",
            "alias": "test"
        })
        assert response.status_code == 409

class TestRutaRedireccion:
    """Pruebas para redirección"""

    def test_redireccion_valida(self, client, app_context):
        """Redirecciona a URL original"""
        # Crear enlace
        link = Link(alias="test", url="https://ejemplo.com")
        db.session.add(link)
        db.session.commit()

        # Hacer request
        response = client.get("/test", follow_redirects=False)
        
        # Verificar redirección
        assert response.status_code == 302
        assert "https://ejemplo.com" in response.location

        # Verificar incremento de clics
        link_actual = Link.query.filter_by(alias="test").first()
        assert link_actual.clicks == 1

    def test_alias_no_existe(self, client):
        """Retorna 404 para alias inexistente"""
        response = client.get("/inexistente")
        assert response.status_code == 404
        assert b"no encontrado" in response.data.lower()

    def test_incremento_clics(self, client, app_context):
        """Incrementa contador de clics"""
        link = Link(alias="test", url="https://ejemplo.com")
        db.session.add(link)
        db.session.commit()

        # Hacer 3 requests
        for _ in range(3):
            client.get("/test", follow_redirects=False)

        link_actual = Link.query.filter_by(alias="test").first()
        assert link_actual.clicks == 3

class TestRutasQR:
    """Pruebas para generación de QR"""

    def test_qr_alias_valido(self, client, app_context):
        """Genera QR para alias válido"""
        link = Link(alias="test", url="https://ejemplo.com")
        db.session.add(link)
        db.session.commit()

        response = client.get("/qr/test")
        assert response.status_code == 200
        assert response.content_type == "image/png"

    def test_qr_alias_invalido(self, client):
        """Retorna error para alias inválido"""
        response = client.get("/qr/inexistente")
        assert response.status_code == 404

    def test_qr_directo_valido(self, client):
        """Genera QR directo para URL válida"""
        response = client.get("/qr_directo?data=https://ejemplo.com")
        assert response.status_code == 200
        assert response.content_type == "image/png"

    def test_qr_directo_sin_datos(self, client):
        """Retorna error si no hay parámetro data"""
        response = client.get("/qr_directo")
        assert response.status_code == 400

    def test_qr_directo_url_invalida(self, client):
        """Retorna error para URL inválida"""
        response = client.get("/qr_directo?data=no-es-valida")
        assert response.status_code == 400

    def test_qr_directo_personalizado(self, client):
        """Genera QR personalizado con color e icono"""
        response = client.get(
            "/qr_directo?data=https://ejemplo.com&fill=%230053ff&back=%23fefefe&icon=diamond"
        )
        assert response.status_code == 200
        assert response.content_type == "image/png"


class TestVistaDB:
    """Pruebas para la vista de base de datos"""

    def test_db_view_disponible(self, client, app_context):
        """La página de base de datos responde correctamente"""
        link = Link(alias="base", url="https://ejemplo.com", clicks=2)
        db.session.add(link)
        db.session.commit()

        response = client.get("/db")
        assert response.status_code == 200
        assert b"base" in response.data

class TestAPILinks:
    """Pruebas para API de links"""

    def test_api_links_vacio(self, client):
        """API retorna lista vacía al principio"""
        response = client.get("/api/links")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_api_links_con_datos(self, client, app_context):
        """API retorna links creados"""
        link = Link(alias="test", url="https://ejemplo.com", clicks=5)
        db.session.add(link)
        db.session.commit()

        response = client.get("/api/links")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['alias'] == "test"
        assert data[0]['clicks'] == 5

class TestManejadorErrores:
    """Pruebas para manejadores de errores"""

    def test_404_personalizado(self, client):
        """Retorna página 404 personalizada"""
        response = client.get("/pagina-inexistente")
        assert response.status_code == 404
        assert b"Oops" in response.data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
