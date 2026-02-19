from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import io
import base64
from datetime import datetime

# Añadir directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos locales
from api.database import db, DATABASE_PATH
from api import pdf_generator

app = Flask(__name__)
CORS(app)  # Permitir CORS para GitHub Pages

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/auth/verify', methods=['POST'])
def verify_license():
    """Verificar licencia y retornar información"""
    data = request.json
    license_key = data.get('license_key', '').strip()
    fingerprint = data.get('fingerprint', '')
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    # Verificar licencia existe y está activa
    license_info = db.verify_license(license_key)
    
    if not license_info:
        return jsonify({'error': 'Invalid or inactive license'}), 403
    
    # Verificar límite de dispositivos
    if fingerprint:
        device_allowed = db.check_device_limit(license_key, fingerprint, max_devices=3)
        if not device_allowed:
            return jsonify({
                'error': 'Device limit reached',
                'message': 'Maximum 3 devices allowed per license. Contact support to reset.'
            }), 403
    
    # Log de auditoría
    db.log_usage(license_key, fingerprint, request.remote_addr, 'LOGIN')
    
    return jsonify({
        'success': True,
        'email': license_info['email'],
        'company': license_info['company_name'],
        'credits_total': license_info['credits_total'],
        'credits_used': license_info['credits_used'],
        'credits_remaining': license_info['credits_total'] - license_info['credits_used'],
        'reset_date': license_info['reset_date']
    }), 200

@app.route('/api/auth/info', methods=['GET'])
def get_license_info():
    """Obtener información detallada de licencia"""
    auth_header = request.headers.get('Authorization', '')
    license_key = auth_header.replace('Bearer ', '').strip()
    
    if not license_key:
        return jsonify({'error': 'Authorization required'}), 401
    
    info = db.get_license_info(license_key)
    
    if not info:
        return jsonify({'error': 'Invalid license'}), 403
    
    return jsonify(info), 200

# ============================================
# BIN DATA ROUTE
# ============================================

@app.route('/api/bin/<bin_number>', methods=['GET'])
def get_bin_data(bin_number):
    """Obtener datos de BIN desde NYC Open Data"""
    auth_header = request.headers.get('Authorization', '')
    license_key = auth_header.replace('Bearer ', '').strip()
    
    # Verificar autenticación
    if not db.verify_license(license_key):
        return jsonify({'error': 'Invalid license'}), 403
    
    try:
        # Usar función de tu main.py
        data = pdf_generator.obtener_datos_completos(bin_number)
        
        if data:
            db.log_usage(license_key, '', request.remote_addr, f'BIN_LOOKUP:{bin_number}')
            return jsonify(data), 200
        else:
            return jsonify({'error': 'BIN not found or API error'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# DOCUMENT GENERATION ROUTE
# ============================================

@app.route('/api/generate', methods=['POST'])
def generate_documents():
    """Generar documentos FDNY"""
    auth_header = request.headers.get('Authorization', '')
    license_key = auth_header.replace('Bearer ', '').strip()
    fingerprint = request.headers.get('X-Fingerprint', '')
    
    # 1. Verificar licencia
    license_info = db.verify_license(license_key)
    if not license_info:
        return jsonify({'error': 'Invalid license'}), 403
    
    # 2. Verificar créditos
    if not db.check_credits(license_key):
        return jsonify({
            'error': 'No credits remaining',
            'credits_used': license_info['credits_used'],
            'credits_total': license_info['credits_total'],
            'reset_date': license_info['reset_date']
        }), 429
    
    # 3. Verificar rate limit
    if not db.check_rate_limit(license_key, max_per_hour=15):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Maximum 15 documents per hour. Please try again later.'
        }), 429
    
    # 4. Obtener datos del request
    data = request.json
    bin_number = data.get('bin')
    devices = data.get('devices', [])
    bin_data = data.get('bin_data', {})
    
    if not bin_number:
        return jsonify({'error': 'BIN number required'}), 400
    
    try:
        # 5. Generar PDFs
        full_data = {**bin_data, 'devices': devices}
        
        # Paths temporales
        temp_dir = '/tmp'
        tm1_path = os.path.join(temp_dir, f'TM1_{bin_number}.pdf')
        a433_path = os.path.join(temp_dir, f'A433_{bin_number}.pdf')
        b45_path = os.path.join(temp_dir, f'B45_{bin_number}.pdf')
        report_path = os.path.join(temp_dir, f'REPORT_{bin_number}.txt')
        
        # Generar documentos usando tu código
        pdf_generator.generar_tm1(full_data, 'templates/tm-1.pdf', tm1_path)
        pdf_generator.generar_a433(full_data, 'templates/a-433.pdf', a433_path)
        pdf_generator.generar_b45(full_data, 'templates/b45.pdf', b45_path)
        pdf_generator.generar_reporte_auditoria(full_data, report_path)
        
        # Convertir a base64 para enviar al frontend
        files = {}
        for key, path in [('tm1', tm1_path), ('a433', a433_path), ('b45', b45_path), ('report', report_path)]:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    content = f.read()
                    files[key] = base64.b64encode(content).decode('utf-8')
        
        # 6. Consumir crédito
        db.consume_credit(license_key)
        db.log_request(license_key)
        db.log_usage(license_key, fingerprint, request.remote_addr, f'GENERATE:{bin_number}')
        
        # 7. Actualizar info de licencia
        updated_license = db.verify_license(license_key)
        
        return jsonify({
            'success': True,
            'files': files,
            'credits_used': updated_license['credits_used'],
            'credits_total': updated_license['credits_total'],
            'message': 'Documents generated successfully'
        }), 200
        
    except Exception as e:
        print(f"Error generating documents: {e}")
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500

# ============================================
# ADMIN ROUTES (Opcional)
# ============================================

@app.route('/api/admin/create-license', methods=['POST'])
def admin_create_license():
    """Crear nueva licencia (solo admin)"""
    # TODO: Agregar autenticación de admin
    
    data = request.json
    email = data.get('email')
    company = data.get('company_name', '')
    credits = data.get('credits', 50)
    months = data.get('months', 1)
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    result = db.create_license(email, company, credits, months)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/admin/list-licenses', methods=['GET'])
def admin_list_licenses():
    """Listar todas las licencias (solo admin)"""
    # TODO: Agregar autenticación de admin
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT license_key, email, company_name, credits_total, credits_used, 
               active, created_at, last_used
        FROM licenses
        ORDER BY created_at DESC
    ''')
    
    licenses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(licenses), 200

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar que la API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# DEVELOPMENT SERVER
# ============================================

if __name__ == '__main__':
    print("🚀 FDNY Auto-Filer API Server")
    print("📝 Initializing database...")
    
    # Crear licencias de prueba en desarrollo
    if not os.path.exists(DATABASE_PATH):
        print("Creating test licenses...")
        from api.database import create_test_license, create_admin_license
        create_test_license()
        create_admin_license()
    
    print("✅ Ready!")
    print("🌐 Server running on http://localhost:5000")
    
    app.run(debug=True, port=5000)
