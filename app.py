#!/usr/bin/env python3
"""
BioScript - Web Versiyası
Flask əsaslı tibbi resept idarəetmə sistemi
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from datetime import datetime, timedelta
import os
import json

# Database manager import
from database.db_manager import DatabaseManager

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bioscript-secret-key-2025')

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Giriş etməniz tələb olunur.'

# Database manager
db_manager = DatabaseManager()

class User(UserMixin):
    """İstifadəçi sinifi"""
    def __init__(self, doctor_data):
        self.id = str(doctor_data['id'])
        self.username = doctor_data['username']
        self.name = doctor_data['name']
        self.surname = doctor_data['surname']
        self.specialty = doctor_data['specialty']
        self.email = doctor_data.get('email', '')

@login_manager.user_loader
def load_user(user_id):
    """İstifadəçi yükləmə"""
    try:
        doctor = db_manager.get_doctor_by_id(int(user_id))
        if doctor:
            return User(doctor)
    except:
        pass
    return None

@app.route('/')
def index():
    """Ana səhifə"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş səhifəsi"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('İstifadəçi adı və şifrə tələb olunur!', 'error')
            return render_template('login.html')
        
        # Həkim autentifikasiyası
        doctor_data = db_manager.authenticate_doctor(username, password)
        
        if doctor_data:
            user = User(doctor_data)
            login_user(user, remember=True)
            flash(f'Xoş gəlmisiniz, Dr. {doctor_data["name"]} {doctor_data["surname"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('İstifadəçi adı və ya şifrə yanlışdır!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Çıxış"""
    logout_user()
    flash('Uğurla çıxış etdiniz.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Əsas dashboard"""
    # Statistikaları al
    stats = db_manager.get_doctor_statistics(current_user.id)
    
    return render_template('dashboard.html', stats=stats)

@app.route('/patients')
@login_required
def patients():
    """Pasiyentlər səhifəsi"""
    search = request.args.get('search', '').strip()
    
    if search:
        patients_list = db_manager.search_patients(search)
    else:
        patients_list = db_manager.search_patients('')[:50]  # İlk 50 pasiyent
    
    return render_template('patients.html', patients=patients_list, search=search)

@app.route('/patient/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """Pasiyent detalları"""
    patient = db_manager.get_patient_by_id(patient_id)
    if not patient:
        flash('Pasiyent tapılmadı!', 'error')
        return redirect(url_for('patients'))
    
    # Pasiyentin reseptləri
    prescriptions = db_manager.get_patient_prescriptions(patient_id)
    
    return render_template('patient_detail.html', patient=patient, prescriptions=prescriptions)

@app.route('/prescription/new/<int:patient_id>')
@login_required
def new_prescription(patient_id):
    """Yeni resept yazma"""
    patient = db_manager.get_patient_by_id(patient_id)
    if not patient:
        flash('Pasiyent tapılmadı!', 'error')
        return redirect(url_for('patients'))
    
    # Dərmanlar siyahısı
    medications = db_manager.get_medications_list()
    
    return render_template('new_prescription.html', patient=patient, medications=medications)

@app.route('/prescription/save', methods=['POST'])
@login_required
def save_prescription():
    """Resepti yadda saxlama"""
    try:
        patient_id = int(request.form.get('patient_id'))
        complaint = request.form.get('complaint', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Dərmanlar məlumatları
        medications_data = []
        medication_names = request.form.getlist('medication_name[]')
        dosages = request.form.getlist('dosage[]')
        frequencies = request.form.getlist('frequency[]')
        durations = request.form.getlist('duration[]')
        quantities = request.form.getlist('quantity[]')
        instructions = request.form.getlist('instructions[]')
        
        for i in range(len(medication_names)):
            if medication_names[i].strip():
                medications_data.append({
                    'medication_name': medication_names[i].strip(),
                    'dosage': dosages[i].strip(),
                    'frequency': frequencies[i].strip(),
                    'duration': durations[i].strip(),
                    'quantity': int(quantities[i]) if quantities[i].isdigit() else 1,
                    'instructions': instructions[i].strip()
                })
        
        if not medications_data:
            flash('Ən azı bir dərman əlavə edin!', 'error')
            return redirect(request.referrer)
        
        # Resept məlumatları
        prescription_data = {
            'doctor_id': int(current_user.id),
            'patient_id': patient_id,
            'complaint': complaint,
            'diagnosis': diagnosis,
            'notes': notes,
            'medications': medications_data
        }
        
        # Yadda saxla
        prescription_id = db_manager.create_prescription(prescription_data)
        
        if prescription_id:
            flash(f'Resept uğurla yaradıldı! (ID: {prescription_id})', 'success')
            return redirect(url_for('patient_detail', patient_id=patient_id))
        else:
            flash('Resept yaradılmadı!', 'error')
            
    except Exception as e:
        flash(f'Xəta baş verdi: {str(e)}', 'error')
    
    return redirect(request.referrer)

@app.route('/statistics')
@login_required
def statistics():
    """Statistika səhifəsi"""
    # Tarix filtri
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
            end_date = None
    else:
        # Default: son 30 gün
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Statistikaları al
    stats = db_manager.get_doctor_statistics(current_user.id, start_date, end_date)
    
    return render_template('statistics.html', 
                         stats=stats, 
                         start_date=start_date, 
                         end_date=end_date)

@app.route('/api/medications/search')
@login_required
def api_medications_search():
    """Dərman axtarışı API"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    medications = db_manager.get_medications_list()
    
    # Filtrlə
    filtered = [med for med in medications 
                if query.lower() in med['name'].lower()]
    
    return jsonify(filtered[:10])  # İlk 10 nəticə

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message='Səhifə tapılmadı'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message='Daxili server xətası'), 500

if __name__ == '__main__':
    # Portun host və portunu təyin et
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🏥 BioScript Web sistemi başladılır...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"👨‍⚕️ Test həkim: hekim1 / 123456")
    
    app.run(host=host, port=port, debug=True)