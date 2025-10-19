# ml/predictor.py - COMPLETE FIXED VERSION
import joblib
import pandas as pd
import numpy as np
import os

class HeartDiseasePredictor:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the trained model - FIXED PATHS"""
        try:
            # Try multiple possible locations
            possible_paths = [
                'heart_disease_model.pkl',  # Same directory
                'ml/heart_disease_model.pkl',  # ml subdirectory
                './heart_disease_model.pkl',  # Current directory
            ]
            
            model_loaded = False
            for path in possible_paths:
                if os.path.exists(path):
                    self.model = joblib.load(path)
                    model_loaded = True
                    print(f"✅ AI Model loaded from: {path}")
                    break
            
            if not model_loaded:
                print("❌ Model file not found in any location!")
                print("📁 Current directory:", os.getcwd())
                print("📁 Files here:", os.listdir('.'))
                if os.path.exists('ml'):
                    print("📁 Files in ml folder:", os.listdir('ml'))
                self.model = None
                return
            
            self.model_loaded = True
            print("🤖 AI Heart Disease Predictor READY!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
            self.model_loaded = False
    
    def predict_risk(self, patient_data):
        """Predict heart disease risk for a patient - FIXED LOGIC"""
        if not self.model_loaded or self.model is None:
            error_msg = "AI model not available. Using fallback calculation."
            print(f"⚠️ {error_msg}")
            return self._fallback_prediction(patient_data)
        
        try:
            # Define the exact feature order used during training
            features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                       'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            
            # Create input array with correct feature order
            input_data = []
            for feature in features:
                if feature in patient_data:
                    input_data.append(patient_data[feature])
                else:
                    # Provide default values for missing features
                    default_values = {
                        'age': 50, 'sex': 1, 'cp': 0, 'trestbps': 120,
                        'chol': 200, 'fbs': 0, 'restecg': 0, 'thalach': 150,
                        'exang': 0, 'oldpeak': 1.0, 'slope': 1, 'ca': 0, 'thal': 2
                    }
                    input_data.append(default_values[feature])
                    print(f"⚠️ Using default value for {feature}: {default_values[feature]}")
            
            # Convert to DataFrame
            patient_df = pd.DataFrame([input_data], columns=features)
            
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
                "model_used": "AI_RandomForest"
            }
            
        except Exception as e:
            print(f"❌ AI prediction failed: {e}")
            return self._fallback_prediction(patient_data)
    
    def _fallback_prediction(self, patient_data):
        """Fallback prediction when AI model is unavailable"""
        print("🔄 Using rule-based fallback prediction")
        
        # Extract parameters with defaults
        age = patient_data.get('age', 50)
        cholesterol = patient_data.get('chol', patient_data.get('cholesterol', 200))
        bp = patient_data.get('trestbps', patient_data.get('bp_systolic', 120))
        heart_rate = patient_data.get('thalach', patient_data.get('heart_rate', 72))
        
        # Simple risk calculation
        risk_score = 0
        if age > 55: risk_score += 0.3
        if cholesterol > 240: risk_score += 0.3  
        if bp > 140: risk_score += 0.2
        if heart_rate > 100: risk_score += 0.1
        
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
            "model_used": "RuleBased_Fallback"
        }
    
    def _get_recommendations(self, risk_category, patient_data):
        """Get personalized recommendations based on risk"""
        base_recommendations = {
            "Low": [
                "Maintain healthy lifestyle",
                "Regular exercise 30min/day",
                "Balanced diet with fruits/vegetables"
            ],
            "Moderate": [
                "Consult doctor for checkup",
                "Monitor blood pressure regularly", 
                "Consider cholesterol screening",
                "Maintain healthy weight"
            ],
            "High": [
                "Immediate medical consultation",
                "Comprehensive cardiac evaluation",
                "Regular monitoring of vital signs",
                "Lifestyle modifications advised"
            ]
        }
        
        # Add personalized recommendations based on patient data
        personalized = []
        age = patient_data.get('age', 0)
        cholesterol = patient_data.get('chol', patient_data.get('cholesterol', 0))
        
        if age > 50:
            personalized.append("Regular heart health screenings recommended")
        if cholesterol > 200:
            personalized.append("Consider dietary changes to lower cholesterol")
        
        return base_recommendations.get(risk_category, []) + personalized
    
    def get_model_status(self):
        """Check if model is loaded and ready"""
        return {
            "model_loaded": self.model_loaded,
            "status": "READY" if self.model_loaded else "FALLBACK_MODE",
            "message": "AI Model Active" if self.model_loaded else "Using Rule-Based Fallback"
        }

# Create global instance
predictor = HeartDiseasePredictor()

def test_prediction():
    """Test the predictor"""
    print("\n🧪 TESTING PREDICTOR...")
    
    # Test patient data
    test_patient = {
        'age': 52, 'sex': 1, 'cp': 0, 'trestbps': 125, 'chol': 212,
        'fbs': 0, 'restecg': 1, 'thalach': 168, 'exang': 0, 
        'oldpeak': 1.0, 'slope': 2, 'ca': 2, 'thal': 3
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