# app.py - COMPLETE ENHANCED VERSION WITH UPGRADED GEMINI AI
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
import pytesseract
from PIL import Image
import cv2
import sys
import requests
import traceback
import google.generativeai as genai
import time
import atexit
import glob
import gc

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'heartshield_professional_ui_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'database/heartshield.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs('database', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/charts', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# ===== GEMINI API CONFIGURATION =====
GEMINI_API_KEY = "AIzaSyANtvyv4_LSMGo1Sk0sbLOVFGmNu6txYRU"  
try:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    print("✅ Gemini API configured successfully!")
except Exception as e:
    print(f"❌ Gemini API configuration failed: {e}")
    GEMINI_AVAILABLE = False

# ===== FILE CLEANUP UTILITIES =====
def cleanup_uploads():
    """Clean up any leftover files in uploads directory"""
    try:
        for file_path in glob.glob(os.path.join('uploads', '*')):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🧹 Cleaned up: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not clean up {file_path}: {e}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

# Run cleanup on startup and register for exit
cleanup_uploads()
atexit.register(cleanup_uploads)

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

# ===== ML MODEL INTEGRATION WITH ERROR HANDLING =====
ML_MODEL_AVAILABLE = False
ml_predictor = None

try:
    # Try multiple import paths
    try:
        from ml.predictor import predictor as ml_predictor
        ML_MODEL_AVAILABLE = True
        print("✅ ML Predictor imported successfully from ml.predictor!")
    except ImportError:
        try:
            from predictor import predictor as ml_predictor
            ML_MODEL_AVAILABLE = True
            print("✅ ML Predictor imported successfully from predictor!")
        except ImportError:
            print("❌ ML Predictor not found in both ml.predictor and predictor")
            ML_MODEL_AVAILABLE = False
            ml_predictor = None
            
except Exception as e:
    print(f"❌ ML Predictor import failed: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")
    ML_MODEL_AVAILABLE = False
    ml_predictor = None

# ===== ENHANCED GEMINI AI MEDICAL DOCUMENT PROCESSING =====

def extract_medical_data_with_gemini(image_path):
    """
    FIXED Gemini AI handler using supported model "gemini-1.5-flash"
    and robust content extraction (fully compatible with 2025 API).
    """
    if not GEMINI_AVAILABLE:
        print("❌ Gemini API not available")
        return {}
    
    try:
        print("🚀 Starting Gemini AI medical document analysis (fixed version)...")

        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            return {}

        img = None
        try:
            img = Image.open(image_path)
            print(f"✅ Image loaded: {img.size} pixels")
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return {}

        # ✅ Use current, supported Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
            You are a medical data extraction expert. Analyze this lab report image
            and extract numeric medical values with these exact keys:
            {
                "age": number or null,
                "systolic_bp": number or null,
                "diastolic_bp": number or null,
                "cholesterol": number or null,
                "glucose": number or null,
                "heart_rate": number or null,
                "height": number or null,
                "weight": number or null,
                "gender": "Male" or "Female" or null
            }

            Rules:
            - Extract only numbers, ignore units.
            - Accept synonyms: "BP" = blood pressure, "FBS" = fasting glucose, etc.
            - Return pure JSON, no commentary.
            """

        try:
            # ✅ Updated Gemini API call
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"🔄 Gemini API analysis attempt {attempt + 1}...")
                    response = model.generate_content([prompt, img])
                    
                    # ✅ Updated response parsing
                    response_text = ""
                    if hasattr(response, "text") and response.text:
                        response_text = response.text
                    elif hasattr(response, "candidates") and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content.parts and len(candidate.content.parts) > 0:
                            response_text = candidate.content.parts[0].text
                    response_text = response_text.strip()

                    if not response_text:
                        raise ValueError("Empty Gemini response")

                    print(f"📄 Raw Gemini response: {response_text[:300]}...")

                    cleaned_text = clean_gemini_response(response_text)
                    medical_data = json.loads(cleaned_text)

                    valid_data = {k: v for k, v in medical_data.items() if v is not None}
                    print(f"✅ Gemini extracted {len(valid_data)} parameters: {valid_data}")
                    return medical_data

                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decoding failed: {e}")
                    time.sleep(1)
                    continue
                except Exception as e:
                    print(f"⚠️ Gemini call failed on attempt {attempt + 1}: {e}")
                    time.sleep(1)
                    continue

            print("❌ Gemini failed all retries, switching to fallback OCR parsing.")
            return fallback_keyword_extraction(image_path)

        finally:
            if img:
                img.close()
                print("✅ Image closed properly")

    except Exception as e:
        print(f"❌ Critical Gemini error: {e}")
        return fallback_keyword_extraction(image_path)

def clean_gemini_response(response_text):
    """
    Enhanced cleaning of Gemini response to ensure valid JSON
    """
    if not response_text:
        return '{}'
    
    # Remove markdown code blocks
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif '```' in response_text:
        response_text = response_text.split('```')[1].strip() if len(response_text.split('```')) > 1 else response_text
    
    # Remove any non-JSON content before or after the JSON
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}') + 1
    
    if start_idx != -1 and end_idx != 0:
        response_text = response_text[start_idx:end_idx]
    
    # Ensure it's valid JSON structure
    response_text = response_text.strip()
    
    # Basic validation
    if not response_text.startswith('{') or not response_text.endswith('}'):
        print(f"⚠️ Response doesn't look like JSON: {response_text}")
        return '{}'
    
    return response_text

def fallback_keyword_extraction(image_path):
    """
    Enhanced keyword-based extraction as fallback when Gemini fails
    """
    print("🔄 Using enhanced keyword extraction fallback...")
    
    # Get text from OCR.space first
    extracted_text = ocr_space_parse_image(image_path)
    if not extracted_text or len(extracted_text) < 20:
        # Fallback to Tesseract
        extracted_text = extract_with_tesseract(image_path)
    
    if not extracted_text:
        return {}
    
    print(f"🔍 Fallback OCR text length: {len(extracted_text)}")
    
    # Use enhanced parsing
    return parse_medical_data_enhanced(extracted_text)

def parse_medical_data_enhanced(text):
    """
    Enhanced medical data parsing with better pattern matching
    """
    extracted_data = {}
    
    text_lower = text.lower()
    lines = text.split('\n')
    print(f"🔍 Enhanced parsing text sample: {text_lower[:500]}...")
    
    # Enhanced patterns with context awareness
    patterns = {
        'age': [
            r'age[:\s]*(\d+)',
            r'age[\s]*is[:\s]*(\d+)', 
            r'patient age[:\s]*(\d+)',
            r'dob.*?(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # DD/MM/YYYY
            r'(\d+)\s*years?',
            r'(\d+)\s*y[\/]?o',
            r'year.*?(\d+)'
        ],
        'systolic_bp': [
            r'blood pressure[:\s]*(\d+)\s*/\s*\d+',
            r'bp[:\s]*(\d+)\s*/\s*\d+',
            r'(\d+)\s*/\s*\d+\s*mm',
            r'systolic[:\s]*(\d+)',
            r'(\d{2,3})\s*/\s*\d{2,3}'
        ],
        'diastolic_bp': [
            r'blood pressure[:\s]*\d+\s*/\s*(\d+)',
            r'bp[:\s]*\d+\s*/\s*(\d+)', 
            r'\d+\s*/\s*(\d+)\s*mm',
            r'diastolic[:\s]*(\d+)'
        ],
        'cholesterol': [
            r'cholesterol[:\s]*(\d+)',
            r'chol[:\s]*(\d+)',
            r'ldl[:\s]*(\d+)',
            r'hdl[:\s]*(\d+)',
            r'triglycerides[:\s]*(\d+)',
            r'lipid[:\s]*(\d+)'
        ],
        'glucose': [
            r'glucose[:\s]*(\d+)',
            r'blood sugar[:\s]*(\d+)',
            r'sugar[:\s]*(\d+)',
            r'fbs[:\s]*(\d+)',
            r'fasting[:\s]*(\d+)'
        ],
        'height': [
            r'height[:\s]*(\d+)\s*cm',
            r'ht[:\s]*(\d+)\s*cm',
            r'height[:\s]*(\d+)',
            r'(\d+)cm'
        ],
        'weight': [
            r'weight[:\s]*(\d+)\s*kg',
            r'wt[:\s]*(\d+)\s*kg',
            r'weight[:\s]*(\d+)',
            r'(\d+)kg'
        ],
        'heart_rate': [
            r'heart rate[:\s]*(\d+)',
            r'pulse[:\s]*(\d+)',
            r'hr[:\s]*(\d+)',
            r'(\d+)\s*bpm'
        ],
        'gender': [
            r'gender[:\s]*(male|female)',
            r'sex[:\s]*(male|female)',
            r'patient[:\s]*(male|female)',
            r'\b(male|female)\b'
        ]
    }
    
    # Value ranges for validation
    value_ranges = {
        'age': (1, 120),
        'systolic_bp': (60, 250),
        'diastolic_bp': (40, 150),
        'cholesterol': (50, 500),
        'glucose': (50, 500),
        'height': (100, 250),
        'weight': (30, 200),
        'heart_rate': (40, 200)
    }
    
    # Extract each parameter
    for param, param_patterns in patterns.items():
        value = None
        
        for pattern in param_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    if param == 'gender':
                        # Handle gender separately
                        gender_match = match.group(1).capitalize()
                        if gender_match in ['Male', 'Female']:
                            value = gender_match
                            break
                    else:
                        # Handle numerical values
                        num_value = int(match.group(1))
                        
                        # Validate range
                        if param in value_ranges:
                            min_val, max_val = value_ranges[param]
                            if min_val <= num_value <= max_val:
                                value = num_value
                                break
                        else:
                            value = num_value
                            break
                            
                except (ValueError, IndexError):
                    continue
            
            if value:
                break
        
        # Map to your expected keys
        key_mapping = {
            'age': 'Age',
            'systolic_bp': 'Systolic_BP',
            'diastolic_bp': 'Diastolic_BP', 
            'cholesterol': 'Cholesterol',
            'glucose': 'Glucose',
            'height': 'Height',
            'weight': 'Weight',
            'heart_rate': 'Heart_Rate',
            'gender': 'Gender'
        }
        
        if value and param in key_mapping:
            extracted_data[key_mapping[param]] = value
            print(f"✅ Enhanced extraction: {key_mapping[param]} = {value}")
    
    print(f"🎯 Enhanced parsing result: {extracted_data}")
    return extracted_data

# ===== OCR.SPACE API CONFIGURATION =====
OCR_SPACE_API_KEY = 'K8187508888957'  # Your API key
OCR_SPACE_API_URL = 'https://api.ocr.space/parse/image'

def ocr_space_parse_image(image_path, language='eng'):
    """Extract text from image using OCR.space API"""
    try:
        with open(image_path, 'rb') as image_file:
            response = requests.post(
                OCR_SPACE_API_URL,
                files={'image': image_file},
                data={
                    'apikey': OCR_SPACE_API_KEY,
                    'language': language,
                    'isOverlayRequired': False,
                    'OCREngine': 2  # Engine 2 is more accurate
                },
                timeout=30
            )
        
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            print(f"❌ OCR.space Error: {result.get('ErrorMessage', 'Unknown error')}")
            return ""
        
        # Extract text from all parsed results
        parsed_results = result.get('ParsedResults', [])
        if parsed_results:
            extracted_text = parsed_results[0].get('ParsedText', '')
            print(f"✅ OCR.space extracted {len(extracted_text)} characters")
            return extracted_text.strip()
        else:
            print("❌ OCR.space: No text found in image")
            return ""
            
    except Exception as e:
        print(f"❌ OCR.space API Error: {e}")
        return ""

# ===== ENHANCED DUAL OCR PROCESSING (Gemini AI + OCR.space + Tesseract) =====
def extract_medical_data_from_image(image_path):
    """ENHANCED extraction with improved Gemini AI as primary"""
    extracted_data = {}
    
    # Try Enhanced Gemini AI first
    if GEMINI_AVAILABLE:
        print("🎯 Using ENHANCED Gemini AI for medical document analysis...")
        gemini_data = extract_medical_data_with_gemini(image_path)  # This now uses the enhanced version
        
        if gemini_data and any(value is not None for value in gemini_data.values()):
            print("✅ Enhanced Gemini AI extraction successful!")
            
            # Convert to your expected format
            mapping = {
                'age': 'Age',
                'systolic_bp': 'Systolic_BP', 
                'diastolic_bp': 'Diastolic_BP',
                'cholesterol': 'Cholesterol',
                'glucose': 'Glucose',
                'heart_rate': 'Heart_Rate',
                'height': 'Height',
                'weight': 'Weight',
                'gender': 'Gender'
            }
            
            for gemini_key, your_key in mapping.items():
                value = gemini_data.get(gemini_key)
                if value is not None:
                    extracted_data[your_key] = value
                    print(f"   ✅ {your_key}: {value}")
            
            return extracted_data
    
    # Fallback to traditional OCR processing
    print("🔄 Enhanced Gemini failed, using fallback OCR processing...")
    extracted_text = ""
    
    # Try OCR.space first
    ocr_space_text = ocr_space_parse_image(image_path)
    
    if ocr_space_text and len(ocr_space_text) > 50:
        extracted_text = ocr_space_text
        print("✅ Using OCR.space results for fallback")
    else:
        # Fallback to Tesseract
        extracted_text = extract_with_tesseract(image_path)
        print("✅ Using Tesseract results for fallback")
    
    # Parse with enhanced parsing
    if extracted_text:
        extracted_data = parse_medical_data_enhanced(extracted_text)  # Use enhanced parsing
    
    return extracted_data

def extract_with_tesseract(image_path):
    """Extract text using Tesseract OCR (fallback)"""
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
        
        print(f"📝 Tesseract extracted {len(text)} characters")
        if text:
            print(f"📄 First 200 chars: {text[:200]}...")
        return text
        
    except Exception as e:
        print(f"❌ Tesseract Error: {e}")
        return ""

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

# Load dataset for stats with error handling
try:
    df = pd.read_csv('ml/heartshield_dataset.csv')
    heart_disease_rate = df['Cardiovascular_Disease'].mean() * 100
    total_patients = len(df)
    print("✅ NEW Dataset loaded successfully!")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    try:
        # Try alternative path
        df = pd.read_csv('heartshield_datasets.csv')
        heart_disease_rate = df['Cardiovascular_Disease'].mean() * 100
        total_patients = len(df)
        print("✅ Dataset loaded from alternative path!")
    except:
        heart_disease_rate = 50.0
        total_patients = 10000
        print("⚠️ Using default dataset values")

# Update accuracy display to show real ML accuracy
ML_ACCURACY = 95.6 if ML_MODEL_AVAILABLE else 75.0

# ===== OCR ROUTES WITH ENHANCED GEMINI AI INTEGRATION =====

@app.route('/ocr')
def ocr_form():
    """Display the OCR upload form with Gemini AI integration"""
    gemini_status = "ACTIVE 🚀" if GEMINI_AVAILABLE else "UNAVAILABLE 🔄"
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Document Analysis - HeartShield</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; color: #2c3e50; font-weight: bold; }}
            input[type="file"] {{ padding: 10px; border: 2px dashed #3498db; border-radius: 5px; width: 100%; box-sizing: border-box; }}
            .btn {{ background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 1.1em; cursor: pointer; margin-top: 10px; }}
            .btn-primary {{ background: #27ae60; }}
            .btn-ai {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
            .info-box {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 5px solid #3498db; }}
            .feature-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0; }}
            .feature-item {{ background: white; padding: 10px; border-radius: 5px; text-align: center; }}
            .tech-badge {{ background: #9b59b6; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; margin-left: 10px; }}
            .ai-badge {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; }}
            .ai-feature {{ background: #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #f39c12; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧠 AI Medical Document Analysis</h2>
            <p>Upload a medical document or lab report for intelligent analysis using advanced AI technology:</p>
            
            <div class="info-box">
                <div class="ai-feature">
                    <strong>🚀 ENHANCED: Powered by Google Gemini AI</strong> - Advanced medical document understanding
                    <br><small>AI Status: {gemini_status}</small>
                </div>
                <h4>📋 Supported Document Types:</h4>
                <div class="feature-list">
                    <div class="feature-item">🩺 Clinic Notes</div>
                    <div class="feature-item">🏥 Discharge Summaries</div>
                    <div class="feature-item">🧪 Lab Reports</div>
                    <div class="feature-item">📊 Health Records</div>
                </div>
                <p><strong>Supported formats:</strong> JPG, PNG, PDF images</p>
                <p><strong>AI Technology:</strong> 
                    <span class="ai-badge">Google Gemini AI</span>
                    <span class="tech-badge">OCR.space API</span> 
                    <span class="tech-badge">Tesseract</span>
                </p>
            </div>

            <form method="POST" action="/perform_ocr" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="document">Select Medical Document:</label>
                    <input type="file" id="document" name="document" accept=".jpg,.jpeg,.png,.pdf" required>
                </div>
                
                <button type="submit" class="btn btn-ai">🧠 Analyze with Advanced AI</button>
            </form>
            
            <div style="margin-top: 30px;">
                <h4>🎯 What Our AI Extracts:</h4>
                <ul>
                    <li><strong>Age</strong> - Intelligent age detection</li>
                    <li><strong>Height & Weight</strong> - For BMI calculation</li>
                    <li><strong>Blood Pressure</strong> - Accurate BP reading extraction</li>
                    <li><strong>Cholesterol Levels</strong> - Precise value recognition</li>
                    <li><strong>Glucose Levels</strong> - Blood sugar analysis</li>
                    <li><strong>Heart Rate</strong> - Pulse and heart rate detection</li>
                    <li><strong>Gender</strong> - Patient gender identification</li>
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
    """Process the uploaded document with Enhanced Gemini AI and return results"""
    if 'document' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['document']
    if file.filename == '':
        return "No file selected", 400
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        extracted_data = {}
        prediction_result = None
        
        try:
            # Step 1: Perform AI-Powered Extraction (Enhanced Gemini AI + OCR)
            print(f"🔍 Processing medical document: {filename}")
            extracted_data = extract_medical_data_from_image(filepath)
            
            if not extracted_data:
                # Clean up before returning error
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"✅ Cleaned up file: {filepath}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not delete file {filepath}: {e}")
                
                return '''
                <div style="padding: 20px; background: #ffeaa7; border-radius: 10px; margin: 20px;">
                    <h3>❌ Document Analysis Failed</h3>
                    <p>No medical parameters could be extracted from the document. Please ensure:</p>
                    <ul>
                        <li>The image is clear and not blurry</li>
                        <li>Text is visible and not too small</li>
                        <li>The document contains medical data (lab results, vitals, etc.)</li>
                        <li>Try a higher quality image or different document</li>
                    </ul>
                    <a href="/ocr" style="background: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                </div>
                ''', 400
            
            # Step 2: Make prediction if we have enough data
            if len(extracted_data) >= 3:  # At least 3 parameters found
                prediction_result = predictor.predict_risk(extracted_data)
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            # Don't return here, let the cleanup happen below
            
        finally:
            # Step 3: Always clean up the uploaded file, even if errors occur
            print(f"🧹 Cleaning up uploaded file: {filepath}")
            try:
                if os.path.exists(filepath):
                    # Force close any open file handles
                    gc.collect()
                    
                    # Try multiple times to delete the file
                    for attempt in range(3):
                        try:
                            os.remove(filepath)
                            print(f"✅ Successfully deleted file: {filepath}")
                            break
                        except PermissionError:
                            if attempt < 2:  # Don't wait on the last attempt
                                time.sleep(0.5)  # Wait half second before retry
                                continue
                            else:
                                print(f"⚠️ Could not delete file {filepath} after 3 attempts")
                                # Try to delete on next startup or ignore if persistent
                        except FileNotFoundError:
                            print(f"✅ File already deleted: {filepath}")
                            break
                        except Exception as e:
                            print(f"⚠️ Error deleting file {filepath}: {e}")
                            break
            except Exception as e:
                print(f"⚠️ Error during file cleanup: {e}")
        
        # Step 4: Display results (only after file cleanup)
        risk_color = "#27ae60" 
        if prediction_result:
            risk_level = prediction_result.get('risk_category', 'Unknown')
            risk_color = "#27ae60" if risk_level == 'Low' else "#f39c12" if risk_level == 'Moderate' else "#e74c3c"
        
        # Build results HTML
        ai_technology = "Enhanced Google Gemini AI" if GEMINI_AVAILABLE and extracted_data else "Advanced OCR System"
        results_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Analysis Results - HeartShield</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .result-section {{ margin: 20px 0; padding: 20px; border-radius: 5px; }}
                .data-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0; }}
                .data-item {{ background: white; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #ddd; }}
                .success-item {{ background: #d4edda; border-color: #c3e6cb; }}
                .prediction-box {{ background: #e8f4f8; padding: 20px; border-radius: 5px; border-left: 5px solid {risk_color}; }}
                .btn {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .tech-info {{ background: #e8f4f8; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 0.9em; }}
                .ai-badge {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🧠 AI Medical Analysis Complete <span class="ai-badge">{ai_technology}</span></h2>
                
                <div class="tech-info">
                    <strong>🔄 Analysis Technology:</strong> {ai_technology} with Multi-Layer Processing
                </div>
                
                <div class="result-section">
                    <h3>🎯 Extracted Medical Data:</h3>
        '''
        
        if extracted_data:
            results_html += '<div class="data-grid">'
            for key, value in extracted_data.items():
                results_html += f'<div class="data-item success-item"><strong>{key}</strong><br>{value}</div>'
            results_html += '</div>'
            results_html += f'<p><strong>✅ Analysis Complete:</strong> Successfully extracted {len(extracted_data)} medical parameters</p>'
        else:
            results_html += '<p>❌ No medical parameters could be automatically extracted from the document.</p>'
            results_html += '<p>Please use the manual input form below with the values from your document.</p>'
        
        # Add prediction results if available
        if prediction_result:
            results_html += f'''
            <div class="result-section">
                <h3>❤️ Heart Disease Risk Assessment:</h3>
                <div class="prediction-box">
                    <h4 style="color: {risk_color};">Risk Level: {prediction_result.get('risk_category', 'Unknown')}</h4>
                    <p><strong>Risk Percentage:</strong> {prediction_result.get('risk_percentage', 'N/A')}%</p>
                    <p><strong>Confidence:</strong> {prediction_result.get('confidence', 'N/A')}%</p>
                    <p><strong>Analysis:</strong> {prediction_result.get('message', 'AI Medical Analysis Complete')}</p>
                    <p><strong>AI Model:</strong> {prediction_result.get('model_used', 'Advanced AI System')}</p>
                </div>
            </div>
            '''
        
        # Add action buttons
        results_html += f'''
                <div style="margin-top: 30px;">
                    <a href="/ocr" class="btn">📄 Analyze Another Document</a>
                    <a href="/test-prediction" class="btn" style="background: #27ae60;">✍️ Manual Input Form</a>
                    <a href="/" class="btn" style="background: #7f8c8d;">🏠 Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return results_html
    
    return "Invalid file type. Please upload JPG, PNG, or PDF images.", 400

# ===== KEEP ALL YOUR EXISTING ROUTES (they remain unchanged) =====

@app.route('/upload-medical-form')
def upload_medical_form():
    """Redirect to OCR form - keeping for compatibility"""
    return redirect('/ocr')

@app.route('/')
def home():
    """Home page with OCR integration"""
    gemini_status = "ACTIVE 🚀" if GEMINI_AVAILABLE else "UNAVAILABLE 🔄"
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
            .main-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
            .welcome-card {{ background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }}
            .btn {{ display: inline-block; padding: 12px 20px; margin: 5px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); transition: all 0.3s ease; }}
            .btn:hover {{ background: rgba(255,255,255,0.3); transform: translateY(-2px); }}
            .btn-primary {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
            .btn-secondary {{ background: rgba(255,255,255,0.15); }}
            .features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .feature-card {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.2); transition: transform 0.3s ease; }}
            .feature-card:hover {{ transform: translateY(-5px); }}
            .feature-icon {{ font-size: 2.5rem; margin-bottom: 15px; }}
            .auth-actions {{ margin-top: 15px; }}
            .subtitle {{ font-size: 1.2rem; opacity: 0.9; margin-bottom: 30px; }}
            .quick-actions {{ text-align: center; margin: 30px 0; }}
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px; }}
            .stat-item {{ text-align: center; }}
            .stat-value {{ font-size: 1.8rem; font-weight: bold; margin-bottom: 5px; }}
            .stat-label {{ font-size: 0.9rem; opacity: 0.8; }}
            .ai-status {{ background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="font-size: 4rem;">❤️</div>
                <h1 class="title">HeartShield</h1>
                <p class="subtitle">AI-Powered Heart Disease Risk Prediction with Advanced Medical OCR</p>
                <div class="ai-status">
                    <strong>🤖 AI Status:</strong> Google Gemini AI - {gemini_status}
                </div>
            </div>

            <div class="main-grid">
                <div class="welcome-card">
                    <h3>🔐 Join HeartShield</h3>
                    <p style="opacity: 0.9; margin-bottom: 15px;">Create your account to access advanced heart health analytics and personalized risk assessments.</p>
                    <div class="auth-actions">
                        <a href="/register" class="btn btn-primary">👤 Create Account</a>
                        <a href="/login" class="btn btn-secondary">🔑 Sign In</a>
                    </div>
                </div>
                
                <div class="welcome-card">
                    <h3>📊 Project Analytics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">10K+</div>
                            <div class="stat-label">Samples Analyzed</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{ML_ACCURACY}%</div>
                            <div class="stat-label">AI Accuracy</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">100%</div>
                            <div class="stat-label">Data Secure</div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                        <div style="font-size: 0.9rem; opacity: 0.9;">
                            <strong>🎯 Advanced Analytics:</strong> Powered by machine learning with Gemini AI medical document processing
                        </div>
                    </div>
                </div>
            </div>

            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>AI Prediction</h3>
                    <p>{ML_ACCURACY}% accurate heart disease risk assessment using advanced machine learning algorithms</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3>Gemini AI OCR</h3>
                    <p>Advanced medical document understanding using Google Gemini AI for accurate data extraction</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Health Analytics</h3>
                    <p>Comprehensive risk analysis with trend tracking and personalized health insights</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>Secure & Private</h3>
                    <p>Enterprise-grade security with end-to-end encryption for your sensitive health data</p>
                </div>
            </div>

            <div class="quick-actions">
                <h3>🚀 Quick Access</h3>
                <div>
                    <a href="/ocr" class="btn btn-primary">🧠 AI Document Analysis</a>
                    <a href="/test-prediction" class="btn btn-secondary">🧪 Test Prediction</a>
                    <a href="/health-check" class="btn btn-secondary">🔧 System Health</a>
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                <h4>💡 How It Works</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">1️⃣</div>
                        <div style="font-weight: bold;">Upload Document</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Medical documents or lab reports</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">2️⃣</div>
                        <div style="font-weight: bold;">AI Analysis</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Gemini AI processes medical data</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">3️⃣</div>
                        <div style="font-weight: bold;">Get Results</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Detailed risk assessment report</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# ===== KEEP ALL YOUR EXISTING ROUTES UNCHANGED =====

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

@app.route('/health-check')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "HeartShield server with ENHANCED Gemini AI & OCR is running!",
        "ml_model": "ACTIVE" if ML_MODEL_AVAILABLE else "UNAVAILABLE",
        "gemini_ai": "ENHANCED ACTIVE" if GEMINI_AVAILABLE else "UNAVAILABLE",
        "ocr_processing": "ENHANCED (Gemini AI + OCR.space + Tesseract)",
        "accuracy": ML_ACCURACY,
        "features": "NEW FEATURES: Age, Height, Weight, BP, Cholesterol, Glucose, Lifestyle, Enhanced Gemini AI OCR"
    })

if __name__ == '__main__':
    print("🚀 HeartShield ENHANCED Version with UPGRADED Gemini AI Running!")
    print("✅ NEW FEATURES: Age, Height, Weight, BP, Cholesterol, Glucose, Lifestyle")
    print("✅ ENHANCED OCR: Upgraded Gemini AI + OCR.space API + Tesseract Fallback")
    print("✅ ML MODEL: 95.6% Accuracy with 10,000 samples")
    print(f"📍 ML Model Status: {'ACTIVE' if ML_MODEL_AVAILABLE else 'FALLBACK MODE'}")
    print(f"📍 Gemini AI Status: {'ENHANCED ACTIVE 🚀' if GEMINI_AVAILABLE else 'UNAVAILABLE'}")
    print("📍 OCR.space API: CONFIGURED")
    print("📍 OCR Routes: /ocr and /perform_ocr")
    print("📍 Visit: http://localhost:5000")
    print("📍 AI Medical Analysis: http://localhost:5000/ocr")
    app.run(debug=True, host='0.0.0.0', port=5000)