# ocr/utils/data_validator.py
import logging
from typing import Dict, Any, List

class DataValidator:
    """
    Validates extracted medical data and prepares it for prediction
    Implements graceful degradation for incomplete data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.critical_params = ['age', 'cholesterol', 'blood_pressure']
        self.optional_params = ['heart_rate', 'glucose', 'hdl', 'ldl']
        self.logger.info("✅ DataValidator initialized")
    
    def validate_and_prepare_prediction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation method with graceful degradation
        """
        self.logger.info("🛡️ Starting data validation...")
        
        # Clean the extracted data
        cleaned_data = self._clean_extracted_data(extracted_data)
        
        # Assess data completeness
        completeness = self.assess_completeness(cleaned_data)
        self.logger.info(f"📊 Data completeness: {completeness}")
        
        # Apply appropriate handling based on completeness
        if completeness == 'EXCELLENT':
            return self._handle_excellent_data(cleaned_data)
        elif completeness == 'GOOD':
            return self._handle_good_data(cleaned_data)
        elif completeness == 'MINIMAL':
            return self._handle_minimal_data(cleaned_data)
        else:  # POOR
            return self._handle_poor_data(cleaned_data)
    
    def assess_completeness(self, extracted_data: Dict[str, Any]) -> str:
        """Assess how complete the extracted data is"""
        missing_critical = self.get_missing_critical(extracted_data)
        
        if not missing_critical:
            return 'EXCELLENT'
        elif len(missing_critical) == 1:
            return 'GOOD'
        elif len(missing_critical) <= 2:
            return 'MINIMAL'
        else:
            return 'POOR'
    
    def get_missing_critical(self, extracted_data: Dict[str, Any]) -> List[str]:
        """Get list of missing critical parameters"""
        return [param for param in self.critical_params 
                if param not in extracted_data or not extracted_data[param]]
    
    def _clean_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize extracted data"""
        cleaned = {}
        
        for key, value in extracted_data.items():
            if value and value != 'None' and value != 'null':
                # Convert age to integer
                if key == 'age' and str(value).isdigit():
                    cleaned[key] = int(value)
                # Validate blood pressure format
                elif key == 'blood_pressure':
                    bp_cleaned = self._clean_blood_pressure(value)
                    if bp_cleaned:
                        cleaned[key] = bp_cleaned
                # Convert numeric values
                elif key in ['cholesterol', 'heart_rate', 'glucose', 'hdl', 'ldl']:
                    if str(value).isdigit():
                        cleaned[key] = int(value)
                else:
                    cleaned[key] = value
        
        return cleaned
    
    def _clean_blood_pressure(self, bp_value: Any) -> str:
        """Clean and validate blood pressure values"""
        if not bp_value:
            return None
        
        bp_str = str(bp_value)
        
        # Handle various BP formats
        if '/' in bp_str:
            parts = bp_str.split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                systolic, diastolic = int(parts[0]), int(parts[1])
                # Validate reasonable BP ranges
                if 70 <= systolic <= 250 and 40 <= diastolic <= 150:
                    return f"{systolic}/{diastolic}"
        
        return None
    
    def _handle_excellent_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when all critical data is available"""
        self.logger.info("🎉 All critical data available for prediction")
        return {
            'status': 'READY_FOR_PREDICTION',
            'message': 'All critical data extracted successfully!',
            'data': data,
            'prediction_confidence': 'HIGH',
            'missing_fields': [],
            'risk_insights': self._extract_risk_insights(data)
        }
    
    def _handle_good_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when most critical data is available"""
        missing = self.get_missing_critical(data)
        self.logger.info(f"⚠️ Some data missing, but can proceed: {missing}")
        
        return {
            'status': 'READY_WITH_WARNING',
            'message': f'We can provide prediction, but {missing[0]} is missing',
            'data': data,
            'missing_fields': missing,
            'prediction_confidence': 'MEDIUM',
            'risk_insights': self._extract_risk_insights(data),
            'suggestion': 'Prediction will use estimated values for missing fields'
        }
    
    def _handle_minimal_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when minimal data is available"""
        missing = self.get_missing_critical(data)
        self.logger.warning(f"🚧 Insufficient data for prediction: {missing}")
        
        return {
            'status': 'PARTIAL_INSIGHTS',
            'message': 'Insufficient for full prediction, but here are risk factors we identified:',
            'identified_risks': self._extract_risk_insights(data),
            'available_data': data,
            'missing_critical': missing,
            'prediction_confidence': 'LOW',
            'suggestion': 'Please provide lab reports with cholesterol and blood pressure for complete analysis'
        }
    
    def _handle_poor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when very little data is available"""
        self.logger.error("❌ Cannot process - insufficient medical data")
        
        return {
            'status': 'CANNOT_PROCESS',
            'message': 'We could not extract sufficient medical data from this document',
            'available_data': data,
            'prediction_confidence': 'NONE',
            'suggestion': 'Try uploading lab reports, discharge summaries, or clinic notes with clear medical values'
        }
    
    def _extract_risk_insights(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract risk insights from available data"""
        insights = {}
        
        # Age-based insights
        if 'age' in extracted_data:
            age = extracted_data['age']
            if age > 45:
                insights['age_risk'] = 'Increased risk due to age > 45'
            elif age > 60:
                insights['age_risk'] = 'Higher risk due to age > 60'
        
        # Cholesterol insights
        if 'cholesterol' in extracted_data:
            chol = extracted_data['cholesterol']
            if chol > 240:
                insights['cholesterol_risk'] = 'High cholesterol level (>240)'
            elif chol > 200:
                insights['cholesterol_risk'] = 'Borderline high cholesterol (200-239)'
        
        # Blood pressure insights
        if 'blood_pressure' in extracted_data:
            bp = extracted_data['blood_pressure']
            if '/' in bp:
                systolic = int(bp.split('/')[0])
                if systolic > 140:
                    insights['bp_risk'] = 'Elevated systolic blood pressure (>140)'
                elif systolic > 130:
                    insights['bp_risk'] = 'High-normal blood pressure (130-139)'
        
        # General insights
        if not insights:
            available_fields = [k for k in extracted_data.keys() if k not in ['document_type', 'error']]
            if available_fields:
                insights['info'] = f'Data available for: {", ".join(available_fields)}'
        
        return insights
    
    def prepare_for_ml_model(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert validated OCR data to format expected by ML model
        """
        if validated_data.get('status') != 'READY_FOR_PREDICTION':
            return None
        
        data = validated_data['data']
        ml_input = {}
        
        # Direct mappings from OCR to ML features
        mapping = {
            'age': 'age',
            'cholesterol': 'chol',
            'heart_rate': 'thalach', 
            'glucose': 'fbs'
        }
        
        # Map available fields
        for source_key, target_key in mapping.items():
            if source_key in data:
                ml_input[target_key] = data[source_key]
        
        # Handle blood pressure (extract systolic)
        if 'blood_pressure' in data:
            bp_parts = data['blood_pressure'].split('/')
            if len(bp_parts) == 2:
                ml_input['trestbps'] = int(bp_parts[0])  # Systolic BP
        
        # Set default values for missing required fields
        defaults = {
            'sex': 1,           # Default to male
            'cp': 0,            # No chest pain
            'restecg': 0,       # Normal ECG
            'exang': 0,         # No exercise angina
            'oldpeak': 1.0,     # Default ST depression
            'slope': 1,         # Upsloping
            'ca': 0,            # 0 major vessels
            'thal': 3           # Normal
        }
        
        # Apply defaults only for missing fields
        for field, default_value in defaults.items():
            if field not in ml_input:
                ml_input[field] = default_value
        
        # Convert fasting blood sugar to binary (1 if > 120)
        if 'fbs' in ml_input:
            ml_input['fbs'] = 1 if ml_input['fbs'] > 120 else 0
        
        self.logger.info(f"🧠 ML Input prepared: {ml_input}")
        return ml_input