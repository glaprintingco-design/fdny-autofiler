#!/usr/bin/env python3
"""
Script para generar licencias iniciales del sistema
Ejecutar ANTES del primer deployment
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from api.database import db

def main():
    print("=" * 60)
    print("🚒 FDNY AUTO-FILER - INITIAL SETUP")
    print("=" * 60)
    print()
    
    # Licencia de prueba
    print("📝 Creating TEST license...")
    test = db.create_license(
        email="test@fdnyautofiler.com",
        company_name="Test Company",
        credits=100,
        months=1
    )
    
    if test['success']:
        print("✅ Test License Created:")
        print(f"   Email: {test['email']}")
        print(f"   Key:   {test['license_key']}")
        print(f"   Credits: {test['credits']}")
        print()
    
    # Licencia de administrador
    print("📝 Creating ADMIN license...")
    admin = db.create_license(
        email="admin@fdnyautofiler.com",
        company_name="Admin",
        credits=999999,
        months=12
    )
    
    if admin['success']:
        print("✅ Admin License Created:")
        print(f"   Email: {admin['email']}")
        print(f"   Key:   {admin['license_key']}")
        print(f"   Credits: {admin['credits']}")
        print()
    
    # IMPORTANTE: Crear TU primera licencia real
    print("📝 Creating YOUR first license...")
    print()
    your_email = input("Enter your email: ").strip()
    your_company = input("Enter your company name: ").strip()
    
    your_license = db.create_license(
        email=your_email,
        company_name=your_company,
        credits=50,
        months=1
    )
    
    if your_license['success']:
        print()
        print("✅ Your License Created:")
        print(f"   Email: {your_license['email']}")
        print(f"   Key:   {your_license['license_key']}")
        print(f"   Credits: {your_license['credits']}")
        print()
        print("🔑 SAVE THIS KEY! You'll need it to access the system.")
        print()
        print(f"   {your_license['license_key']}")
        print()
    
    print("=" * 60)
    print("✅ INITIAL SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Save your license keys somewhere safe")
    print("2. Deploy the backend to Vercel")
    print("3. Deploy the frontend to GitHub Pages")
    print("4. Update the API URL in frontend/app.js")
    print()
    print("See docs/DEPLOYMENT.md for detailed instructions.")
    print()

if __name__ == "__main__":
    main()
