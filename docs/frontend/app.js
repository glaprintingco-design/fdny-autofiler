// ============================================
// CONFIGURATION
// ============================================
const API_URL = 'http://localhost:5000/api';

// ============================================
// GLOBAL STATE
// ============================================
let currentLicense = null;
let currentFingerprint = null;
let binData = null;
let devices = [];

// Device catalog
const FLOOR_LIST = [
    "Sub Cellar", "Cellar", "Basement", "Ground Floor", "1st Floor", "2nd Floor", 
    "3rd Floor", "4th Floor", "5th Floor", "6th Floor", "7th Floor", "8th Floor", 
    "9th Floor", "10th Floor", "Roof", "Penthouse", "Mechanical Floor"
];

const DEVICE_CATALOG = {
    "Initiating": [
        "Manual Pull Station", "Smoke Detector", "Heat Detector", 
        "Duct Smoke Detector", "Water Flow Switch", "Carbon Monoxide Detector"
    ],
    "Supervisory": [
        "Valve Tamper Switch", "Low Air Switch", "Pump Running", 
        "Generator Failure", "Tank Temperature Switch"
    ],
    "Control": [
        "Fire Door Holder", "HVAC Shut Down", "Elevator Recall", 
        "Fire Damper", "Smoke Damper"
    ],
    "Signals": [
        "Horn", "Strobe", "Horn Strobe", "Speaker", 
        "Speaker Strobe", "Chime"
    ],
    "Communication": [
        "Warden Telephone", "Warden Jack", "Remote Microphone"
    ],
    "Firepanel": [
        "Fire Alarm Control", "Fire Command Center", "Annunciator Panel"
    ]
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    
    const storedLicense = localStorage.getItem('fdny_license');
    if (storedLicense) {
        verifyAndLoadSession(storedLicense);
    }
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    populateFloorSelect();
    generateFingerprint();
    
    log('System initialized', 'success');
});

// ============================================
// AUTHENTICATION
// ============================================
async function handleLogin(e) {
    e.preventDefault();
    
    const licenseKey = document.getElementById('licenseInput').value.trim();
    const errorDiv = document.getElementById('loginError');
    
    if (!licenseKey) {
        showError('Please enter a license key');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(API_URL + '/auth/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                license_key: licenseKey,
                fingerprint: currentFingerprint
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentLicense = licenseKey;
            localStorage.setItem('fdny_license', licenseKey);
            
            updateCreditsDisplay(data.credits_used, data.credits_total);
            
            document.getElementById('loginScreen').classList.remove('active');
            document.getElementById('appScreen').classList.add('active');
            
            log('Welcome! You have ' + (data.credits_total - data.credits_used) + ' credits remaining.', 'success');
        } else {
            showError(data.error || 'Invalid license key');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Connection error. Make sure backend is running on http://localhost:5000');
    } finally {
        showLoading(false);
    }
}

async function verifyAndLoadSession(license) {
    try {
        const response = await fetch(API_URL + '/auth/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                license_key: license,
                fingerprint: currentFingerprint
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentLicense = license;
            updateCreditsDisplay(data.credits_used, data.credits_total);
            
            document.getElementById('loginScreen').classList.remove('active');
            document.getElementById('appScreen').classList.add('active');
            
            log('Session restored', 'success');
        } else {
            localStorage.removeItem('fdny_license');
        }
    } catch (error) {
        console.error('Session verification failed:', error);
        localStorage.removeItem('fdny_license');
    }
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        currentLicense = null;
        localStorage.removeItem('fdny_license');
        devices = [];
        binData = null;
        
        document.getElementById('appScreen').classList.remove('active');
        document.getElementById('loginScreen').classList.add('active');
        
        document.getElementById('licenseInput').value = '';
        document.getElementById('binInput').value = '';
        updateDeviceTable();
        
        log('Logged out successfully', 'success');
    }
}

// ============================================
// FINGERPRINTING
// ============================================
async function generateFingerprint() {
    const data = {
        screen: screen.width + 'x' + screen.height,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        platform: navigator.platform,
        userAgent: navigator.userAgent.substring(0, 100)
    };
    
    const jsonStr = JSON.stringify(data);
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(jsonStr);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    currentFingerprint = hashArray.map(function(b) { return b.toString(16).padStart(2, '0'); }).join('');
    
    console.log('Fingerprint generated:', currentFingerprint.substring(0, 16) + '...');
}

// ============================================
// BIN DATA LOADING
// ============================================
async function loadBINData() {
    const binInput = document.getElementById('binInput').value.trim();
    
    if (!binInput) {
        alert('Please enter a BIN number');
        return;
    }
    
    showLoading(true);
    log('Loading data for BIN: ' + binInput + '...');
    
    try {
        const response = await fetch(API_URL + '/bin/' + binInput, {
            headers: {
                'Authorization': 'Bearer ' + currentLicense
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            binData = data;
            displayBINInfo(data);
            log('BIN data loaded successfully', 'success');
        } else {
            log(data.error || 'Failed to load BIN data', 'error');
            alert(data.error || 'Failed to load BIN data');
        }
    } catch (error) {
        console.error('BIN load error:', error);
        log('Connection error', 'error');
        alert('Connection error. Please try again.');
    } finally {
        showLoading(false);
    }
}

function displayBINInfo(data) {
    const infoDiv = document.getElementById('binInfo');
    infoDiv.innerHTML = '<h3>Property Information Loaded</h3>' +
        '<p><strong>Address:</strong> ' + data.house + ' ' + data.street + ', ' + data.borough + ', NY ' + data.zip + '</p>' +
        '<p><strong>Owner:</strong> ' + data.owner_first + ' ' + data.owner_last + '</p>' +
        '<p><strong>Construction:</strong> ' + (data.construction_class || 'N/A') + '</p>' +
        '<p><strong>Occupancy:</strong> ' + (data.occupancy_group || 'N/A') + '</p>';
    infoDiv.classList.add('show');
}

// ============================================
// DEVICE MANAGEMENT
// ============================================
function populateFloorSelect() {
    const select = document.getElementById('floorSelect');
    if (!select) return;
    
    FLOOR_LIST.forEach(function(floor) {
        const option = document.createElement('option');
        option.value = floor;
        option.textContent = floor;
        select.appendChild(option);
    });
}

function updateDeviceOptions() {
    const category = document.getElementById('categorySelect').value;
    const deviceSelect = document.getElementById('deviceSelect');
    
    deviceSelect.innerHTML = '<option value="">Select Device...</option>';
    
    if (category && DEVICE_CATALOG[category]) {
        DEVICE_CATALOG[category].forEach(function(device) {
            const option = document.createElement('option');
            option.value = device;
            option.textContent = device;
            deviceSelect.appendChild(option);
        });
    }
}

function addDevice() {
    const floor = document.getElementById('floorSelect').value;
    const category = document.getElementById('categorySelect').value;
    const device = document.getElementById('deviceSelect').value;
    const quantity = parseInt(document.getElementById('quantityInput').value) || 1;
    
    if (!floor || !category || !device) {
        alert('Please fill all fields');
        return;
    }
    
    devices.push({
        floor: floor,
        category: category,
        device: device,
        qty: quantity
    });
    
    updateDeviceTable();
    log('Added: ' + quantity + 'x ' + device + ' on ' + floor, 'success');
    
    document.getElementById('quantityInput').value = 1;
}

function removeDevice(index) {
    const device = devices[index];
    devices.splice(index, 1);
    updateDeviceTable();
    log('Removed: ' + device.device, 'warning');
}

function updateDeviceTable() {
    const tbody = document.getElementById('deviceTableBody');
    
    if (devices.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No devices added yet. Add devices to generate A-433 form.</td></tr>';
        return;
    }
    
    tbody.innerHTML = devices.map(function(d, index) {
        return '<tr>' +
            '<td>' + d.floor + '</td>' +
            '<td>' + d.device + '</td>' +
            '<td>' + d.category + '</td>' +
            '<td>' + d.qty + '</td>' +
            '<td><button class="btn-delete" onclick="removeDevice(' + index + ')">Delete</button></td>' +
            '</tr>';
    }).join('');
}

// ============================================
// DOCUMENT GENERATION
// ============================================
async function generateDocuments() {
    if (!binData) {
        alert('Please load BIN data first (Step 1)');
        return;
    }
    
    const generateBtn = document.getElementById('generateBtn');
    const progressBar = document.getElementById('progressBar');
    const downloadSection = document.getElementById('downloadSection');
    
    generateBtn.disabled = true;
    progressBar.classList.remove('hidden');
    downloadSection.classList.add('hidden');
    
    log('Starting document generation...');
    showLoading(true);
    
    try {
        const response = await fetch(API_URL + '/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + currentLicense,
                'X-Fingerprint': currentFingerprint
            },
            body: JSON.stringify({
                bin: binData.bin,
                devices: devices,
                bin_data: binData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            updateCreditsDisplay(data.credits_used, data.credits_total);
            displayDownloadLinks(data.files);
            
            log('All documents generated successfully!', 'success');
            log('Credits remaining: ' + (data.credits_total - data.credits_used), 'success');
            
            progressBar.classList.add('hidden');
            downloadSection.classList.remove('hidden');
        } else {
            log(data.error || 'Generation failed', 'error');
            alert(data.error || 'Document generation failed');
            progressBar.classList.add('hidden');
        }
    } catch (error) {
        console.error('Generation error:', error);
        log('Connection error during generation', 'error');
        alert('Connection error. Please try again.');
        progressBar.classList.add('hidden');
    } finally {
        showLoading(false);
        generateBtn.disabled = false;
    }
}

function displayDownloadLinks(files) {
    const container = document.getElementById('downloadButtons');
    
    const fileNames = {
        'tm1': 'TM-1 Application',
        'a433': 'A-433 Form',
        'b45': 'B-45 Inspection Request',
        'report': 'Audit Report'
    };
    
    const links = [];
    for (var key in files) {
        if (files.hasOwnProperty(key)) {
            links.push('<a href="data:application/pdf;base64,' + files[key] + '" download="' + key + '.pdf" class="btn-download">' + fileNames[key] + '</a>');
        }
    }
    
    container.innerHTML = links.join('');
}

// ============================================
// UI HELPERS
// ============================================
function updateCreditsDisplay(used, total) {
    const remaining = total - used;
    const creditsValue = document.getElementById('creditsValue');
    creditsValue.textContent = remaining + '/' + total;
    
    if (remaining < 10) {
        creditsValue.style.color = '#FF4444';
    } else if (remaining < 25) {
        creditsValue.style.color = '#FFAA00';
    } else {
        creditsValue.style.color = '#00FF00';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('loginError');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    
    setTimeout(function() {
        errorDiv.classList.remove('show');
    }, 5000);
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function log(message, type) {
    const consoleDiv = document.getElementById('console');
    const timestamp = new Date().toLocaleTimeString();
    const classMap = {
        'success': 'success',
        'error': 'error',
        'warning': 'warning',
        'info': ''
    };
    
    const p = document.createElement('p');
    p.className = classMap[type] || '';
    p.textContent = '[' + timestamp + '] ' + message;
    
    consoleDiv.appendChild(p);
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}
