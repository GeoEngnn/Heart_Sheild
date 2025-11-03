# ocr/utils/data_validator.py - UPDATED FOR NEW DATASET
import logging
from typing import Dict, Any, List

class DataValidator:
    """
    UPDATED: Validates extracted medical data for NEW DATASET FEATURES
    Implements graceful degradation for incomplete data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # UPDATED: Critical parameters for new model
        self.critical_params = ['age', 'cholesterol', 'systolic_bp', 'diastolic_bp']
        self.important_params = ['height', 'weight', 'glucose', 'gender']
        self.lifestyle_params = ['smoking', 'alcohol_intake', 'physical_activity']
        
        self.logger.info("✅ DataValidator UPDATED for new dataset features")
    
    def validate_and_prepare_prediction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        UPDATED: Main validation method for new features
        """
        self.logger.info("🛡️ Starting data validation for NEW FEATURES...")
        
        # Clean the extracted data
        cleaned_data = self._clean_extracted_data(extracted_data)
        
        # Calculate BMI if height and weight are available
        if 'height' in cleaned_data and 'weight' in cleaned_data:
            try:
                height_m = cleaned_data['height'] / 100
                cleaned_data['bmi'] = cleaned_data['weight'] / (height_m ** 2)
                self.logger.info(f"✅ BMI calculated: {cleaned_data['bmi']:.1f}")
            except Exception as e:
                self.logger.warning(f"⚠️ BMI calculation failed: {e}")
        
        # Assess data completeness for new features
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
        """UPDATED: Assess completeness for new feature set"""
        missing_critical = self.get_missing_critical(extracted_data)
        available_important = self.get_available_important(extracted_data)
        
        # New completeness logic
        if not missing_critical and available_important >= 3:
            return 'EXCELLENT'
        elif len(missing_critical) <= 1 and available_important >= 2:
            return 'GOOD'
        elif len(missing_critical) <= 2:
            return 'MINIMAL'
        else:
            return 'POOR'
    
    def get_missing_critical(self, extracted_data: Dict[str, Any]) -> List[str]:
        """Get list of missing critical parameters"""
        return [param for param in self.critical_params 
                if param not in extracted_data or not extracted_data[param]]
    
    def get_available_important(self, extracted_data: Dict[str, Any]) -> int:
        """Count available important parameters"""
        return sum(1 for param in self.important_params 
                  if param in extracted_data and extracted_data[param])
    
    def _clean_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATED: Clean and normalize extracted data for new features"""
        cleaned = {}
        
        for key, value in extracted_data.items():
            if value and value != 'None' and value != 'null':
                # Convert numeric values
                if key in ['age', 'height', 'weight', 'cholesterol', 'glucose', 'heart_rate']:
                    if str(value).replace('.', '').isdigit():
                        cleaned[key] = float(value) if '.' in str(value) else int(value)
                
                # Handle blood pressure components
                elif key in ['systolic_bp', 'diastolic_bp']:
                    if str(value).isdigit():
                        bp_value = int(value)
                        if self._is_valid_bp_component(key, bp_value):
                            cleaned[key] = bp_value
                
                # Handle lifestyle factors (convert to binary)
                elif key in ['smoking', 'alcohol_intake', 'physical_activity']:
                    if str(value).isdigit():
                        cleaned[key] = int(value)
                    elif isinstance(value, str):
                        # Convert yes/no to binary
                        if value.lower() in ['y', 'yes', '1', 'true']:
                            cleaned[key] = 1
                        elif value.lower() in ['n', 'no', '0', 'false']:
                            cleaned[key] = 0
                
                # Handle gender
                elif key == 'gender':
                    gender_str = str(value).lower()
                    if gender_str in ['m', 'male', 'f', 'female']:
                        cleaned[key] = 'Male' if gender_str in ['m', 'male'] else 'Female'
                
                else:
                    cleaned[key] = value
        
        return cleaned
    
    def _is_valid_bp_component(self, bp_type: str, value: int) -> bool:
        """Validate blood pressure components"""
        if bp_type == 'systolic_bp':
            return 70 <= value <= 250
        elif bp_type == 'diastolic_bp':
            return 40 <= value <= 150
        return False
    
    def _handle_excellent_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when all critical data is available"""
        self.logger.info("🎉 All critical data available for NEW MODEL prediction")
        return {
            'status': 'READY_FOR_PREDICTION',
            'message': 'All critical data extracted successfully for new model!',
            'validated_data': data,
            'prediction_confidence': 'HIGH',
            'missing_fields': [],
            'risk_insights': self._extract_risk_insights(data),
            'model_compatibility': 'FULL'
        }
    
    def _handle_good_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when most critical data is available"""
        missing = self.get_missing_critical(data)
        self.logger.info(f"⚠️ Some data missing, but can proceed: {missing}")
        
        return {
            'status': 'READY_FOR_PREDICTION',
            'message': f'Sufficient data for prediction, but {missing[0]} is estimated',
            'validated_data': data,
            'missing_fields': missing,
            'prediction_confidence': 'MEDIUM',
            'risk_insights': self._extract_risk_insights(data),
            'model_compatibility': 'PARTIAL',
            'suggestion': 'Prediction will use estimated values for missing fields'
        }
    
    def _handle_minimal_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when minimal data is available"""
        missing = self.get_missing_critical(data)
        self.logger.warning(f"🚧 Limited data for prediction: {missing}")
        
        return {
            'status': 'READY_WITH_WARNING',
            'message': 'Limited data available, prediction may be less accurate',
            'validated_data': data,
            'missing_critical': missing,
            'prediction_confidence': 'LOW',
            'risk_insights': self._extract_risk_insights(data),
            'model_compatibility': 'LIMITED',
            'suggestion': 'Please provide documents with blood pressure and cholesterol for better accuracy'
        }
    
    def _handle_poor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when very little data is available"""
        self.logger.error("❌ Cannot process - insufficient medical data for new model")
        
        return {
            'status': 'CANNOT_PROCESS',
            'message': 'We could not extract sufficient medical data for the new prediction model',
            'available_data': data,
            'prediction_confidence': 'NONE',
            'model_compatibility': 'POOR',
            'suggestion': 'Try uploading lab reports with blood pressure, cholesterol, height, and weight measurements'
        }
    
    def _extract_risk_insights(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATED: Extract risk insights from available data for new features"""
        insights = {}
        
        # Age-based insights
        if 'age' in extracted_data:
            age = extracted_data['age']
            if age > 55:
                insights['age_risk'] = 'Increased risk due to age > 55'
            elif age > 45:
                insights['age_risk'] = 'Moderate risk due to age > 45'
        
        # Blood pressure insights
        systolic = extracted_data.get('systolic_bp')
        diastolic = extracted_data.get('diastolic_bp')
        
        if systolic and diastolic:
            if systolic > 140 or diastolic > 90:
                insights['bp_risk'] = 'High blood pressure detected'
            elif systolic > 130 or diastolic > 85:
                insights['bp_risk'] = 'Elevated blood pressure'
        
        # Cholesterol insights
        if 'cholesterol' in extracted_data:
            chol = extracted_data['cholesterol']
            if chol > 240:
                insights['cholesterol_risk'] = 'High cholesterol level (>240)'
            elif chol > 200:
                insights['cholesterol_risk'] = 'Borderline high cholesterol'
        
        # BMI insights
        if 'bmi' in extracted_data:
            bmi = extracted_data['bmi']
            if bmi > 30:
                insights['bmi_risk'] = 'Obese (BMI > 30)'
            elif bmi > 25:
                insights['bmi_risk'] = 'Overweight (BMI 25-30)'
        
        # Lifestyle insights
        if extracted_data.get('smoking') == 1:
            insights['lifestyle_risk'] = 'Smoking increases cardiovascular risk'
        
        if extracted_data.get('physical_activity') == 0:
            insights['activity_risk'] = 'Physical inactivity increases risk'
        
        # General insights
        if not insights:
            available_fields = [k for k in extracted_data.keys() if k not in ['document_type', 'error']]
            if available_fields:
                insights['info'] = f'Data available for: {", ".join(available_fields)}'
        
        return insights
    
    def prepare_for_ml_model(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        UPDATED: Convert validated OCR data to format expected by NEW ML model
        """
        data = validated_data.get('validated_data', {})
        
        # Prepare ML input with new feature mapping
        ml_input = {}
        
        # Direct mappings from OCR to NEW ML features
        mapping = {
            'age': 'Age',
            'height': 'Height',
            'weight': 'Weight', 
            'gender': 'Gender',
            'systolic_bp': 'Systolic_BP',
            'diastolic_bp': 'Diastolic_BP',
            'cholesterol': 'Cholesterol',
            'glucose': 'Glucose',
            'smoking': 'Smoking',
            'alcohol_intake': 'Alcohol_Intake',
            'physical_activity': 'Physical_Activity',
            'bmi': 'BMI'
        }
        
        # Map available fields
        for source_key, target_key in mapping.items():
            if source_key in data:
                ml_input[target_key] = data[source_key]
        
        # Calculate BMI if not provided but height/weight available
        if 'BMI' not in ml_input and 'Height' in ml_input and 'Weight' in ml_input:
            try:
                height_m = ml_input['Height'] / 100
                ml_input['BMI'] = ml_input['Weight'] / (height_m ** 2)
            except:
                ml_input['BMI'] = 24.2  # Default BMI
        
        # Set default values for missing required fields
        defaults = {
            'Age': 50,
            'Height': 170,
            'Weight': 70,
            'Gender': 'Male',
            'Systolic_BP': 120,
            'Diastolic_BP': 80,
            'Cholesterol': 200,
            'Glucose': 100,
            'Smoking': 0,
            'Alcohol_Intake': 0,
            'Physical_Activity': 1,
            'BMI': 24.2
        }
        
        # Apply defaults only for missing fields
        for field, default_value in defaults.items():
            if field not in ml_input:
                ml_input[field] = default_value
                self.logger.info(f"⚠️ Using default for {field}: {default_value}")
        
        # Ensure Gender is properly formatted
        if 'Gender' in ml_input:
            gender = str(ml_input['Gender']).lower()
            if gender in ['m', 'male']:
                ml_input['Gender'] = 'Male'
            elif gender in ['f', 'female']:
                ml_input['Gender'] = 'Female'
            else:
                ml_input['Gender'] = 'Male'  # Default
        
        # Ensure lifestyle factors are integers
        lifestyle_fields = ['Smoking', 'Alcohol_Intake', 'Physical_Activity']
        for field in lifestyle_fields:
            if field in ml_input:
                try:
                    ml_input[field] = int(ml_input[field])
                except (ValueError, TypeError):
                    ml_input[field] = 0  # Default to no
        
        self.logger.info(f"🧠 NEW ML Input prepared: {list(ml_input.keys())}")
        return ml_input
    
    def get_new_model_requirements(self) -> Dict[str, Any]:
        """Return requirements for the new ML model"""
        return {
            'critical_features': self.critical_params,
            'important_features': self.important_params,
            'lifestyle_features': self.lifestyle_params,
            'all_required': ['Age', 'Height', 'Weight', 'Gender', 'Systolic_BP', 'Diastolic_BP', 
                           'Cholesterol', 'Glucose', 'Smoking', 'Alcohol_Intake', 'Physical_Activity', 'BMI']
        }