#!/bin/bash

echo "🚒 FDNY Auto-Filer - Quick Start Script"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Verificar si estamos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Instalar dependencias del backend
echo "📦 Installing backend dependencies..."
cd backend
python3 -m pip install -r requirements.txt --quiet
cd ..
echo "✅ Backend dependencies installed"
echo ""

# Inicializar base de datos
echo "🗄️  Initializing database..."
cd backend
python3 << EOF
from api.database import create_test_license, create_admin_license
print("Creating test licenses...")
test = create_test_license()
admin = create_admin_license()
print("\n📝 TEST LICENSE:")
print(f"   Email: {test['email']}")
print(f"   Key:   {test['license_key']}")
print(f"\n🔑 ADMIN LICENSE:")
print(f"   Email: {admin['email']}")
print(f"   Key:   {admin['license_key']}")
EOF
cd ..
echo ""

# Mostrar instrucciones
echo "✅ Setup complete!"
echo ""
echo "🚀 TO START THE BACKEND:"
echo "   cd backend"
echo "   python3 api/main.py"
echo "   → API will run on http://localhost:5000"
echo ""
echo "🌐 TO START THE FRONTEND:"
echo "   cd frontend"
echo "   python3 -m http.server 8000"
echo "   → Frontend will run on http://localhost:8000"
echo ""
echo "🔧 TO MANAGE LICENSES:"
echo "   cd backend"
echo "   python3 admin.py"
echo ""
echo "📚 Read README.md for deployment instructions"
echo ""
