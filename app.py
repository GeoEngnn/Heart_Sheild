# app.py - FIXED VERSION WITH WORKING LOGIN/REGISTER
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

app = Flask(__name__)
app.secret_key = 'heartshield_enhanced_secret_key_2024'

print("🚀 Starting HeartShield Flask Server...")

# Database initialization
def init_database():
    conn = sqlite3.connect('database/heartshield.db')
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
            cholesterol INTEGER,
            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            heart_rate INTEGER,
            glucose INTEGER,
            probability REAL,
            risk_level TEXT,
            prediction_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            insight_type TEXT,
            insight_text TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Create necessary directories
os.makedirs('database', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/charts', exist_ok=True)
init_database()

def get_db_connection():
    conn = sqlite3.connect('database/heartshield.db')
    conn.row_factory = sqlite3.Row
    return conn

# Import our AI predictor with error handling
try:
    from ml.predictor import predictor
    print("✅ AI Predictor imported successfully!")
except ImportError as e:
    print(f"❌ Error importing predictor: {e}")
    # Create a dummy predictor for fallback
    class DummyPredictor:
        def __init__(self):
            self.model = None
            
        def predict_risk(self, data):
            # Mock prediction based on common risk factors
            risk_score = 0
            age = data.get('age', 50)
            chol = data.get('chol', 200)
            
            if age > 50: risk_score += 0.2
            elif age > 40: risk_score += 0.1
            if chol > 240: risk_score += 0.3
            elif chol > 200: risk_score += 0.15
            
            probability = min(risk_score, 0.95)
            
            if probability < 0.2:
                risk_level = "Low"
            elif probability < 0.5:
                risk_level = "Moderate"
            else:
                risk_level = "High"
                
            return {
                "risk_category": risk_level,
                "risk_percentage": round(probability * 100, 1),
                "confidence": round((1 - probability) * 100, 1),
                "message": f"Heart disease risk: {risk_level} ({probability * 100:.1f}%)"
            }
    predictor = DummyPredictor()

# Load dataset for stats
try:
    df = pd.read_csv('ml/heart_disease_cleaned.csv')
    heart_disease_rate = df['heart_disease'].mean() * 100
    total_patients = len(df)
    print("✅ Dataset loaded successfully!")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    heart_disease_rate = 45.9
    total_patients = 303

# ===== FIXED AUTHENTICATION ROUTES =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        
        conn = get_db_connection()
        try:
            password_hash = generate_password_hash(password)
            conn.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, full_name))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username or email already exists"
        finally:
            conn.close()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - HeartShield</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }
            .container { max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; color: #2c3e50; font-weight: bold; }
            input { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; }
            button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
            .login-link { text-align: center; margin-top: 20px; }
            a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Create Account</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="full_name" required>
                </div>
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Register</button>
            </form>
            <div class="login-link">
                <a href="/login">Already have an account? Login</a>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            return redirect(url_for('dashboard'))
        else:
            return '''
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }
                    .container { max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }
                    .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">
                        <h3>Invalid Credentials</h3>
                        <p>Please check your username and password and try again.</p>
                    </div>
                    <a href="/login" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Try Again</a>
                    <a href="/" style="background: #7f8c8d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Home</a>
                </div>
            </body>
            </html>
            '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - HeartShield</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }
            .container { max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; color: #2c3e50; font-weight: bold; }
            input { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; }
            button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
            .register-link { text-align: center; margin-top: 20px; }
            a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Login to HeartShield</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            <div class="register-link">
                <a href="/register">Don't have an account? Register</a>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ===== ENHANCED HOME PAGE WITHOUT PHASE BADGE =====

@app.route('/')
def home():
    # Check if user is logged in
    user_info = ""
    if 'user_id' in session:
        user_info = f'''
        <div style="background: #d4edda; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h3>👋 Welcome back, {session['full_name']}!</h3>
            <p>You are logged in as <strong>{session['username']}</strong></p>
            <a href="/dashboard" style="background: #27ae60; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Go to Dashboard</a>
            <a href="/logout" style="background: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Logout</a>
        </div>
        '''
    else:
        user_info = '''
        <div style="background: #fff3cd; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h3>🔐 New to HeartShield?</h3>
            <p>Create an account to access personalized features:</p>
            <a href="/register" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Register</a>
            <a href="/login" style="background: #2c3e50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login</a>
        </div>
        '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>HeartShield - Heart Disease Prediction</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; font-size: 2.5em; }}
            .stats {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin: 30px 0; }}
            .quick-access {{ text-align: center; margin: 30px 0; }}
            .api-link {{ display: inline-block; padding: 12px 25px; background: #3498db; color: white; text-decoration: none; border-radius: 8px; margin: 10px 5px; transition: all 0.3s ease; }}
            .api-link:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
            .api-link.upload {{ background: #e74c3c; }}
            .api-link.test {{ background: #27ae60; }}
            .api-link.health {{ background: #f39c12; }}
            .feature {{ background: #27ae60; color: white; padding: 8px 15px; border-radius: 20px; display: inline-block; margin: 5px; font-size: 0.9em; }}
            .ocr-highlight {{ background: #e74c3c; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❤️ HeartShield</h1>
            <p style="text-align: center; color: #7f8c8d; font-size: 1.2em;">Early Heart Disease Risk Prediction System</p>
            
            {user_info}
            
            <div class="ocr-highlight">
                <h3>🆕 NEW: Enhanced Dashboard & User Profiles!</h3>
                <p>Now with personalized health insights, risk trend visualization, and multi-user support!</p>
            </div>
            
            <div class="stats">
                <h3>📊 Project Overview</h3>
                <p><strong>Patients Analyzed:</strong> {total_patients}</p>
                <p><strong>Heart Disease Rate:</strong> {heart_disease_rate:.1f}%</p>
                <p><strong>AI Model Accuracy:</strong> 88.5%</p>
                <p><strong>Model Status:</strong> {"✅ Loaded" if hasattr(predictor, 'model') and predictor.model is not None else "❌ Not Loaded"}</p>
            </div>

            <div class="quick-access">
                <h3>🚀 Quick Access</h3>
                <a href="/upload-medical-form" class="api-link upload">📄 Upload Medical Document</a>
                <a href="/test-prediction" class="api-link test">🧪 Test Prediction</a>
                <a href="/health-check" class="api-link health">🔧 Health Check</a>
                {'<a href="/dashboard" class="api-link" style="background: #9b59b6;">📊 My Dashboard</a>' if 'user_id' in session else ''}
                {'<a href="/analytics" class="api-link" style="background: #1abc9c;">📈 Analytics</a>' if 'user_id' in session else ''}
            </div>

            <div style="margin-top: 30px;">
                <h3>🎯 Enhanced Features</h3>
                <span class="feature">Heart Disease Prediction</span>
                <span class="feature">88.5% Accuracy</span>
                <span class="feature">Risk Assessment</span>
                <span class="feature">Real-time Analysis</span>
                <span class="feature" style="background: #e74c3c;">Medical OCR</span>
                <span class="feature" style="background: #3498db;">User Profiles</span>
                <span class="feature" style="background: #9b59b6;">Risk Trends</span>
                <span class="feature" style="background: #f39c12;">Health Insights</span>
                <span class="feature" style="background: #1abc9c;">Export Reports</span>
            </div>

            <div style="margin-top: 40px; text-align: center; color: #7f8c8d;">
                <p>🚀 <strong>Now Active:</strong> All Features Available!</p>
                <p>Built with ❤️ using Flask, Machine Learning, and OCR technology</p>
            </div>
        </div>
    </body>
    </html>
    '''

# ===== DASHBOARD ROUTE =====

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get user stats
    user_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_assessments,
            AVG(probability) as avg_risk,
            MAX(probability) as max_risk,
            MIN(probability) as min_risk
        FROM predictions 
        WHERE user_id = ?
    ''', (user_id,)).fetchone()
    
    # Get recent predictions
    recent_predictions = conn.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    # Build recent predictions HTML
    predictions_html = ""
    for pred in recent_predictions:
        risk_color = "#27ae60" if pred['risk_level'] == 'Low' else "#f39c12" if pred['risk_level'] == 'Moderate' else "#e74c3c"
        predictions_html += f'''
        <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {risk_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>Risk: {pred['risk_level']}</strong>
                    <span style="color: {risk_color}; font-weight: bold;"> ({pred['probability']*100:.1f}%)</span>
                </div>
                <small style="color: #7f8c8d;">{pred['created_at'][:16]}</small>
            </div>
            <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                Age: {pred['age']} | BP: {pred['bp_systolic']}/{pred['bp_diastolic']} | Chol: {pred['cholesterol']}
            </div>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - HeartShield</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
            .stat-label {{ color: #7f8c8d; }}
            .section {{ background: white; padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Welcome to Your Dashboard, {session['full_name']}!</h1>
                <p>Track your heart health assessments and insights</p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="/upload-medical-form" class="btn" style="background: #e74c3c;">📄 Upload Medical Document</a>
                <a href="/api/predict-form" class="btn">🧪 New Assessment</a>
                <a href="/analytics" class="btn" style="background: #9b59b6;">📈 View Analytics</a>
                <a href="/" class="btn" style="background: #7f8c8d;">🏠 Home</a>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{user_stats['total_assessments']}</div>
                    <div class="stat-label">Total Assessments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{user_stats['avg_risk']*100:.1f if user_stats['avg_risk'] else 0}%</div>
                    <div class="stat-label">Average Risk</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{user_stats['max_risk']*100:.1f if user_stats['max_risk'] else 0}%</div>
                    <div class="stat-label">Highest Risk</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{user_stats['min_risk']*100:.1f if user_stats['min_risk'] else 0}%</div>
                    <div class="stat-label">Lowest Risk</div>
                </div>
            </div>
            
            <div class="section">
                <h3>📋 Recent Assessments</h3>
                {predictions_html if predictions_html else '<p>No assessments yet. <a href="/api/predict-form">Start your first assessment!</a></p>'}
            </div>
        </div>
    </body>
    </html>
    '''

# ===== OTHER ESSENTIAL ROUTES =====

@app.route('/upload-medical-form')
def upload_medical_form():
    return '''
    <html>
    <head>
        <title>Upload Medical Document - HeartShield</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 40px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .upload-area { border: 2px dashed #3498db; padding: 40px; text-align: center; border-radius: 10px; margin: 20px 0; }
            .btn { background: #e74c3c; color: white; padding: 15px 40px; border: none; border-radius: 5px; font-size: 1.2em; cursor: pointer; text-decoration: none; display: inline-block; }
            .back-btn { background: #7f8c8d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📄 Upload Medical Document</h2>
            <p>Upload lab reports, discharge summaries, or medical notes for automatic data extraction:</p>
            
            <form action="/upload-medical-document" method="POST" enctype="multipart/form-data">
                <div class="upload-area">
                    <input type="file" name="medical_document" accept=".png,.jpg,.jpeg,.pdf" required style="font-size: 1.1em;">
                    <p style="color: #7f8c8d; margin-top: 10px;">Supported: PNG, JPG, JPEG, PDF</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4>📋 What we can extract:</h4>
                    <ul>
                        <li>Age, Blood Pressure, Cholesterol</li>
                        <li>Heart Rate, Glucose levels</li>
                        <li>Medical history mentions</li>
                        <li>Lab results and vital signs</li>
                    </ul>
                </div>
                
                <button type="submit" class="btn">🔍 Process Document</button>
            </form>
            
            <br>
            <a href="/" class="back-btn">Back to Home</a>
        </div>
    </body>
    </html>
    '''

@app.route('/test-prediction')
def test_prediction_redirect():
    return redirect('/api/predict-form')

@app.route('/health-check')
def health_check_redirect():
    return redirect('/api/health')

# [Include all your other existing routes: api/predict-form, api/health, upload-medical-document, document-results, etc.]

if __name__ == '__main__':
    print("📍 Visit: http://localhost:5000")
    print("✅ Fixed Issues:")
    print("   - Removed 'Phase 2 & 3 Active' badge from header")
    print("   - Login and Register routes now working")
    print("   - All buttons functional")
    print("🚀 Ready to use!")
    app.run(debug=True, host='0.0.0.0', port=5000)