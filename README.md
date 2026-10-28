# marianneyarturo.com

- `public/` — la página (index.html, dibujos, foto) y el panel privado en `/panel/`.
- `netlify/functions/` — servidor del RSVP (`/api/rsvp`), del panel (`/api/admin`) y el resumen diario (8:00 am RD).
- `netlify/lib/` — conexión a Firebase y Resend, y plantillas de correo.
- `netlify.toml` — configuración de Netlify (carpeta pública, funciones, direcciones de cada sección).

Variables en Netlify (Environment variables): RESEND_API_KEY, FIREBASE_SERVICE_ACCOUNT, ADMIN_PASSWORD.
Sin dependencias externas: no hace falta instalar nada.

## Fuentes
`src/` contiene los generadores (Python) de la página, dibujos y estilos. `python3 src/build.py` regenera `public/`.
