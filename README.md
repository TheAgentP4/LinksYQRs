# 🔗 Acortador de URLs + Generador QR

Una aplicación web moderna para acortar URLs y generar códigos QR instantáneamente.

## ✨ Características

- **Acortador de URLs**: Crea enlaces cortos con alias personalizados
- **Generador QR**: Genera códigos QR para URLs o enlaces cortos
- **Combinación automática**: Crea URL corta + QR en un mismo paso
- **Contador de clics**: Monitorea cuántas veces se accede a cada enlace
- **API REST**: Accede a los datos de forma programática
- **Interfaz responsiva**: Compatible con dispositivos móviles
- **Rate limiting**: Protección contra abuso
- **Validación robusta**: Sanitización completa de entrada

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8+
- pip

### Instalación

1. **Clonar o descargar el proyecto**
```bash
cd Prototipo
```

2. **Crear entorno virtual** (opcional pero recomendado)
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Mac/Linux:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:10000`

## 📋 Funcionalidades

### Acortador de URLs
```
1. Ingresa una URL válida (debe comenzar con http:// o https://)
2. Elige el tipo de generación:
   - Solo QR: Genera solo el código QR
   - Solo acortar: Crea solo la URL corta
   - Ambas: Crea URL corta + QR
3. (Opcional) Ingresa un alias personalizado
4. ¡Hecho! Copia tu URL corta o descarga el QR
```

### API REST

#### Obtener lista de todos los enlaces
```
GET /api/links
```

Respuesta:
```json
[
  {
    "alias": "mi-proyecto",
    "url": "https://ejemplo.com/pagina-larga",
    "clicks": 5,
    "created_at": "2026-03-26T15:30:00"
  }
]
```

## 🧪 Tests

### Ejecutar todos los tests
```bash
pytest test_app.py -v
```

### Ejecutar tests de una categoría específica
```bash
pytest test_app.py::TestValidacionURLs -v
pytest test_app.py::TestSanitizacionAlias -v
pytest test_app.py::TestRutaRedireccion -v
```

### Ver cobertura de tests
```bash
pip install pytest-cov
pytest test_app.py --cov=app --cov-report=html
```

## 🔒 Seguridad

### Medidas Implementadas

✅ **Validación de URLs**: Solo acepta URLs válidas con http:// o https://
✅ **Sanitización de alias**: Solo letras, números, guiones y guiones bajos
✅ **Rate limiting**: Máximo 30 solicitudes por minuto en la página principal
✅ **Protección de inyección**: Validación en servidor y cliente
✅ **Límites de longitud**: URLs máximo 500 caracteres, alias máximo 30
✅ **Manejo de errores**: Errores HTTP apropiados (400, 404, 429, 500)

## 📊 Base de Datos

El proyecto utiliza **SQLite** en lugar de JSON, proporcionando:
- Persistencia robusta
- Índices para búsquedas rápidas
- Integridad referencial
- Fácil escalabilidad a PostgreSQL

### Estructura de la tabla `link`
```sql
- id (INTEGER, PRIMARY KEY)
- alias (VARCHAR(50), UNIQUE, INDEXED)
- url (VARCHAR(500))
- created_at (DATETIME)
- clicks (INTEGER)
```

## 🎨 Interfaz

### Tecnologías
- HTML5
- CSS3 (Grid, Flexbox, Gradientes)
- JavaScript puro (sin dependencias)
- Responsive design

### Características de UX
- Copiar URL al portapapeles con un clic
- Descargar QR como imagen PNG
- Feedback visual en botones
- Indicadores de carga
- Mensajes de error claros

## 🛠️ Variables de Entorno

Puedes personalizar el puerto con la variable `PORT`:
```bash
# En Windows PowerShell:
$env:PORT=5000
python app.py

# En CMD:
set PORT=5000
python app.py

# En Mac/Linux:
export PORT=5000
python app.py
```

## 📁 Estructura del Proyecto

```
.
├── app.py                 # Aplicación principal
├── test_app.py           # Tests automatizados
├── requirements.txt      # Dependencias
├── links.db              # Base de datos SQLite (generada)
├── templates/
│   ├── index.html        # Página principal
│   ├── resultado.html    # Página de resultados
│   └── error.html        # Página de errores
└── README.md             # Este archivo
```

## 📦 Dependencias

| Paquete | Versión | Propósito |
|---------|---------|----------|
| Flask | 2.3.3 | Framework web |
| qrcode | 7.4.2 | Generación de QR |
| python-validators | 22.0.0 | Validación de URLs |
| Flask-SQLAlchemy | 3.0.5 | ORM para base de datos |
| Flask-Limiter | 3.5.0 | Rate limiting |
| pytest | 7.4.0 | Framework de testing |
| pytest-flask | 1.2.0 | Fixtures para Flask |
| gunicorn | 21.2.0 | Servidor WSGI para producción |

## 🚀 Deployment

### Heroku
```bash
# Instalar Heroku CLI
# Crear app
heroku create mi-acortador

# Hacer push
git push heroku main

# Ver logs
heroku logs --tail
```

### Render
```bash
# Conectar repositorio en render.com
# Seleccionar rama y ejecutar comando:
python app.py
```

## 📈 Futuras Mejoras

- [ ] Panel de administración con gráficos
- [ ] Autenticación de usuarios (OAuth2)
- [ ] Expiración automática de enlaces
- [ ] Estadísticas avanzadas (geolocalización, dispositivos)
- [ ] QR con logo personalizado
- [ ] API completa con documentación Swagger
- [ ] Descarga de estadísticas en CSV/Excel
- [ ] Generación programática de enlaces

## 🐛 Reporte de Bugs

Si encuentras un error, por favor:
1. Describe el problema
2. Pasos para reproducirlo
3. Resultado esperado vs actual
4. Tu entorno (SO, navegador, Python)

## 📄 Licencia

Este proyecto es de código abierto. Siéntete libre de usarlo y modificarlo.

## 💡 Tips

- **URL muy larga**: Si tu URL original es muy larga, copia el resultado y cierra la ventana
- **QR no se ve claro**: Abre en una nueva pestaña para verlo en tamaño completo
- **Alias especial**: Los alias distinguen entre mayúsculas/minúsculas

---

Hecho con ❤️ usando Flask y Python
