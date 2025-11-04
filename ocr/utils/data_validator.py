# ocr/utils/data_validator.py - UPDATED WITH OCR.SPACE API
import logging
from typing import Dict, Any, List

class DataValidator:
    """
    UPDATED: Validates extracted medical data with OCR.space API integration
    Enhanced for better data quality assessment with improved OCR
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # UPDATED: Enhanced parameter definitions for new model
        self.critical_params = ['age', 'cholesterol', 'systolic_bp', 'diastolic_bp']
        self.important_params = ['height', 'weight', 'glucose', 'gender', 'bmi']
        self.lifestyle_params = ['smoking', 'alcohol_intake', 'physical_activity']
        
        # NEW: OCR quality assessment parameters
        self.ocr_quality_indicators = {
            'high_confidence': ['cholesterol', 'glucose', 'age', 'gender'],
            'medium_confidence': ['systolic_bp', 'diastolic_bp', 'height', 'weight'],
            'low_confidence': ['smoking', 'alcohol_intake', 'physical_activity']
        }
        
        self.logger.info("✅ DataValidator UPDATED with OCR.space enhancements")
    
    def validate_and_prepare_prediction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        UPDATED: Enhanced validation with OCR quality assessment
        """
        self.logger.info("🛡️ Starting enhanced data validation with OCR quality assessment...")
        
        # Clean and normalize the extracted data
        cleaned_data = self._clean_extracted_data_enhanced(extracted_data)
        
        # Calculate BMI if height and weight are available
        if 'height' in cleaned_data and 'weight' in cleaned_data:
            try:
                height_m = cleaned_data['height'] / 100
                cleaned_data['bmi'] = round(cleaned_data['weight'] / (height_m ** 2), 1)
                self.logger.info(f"✅ BMI calculated: {cleaned_data['bmi']:.1f}")
            except Exception as e:
                self.logger.warning(f"⚠️ BMI calculation failed: {e}")
        
        # NEW: Assess OCR data quality
        ocr_quality = self._assess_ocr_data_quality(cleaned_data)
        self.logger.info(f"🔍 OCR Data Quality: {ocr_quality['overall_quality']}")
        
        # Assess data completeness for new features
        completeness = self.assess_completeness_enhanced(cleaned_data, ocr_quality)
        self.logger.info(f"📊 Enhanced data completeness: {completeness}")
        
        # Apply appropriate handling based on completeness and OCR quality
        if completeness == 'EXCELLENT':
            return self._handle_excellent_data_enhanced(cleaned_data, ocr_quality)
        elif completeness == 'GOOD':
            return self._handle_good_data_enhanced(cleaned_data, ocr_quality)
        elif completeness == 'MINIMAL':
            return self._handle_minimal_data_enhanced(cleaned_data, ocr_quality)
        else:  # POOR
            return self._handle_poor_data_enhanced(cleaned_data, ocr_quality)
    
    def _clean_extracted_data_enhanced(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        NEW: Enhanced data cleaning with OCR.space quality improvements
        """
        cleaned = {}
        
        for key, value in extracted_data.items():
            if value and value != 'None' and value != 'null' and value != '':
                try:
                    # Convert numeric values with enhanced validation
                    if key in ['age', 'height', 'weight', 'cholesterol', 'glucose', 'heart_rate']:
                        if self._is_valid_numeric_value(key, value):
                            cleaned[key] = float(value) if '.' in str(value) else int(value)
                    
                    # Enhanced blood pressure validation
                    elif key in ['systolic_bp', 'diastolic_bp']:
                        if self._is_valid_bp_value(key, value):
                            cleaned[key] = int(value)
                    
                    # Enhanced lifestyle factors handling
                    elif key in ['smoking', 'alcohol_intake', 'physical_activity']:
                        cleaned[key] = self._normalize_lifestyle_value(value)
                    
                    # Enhanced gender handling
                    elif key == 'gender':
                        normalized_gender = self._normalize_gender(value)
                        if normalized_gender:
                            cleaned[key] = normalized_gender
                    
                    else:
                        cleaned[key] = value
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to clean {key}: {value} - {e}")
        
        return cleaned
    
    def _is_valid_numeric_value(self, field: str, value: Any) -> bool:
        """Enhanced numeric value validation"""
        try:
            num_val = float(value) if '.' in str(value) else int(value)
            
            validation_ranges = {
                'age': (1, 120),
                'height': (100, 250),  # cm
                'weight': (30, 200),   # kg
                'cholesterol': (100, 400),
                'glucose': (50, 300),
                'heart_rate': (40, 200)
            }
            
            if field in validation_ranges:
                min_val, max_val = validation_ranges[field]
                return min_val <= num_val <= max_val
            
            return True
        except:
            return False
    
    def _is_valid_bp_value(self, bp_type: str, value: Any) -> bool:
        """Enhanced BP value validation"""
        try:
            bp_val = int(value)
            if bp_type == 'systolic_bp':
                return 70 <= bp_val <= 250
            elif bp_type == 'diastolic_bp':
                return 40 <= bp_val <= 150
            return False
        except:
            return False
    
    def _normalize_lifestyle_value(self, value: Any) -> int:
        """Enhanced lifestyle value normalization"""
        if isinstance(value, int):
            return 1 if value == 1 else 0
        
        value_str = str(value).lower().strip()
        positive_indicators = ['y', 'yes', '1', 'true', 'positive', 'smoker', 'drinker', 'active']
        negative_indicators = ['n', 'no', '0', 'false', 'negative', 'non-smoker', 'abstinent', 'sedentary']
        
        if any(indicator in value_str for indicator in positive_indicators):
            return 1
        elif any(indicator in value_str for indicator in negative_indicators):
            return 0
        
        return 0  # Default to negative
    
    def _normalize_gender(self, value: Any) -> str:
        """Enhanced gender normalization"""
        gender_str = str(value).lower().strip()
        
        if gender_str in ['m', 'male', 'man', 'boy']:
            return 'Male'
        elif gender_str in ['f', 'female', 'woman', 'girl']:
            return 'Female'
        
        return None
    
    def _assess_ocr_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        NEW: Assess quality of OCR-extracted data
        """
        quality_score = 0
        max_score = 0
        quality_notes = []
        
        # Assess high-confidence fields
        for field in self.ocr_quality_indicators['high_confidence']:
            if field in data:
                quality_score += 3
                max_score += 3
            else:
                quality_notes.append(f"Missing high-confidence field: {field}")
        
        # Assess medium-confidence fields
        for field in self.ocr_quality_indicators['medium_confidence']:
            if field in data:
                quality_score += 2
                max_score += 2
            else:
                quality_notes.append(f"Missing medium-confidence field: {field}")
        
        # Assess low-confidence fields
        for field in self.ocr_quality_indicators['low_confidence']:
            if field in data:
                quality_score += 1
                max_score += 1
        
        # Calculate overall quality
        quality_percent = (quality_score / max_score) * 100 if max_score > 0 else 0
        
        if quality_percent >= 80:
            overall_quality = 'HIGH'
        elif quality_percent >= 60:
            overall_quality = 'MEDIUM'
        elif quality_percent >= 40:
            overall_quality = 'LOW'
        else:
            overall_quality = 'POOR'
        
        return {
            'overall_quality': overall_quality,
            'quality_score': quality_score,
            'max_possible_score': max_score,
            'quality_percent': round(quality_percent, 2),
            'quality_notes': quality_notes,
            'extracted_fields_count': len(data)
        }
    
    def assess_completeness_enhanced(self, extracted_data: Dict[str, Any], 
                                   ocr_quality: Dict[str, Any]) -> str:
        """UPDATED: Enhanced completeness assessment with OCR quality"""
        missing_critical = self.get_missing_critical(extracted_data)
        available_important = self.get_available_important(extracted_data)
        quality_level = ocr_quality['overall_quality']
        
        # Enhanced logic considering OCR quality
        if not missing_critical and available_important >= 3 and quality_level in ['HIGH', 'MEDIUM']:
            return 'EXCELLENT'
        elif len(missing_critical) <= 1 and available_important >= 2 and quality_level != 'POOR':
            return 'GOOD'
        elif len(missing_critical) <= 2 and quality_level != 'POOR':
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
    
    def _handle_excellent_data_enhanced(self, data: Dict[str, Any], 
                                      ocr_quality: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced handling for excellent data quality"""
        self.logger.info("🎉 Excellent data quality for NEW MODEL prediction")
        
        return {
            'status': 'READY_FOR_PREDICTION',
            'message': 'Excellent data quality with high OCR confidence!',
            'validated_data': data,
            'prediction_confidence': 'VERY_HIGH',
            'missing_fields': [],
            'ocr_quality': ocr_quality,
            'risk_insights': self._extract_enhanced_risk_insights(data),
            'model_compatibility': 'FULL',
            'recommendation': 'Proceed with high-confidence prediction'
        }
    
    def _handle_good_data_enhanced(self, data: Dict[str, Any], 
                                 ocr_quality: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced handling for good data quality"""
        missing = self.get_missing_critical(data)
        self.logger.info(f"⚠️ Good data quality with some missing: {missing}")
        
        return {
            'status': 'READY_FOR_PREDICTION',
            'message': f'Good data quality, {missing[0]} will be estimated',
            'validated_data': data,
            'missing_fields': missing,
            'prediction_confidence': 'HIGH',
            'ocr_quality': ocr_quality,
            'risk_insights': self._extract_enhanced_risk_insights(data),
            'model_compatibility': 'NEAR_FULL',
            'suggestion': 'Prediction will use smart defaults for missing fields'
        }
    
    def _handle_minimal_data_enhanced(self, data: Dict[str, Any], 
                                    ocr_quality: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced handling for minimal data"""
        missing = self.get_missing_critical(data)
        self.logger.warning(f"🚧 Limited data quality: {missing}")
        
        return {
            'status': 'READY_WITH_WARNING',
            'message': 'Limited data available, consider providing additional documents',
            'validated_data': data,
            'missing_critical': missing,
            'prediction_confidence': 'MEDIUM',
            'ocr_quality': ocr_quality,
            'risk_insights': self._extract_enhanced_risk_insights(data),
            'model_compatibility': 'PARTIAL',
            'suggestion': 'Upload lab reports with blood pressure and cholesterol for better accuracy'
        }
    
    def _handle_poor_data_enhanced(self, data: Dict[str, Any], 
                                 ocr_quality: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced handling for poor data quality"""
        self.logger.error("❌ Poor data quality - insufficient for reliable prediction")
        
        return {
            'status': 'CANNOT_PROCESS',
            'message': 'Insufficient medical data extracted for reliable prediction',
            'available_data': data,
            'prediction_confidence': 'LOW',
            'ocr_quality': ocr_quality,
            'model_compatibility': 'POOR',
            'suggestion': 'Try uploading clearer lab reports with blood pressure, cholesterol, and basic measurements'
        }
    
    def _extract_enhanced_risk_insights(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATED: Enhanced risk insights with OCR quality consideration"""
        insights = {}
        
        # Enhanced age-based insights
        if 'age' in extracted_data:
            age = extracted_data['age']
            if age > 60:
                insights['age_risk'] = 'High risk: Age > 60 years'
            elif age > 45:
                insights['age_risk'] = 'Moderate risk: Age 45-60 years'
            else:
                insights['age_risk'] = 'Lower risk: Age < 45 years'
        
        # Enhanced blood pressure insights
        systolic = extracted_data.get('systolic_bp')
        diastolic = extracted_data.get('diastolic_bp')
        
        if systolic and diastolic:
            if systolic >= 140 or diastolic >= 90:
                insights['bp_risk'] = 'Stage 2 Hypertension'
                insights['bp_urgency'] = 'Consult physician'
            elif systolic >= 130 or diastolic >= 85:
                insights['bp_risk'] = 'Stage 1 Hypertension'
            elif systolic < 120 and diastolic < 80:
                insights['bp_status'] = 'Normal blood pressure'
        
        # Enhanced cholesterol insights
        if 'cholesterol' in extracted_data:
            chol = extracted_data['cholesterol']
            if chol >= 240:
                insights['cholesterol_risk'] = 'High: Cholesterol ≥ 240 mg/dL'
            elif chol >= 200:
                insights['cholesterol_risk'] = 'Borderline High: 200-239 mg/dL'
            else:
                insights['cholesterol_status'] = 'Desirable: < 200 mg/dL'
        
        # Enhanced BMI insights
        if 'bmi' in extracted_data:
            bmi = extracted_data['bmi']
            if bmi >= 30:
                insights['bmi_risk'] = 'Obese: BMI ≥ 30'
            elif bmi >= 25:
                insights['bmi_risk'] = 'Overweight: BMI 25-29.9'
            else:
                insights['bmi_status'] = 'Normal weight: BMI < 25'
        
        # Enhanced lifestyle insights
        lifestyle_risks = []
        if extracted_data.get('smoking') == 1:
            lifestyle_risks.append('Smoking')
        if extracted_data.get('alcohol_intake') == 1:
            lifestyle_risks.append('Alcohol consumption')
        if extracted_data.get('physical_activity') == 0:
            lifestyle_risks.append('Physical inactivity')
        
        if lifestyle_risks:
            insights['lifestyle_risks'] = f'Risk factors: {", ".join(lifestyle_risks)}'
        
        # Overall risk assessment
        risk_factors = len([k for k in insights.keys() if 'risk' in k.lower()])
        if risk_factors >= 3:
            insights['overall_risk'] = 'High cardiovascular risk - recommend medical consultation'
        elif risk_factors >= 2:
            insights['overall_risk'] = 'Moderate cardiovascular risk'
        elif risk_factors >= 1:
            insights['overall_risk'] = 'Low cardiovascular risk'
        
        return insights
    
    def prepare_for_ml_model(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        UPDATED: Enhanced ML model preparation with OCR quality awareness
        """
        data = validated_data.get('validated_data', {})
        ocr_quality = validated_data.get('ocr_quality', {})
        
        # Prepare ML input with enhanced feature mapping
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
        
        # Map available fields with quality consideration
        for source_key, target_key in mapping.items():
            if source_key in data:
                ml_input[target_key] = data[source_key]
                # Add quality flags for sensitive fields
                if source_key in ['cholesterol', 'systolic_bp', 'diastolic_bp']:
                    ml_input[f'{target_key}_Quality'] = 'HIGH' if ocr_quality.get('overall_quality') in ['HIGH', 'MEDIUM'] else 'ESTIMATED'
        
        # Enhanced BMI calculation
        if 'BMI' not in ml_input and 'Height' in ml_input and 'Weight' in ml_input:
            try:
                height_m = ml_input['Height'] / 100
                ml_input['BMI'] = round(ml_input['Weight'] / (height_m ** 2), 1)
                ml_input['BMI_Source'] = 'CALCULATED'
            except:
                ml_input['BMI'] = 24.2
                ml_input['BMI_Source'] = 'DEFAULT'
        
        # Smart defaults based on available data
        defaults = self._get_smart_defaults(ml_input, data)
        
        # Apply smart defaults only for missing fields
        for field, default_info in defaults.items():
            if field not in ml_input:
                ml_input[field] = default_info['value']
                ml_input[f'{field}_Source'] = default_info['source']
                self.logger.info(f"🔧 Using {default_info['source']} for {field}: {default_info['value']}")
        
        # Ensure data types and formats
        ml_input = self._ensure_ml_data_types(ml_input)
        
        self.logger.info(f"🧠 Enhanced ML Input prepared: {len(ml_input)} features")
        return ml_input
    
    def _get_smart_defaults(self, ml_input: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEW: Get smart defaults based on available data patterns"""
        defaults = {
            'Age': {'value': 50, 'source': 'POPULATION_AVERAGE'},
            'Height': {'value': 170, 'source': 'POPULATION_AVERAGE'},
            'Weight': {'value': 70, 'source': 'POPULATION_AVERAGE'},
            'Gender': {'value': 'Male', 'source': 'ASSUMED'},
            'Systolic_BP': {'value': 120, 'source': 'NORMAL_RANGE'},
            'Diastolic_BP': {'value': 80, 'source': 'NORMAL_RANGE'},
            'Cholesterol': {'value': 200, 'source': 'BORDERLINE_RANGE'},
            'Glucose': {'value': 100, 'source': 'NORMAL_RANGE'},
            'Smoking': {'value': 0, 'source': 'ASSUMED_NEGATIVE'},
            'Alcohol_Intake': {'value': 0, 'source': 'ASSUMED_NEGATIVE'},
            'Physical_Activity': {'value': 1, 'source': 'ASSUMED_ACTIVE'},
            'BMI': {'value': 24.2, 'source': 'NORMAL_RANGE'}
        }
        
        # Adjust defaults based on available data patterns
        if 'Age' in original_data:
            age = original_data['Age']
            if age > 60:
                defaults['Cholesterol']['value'] = 220  # Slightly higher for older adults
        
        return defaults
    
    def _ensure_ml_data_types(self, ml_input: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure proper data types for ML model"""
        # Convert lifestyle factors to integers
        lifestyle_fields = ['Smoking', 'Alcohol_Intake', 'Physical_Activity']
        for field in lifestyle_fields:
            if field in ml_input:
                try:
                    ml_input[field] = int(ml_input[field])
                except (ValueError, TypeError):
                    ml_input[field] = 0
        
        # Ensure Gender is properly formatted
        if 'Gender' in ml_input:
            gender = str(ml_input['Gender']).strip().title()
            if gender not in ['Male', 'Female']:
                ml_input['Gender'] = 'Male'
        
        return ml_input
    
    def get_new_model_requirements(self) -> Dict[str, Any]:
        """Return enhanced requirements for the new ML model"""
        return {
            'critical_features': self.critical_params,
            'important_features': self.important_params,
            'lifestyle_features': self.lifestyle_params,
            'ocr_quality_indicators': self.ocr_quality_indicators,
            'all_required_features': [
                'Age', 'Height', 'Weight', 'Gender', 'Systolic_BP', 'Diastolic_BP', 
                'Cholesterol', 'Glucose', 'Smoking', 'Alcohol_Intake', 'Physical_Activity', 'BMI'
            ],
            'data_quality_levels': ['HIGH', 'MEDIUM', 'LOW', 'POOR']
        }
    
    def validate_ocr_space_integration(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        NEW: Test method to validate OCR.space integration quality
        """
        self.logger.info("🧪 Validating OCR.space integration quality...")
        
        try:
            # Clean data
            cleaned_data = self._clean_extracted_data_enhanced(extracted_data)
            
            # Assess quality
            ocr_quality = self._assess_ocr_data_quality(cleaned_data)
            completeness = self.assess_completeness_enhanced(cleaned_data, ocr_quality)
            
            # Prepare ML data
            ml_ready_data = self.prepare_for_ml_model({
                'validated_data': cleaned_data,
                'ocr_quality': ocr_quality
            })
            
            return {
                "status": "success",
                "ocr_quality_assessment": ocr_quality,
                "data_completeness": completeness,
                "cleaned_fields": list(cleaned_data.keys()),
                "ml_ready_features": list(ml_ready_data.keys()),
                "extraction_confidence": "HIGH" if ocr_quality['overall_quality'] in ['HIGH', 'MEDIUM'] else "LOW"
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space validation failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }