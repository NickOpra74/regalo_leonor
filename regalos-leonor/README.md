# 💙 Regalo Web - Leonor

Un regalo digital interactivo con álbum de fotos y cartas de amor.

## Estructura del proyecto

```
regalos-leonor/
├── app.py                        # Servidor Flask
├── requirements.txt              # Dependencias
├── templates/
│   ├── index.html                # Login (contraseña: 01/12/2025)
│   ├── menu.html                 # Panel con cartas y acceso al álbum
│   └── almanaque.html            # Álbum de fotos interactivo
└── static/
    ├── css/styles.css
    ├── js/auth.js
    ├── js/main.js
    └── assets/
        ├── images/               # foto1.jpeg … foto8.jpeg
        └── audio/musica.mp3      # ← AÑADIR MANUALMENTE
```

## ⚠️ Archivo de música

Sube tu archivo de música como `static/assets/audio/musica.mp3` antes de desplegar.

## Despliegue en Render

1. Sube el proyecto a GitHub
2. En Render → **New Web Service** → conecta el repositorio
3. Configuración:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Añade variable de entorno:
   - `SECRET_KEY` → cualquier string secreto largo

## Contraseña de acceso

```
01/12/2025
```
