@echo off
echo ========================================
echo    FDNY Auto-Filer - Quick Start
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python desde https://www.python.org
    pause
    exit /b 1
)

echo Python encontrado: 
python --version
echo.

REM Verificar si estamos en el directorio correcto
if not exist "backend" (
    echo ERROR: Por favor ejecuta este script desde la carpeta del proyecto
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: Por favor ejecuta este script desde la carpeta del proyecto
    pause
    exit /b 1
)

echo Instalando dependencias del backend...
cd backend
python -m pip install -r requirements.txt --quiet
cd ..
echo Dependencias instaladas!
echo.

echo Inicializando base de datos...
cd backend
python setup_initial_licenses.py
cd ..
echo.

echo ========================================
echo   SETUP COMPLETO!
echo ========================================
echo.
echo PARA INICIAR EL BACKEND:
echo    1. Abrir terminal en la carpeta 'backend'
echo    2. Ejecutar: python api/main.py
echo    3. API corriendo en: http://localhost:5000
echo.
echo PARA INICIAR EL FRONTEND:
echo    1. Abrir otra terminal en la carpeta 'frontend'
echo    2. Ejecutar: python -m http.server 8000
echo    3. Abrir navegador en: http://localhost:8000
echo.
echo PARA GESTIONAR LICENCIAS:
echo    1. Abrir terminal en la carpeta 'backend'
echo    2. Ejecutar: python admin.py
echo.
pause
