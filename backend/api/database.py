import sqlite3
import hashlib
import hmac
from datetime import datetime, timedelta
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'licenses.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'FDNY_AUTO_FILER_SECRET_KEY_2026_CHANGE_THIS').encode()
class LicenseDB:
    def __init__(self):
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializar base de datos con tabla de licencias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de licencias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                company_name TEXT,
                credits_total INTEGER DEFAULT 50,
                credits_used INTEGER DEFAULT 0,
                reset_date TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_used TEXT
            )
        ''')
        
        # Tabla de dispositivos registrados (fingerprints)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key),
                UNIQUE(license_key, fingerprint)
            )
        ''')
        
        # Tabla de uso/auditoría
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                fingerprint TEXT,
                ip_address TEXT,
                action TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key)
            )
        ''')
        
        # Tabla de rate limiting
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_license_key(self, email):
        """Generar clave de licencia única basada en email"""
        msg = email.lower().strip().encode()
        signature = hmac.new(SECRET_KEY, msg, hashlib.sha256).hexdigest()
        
        # Formatear como XXXX-XXXX-XXXX-XXXX
        key = signature[:16].upper()
        formatted = f"{key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
        return formatted
    
    def create_license(self, email, company_name="", credits=50, months=1):
        """Crear nueva licencia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        license_key = self.generate_license_key(email)
        reset_date = (datetime.now() + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        
        try:
            cursor.execute('''
                INSERT INTO licenses (license_key, email, company_name, credits_total, reset_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (license_key, email, company_name, credits, reset_date))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "license_key": license_key,
                "email": email,
                "credits": credits,
                "reset_date": reset_date
            }
        except sqlite3.IntegrityError:
            conn.close()
            return {
                "success": False,
                "error": "License already exists for this email"
            }
    
    def verify_license(self, license_key):
        """Verificar si la licencia existe y está activa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM licenses WHERE license_key = ? AND active = 1
        ''', (license_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def check_device_limit(self, license_key, fingerprint, max_devices=3):
        """Verificar límite de dispositivos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Contar dispositivos registrados
        cursor.execute('''
            SELECT COUNT(*) as count FROM devices WHERE license_key = ?
        ''', (license_key,))
        
        device_count = cursor.fetchone()['count']
        
        # Verificar si este fingerprint ya está registrado
        cursor.execute('''
            SELECT * FROM devices WHERE license_key = ? AND fingerprint = ?
        ''', (license_key, fingerprint))
        
        existing = cursor.fetchone()
        
        if existing:
            # Actualizar última vez visto
            cursor.execute('''
                UPDATE devices SET last_seen = CURRENT_TIMESTAMP 
                WHERE license_key = ? AND fingerprint = ?
            ''', (license_key, fingerprint))
            conn.commit()
            conn.close()
            return True
        
        # Si no existe y ya llegó al límite
        if device_count >= max_devices:
            conn.close()
            return False
        
        # Registrar nuevo dispositivo
        cursor.execute('''
            INSERT INTO devices (license_key, fingerprint, last_seen)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (license_key, fingerprint))
        
        conn.commit()
        conn.close()
        return True
    
    def check_rate_limit(self, license_key, max_per_hour=15):
        """Verificar rate limit"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM rate_limits 
            WHERE license_key = ? AND timestamp > ?
        ''', (license_key, one_hour_ago))
        
        count = cursor.fetchone()['count']
        conn.close()
        
        return count < max_per_hour
    
    def log_request(self, license_key):
        """Registrar request para rate limiting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rate_limits (license_key) VALUES (?)
        ''', (license_key,))
        
        conn.commit()
        conn.close()
    
    def consume_credit(self, license_key):
        """Consumir un crédito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE licenses 
            SET credits_used = credits_used + 1, last_used = CURRENT_TIMESTAMP
            WHERE license_key = ?
        ''', (license_key,))
        
        conn.commit()
        conn.close()
    
    def check_credits(self, license_key):
        """Verificar créditos disponibles"""
        license_data = self.verify_license(license_key)
        
        if not license_data:
            return False
        
        remaining = license_data['credits_total'] - license_data['credits_used']
        return remaining > 0
    
    def log_usage(self, license_key, fingerprint, ip_address, action):
        """Registrar uso en auditoría"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usage_log (license_key, fingerprint, ip_address, action)
            VALUES (?, ?, ?, ?)
        ''', (license_key, fingerprint, ip_address, action))
        
        conn.commit()
        conn.close()
    
    def get_license_info(self, license_key):
        """Obtener información completa de licencia"""
        license_data = self.verify_license(license_key)
        
        if not license_data:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener dispositivos
        cursor.execute('''
            SELECT fingerprint, registered_at, last_seen 
            FROM devices WHERE license_key = ?
        ''', (license_key,))
        devices = [dict(row) for row in cursor.fetchall()]
        
        # Obtener uso reciente
        cursor.execute('''
            SELECT action, timestamp FROM usage_log 
            WHERE license_key = ? 
            ORDER BY timestamp DESC LIMIT 10
        ''', (license_key,))
        recent_usage = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            **license_data,
            'devices': devices,
            'recent_usage': recent_usage,
            'credits_remaining': license_data['credits_total'] - license_data['credits_used']
        }
    
    def reset_monthly_credits(self):
        """Resetear créditos mensuales (ejecutar con cron)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            UPDATE licenses 
            SET credits_used = 0, reset_date = date(reset_date, '+1 month')
            WHERE reset_date <= ?
        ''', (today,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected

# Instancia global
db = LicenseDB()

# ============================================
# FUNCIONES DE ADMINISTRACIÓN
# ============================================

def create_test_license():
    """Crear licencia de prueba"""
    result = db.create_license(
        email="test@fdnyautofiler.com",
        company_name="Test Company",
        credits=100,
        months=1
    )
    print("Test license created:", result)
    return result

def create_admin_license():
    """Crear licencia de administrador con créditos ilimitados"""
    result = db.create_license(
        email="admin@fdnyautofiler.com",
        company_name="Admin",
        credits=999999,
        months=12
    )
    print("Admin license created:", result)
    return result

if __name__ == "__main__":
    # Crear licencias de prueba
    print("Creating test licenses...")
    create_test_license()
    create_admin_license()
    print("Done!")
