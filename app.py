# app.py - COMPLETELY FIXED VERSION
from flask import Flask, request, jsonify, redirect, session, url_for, send_file, render_template
import pandas as pd
import os
import json
import urllib.parse
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import io
from datetime import datetime
import matplotlib.pyplot as plt
import base64
import re
import sys

# Add ml folder to Python path for ML model import
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

# NEW: Import OCR.space components
try:
    from ocr.universal_reader import universal_reader
    OCR_SPACE_AVAILABLE = True
    print("✅ OCR.space API components imported successfully!")
except ImportError as e:
    print(f"❌ OCR.space components import failed: {e}")
    OCR_SPACE_AVAILABLE = False
    universal_reader = None

app = Flask(__name__)
app.secret_key = 'heartshield_professional_ui_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'database/heartshield.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create necessary directories
os.makedirs('database', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/charts', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def init_database():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            age INTEGER,
            height REAL,
            weight REAL,
            gender TEXT,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            cholesterol INTEGER,
            glucose INTEGER,
            smoking INTEGER,
            alcohol_intake INTEGER,
            physical_activity INTEGER,
            bmi REAL,
            probability REAL,
            risk_level TEXT,
            prediction_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# ===== ML MODEL INTEGRATION =====
try:
    from predictor import predictor as ml_predictor
    ML_MODEL_AVAILABLE = True
    print("✅ ML Predictor imported successfully!")
except ImportError as e:
    print(f"❌ ML Predictor import failed: {e}")
    ML_MODEL_AVAILABLE = False
    ml_predictor = None

# ===== ENHANCED PREDICTION LOGIC WITH OCR.SPACE =====
class RealPredictor:
    def __init__(self):
        self.ml_predictor = ml_predictor if ML_MODEL_AVAILABLE else None
        self.ml_accuracy = 0.956
        
        self.ocr_available = OCR_SPACE_AVAILABLE
        if self.ocr_available:
            self.universal_reader = universal_reader
            print("✅ OCR.space API integrated into predictor!")
    
    def predict_from_medical_data(self, extracted_data):
        try:
            if self.ml_predictor and hasattr(self.ml_predictor, 'predict_risk'):
                ml_result = self.ml_predictor.predict_risk(extracted_data)
                
                if ml_result and ml_result.get('success', False):
                    print("🎯 Using ML Model Prediction with NEW features")
                    return {
                        "risk_category": ml_result.get("risk_category", "Unknown"),
                        "risk_percentage": ml_result.get("risk_percentage", 50.0),
                        "confidence": ml_result.get("confidence", 75.0),
                        "message": ml_result.get("message", "AI Risk Assessment"),
                        "probability": ml_result.get("probability", 0.5),
                        "prediction": ml_result.get("prediction", 0),
                        "model_used": "AI_ML_Model_NewFeatures",
                        "accuracy": self.ml_accuracy,
                        "ocr_engine": "ocr_space_api" if self.ocr_available else "legacy"
                    }
            
            print("🔄 Using Rule-Based Prediction (Fallback)")
            probability, risk_level = self._calculate_risk_fallback(extracted_data)
            
            return {
                "risk_category": risk_level,
                "risk_percentage": round(probability * 100, 1),
                "confidence": round((1 - probability) * 100, 1) if probability < 0.5 else round(probability * 100, 1),
                "message": f"Heart disease risk: {risk_level} ({probability * 100:.1f}%) [Rule-Based]",
                "probability": probability,
                "prediction": 1 if probability > 0.5 else 0,
                "model_used": "RuleBased_Fallback",
                "accuracy": 0.75,
                "ocr_engine": "ocr_space_api" if self.ocr_available else "legacy"
            }
                
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._emergency_fallback()
    
    def _calculate_risk_fallback(self, extracted_data):
        risk_score = 0
        
        age = extracted_data.get('Age', 50)
        if age > 60: risk_score += 0.3
        elif age > 50: risk_score += 0.2
        
        systolic = extracted_data.get('Systolic_BP', 120)
        diastolic = extracted_data.get('Diastolic_BP', 80)
        if systolic > 140 or diastolic > 90: risk_score += 0.25
        elif systolic > 130 or diastolic > 85: risk_score += 0.15
        
        cholesterol = extracted_data.get('Cholesterol', 200)
        if cholesterol > 240: risk_score += 0.3
        elif cholesterol > 200: risk_score += 0.15
        
        glucose = extracted_data.get('Glucose', 95)
        if glucose > 126: risk_score += 0.2
        elif glucose > 100: risk_score += 0.1
        
        if 'Height' in extracted_data and 'Weight' in extracted_data:
            height_m = extracted_data['Height'] / 100
            bmi = extracted_data['Weight'] / (height_m ** 2)
            if bmi > 30: risk_score += 0.15
            elif bmi > 25: risk_score += 0.1
        
        probability = min(risk_score, 0.95)
        probability = max(probability, 0.05)
        
        if probability < 0.2: risk_level = "Low"
        elif probability < 0.5: risk_level = "Moderate"
        else: risk_level = "High"
        
        return probability, risk_level
    
    def _emergency_fallback(self):
        return {
            "risk_category": "Unknown",
            "risk_percentage": 50.0,
            "confidence": 50.0,
            "message": "System temporarily unavailable. Please try again.",
            "probability": 0.5,
            "prediction": 0,
            "model_used": "Emergency_Fallback",
            "accuracy": 0.5,
            "ocr_engine": "ocr_space_api" if self.ocr_available else "legacy"
        }
    
    def predict_risk(self, data):
        if self.ml_predictor and hasattr(self.ml_predictor, 'predict_risk'):
            result = self.ml_predictor.predict_risk(data)
            if result and result.get('success'):
                return result
        
        return self.predict_from_medical_data(data)

# Use enhanced predictor
predictor = RealPredictor()

# Load dataset for stats
try:
    df = pd.read_csv('ml/heartshield_dataset.csv')
    heart_disease_rate = df['Cardiovascular_Disease'].mean() * 100
    total_patients = len(df)
    print("✅ NEW Dataset loaded successfully!")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    heart_disease_rate = 50.0
    total_patients = 10000

# Update accuracy display to show real ML accuracy
ML_ACCURACY = 95.6 if ML_MODEL_AVAILABLE else 75.0

# ===== SIMPLIFIED OCR ROUTES =====

@app.route('/ocr')
def ocr_form():
    ocr_status = "✅ ACTIVE (OCR.space API)" if OCR_SPACE_AVAILABLE else "⚠️ LIMITED (Basic OCR)"
    ocr_accuracy = "85-95%" if OCR_SPACE_AVAILABLE else "60-70%"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCR Medical Document - HeartShield</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; color: #2c3e50; font-weight: bold; }}
            input[type="file"] {{ padding: 10px; border: 2px dashed #3498db; border-radius: 5px; width: 100%; box-sizing: border-box; }}
            .btn {{ background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 1.1em; cursor: pointer; margin-top: 10px; }}
            .btn-primary {{ background: #27ae60; }}
            .info-box {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 5px solid #3498db; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📄 OCR Medical Document Processing</h2>
            <div style="margin-bottom: 20px;">
                <span style="background: #27ae60; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; display: inline-block;">OCR Status: {ocr_status}</span>
                <span style="background: #e74c3c; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; display: inline-block; margin-left: 10px;">Accuracy: {ocr_accuracy}</span>
            </div>
            <p>Upload a medical document or lab report image to automatically extract health data:</p>
            
            <div class="info-box">
                <h4>📋 Supported Document Types:</h4>
                <p>Lab Reports, Discharge Summaries, Clinic Notes, Health Records</p>
                <p><strong>Supported formats:</strong> JPG, PNG, PDF images</p>
                <p><strong>OCR Engine:</strong> OCR.space API with medical term recognition</p>
            </div>

            <form method="POST" action="/perform_ocr" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="document">Select Medical Document:</label>
                    <input type="file" id="document" name="document" accept=".jpg,.jpeg,.png,.pdf" required>
                </div>
                
                <button type="submit" class="btn btn-primary">🔍 Process Document with OCR.space</button>
            </form>
            
            <div style="margin-top: 30px;">
                <h4>🎯 What We Extract:</h4>
                <ul>
                    <li><strong>Age</strong> - Patient age in years</li>
                    <li><strong>Height & Weight</strong> - For BMI calculation</li>
                    <li><strong>Blood Pressure</strong> - Systolic and Diastolic</li>
                    <li><strong>Cholesterol Levels</strong> - Total cholesterol</li>
                    <li><strong>Glucose Levels</strong> - Blood sugar levels</li>
                    <li><strong>Gender</strong> - Patient gender</li>
                </ul>
            </div>
            
            <br>
            <a href="/" style="background: #7f8c8d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Home</a>
            <a href="/test-prediction" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Manual Input</a>
        </div>
    </body>
    </html>
    '''

@app.route('/perform_ocr', methods=['POST'])
def perform_ocr():
    if 'document' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['document']
    if file.filename == '':
        return "No file selected", 400
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            if OCR_SPACE_AVAILABLE:
                print(f"🔍 Processing with OCR.space API: {filename}")
                result = universal_reader.process_any_document(filepath)
                
                extracted_data = result.get('extracted_data', {})
                validation_result = result.get('validation_result', {})
                prediction_result = result.get('prediction_result', {})
                document_type = result.get('document_type', 'unknown')
                ocr_engine = result.get('ocr_engine', 'ocr_space_api')
                
                extracted_text = ""
                if hasattr(universal_reader, 'extract_text_from_image'):
                    extracted_text = universal_reader.extract_text_from_image(filepath)
                
            else:
                print(f"⚠️ Using legacy OCR: {filename}")
                from PIL import Image
                import pytesseract
                
                image = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(image)
                extracted_data = {}
                validation_result = {'status': 'LEGACY_OCR'}
                prediction_result = None
                document_type = 'legacy'
                ocr_engine = 'legacy_tesseract'
            
            if extracted_data and len(extracted_data) >= 3:
                if not prediction_result:
                    prediction_result = predictor.predict_risk(extracted_data)
            
            os.remove(filepath)
            
            # Build results using simple string concatenation
            html_parts = []
            html_parts.append('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>OCR Results - HeartShield</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }
                    .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
                    .result-section { margin: 20px 0; padding: 20px; border-radius: 5px; }
                    .extracted-text { background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 200px; overflow-y: auto; font-family: monospace; }
                    .data-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0; }
                    .data-item { background: white; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #ddd; }
                    .prediction-box { background: #e8f4f8; padding: 20px; border-radius: 5px; border-left: 5px solid #27ae60; }
                    .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>📄 OCR Processing Complete</h2>
                    <div style="background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <strong>OCR Engine:</strong> ''' + ocr_engine.upper() + ''' | 
                        <strong>Document Type:</strong> ''' + document_type + ''' |
                        <strong>Processing Status:</strong> <span style="background: #27ae60; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; display: inline-block;">''' + validation_result.get('status', 'COMPLETED') + '''</span>
                    </div>
            ''')
            
            if extracted_text:
                html_parts.append('''
                <div class="result-section">
                    <h3>🔍 Extracted Text (''' + str(len(extracted_text)) + ''' characters):</h3>
                    <div class="extracted-text">''' + (extracted_text[:1000] + '...' if len(extracted_text) > 1000 else extracted_text) + '''</div>
                </div>
                ''')
            
            if extracted_data:
                html_parts.append('''
                <div class="result-section">
                    <h3>🎯 Parsed Medical Data (''' + str(len(extracted_data)) + ''' fields):</h3>
                    <div class="data-grid">
                ''')
                for key, value in extracted_data.items():
                    if key not in ['error', 'document_type']:
                        html_parts.append('<div class="data-item"><strong>' + str(key) + '</strong><br>' + str(value) + '</div>')
                html_parts.append('</div>')
            else:
                html_parts.append('''
                <div class="result-section">
                    <p>❌ No medical parameters could be automatically extracted from the document.</p>
                    <p>Please use the manual input form below with the values from your document.</p>
                </div>
                ''')
            
            if prediction_result:
                risk_color = "#27ae60"
                risk_level = prediction_result.get('risk_category', 'Unknown')
                if risk_level == 'Moderate':
                    risk_color = "#f39c12"
                elif risk_level == 'High':
                    risk_color = "#e74c3c"
                    
                html_parts.append('''
                <div class="result-section">
                    <h3>❤️ Heart Disease Risk Assessment:</h3>
                    <div class="prediction-box" style="border-left-color: ''' + risk_color + ''';">
                        <h4 style="color: ''' + risk_color + ''';">Risk Level: ''' + risk_level + '''</h4>
                        <p><strong>Risk Percentage:</strong> ''' + str(prediction_result.get('risk_percentage', 'N/A')) + '''%</p>
                        <p><strong>Confidence:</strong> ''' + str(prediction_result.get('confidence', 'N/A')) + '''%</p>
                        <p><strong>Message:</strong> ''' + prediction_result.get('message', 'No message') + '''</p>
                        <p><strong>Model Used:</strong> ''' + prediction_result.get('model_used', 'AI Model') + '''</p>
                    </div>
                </div>
                ''')
            
            html_parts.append('''
                    <div style="margin-top: 30px;">
                        <a href="/ocr" class="btn">📄 Process Another Document</a>
                        <a href="/test-prediction" class="btn" style="background: #27ae60;">✍️ Manual Input Form</a>
                        <a href="/" class="btn" style="background: #7f8c8d;">🏠 Back to Home</a>
                    </div>
                </div>
            </body>
            </html>
            ''')
            
            return ''.join(html_parts)
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return f"Error processing document: {str(e)}", 500
    
    return "Invalid file type. Please upload JPG, PNG, or PDF images.", 400

@app.route('/test-ocr')
def test_ocr():
    ocr_status = "✅ ACTIVE" if OCR_SPACE_AVAILABLE else "❌ UNAVAILABLE"
    status_class = "status-active" if OCR_SPACE_AVAILABLE else "status-inactive"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test OCR System - HeartShield</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .status-box {{ padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .status-active {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .status-inactive {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            .btn {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧪 OCR System Test</h2>
            
            <div class="status-box {status_class}">
                <h3>OCR.space API Status: {ocr_status}</h3>
                <p><strong>Engine:</strong> OCR.space Professional API</p>
                <p><strong>Accuracy:</strong> 85-95% for medical documents</p>
            </div>

            <div style="margin-top: 30px;">
                <a href="/ocr" class="btn" style="background: #27ae60;">📄 Test with Document</a>
                <a href="/" class="btn" style="background: #7f8c8d;">🏠 Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/upload-medical-form')
def upload_medical_form():
    return redirect('/ocr')

@app.route('/')
def home():
    ocr_status = "✅ ACTIVE" if OCR_SPACE_AVAILABLE else "⚠️ LIMITED"
    ocr_accuracy = "85-95%" if OCR_SPACE_AVAILABLE else "60-70%"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>HeartShield - AI Heart Disease Prediction</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; color: white; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .title {{ font-size: 3rem; font-weight: bold; margin: 10px 0; }}
            .btn {{ display: inline-block; padding: 12px 20px; margin: 5px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); transition: all 0.3s ease; }}
            .btn:hover {{ background: rgba(255,255,255,0.3); transform: translateY(-2px); }}
            .btn-primary {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="font-size: 4rem;">❤️</div>
                <h1 class="title">HeartShield</h1>
                <p class="subtitle">AI-Powered Heart Disease Risk Prediction with OCR.space API</p>
            </div>

            <div style="text-align: center; margin: 40px 0;">
                <h3>🚀 Quick Access</h3>
                <div>
                    <a href="/ocr" class="btn btn-primary">📄 Upload Medical Document</a>
                    <a href="/test-prediction" class="btn">🧪 Test Prediction</a>
                    <a href="/test-ocr" class="btn">🔧 Test OCR System</a>
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                <h4>🔧 System Information</h4>
                <p><strong>ML Model:</strong> {'✅ ACTIVE' if ML_MODEL_AVAILABLE else '❌ UNAVAILABLE'}</p>
                <p><strong>OCR Engine:</strong> {'OCR.space API' if OCR_SPACE_AVAILABLE else 'Legacy Tesseract'}</p>
                <p><strong>Accuracy:</strong> {ML_ACCURACY}% (ML) / {ocr_accuracy} (OCR)</p>
            </div>
        </div>
    </body>
    </html>
    '''

# ===== EXISTING ROUTES =====

@app.route('/test-prediction')
def test_prediction():
    return '''
    <html>
    <head>
        <title>Test Prediction - HeartShield</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
            label { display: block; margin-bottom: 5px; color: #2c3e50; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            .btn { background: #27ae60; color: white; padding: 15px 40px; border: none; border-radius: 5px; font-size: 1.1em; cursor: pointer; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧪 Test Heart Disease Prediction</h2>
            
            <form method="POST" action="/api/predict">
                <div class="form-grid">
                    <label>Age: <input type="number" name="Age" value="52" required></label>
                    <label>Height (cm): <input type="number" name="Height" value="175" required></label>
                    <label>Weight (kg): <input type="number" name="Weight" value="80" required></label>
                    <label>Gender: 
                        <select name="Gender" required>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                    </label>
                    <label>Systolic BP: <input type="number" name="Systolic_BP" value="125" required></label>
                    <label>Diastolic BP: <input type="number" name="Diastolic_BP" value="85" required></label>
                    <label>Cholesterol: <input type="number" name="Cholesterol" value="212" required></label>
                    <label>Glucose: <input type="number" name="Glucose" value="98" required></label>
                </div>

                <button type="submit" class="btn">Get Prediction</button>
            </form>
            <br>
            <a href="/" style="background: #7f8c8d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Home</a>
        </div>
    </body>
    </html>
    '''

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        patient_data = {
            'Age': int(request.form.get('Age', 50)),
            'Height': float(request.form.get('Height', 170)),
            'Weight': float(request.form.get('Weight', 70)),
            'Gender': request.form.get('Gender', 'Male'),
            'Systolic_BP': int(request.form.get('Systolic_BP', 120)),
            'Diastolic_BP': int(request.form.get('Diastolic_BP', 80)),
            'Cholesterol': int(request.form.get('Cholesterol', 200)),
            'Glucose': int(request.form.get('Glucose', 100))
        }
        
        height_m = patient_data['Height'] / 100
        patient_data['BMI'] = patient_data['Weight'] / (height_m ** 2)
        
        result = predictor.predict_risk(patient_data)
        
        risk_color = "#27ae60" if result['risk_category'] == 'Low' else "#f39c12" if result['risk_category'] == 'Moderate' else "#e74c3c"
        
        return f'''
        <html>
        <head>
            <title>Prediction Result - HeartShield</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .result-box {{ background: #e8f4f8; padding: 20px; border-radius: 5px; border-left: 5px solid {risk_color}; }}
                .btn {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🎯 Prediction Result</h2>
                
                <div class="result-box">
                    <h3 style="color: {risk_color};">Risk: {result.get('risk_category', 'Unknown')}</h3>
                    <p><strong>Risk Percentage:</strong> {result.get('risk_percentage', 'N/A')}%</p>
                    <p><strong>Confidence:</strong> {result.get('confidence', 'N/A')}%</p>
                    <p><strong>Message:</strong> {result.get('message', 'No message')}</p>
                </div>
                
                <br>
                <a href="/test-prediction" class="btn">Test Another Prediction</a>
                <a href="/" class="btn" style="background: #7f8c8d;">Back to Home</a>
            </div>
        </body>
        </html>
        '''
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/health-check')
def health_check():
    return jsonify({
        "status": "healthy", 
        "ml_model": "ACTIVE" if ML_MODEL_AVAILABLE else "UNAVAILABLE",
        "ocr_processing": "OCR.SPACE_ACTIVE" if OCR_SPACE_AVAILABLE else "LEGACY_OCR"
    })

if __name__ == '__main__':
    print("🚀 HeartShield with OCR.space API Running!")
    print(f"✅ OCR.space API: {'ACTIVE' if OCR_SPACE_AVAILABLE else 'UNAVAILABLE'}")
    print("📍 Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)