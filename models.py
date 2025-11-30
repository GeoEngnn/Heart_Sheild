# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ADD FULL_NAME FIELD HERE
    full_name = db.Column(db.String(120), nullable=False)  # Add this line
    password_hash = db.Column(db.String(255))  # Increased from 128 to 255 for werkzeug scrypt hashes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,  # Add this line
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Prediction results
    probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Medical parameters from your OCR
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    systolic_bp = db.Column(db.Float)
    diastolic_bp = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    glucose = db.Column(db.Float)
    heart_rate = db.Column(db.Integer)
    smoking = db.Column(db.Boolean)
    alcohol_intake = db.Column(db.Boolean)
    physical_activity = db.Column(db.Boolean)
    medical_data = db.Column(db.Text)  # Store OCR JSON data
    confidence = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'probability': round(self.probability * 100, 2) if self.probability else 0,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'cholesterol': self.cholesterol,
            'glucose': self.glucose,
            'heart_rate': self.heart_rate,
            'smoking': self.smoking,
            'alcohol_intake': self.alcohol_intake,
            'physical_activity': self.physical_activity,
            'confidence': round(self.confidence * 100, 2) if self.confidence else 0
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'username': self.user.username if self.user else None
        }