"""
Módulo de generación de PDFs FDNY
Adaptado de main.py para funcionar como API
"""
import json
import datetime
import requests
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject, NumberObject

# Configuración (se carga desde variables de entorno en producción)
API_KEY_NYC = "d5e07d1f59074591b9e1a70610ed8069"  # Tu API key
APP_TOKEN_SOCRATA = "CKHVd7U76JgGB0kTjH0WCA2G8"  # Tu token

# Cargar configuración desde archivo
import os
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

CONFIG = load_config()

COMPANY = CONFIG.get("fire_alarm_company", {})
ARCHITECT = CONFIG.get("architect_applicant", {})
ELECTRICIAN = CONFIG.get("electrical_contractor", {})
TECH_DEFAULTS = CONFIG.get("technical_defaults", {})
CENTRAL_STATION = CONFIG.get("central_station", {})

fecha_hoy = datetime.date.today().strftime("%m/%d/%Y")

# Listas maestras (copiadas de tu main.py)
FULL_FLOOR_LIST = [
    "Sub Cellar", "Cellar", "Basement", "Ground Floor", "1st Floor", "2nd Floor", 
    "3rd Floor", "4th Floor", "5th Floor", "6th Floor", "7th Floor", "8th Floor",
    "9th Floor", "10th Floor", "Roof", "Penthouse"
]

MASTER_DEVICE_LIST = {
    "Initiating": ["Manual Pull Station", "Smoke Detector", "Heat Detector"],
    "Supervisory": ["Valve Tamper Switch", "Pump Running"],
    "Control": ["Fire Door Holder", "HVAC Shut Down"],
    "Signals": ["Horn", "Strobe", "Horn Strobe"],
    "Communication": ["Warden Telephone"],
    "Firepanel": ["Fire Alarm Control"]
}

# ==========================================
# API NYC OPEN DATA
# ==========================================

def obtener_datos_completos(bin_number):
    """
    Obtener datos completos del BIN desde NYC Open Data
    """
    try:
        # BIS API
        url_bis = f"https://data.cityofnewyork.us/resource/ipu4-2q9a.json?bin={bin_number}"
        headers = {"X-App-Token": APP_TOKEN_SOCRATA}
        response_bis = requests.get(url_bis, headers=headers, timeout=10)
        
        if response_bis.status_code != 200 or not response_bis.json():
            return None
        
        data_bis = response_bis.json()[0]
        
        # Extraer datos básicos
        result = {
            "bin": bin_number,
            "house": data_bis.get("house", ""),
            "street": data_bis.get("street_name", ""),
            "borough": data_bis.get("boro", ""),
            "zip": data_bis.get("postcode", ""),
            "construction_class": data_bis.get("cnstrct_yr", ""),
            "occupancy_group": data_bis.get("occupancy", ""),
            "owner_first": "",
            "owner_last": "",
            "owner_business": data_bis.get("owner_name", ""),
            "owner_address": data_bis.get("owner_stname", ""),
            "owner_city": data_bis.get("owner_city", ""),
            "owner_state": data_bis.get("owner_state", ""),
            "owner_zip": data_bis.get("owner_zip", ""),
            "owner_phone": data_bis.get("owner_phone", ""),
            "owner_email": ""
        }
        
        return result
        
    except Exception as e:
        print(f"Error obteniendo datos BIN: {e}")
        return None

# ==========================================
# GENERADORES DE PDF
# ==========================================

def generar_tm1(datos, input_pdf, output_pdf):
    """Generar formulario TM-1"""
    print("📄 Generating TM-1...")
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        if "/AcroForm" in reader.root_object:
            writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
        
        writer.root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
        
        # Campos del formulario
        campos = {
            "buildingNo": datos.get("house", ""),
            "streetName": datos.get("street", ""),
            "borough": datos.get("borough", ""),
            "zip": datos.get("zip", ""),
            "bin": datos.get("bin", ""),
            "lastName": ARCHITECT.get("Last Name", ""),
            "firstName": ARCHITECT.get("First Name", ""),
            "businessName": ARCHITECT.get("Company Name", ""),
            "licenseNumber": ARCHITECT.get("License No", ""),
            "businessTel": ARCHITECT.get("Phone", ""),
            "email": ARCHITECT.get("Email", "")
        }
        
        for i in range(len(writer.pages)):
            writer.update_page_form_field_values(writer.pages[i], campos)
        
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        print("   ✅ TM-1 Generated")
        return True
        
    except Exception as e:
        print(f"   ❌ TM-1 Error: {e}")
        return False

def generar_a433(datos, input_pdf, output_pdf):
    """Generar formulario A-433"""
    print("📄 Generating A-433...")
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        if "/AcroForm" in reader.root_object:
            writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
        
        writer.root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
        
        datos_instalacion = datos.get("devices", [])
        pisos_trabajados = sorted(list(set(d['floor'] for d in datos_instalacion)))
        
        campos = {
            "Building No": datos.get("house", ""),
            "Street Name": datos.get("street", ""),
            "Borough": datos.get("borough", ""),
            "ZIP": datos.get("zip", ""),
            "Work on floor(s)": ", ".join(pisos_trabajados),
            "New": "/On"
        }
        
        # Datos de contratistas
        elec = ELECTRICIAN
        emp = COMPANY
        cs = CENTRAL_STATION
        
        campos.update({
            "First Name_2": elec.get("First Name"),
            "Last Name_2": elec.get("Last Name"),
            "Business Name_2": elec.get("Company Name"),
            "License Number": elec.get("License No")
        })
        
        campos.update({
            "First Name_3": emp.get("First Name"),
            "Last Name_3": emp.get("Last Name"),
            "Business Name_3": emp.get("Company Name"),
            "COF S97": emp.get("COF S97")
        })
        
        campos.update({
            "Business Name_4": cs.get("Company Name"),
            "Station Code": cs.get("CS Code")
        })
        
        for i in range(len(writer.pages)):
            writer.update_page_form_field_values(writer.pages[i], campos)
        
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        print("   ✅ A-433 Generated")
        return True
        
    except Exception as e:
        print(f"   ❌ A-433 Error: {e}")
        return False

def generar_b45(datos, input_pdf, output_pdf):
    """Generar formulario B-45"""
    print("📄 Generating B-45...")
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        if "/AcroForm" in reader.root_object:
            writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
        
        writer.root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
        
        emp = COMPANY
        
        campos = {
            "adress": f"{datos['house']} {datos['street']}, {datos['borough']}, NY {datos['zip']}",
            "name": f"{emp.get('First Name')} {emp.get('Last Name')}",
            "company": emp.get("Company Name"),
            "cphone": emp.get("Phone"),
            "email": emp.get("Email"),
            "date1": fecha_hoy
        }
        
        for i in range(len(writer.pages)):
            writer.update_page_form_field_values(writer.pages[i], campos)
        
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        print("   ✅ B-45 Generated")
        return True
        
    except Exception as e:
        print(f"   ❌ B-45 Error: {e}")
        return False

def generar_reporte_auditoria(datos, output_file):
    """Generar reporte de auditoría"""
    print("📄 Generating Audit Report...")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("AUTOMATED GENERATION REPORT - FDNY SYSTEM\n")
            f.write("=" * 60 + "\n")
            f.write(f"DATE: {fecha_hoy}\n")
            f.write(f"BIN: {datos.get('bin')}\n")
            f.write(f"ADDRESS: {datos.get('house')} {datos.get('street')}\n\n")
            f.write("Generated via Web Application\n")
        
        print("   ✅ Report Generated")
        return True
        
    except Exception as e:
        print(f"   ❌ Report Error: {e}")
        return False
