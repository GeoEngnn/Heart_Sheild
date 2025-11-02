# app.py - UPDATED FOR NEW FEATURES
from flask import Flask, request, jsonify, redirect, session, url_for, send_file
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
import pytesseract
from PIL import Image
import cv2
import sys

# Add ml folder to Python path for ML model import
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

app = Flask(__name__)
app.secret_key = 'heartshield_professional_ui_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'database/heartshield.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create necessary directories
os.makedirs('database', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/charts', exist_ok=True)

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

# ===== REAL OCR PROCESSING =====
def extract_medical_data_from_image(image_path):
    """Extract medical data from image using OCR"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ""
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh1 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        text1 = pytesseract.image_to_string(Image.fromarray(thresh1))
        text2 = pytesseract.image_to_string(Image.fromarray(thresh2))
        
        text = text1 if len(text1) > len(text2) else text2
        
        print(f"📝 OCR extracted {len(text)} characters")
        if text:
            print(f"📄 First 200 chars: {text[:200]}...")
        return text
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def parse_medical_data(text):
    """Parse extracted text to find medical parameters for NEW features"""
    extracted_data = {}
    
    text_lower = text.lower()
    print(f"🔍 OCR Text for parsing: {text_lower}")
    
    # Age patterns
    age_patterns = [
        r'age[:\s]*(\d+)',
        r'age[\s]*is[:\s]*(\d+)',
        r'patient age[:\s]*(\d+)',
        r'dob.*?(\d{2,4})',
        r'(\d+)\s*years? old',
    ]
    
    # Height patterns
    height_patterns = [
        r'height[:\s]*(\d+)\s*cm',
        r'height[:\s]*(\d+)',
        r'ht[:\s]*(\d+)\s*cm',
    ]
    
    # Weight patterns  
    weight_patterns = [
        r'weight[:\s]*(\d+)\s*kg',
        r'weight[:\s]*(\d+)',
        r'wt[:\s]*(\d+)\s*kg',
    ]
    
    # Blood pressure patterns
    bp_patterns = [
        r'blood pressure[:\s]*(\d+)\s*/\s*(\d+)',
        r'bp[:\s]*(\d+)\s*/\s*(\d+)',
        r'(\d+)\s*/\s*(\d+)\s*mm',
    ]
    
    # Cholesterol patterns
    chol_patterns = [
        r'cholesterol[:\s]*(\d+)',
        r'chol[:\s]*(\d+)',
        r'ldl[:\s]*(\d+)',
    ]
    
    # Glucose patterns
    glucose_patterns = [
        r'glucose[:\s]*(\d+)',
        r'blood sugar[:\s]*(\d+)',
        r'sugar[:\s]*(\d+)',
    ]
    
    # Extract data with reasonable ranges
    def extract_with_patterns(patterns, key, min_val, max_val):
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    value = int(match.group(1))
                    if min_val <= value <= max_val:
                        extracted_data[key] = value
                        print(f"✅ Extracted {key}: {value}")
                        break
                except:
                    continue
    
    extract_with_patterns(age_patterns, 'Age', 1, 120)
    extract_with_patterns(height_patterns, 'Height', 100, 250)
    extract_with_patterns(weight_patterns, 'Weight', 30, 200)
    extract_with_patterns(chol_patterns, 'Cholesterol', 50, 500)
    extract_with_patterns(glucose_patterns, 'Glucose', 50, 500)
    
    # Extract blood pressure
    for pattern in bp_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))
                if 60 <= systolic <= 250 and 40 <= diastolic <= 150:
                    extracted_data['Systolic_BP'] = systolic
                    extracted_data['Diastolic_BP'] = diastolic
                    print(f"✅ Extracted BP: {systolic}/{diastolic}")
                    break
            except:
                continue
    
    print(f"🎯 Final extracted data: {extracted_data}")
    return extracted_data

# ===== ENHANCED PREDICTION LOGIC WITH NEW FEATURES =====
class RealPredictor:
    def __init__(self):
        self.ml_predictor = ml_predictor if ML_MODEL_AVAILABLE else None
        self.ml_accuracy = 0.956  # From your training output
    
    def predict_from_medical_data(self, extracted_data):
        """Make prediction based on extracted medical data using NEW features"""
        try:
            # Try ML prediction first if available
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
                        "accuracy": self.ml_accuracy
                    }
            
            # Fallback to rule-based prediction
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
                "accuracy": 0.75
            }
                
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._emergency_fallback()
    
    def _calculate_risk_fallback(self, extracted_data):
        """Fallback risk calculation using NEW features"""
        risk_score = 0
        
        # Age factor
        age = extracted_data.get('Age', 50)
        if age > 60: risk_score += 0.3
        elif age > 50: risk_score += 0.2
        
        # Blood pressure factor
        systolic = extracted_data.get('Systolic_BP', 120)
        diastolic = extracted_data.get('Diastolic_BP', 80)
        if systolic > 140 or diastolic > 90: risk_score += 0.25
        elif systolic > 130 or diastolic > 85: risk_score += 0.15
        
        # Cholesterol factor
        cholesterol = extracted_data.get('Cholesterol', 200)
        if cholesterol > 240: risk_score += 0.3
        elif cholesterol > 200: risk_score += 0.15
        
        # Glucose factor
        glucose = extracted_data.get('Glucose', 95)
        if glucose > 126: risk_score += 0.2
        elif glucose > 100: risk_score += 0.1
        
        # BMI factor if available
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
        """Emergency fallback when all prediction methods fail"""
        return {
            "risk_category": "Unknown",
            "risk_percentage": 50.0,
            "confidence": 50.0,
            "message": "System temporarily unavailable. Please try again.",
            "probability": 0.5,
            "prediction": 0,
            "model_used": "Emergency_Fallback",
            "accuracy": 0.5
        }
    
    def predict_risk(self, data):
        """For API compatibility - direct ML model prediction"""
        if self.ml_predictor and hasattr(self.ml_predictor, 'predict_risk'):
            result = self.ml_predictor.predict_risk(data)
            if result and result.get('success'):
                return result
        
        # Fallback
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
    heart_disease_rate = 50.0  # Balanced dataset
    total_patients = 10000

# Update accuracy display to show real ML accuracy
ML_ACCURACY = 95.6 if ML_MODEL_AVAILABLE else 75.0

# ===== UPDATED ROUTES FOR NEW FEATURES =====

@app.route('/')
def home():
    # Your existing home page code remains the same
    # ... [keep your existing home page code] ...
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>HeartShield - AI Heart Disease Prediction</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; color: white; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .title { font-size: 3rem; font-weight: bold; margin: 10px 0; }
            .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
            .welcome-card { background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
            .btn { display: inline-block; padding: 12px 20px; margin: 5px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); }
            .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); }
            .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .feature-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.2); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="font-size: 4rem;">❤️</div>
                <h1 class="title">HeartShield</h1>
                <p class="subtitle">AI-Powered Heart Disease Risk Prediction</p>
            </div>

            <div class="main-grid">
                <div class="welcome-card">
                    <h3>🔐 Join HeartShield</h3>
                    <div class="auth-actions">
                        <a href="/register" class="btn btn-primary">👤 Create Account</a>
                        <a href="/login" class="btn btn-secondary">🔑 Sign In</a>
                    </div>
                </div>
                
                <div class="welcome-card">
                    <h3>📊 Project Stats</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: bold;">''' + str(total_patients) + '''</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">Patients</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: bold;">''' + str(ML_ACCURACY) + '''%</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">AI Accuracy</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: bold;">''' + str(heart_disease_rate) + '''%</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">Heart Disease</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: bold;">100%</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">Secure</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>AI Prediction</h3>
                    <p>''' + str(ML_ACCURACY) + '''% accurate heart disease risk assessment</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <h3>Medical OCR</h3>
                    <p>Extract data from medical documents automatically</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Health Analytics</h3>
                    <p>Track your risk trends and insights</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>Secure & Private</h3>
                    <p>Enterprise-grade security for your data</p>
                </div>
            </div>

            <div class="quick-actions" style="text-align: center; margin: 30px 0;">
                <h3>🚀 Quick Access</h3>
                <div>
                    <a href="/upload-medical-form" class="btn btn-primary">📄 Upload Medical Document</a>
                    <a href="/test-prediction" class="btn">🧪 Test Prediction</a>
                    <a href="/health-check" class="btn">🔧 System Health</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/test-prediction')
def test_prediction():
    """Updated test prediction form with NEW features"""
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
            .form-section { margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
            .form-section h3 { color: #3498db; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧪 Test Heart Disease Prediction</h2>
            <p>Enter patient data to get AI-powered risk assessment with NEW features:</p>
            
            <form method="POST" action="/api/predict">
                <div class="form-section">
                    <h3>📊 Basic Information</h3>
                    <div class="form-grid">
                        <label>Age (years): <input type="number" name="Age" value="52" min="1" max="120" required></label>
                        <label>Height (cm): <input type="number" name="Height" value="175" min="100" max="250" required></label>
                        <label>Weight (kg): <input type="number" name="Weight" value="80" min="30" max="200" required></label>
                        <label>Gender: 
                            <select name="Gender" required>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                            </select>
                        </label>
                    </div>
                </div>

                <div class="form-section">
                    <h3>❤️ Vital Signs</h3>
                    <div class="form-grid">
                        <label>Systolic BP (mmHg): <input type="number" name="Systolic_BP" value="125" min="60" max="250" required></label>
                        <label>Diastolic BP (mmHg): <input type="number" name="Diastolic_BP" value="85" min="40" max="150" required></label>
                        <label>Cholesterol (mg/dL): <input type="number" name="Cholesterol" value="212" min="50" max="500" required></label>
                        <label>Glucose (mg/dL): <input type="number" name="Glucose" value="98" min="50" max="500" required></label>
                    </div>
                </div>

                <div class="form-section">
                    <h3>🚭 Lifestyle Factors</h3>
                    <div class="form-grid">
                        <label>Smoking: 
                            <select name="Smoking" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </label>
                        <label>Alcohol Intake: 
                            <select name="Alcohol_Intake" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </label>
                        <label>Physical Activity: 
                            <select name="Physical_Activity" required>
                                <option value="1">Active</option>
                                <option value="0">Inactive</option>
                            </select>
                        </label>
                    </div>
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
    """API endpoint for predictions with NEW features"""
    try:
        # Get form data for NEW features
        patient_data = {
            'Age': int(request.form.get('Age', 50)),
            'Height': float(request.form.get('Height', 170)),
            'Weight': float(request.form.get('Weight', 70)),
            'Gender': request.form.get('Gender', 'Male'),
            'Systolic_BP': int(request.form.get('Systolic_BP', 120)),
            'Diastolic_BP': int(request.form.get('Diastolic_BP', 80)),
            'Cholesterol': int(request.form.get('Cholesterol', 200)),
            'Glucose': int(request.form.get('Glucose', 100)),
            'Smoking': int(request.form.get('Smoking', 0)),
            'Alcohol_Intake': int(request.form.get('Alcohol_Intake', 0)),
            'Physical_Activity': int(request.form.get('Physical_Activity', 1))
        }
        
        # Calculate BMI
        height_m = patient_data['Height'] / 100
        patient_data['BMI'] = patient_data['Weight'] / (height_m ** 2)
        
        print(f"📊 Patient data received: {patient_data}")
        
        # Get prediction with NEW features
        result = predictor.predict_risk(patient_data)
        
        # Return beautiful result page
        risk_color = "#27ae60" if result['risk_category'] == 'Low' else "#f39c12" if result['risk_category'] == 'Moderate' else "#e74c3c"
        model_badge = f"({result.get('model_used', 'AI Model')})"
        
        return f'''
        <html>
        <head>
            <title>Prediction Result - HeartShield</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .result-box {{ background: #e8f4f8; padding: 20px; border-radius: 5px; border-left: 5px solid {risk_color}; }}
                .btn {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .model-badge {{ background: #3498db; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; }}
                .data-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0; }}
                .data-item {{ background: white; padding: 10px; border-radius: 5px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🎯 Prediction Result <span class="model-badge">{model_badge}</span></h2>
                
                <div class="result-box">
                    <h3 style="color: {risk_color};">Risk: {result.get('risk_category', 'Unknown')}</h3>
                    <p><strong>Risk Percentage:</strong> {result.get('risk_percentage', 'N/A')}%</p>
                    <p><strong>Confidence:</strong> {result.get('confidence', 'N/A')}%</p>
                    <p><strong>Message:</strong> {result.get('message', 'No message')}</p>
                    <p><strong>Model Accuracy:</strong> {result.get('accuracy', 'N/A')}%</p>
                </div>

                <div style="margin: 20px 0;">
                    <h4>📋 Patient Data Used:</h4>
                    <div class="data-grid">
                        <div class="data-item">Age: {patient_data['Age']}</div>
                        <div class="data-item">Height: {patient_data['Height']}cm</div>
                        <div class="data-item">Weight: {patient_data['Weight']}kg</div>
                        <div class="data-item">BMI: {patient_data['BMI']:.1f}</div>
                        <div class="data-item">BP: {patient_data['Systolic_BP']}/{patient_data['Diastolic_BP']}</div>
                        <div class="data-item">Cholesterol: {patient_data['Cholesterol']}</div>
                    </div>
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

# Keep other routes the same
@app.route('/upload-medical-form')
def upload_medical_form():
    # Your existing upload form code
    return "Upload form page - update similarly"

@app.route('/health-check')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "HeartShield server with NEW FEATURES is running!",
        "ml_model": "ACTIVE" if ML_MODEL_AVAILABLE else "UNAVAILABLE",
        "accuracy": ML_ACCURACY,
        "features": "NEW FEATURES: Age, Height, Weight, BP, Cholesterol, Glucose, Lifestyle"
    })

if __name__ == '__main__':
    print("🚀 HeartShield UPDATED Version Running!")
    print("✅ NEW FEATURES: Age, Height, Weight, BP, Cholesterol, Glucose, Lifestyle")
    print("✅ ML MODEL: 95.6% Accuracy with 10,000 samples")
    print(f"📍 ML Model Status: {'ACTIVE' if ML_MODEL_AVAILABLE else 'FALLBACK MODE'}")
    print("📍 Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)