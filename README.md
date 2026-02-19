# 🚒 FDNY Auto-Filer Pro - Web Edition

Sistema web profesional para generar automáticamente formularios FDNY (Fire Department New York).

## 📋 Características

- ✅ **100% Web-Based** - No requiere instalación
- ✅ **Sistema de Licencias** - Control por usuario con fingerprinting
- ✅ **Créditos Mensuales** - 50 documentos/mes por licencia
- ✅ **Rate Limiting** - Protección contra abuso (15 docs/hora)
- ✅ **Multi-Dispositivo** - Máximo 3 dispositivos por licencia
- ✅ **Auditoría Completa** - Registro de todo el uso
- ✅ **API RESTful** - Backend profesional en Python/Flask

## 🏗️ Arquitectura

```
┌─────────────────┐         ┌──────────────────┐
│  GitHub Pages   │────────>│  Vercel/Railway  │
│   (Frontend)    │  HTTPS  │    (Backend)     │
│  HTML/CSS/JS    │<────────│   Python/Flask   │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   SQLite    │
                              │  (Licenses) │
                              └─────────────┘
```

## 📂 Estructura del Proyecto

```
fdny-web-app/
├── frontend/              # GitHub Pages
│   ├── index.html        # Interfaz principal
│   ├── style.css         # Estilos
│   └── app.js            # Lógica frontend
│
├── backend/              # API Backend
│   ├── api/
│   │   ├── main.py      # API Flask
│   │   ├── database.py  # Sistema de licencias
│   │   └── pdf_generator.py
│   ├── config.json      # Configuración
│   ├── requirements.txt
│   └── vercel.json      # Config deployment
│
├── templates/           # PDFs templates
│   ├── tm-1.pdf
│   ├── a-433.pdf
│   └── b45.pdf
│
└── README.md           # Este archivo
```

## 🚀 DEPLOYMENT

### PARTE 1: Frontend (GitHub Pages)

1. **Crear Repositorio en GitHub:**
   ```bash
   git init
   git add frontend/*
   git commit -m "Initial frontend"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/fdny-autofiler.git
   git push -u origin main
   ```

2. **Activar GitHub Pages:**
   - Ve a: `Settings` → `Pages`
   - Source: `Deploy from a branch`
   - Branch: `main` → carpeta: `/frontend`
   - Save

3. **Dominio Personalizado (Opcional):**
   - En `Pages` → Custom domain: `www.tuempresa.com`
   - En tu proveedor DNS (Namecheap/GoDaddy):
     ```
     CNAME  www  →  tu-usuario.github.io
     ```

### PARTE 2: Backend (Vercel - GRATIS)

1. **Instalar Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Backend:**
   ```bash
   cd backend
   vercel login
   vercel --prod
   ```

3. **Configurar Variables de Entorno:**
   En el dashboard de Vercel:
   ```
   FLASK_ENV = production
   DATABASE_PATH = /tmp/licenses.db
   ```

4. **Obtener URL del Backend:**
   ```
   https://tu-proyecto.vercel.app
   ```

5. **Actualizar Frontend:**
   En `frontend/app.js`, cambiar:
   ```javascript
   const API_URL = 'https://tu-proyecto.vercel.app/api';
   ```

### PARTE 3: Alternativa - Backend en Railway (También GRATIS)

1. **Crear cuenta en Railway.app**

2. **Deploy desde GitHub:**
   - New Project → Deploy from GitHub
   - Seleccionar repositorio
   - Root directory: `/backend`

3. **Configurar:**
   - Add variables de entorno
   - Start command: `python api/main.py`

4. **Obtener URL y actualizar frontend**

## 🔑 SISTEMA DE LICENCIAS

### Crear Licencias

**Opción 1: Script Python**
```bash
cd backend
python3 -c "
from api.database import db
result = db.create_license(
    email='cliente@empresa.com',
    company_name='Empresa ABC',
    credits=50,
    months=1
)
print(f'License Key: {result[\"license_key\"]}')
"
```

**Opción 2: API Endpoint**
```bash
curl -X POST https://tu-api.vercel.app/api/admin/create-license \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cliente@empresa.com",
    "company_name": "Empresa ABC",
    "credits": 50,
    "months": 1
  }'
```

### Licencias de Prueba

Al ejecutar `database.py` se crean automáticamente:
- **Test:** `test@fdnyautofiler.com` → 100 créditos
- **Admin:** `admin@fdnyautofiler.com` → 999,999 créditos

## 📊 Panel de Administración

Crear archivo `frontend/admin.html` para gestionar licencias:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
</head>
<body>
    <h1>License Management</h1>
    <!-- Ver instrucciones completas en /docs/admin-panel.md -->
</body>
</html>
```

## 🔒 Seguridad

El sistema incluye:

1. **Fingerprinting de Dispositivos** - SHA-256 hash único por navegador
2. **Rate Limiting** - 15 documentos/hora máximo
3. **Límite de Dispositivos** - 3 máximo por licencia
4. **Créditos Consumibles** - 50/mes por defecto
5. **Auditoría Completa** - Log de cada acción
6. **SQLite Encriptado** - Base de datos protegida

## 🛠️ Desarrollo Local

### Backend:
```bash
cd backend
pip install -r requirements.txt
python api/main.py
# Server: http://localhost:5000
```

### Frontend:
```bash
cd frontend
# Usar Live Server (VSCode) o:
python -m http.server 8000
# Frontend: http://localhost:8000
```

### Testing:
```bash
# Crear licencia de prueba
cd backend
python api/database.py

# Probar API
curl http://localhost:5000/api/health

# Verificar licencia
curl -X POST http://localhost:5000/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"license_key": "XXXX-XXXX-XXXX-XXXX", "fingerprint": "abc123"}'
```

## 💰 Costos

- **GitHub Pages:** GRATIS (1GB storage, 100GB bandwidth/mes)
- **Vercel:** GRATIS (100GB bandwidth, 100 horas serverless/mes)
- **Railway:** GRATIS ($5 crédito/mes)
- **Dominio:** $10-15/año (opcional)

**Total: $0-15/año**

## 📱 Uso del Cliente

1. Abrir: `https://tudominio.com`
2. Ingresar clave de licencia
3. Escribir BIN → Cargar datos
4. (Opcional) Agregar dispositivos
5. Generar documentos
6. Descargar PDFs

## 🐛 Troubleshooting

**Error: "Invalid license"**
- Verificar que la licencia fue creada correctamente
- Revisar base de datos: `sqlite3 backend/api/licenses.db "SELECT * FROM licenses;"`

**Error: "Connection refused"**
- Verificar que el backend está corriendo
- Revisar URL en `frontend/app.js`

**Error: "Rate limit exceeded"**
- Esperar 1 hora o contactar admin para reset

**Error: "No credits remaining"**
- Esperar hasta la fecha de reset
- Contactar admin para comprar más créditos

## 📞 Soporte

- Email: support@fdnyautofiler.com
- Docs: /docs/
- Issues: GitHub Issues

## 📄 Licencia

Proprietary Software © 2026
Uso solo con licencia válida.

## 🎉 Próximas Características

- [ ] Panel de administración web
- [ ] Pagos automáticos (Stripe)
- [ ] Generación de reportes avanzados
- [ ] API webhooks
- [ ] Mobile app (iOS/Android)

---

**Desarrollado con ❤️ para FDNY contractors**
