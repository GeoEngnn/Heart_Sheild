# ml/predictor.py - UPDATED FOR NEW FEATURES
import joblib
import pandas as pd
import numpy as np
import os

class HeartDiseasePredictor:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.label_encoders = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the trained model and feature names - UPDATED FOR NEW FEATURES"""
        try:
            # Load model
            self.model = joblib.load('heart_disease_model.pkl')
            
            # Load feature names used during training
            self.feature_names = joblib.load('feature_names.pkl')
            
            # Load label encoders for categorical variables
            self.label_encoders = joblib.load('label_encoders.pkl')
            
            self.model_loaded = True
            print("✅ AI Model loaded successfully with NEW features")
            print(f"🔧 Features: {self.feature_names}")
            print(f"🔤 Encoders: {list(self.label_encoders.keys())}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
            self.model_loaded = False
    
    def predict_risk(self, patient_data):
        """Predict heart disease risk for a patient - UPDATED FOR NEW FEATURES"""
        if not self.model_loaded or self.model is None:
            error_msg = "AI model not available. Using fallback calculation."
            print(f"⚠️ {error_msg}")
            return self._fallback_prediction(patient_data)
        
        try:
            # Create input array with NEW feature order
            input_data = []
            for feature in self.feature_names:
                if feature in patient_data:
                    input_data.append(patient_data[feature])
                else:
                    # Provide default values for missing features
                    default_values = {
                        'Age': 50, 'Height': 170, 'Weight': 70, 'Gender': 'Male',
                        'Systolic_BP': 120, 'Diastolic_BP': 80, 'Cholesterol': 200,
                        'Glucose': 100, 'Smoking': 0, 'Alcohol_Intake': 0, 
                        'Physical_Activity': 1, 'BMI': 24.2
                    }
                    input_data.append(default_values[feature])
                    print(f"⚠️ Using default value for {feature}: {default_values[feature]}")
            
            # Convert to DataFrame
            patient_df = pd.DataFrame([input_data], columns=self.feature_names)
            
            # Encode categorical variables using saved encoders
            for feature, encoder in self.label_encoders.items():
                if feature in patient_df.columns:
                    # Convert back to string for encoding (in case it comes as int)
                    original_value = patient_df[feature].iloc[0]
                    if isinstance(original_value, (int, float)) and feature == 'Gender':
                        # Handle case where Gender might come as 0/1 instead of string
                        patient_df[feature] = 'Male' if original_value == 1 else 'Female'
                    
                    patient_df[feature] = encoder.transform([patient_df[feature].iloc[0]])
            
            # Make prediction
            prediction = self.model.predict(patient_df)[0]
            probability = self.model.predict_proba(patient_df)[0]
            
            # Calculate risk percentage (probability of heart disease = class 1)
            heart_disease_probability = probability[1]
            risk_percentage = heart_disease_probability * 100
            
            # Determine risk category
            if risk_percentage < 20:
                risk_category = "Low"
                emoji = "🟢"
            elif risk_percentage < 50:
                risk_category = "Moderate" 
                emoji = "🟡"
            else:
                risk_category = "High"
                emoji = "🔴"
            
            # Generate recommendations
            recommendations = self._get_recommendations(risk_category, patient_data)
            
            return {
                "success": True,
                "prediction": int(prediction),
                "probability": float(heart_disease_probability),
                "risk_percentage": round(risk_percentage, 1),
                "risk_category": risk_category,
                "risk_level": risk_category.upper(),
                "confidence": round(max(probability) * 100, 1),
                "message": f"{emoji} Heart disease risk: {risk_category} ({risk_percentage:.1f}%)",
                "recommendations": recommendations,
                "model_used": "AI_RandomForest_NewFeatures"
            }
            
        except Exception as e:
            print(f"❌ AI prediction failed: {e}")
            return self._fallback_prediction(patient_data)
    
    def _fallback_prediction(self, patient_data):
        """Fallback prediction when AI model is unavailable"""
        print("🔄 Using rule-based fallback prediction")
        
        # Extract parameters with defaults for NEW features
        age = patient_data.get('Age', patient_data.get('age', 50))
        systolic_bp = patient_data.get('Systolic_BP', patient_data.get('systolic_bp', 120))
        diastolic_bp = patient_data.get('Diastolic_BP', patient_data.get('diastolic_bp', 80))
        cholesterol = patient_data.get('Cholesterol', patient_data.get('chol', 200))
        glucose = patient_data.get('Glucose', patient_data.get('glucose', 100))
        smoking = patient_data.get('Smoking', 0)
        
        # Simple risk calculation based on NEW features
        risk_score = 0
        if age > 55: risk_score += 0.3
        if systolic_bp > 130: risk_score += 0.2
        if diastolic_bp > 85: risk_score += 0.1
        if cholesterol > 200: risk_score += 0.2
        if glucose > 120: risk_score += 0.1
        if smoking == 1: risk_score += 0.1
        
        probability = min(risk_score, 0.9)
        risk_percentage = probability * 100
        
        if risk_percentage < 25:
            risk_category = "Low"
            emoji = "🟢"
        elif risk_percentage < 60:
            risk_category = "Moderate"
            emoji = "🟡"
        else:
            risk_category = "High" 
            emoji = "🔴"
        
        recommendations = self._get_recommendations(risk_category, patient_data)
        
        return {
            "success": True,
            "prediction": 1 if probability > 0.5 else 0,
            "probability": probability,
            "risk_percentage": round(risk_percentage, 1),
            "risk_category": risk_category,
            "risk_level": risk_category.upper(),
            "confidence": round((1 - probability) * 100, 1) if probability < 0.5 else round(probability * 100, 1),
            "message": f"{emoji} Heart disease risk: {risk_category} ({risk_percentage:.1f}%) [Fallback Mode]",
            "recommendations": recommendations,
            "model_used": "RuleBased_Fallback_NewFeatures"
        }
    
    def _get_recommendations(self, risk_category, patient_data):
        """Get personalized recommendations based on risk"""
        base_recommendations = {
            "Low": [
                "Maintain healthy lifestyle",
                "Regular exercise 30min/day",
                "Balanced diet with fruits/vegetables",
                "Annual health checkups"
            ],
            "Moderate": [
                "Consult doctor for cardiovascular assessment",
                "Monitor blood pressure regularly", 
                "Consider cholesterol and glucose screening",
                "Maintain healthy weight and BMI",
                "Reduce salt and sugar intake"
            ],
            "High": [
                "Immediate medical consultation recommended",
                "Comprehensive cardiac evaluation needed",
                "Regular monitoring of blood pressure and cholesterol",
                "Lifestyle modifications advised (diet, exercise, no smoking)",
                "Consider stress management techniques"
            ]
        }
        
        # Add personalized recommendations based on patient data
        personalized = []
        age = patient_data.get('Age', patient_data.get('age', 0))
        cholesterol = patient_data.get('Cholesterol', patient_data.get('chol', 0))
        systolic_bp = patient_data.get('Systolic_BP', patient_data.get('systolic_bp', 0))
        smoking = patient_data.get('Smoking', 0)
        
        if age > 50:
            personalized.append("Regular heart health screenings recommended")
        if cholesterol > 200:
            personalized.append("Consider dietary changes to lower cholesterol")
        if systolic_bp > 130:
            personalized.append("Blood pressure management important")
        if smoking == 1:
            personalized.append("Smoking cessation strongly recommended")
        
        return base_recommendations.get(risk_category, []) + personalized
    
    def get_model_status(self):
        """Check if model is loaded and ready"""
        return {
            "model_loaded": self.model_loaded,
            "status": "READY" if self.model_loaded else "FALLBACK_MODE",
            "message": "AI Model with NEW Features Active" if self.model_loaded else "Using Rule-Based Fallback",
            "features": self.feature_names if self.model_loaded else []
        }

# Create global instance
predictor = HeartDiseasePredictor()

def test_prediction():
    """Test the predictor with NEW features"""
    print("\n🧪 TESTING PREDICTOR WITH NEW FEATURES...")
    
    # Test patient data with NEW features
    test_patient = {
        'Age': 52, 'Height': 175, 'Weight': 80, 'Gender': 'Male',
        'Systolic_BP': 125, 'Diastolic_BP': 85, 'Cholesterol': 212,
        'Glucose': 98, 'Smoking': 0, 'Alcohol_Intake': 1, 
        'Physical_Activity': 1
    }
    
    result = predictor.predict_risk(test_patient)
    
    print("📊 PREDICTION RESULT:")
    for key, value in result.items():
        if key != "recommendations":
            print(f"  {key}: {value}")
    
    print("💡 RECOMMENDATIONS:")
    for rec in result.get("recommendations", []):
        print(f"  • {rec}")

if __name__ == "__main__":
    test_prediction()