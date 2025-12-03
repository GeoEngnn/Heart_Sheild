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
    probability = db.Column(db.Float, nullable=False, default=0.0)  # 0.0 to 1.0
    risk_level = db.Column(db.String(20), nullable=False, default="Unknown")
    confidence = db.Column(db.Float, default=0.0)  # 0–100%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Medical parameters
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
    
    # Lifestyle - USE INTEGER, NOT BOOLEAN
    smoking = db.Column(db.Integer, default=0)                    # 0 or 1
    alcohol_intake = db.Column(db.Integer, default=0)             # 0 or 1
    physical_activity = db.Column(db.Integer, default=1)          # 0 or 1
    
    medical_data = db.Column(db.Text)  # JSON string

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'probability': round(self.probability, 4),
            'risk_percentage': round(self.probability * 100, 1),   # ← Add this for frontend
            'risk_level': self.risk_level,
            'confidence': round(self.confidence, 1) if self.confidence else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'bmi': round(self.bmi, 1) if self.bmi else None,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'cholesterol': self.cholesterol,
            'glucose': self.glucose,
            'heart_rate': self.heart_rate,
            'smoking': bool(self.smoking),
            'alcohol_intake': bool(self.alcohol_intake),
            'physical_activity': bool(self.physical_activity),
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