#!/usr/bin/env python3
"""
FDNY Auto-Filer - License Management CLI
Script de administración para gestionar licencias
"""

import sys
import os
from datetime import datetime

# Añadir path del módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from api.database import db

def print_header():
    print("=" * 60)
    print("🚒 FDNY AUTO-FILER - LICENSE MANAGER")
    print("=" * 60)
    print()

def create_license():
    """Crear nueva licencia"""
    print("\n📝 CREATE NEW LICENSE")
    print("-" * 40)
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required!")
        return
    
    company = input("Company Name (optional): ").strip()
    
    try:
        credits = int(input("Credits (default 50): ") or "50")
    except:
        credits = 50
    
    try:
        months = int(input("Duration in months (default 1): ") or "1")
    except:
        months = 1
    
    print("\n⏳ Creating license...")
    result = db.create_license(email, company, credits, months)
    
    if result['success']:
        print("\n✅ LICENSE CREATED SUCCESSFULLY!")
        print("-" * 40)
        print(f"📧 Email:       {result['email']}")
        print(f"🔑 License Key: {result['license_key']}")
        print(f"💳 Credits:     {result['credits']}")
        print(f"📅 Reset Date:  {result['reset_date']}")
        print("-" * 40)
        print("\n📋 Send this key to the client:")
        print(f"\n    {result['license_key']}\n")
    else:
        print(f"\n❌ ERROR: {result['error']}")

def list_licenses():
    """Listar todas las licencias"""
    print("\n📋 ALL LICENSES")
    print("-" * 120)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT license_key, email, company_name, credits_total, credits_used, 
               active, created_at, last_used
        FROM licenses
        ORDER BY created_at DESC
    ''')
    
    licenses = cursor.fetchall()
    conn.close()
    
    if not licenses:
        print("No licenses found.")
        return
    
    print(f"{'KEY':<20} {'EMAIL':<30} {'COMPANY':<20} {'CREDITS':<15} {'STATUS':<10} {'LAST USED':<20}")
    print("-" * 120)
    
    for lic in licenses:
        key = lic['license_key']
        email = lic['email'][:28] + ".." if len(lic['email']) > 30 else lic['email']
        company = (lic['company_name'] or "N/A")[:18] + ".." if lic['company_name'] and len(lic['company_name']) > 20 else (lic['company_name'] or "N/A")
        credits = f"{lic['credits_total'] - lic['credits_used']}/{lic['credits_total']}"
        status = "ACTIVE" if lic['active'] else "INACTIVE"
        last_used = lic['last_used'] or "Never"
        
        print(f"{key:<20} {email:<30} {company:<20} {credits:<15} {status:<10} {last_used:<20}")
    
    print(f"\nTotal licenses: {len(licenses)}")

def license_details():
    """Ver detalles de una licencia específica"""
    print("\n🔍 LICENSE DETAILS")
    print("-" * 40)
    
    key = input("Enter license key: ").strip()
    
    info = db.get_license_info(key)
    
    if not info:
        print("❌ License not found!")
        return
    
    print("\n📊 LICENSE INFORMATION")
    print("-" * 40)
    print(f"🔑 License Key:  {info['license_key']}")
    print(f"📧 Email:        {info['email']}")
    print(f"🏢 Company:      {info['company_name'] or 'N/A'}")
    print(f"💳 Credits:      {info['credits_remaining']}/{info['credits_total']} remaining")
    print(f"📅 Reset Date:   {info['reset_date']}")
    print(f"✅ Status:       {'ACTIVE' if info['active'] else 'INACTIVE'}")
    print(f"📅 Created:      {info['created_at']}")
    print(f"🕐 Last Used:    {info['last_used'] or 'Never'}")
    
    print(f"\n📱 REGISTERED DEVICES ({len(info['devices'])}/3)")
    print("-" * 40)
    if info['devices']:
        for i, dev in enumerate(info['devices'], 1):
            fp_short = dev['fingerprint'][:16] + "..."
            print(f"  {i}. {fp_short} (registered: {dev['registered_at']})")
    else:
        print("  No devices registered yet")
    
    print(f"\n📜 RECENT USAGE (Last 10)")
    print("-" * 40)
    if info['recent_usage']:
        for usage in info['recent_usage']:
            print(f"  • {usage['action']} - {usage['timestamp']}")
    else:
        print("  No usage history")

def reset_credits():
    """Resetear créditos manualmente"""
    print("\n🔄 RESET CREDITS")
    print("-" * 40)
    
    key = input("Enter license key: ").strip()
    
    if not db.verify_license(key):
        print("❌ License not found!")
        return
    
    confirm = input("⚠️  Reset credits for this license? (yes/no): ").lower()
    
    if confirm == 'yes':
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE licenses SET credits_used = 0 WHERE license_key = ?
        ''', (key,))
        
        conn.commit()
        conn.close()
        
        print("✅ Credits reset successfully!")
    else:
        print("❌ Operation cancelled")

def deactivate_license():
    """Desactivar una licencia"""
    print("\n🚫 DEACTIVATE LICENSE")
    print("-" * 40)
    
    key = input("Enter license key: ").strip()
    
    if not db.verify_license(key):
        print("❌ License not found!")
        return
    
    confirm = input("⚠️  Are you sure? This will block access. (yes/no): ").lower()
    
    if confirm == 'yes':
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE licenses SET active = 0 WHERE license_key = ?
        ''', (key,))
        
        conn.commit()
        conn.close()
        
        print("✅ License deactivated!")
    else:
        print("❌ Operation cancelled")

def reset_devices():
    """Resetear dispositivos registrados"""
    print("\n📱 RESET DEVICES")
    print("-" * 40)
    
    key = input("Enter license key: ").strip()
    
    if not db.verify_license(key):
        print("❌ License not found!")
        return
    
    confirm = input("⚠️  Remove all registered devices? (yes/no): ").lower()
    
    if confirm == 'yes':
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM devices WHERE license_key = ?
        ''', (key,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ Removed {affected} device(s)!")
    else:
        print("❌ Operation cancelled")

def main_menu():
    """Menú principal"""
    while True:
        print_header()
        print("1. 📝 Create New License")
        print("2. 📋 List All Licenses")
        print("3. 🔍 View License Details")
        print("4. 🔄 Reset Credits")
        print("5. 📱 Reset Devices")
        print("6. 🚫 Deactivate License")
        print("7. 🚪 Exit")
        print()
        
        choice = input("Select option (1-7): ").strip()
        
        if choice == '1':
            create_license()
        elif choice == '2':
            list_licenses()
        elif choice == '3':
            license_details()
        elif choice == '4':
            reset_credits()
        elif choice == '5':
            reset_devices()
        elif choice == '6':
            deactivate_license()
        elif choice == '7':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid option!")
        
        input("\nPress ENTER to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)
