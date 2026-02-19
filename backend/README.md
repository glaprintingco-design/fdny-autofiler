# Backend - FDNY Auto-Filer API

API RESTful para el sistema FDNY Auto-Filer.

## 🚀 Quick Start

### Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear licencias iniciales
python3 setup_initial_licenses.py

# Ejecutar servidor
python3 api/main.py

# API disponible en: http://localhost:5000
```

### Administración de Licencias

```bash
# Ejecutar panel de administración
python3 admin.py
```

## 📡 Endpoints API

### Autenticación
- `POST /api/auth/verify` - Verificar licencia
- `GET /api/auth/info` - Información de licencia

### Datos
- `GET /api/bin/<bin_number>` - Obtener datos de BIN

### Generación
- `POST /api/generate` - Generar documentos

### Admin
- `POST /api/admin/create-license` - Crear licencia
- `GET /api/admin/list-licenses` - Listar licencias

### Sistema
- `GET /api/health` - Health check

## 🗄️ Base de Datos

SQLite con las siguientes tablas:
- `licenses` - Información de licencias
- `devices` - Dispositivos registrados
- `usage_log` - Auditoría de uso
- `rate_limits` - Control de rate limiting

## 🔐 Seguridad

- Licencias basadas en HMAC-SHA256
- Fingerprinting de dispositivos
- Rate limiting: 15 requests/hora
- Límite de dispositivos: 3 por licencia
- Auditoría completa de acciones

## 📦 Deployment

### Vercel
```bash
vercel --prod
```

### Railway
```bash
railway up
```

### Render
```bash
# Conectar repo en render.com
```

Ver `docs/DEPLOYMENT.md` para instrucciones completas.

## 🛠️ Scripts

- `admin.py` - Panel de administración CLI
- `setup_initial_licenses.py` - Crear licencias iniciales
- `api/database.py` - Gestión de base de datos
- `api/pdf_generator.py` - Generación de PDFs

## 📄 Licencia

Proprietary © 2026
