# 🚀 GUÍA DE DEPLOYMENT PASO A PASO

Esta guía te llevará desde cero hasta tener tu aplicación funcionando en internet.

## 📋 REQUISITOS PREVIOS

- [ ] Cuenta GitHub (gratis)
- [ ] Cuenta Vercel (gratis) - https://vercel.com
- [ ] Git instalado en tu computadora
- [ ] Navegador web moderno

## PASO 1: PREPARAR EL CÓDIGO

### 1.1 Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `fdny-autofiler`
3. Descripción: "FDNY Document Generator Web Application"
4. Visibilidad: **Private** (recomendado)
5. Click en "Create repository"

### 1.2 Subir Código

```bash
# En tu computadora, desde la carpeta del proyecto:
cd fdny-web-app

# Inicializar Git
git init

# Añadir todos los archivos
git add .

# Crear commit inicial
git commit -m "Initial commit - FDNY Auto-Filer"

# Conectar con GitHub (reemplaza TU-USUARIO)
git branch -M main
git remote add origin https://github.com/TU-USUARIO/fdny-autofiler.git

# Subir código
git push -u origin main
```

## PASO 2: DEPLOY DEL FRONTEND (GitHub Pages)

### 2.1 Configurar GitHub Pages

1. En tu repositorio de GitHub, ve a **Settings**
2. En el menú lateral, click en **Pages**
3. En "Source":
   - Selecciona: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/frontend`
4. Click en **Save**

### 2.2 Esperar Deployment

- GitHub procesará tu sitio (toma 1-2 minutos)
- Verás un mensaje: "Your site is published at https://TU-USUARIO.github.io/fdny-autofiler/"

### 2.3 Verificar Frontend

- Abre la URL en tu navegador
- Deberías ver la pantalla de login
- **NOTA:** Aún no funcionará porque falta el backend

## PASO 3: DEPLOY DEL BACKEND (Vercel)

### 3.1 Crear Cuenta en Vercel

1. Ve a https://vercel.com/signup
2. Registra con tu cuenta de GitHub
3. Autoriza a Vercel

### 3.2 Importar Proyecto

1. En Vercel dashboard, click **Add New** → **Project**
2. Selecciona tu repositorio `fdny-autofiler`
3. Configuración:
   - **Framework Preset:** Other
   - **Root Directory:** `backend`
   - **Build Command:** (dejar vacío)
   - **Output Directory:** (dejar vacío)
   - **Install Command:** `pip install -r requirements.txt`

### 3.3 Configurar Variables de Entorno

En "Environment Variables", añade:

```
FLASK_ENV = production
```

### 3.4 Deploy

1. Click en **Deploy**
2. Espera 1-2 minutos
3. Verás: "Your project has been deployed"
4. Copia la URL: `https://tu-proyecto.vercel.app`

## PASO 4: CONECTAR FRONTEND Y BACKEND

### 4.1 Actualizar URL del API

1. En tu editor de código, abre: `frontend/app.js`
2. Busca la línea (cerca de la línea 7):
   ```javascript
   const API_URL = 'https://your-backend.vercel.app/api';
   ```
3. Reemplaza con TU URL de Vercel:
   ```javascript
   const API_URL = 'https://tu-proyecto.vercel.app/api';
   ```

### 4.2 Subir Cambio

```bash
git add frontend/app.js
git commit -m "Update API URL"
git push
```

- GitHub Pages se actualizará automáticamente en 1-2 minutos

## PASO 5: SUBIR TEMPLATES PDF

Los PDFs templates (tm-1.pdf, a-433.pdf, b45.pdf) deben estar en Vercel.

### Opción A: Subir al Repositorio (Recomendado)

```bash
# Asegúrate de que están en /templates/
git add templates/*.pdf
git commit -m "Add PDF templates"
git push
```

### Opción B: Subir a Vercel Storage (Avanzado)

Ver documentación de Vercel Storage.

## PASO 6: CREAR TU PRIMERA LICENCIA

### 6.1 Acceder al Backend

Desde tu computadora:

```bash
# Clonar el repo si no lo tienes
git clone https://github.com/TU-USUARIO/fdny-autofiler.git
cd fdny-autofiler/backend

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar script de admin
python3 admin.py
```

### 6.2 Crear Licencia

1. Selecciona opción `1` (Create New License)
2. Ingresa:
   - Email: `tu@email.com`
   - Company: `Tu Empresa`
   - Credits: `50`
   - Months: `1`
3. **IMPORTANTE:** Copia la clave generada (formato: XXXX-XXXX-XXXX-XXXX)

## PASO 7: PROBAR LA APLICACIÓN

### 7.1 Abrir Frontend

- Ve a: `https://TU-USUARIO.github.io/fdny-autofiler/`

### 7.2 Login

- Ingresa la clave de licencia que creaste
- Click en "Activate"

### 7.3 Generar Documento de Prueba

1. Ingresa un BIN de prueba: `1001234`
2. Click en "Load Data"
3. (Opcional) Agregar dispositivos
4. Click en "Generate All Documents"
5. Descargar los PDFs

## 🎉 ¡LISTO!

Tu aplicación está funcionando en internet. Ahora puedes:

- Compartir la URL con clientes
- Crear más licencias
- Agregar dominio personalizado (siguiente sección)

---

## BONUS: DOMINIO PERSONALIZADO

### B.1 Comprar Dominio

- Namecheap, GoDaddy, etc.
- Ejemplo: `fdnyautofiler.com`
- Costo: ~$10-15/año

### B.2 Configurar DNS

En tu proveedor de dominio:

```
CNAME  www  →  TU-USUARIO.github.io
```

### B.3 Configurar en GitHub

1. GitHub → Settings → Pages
2. Custom domain: `www.fdnyautofiler.com`
3. Save
4. Esperar 24 horas para propagación DNS

### B.4 HTTPS

- GitHub Pages automáticamente habilita HTTPS
- Check "Enforce HTTPS"

---

## 🆘 TROUBLESHOOTING

**Error: "Frontend no carga"**
- Verificar que GitHub Pages esté habilitado
- Revisar carpeta source: debe ser `/frontend`
- Forzar rebuild: hacer commit vacío y push

**Error: "API connection failed"**
- Verificar URL en `app.js`
- Probar endpoint: `https://tu-proyecto.vercel.app/api/health`
- Revisar logs en Vercel dashboard

**Error: "Invalid license"**
- Asegurarse de que creaste la licencia
- Verificar base de datos SQLite local
- Crear licencia de prueba desde admin.py

**Error: "PDFs no se generan"**
- Verificar que los templates estén en `/templates/`
- Revisar logs de Vercel
- Probar generación local primero

---

## 📞 SOPORTE

Si tienes problemas:

1. Revisar logs en Vercel Dashboard
2. Probar localmente primero
3. Verificar todas las URLs
4. Revisar este documento nuevamente

---

**¡Éxito con tu deployment! 🚀**
