# ml/predictor.py - CORRECTED VERSION
import joblib
import pandas as pd
import numpy as np
import os

class HeartDiseasePredictor:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            # CORRECTED PATH - file is in same folder as this script
            self.model = joblib.load('heart_disease_model.pkl')
            print("✅ AI Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            # Let's see what files are actually in the folder
            print("📁 Files in current directory:", os.listdir('.'))
            self.model = None
    
    def predict_risk(self, patient_data):
        """Predict heart disease risk for a patient"""
        if self.model is None:
            return {"error": "Model not loaded"}
        
        try:
            # Convert patient data to DataFrame with correct feature order
            features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                       'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            
            # Create DataFrame with the exact feature order used during training
            patient_df = pd.DataFrame([patient_data], columns=features)
            
            # Make prediction
            prediction = self.model.predict(patient_df)[0]
            probability = self.model.predict_proba(patient_df)[0]
            
            # Calculate risk percentage - PROBABILITY OF HEART DISEASE (class 1)
            risk_percentage = probability[1] * 100
            
            # Determine risk category based on heart disease probability
            if risk_percentage < 25:
                risk_category = "Low"
            elif risk_percentage < 60:
                risk_category = "Moderate"
            else:
                risk_category = "High"
            
            # Make prediction consistent with risk percentage
            # If risk_percentage > 50%, prediction should be 1 (has heart disease)
            consistent_prediction = 1 if risk_percentage > 50 else 0
            
            return {
                "prediction": consistent_prediction,  # Now consistent with risk_percentage
                "risk_percentage": round(risk_percentage, 1),
                "risk_category": risk_category,
                "confidence": round(max(probability) * 100, 1),
                "message": f"Heart disease risk: {risk_category} ({risk_percentage:.1f}%)"
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}

# Create a global predictor instance
predictor = HeartDiseasePredictor()

# Test function
def test_prediction():
    """Test the predictor with sample data"""
    sample_patient = {
        'age': 52, 'sex': 1, 'cp': 0, 'trestbps': 125, 'chol': 212,
        'fbs': 0, 'restecg': 1, 'thalach': 168, 'exang': 0, 
        'oldpeak': 1.0, 'slope': 2, 'ca': 2, 'thal': 3
    }
    
    result = predictor.predict_risk(sample_patient)
    print("🧪 TEST PREDICTION:")
    print(f"Input: {sample_patient}")
    print(f"Result: {result}")

if __name__ == "__main__":
    test_prediction()