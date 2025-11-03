# ocr/parsers/discharge_parser.py - UPDATED FOR NEW DATASET
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class DischargeSummaryParser:
    """
    UPDATED: Parser for hospital discharge summaries - now extracts NEW FEATURES
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # UPDATED: Discharge summary patterns for NEW FEATURES
        self.discharge_patterns = {
            'age': [
                r'age[\s:]*(\d+)',
                r'age[\s:]*(\d+)\s*years',
                r'patient[\s:]*.*age[\s:]*(\d+)',
                r'dob[^:]*age[\s:]*(\d+)'
            ],
            'height': [
                r'height[\s:]*(\d+)\s*cm',
                r'height[\s:]*(\d+)',
                r'ht[\s:]*(\d+)\s*cm'
            ],
            'weight': [
                r'weight[\s:]*(\d+)\s*kg',
                r'weight[\s:]*(\d+)',
                r'wt[\s:]*(\d+)\s*kg',
                r'admission weight[\s:]*(\d+)'
            ],
            'gender': [
                r'gender[\s:]*([mf])',
                r'sex[\s:]*([mf])',
                r'([mf])/f',
                r'gender\s*[=:]?\s*(male|female)'
            ],
            'systolic_bp': [
                r'bp[\s:]*(\d+)/(\d+)',
                r'blood pressure[\s:]*(\d+)/(\d+)',
                r'systolic[\s:]*(\d+)',
                r'admission bp[\s:]*(\d+)/(\d+)',
                r'vitals.*?bp[\s:]*(\d+)/(\d+)'
            ],
            'diastolic_bp': [
                r'bp[\s:]*\d+/(\d+)',
                r'blood pressure[\s:]*\d+/(\d+)',
                r'diastolic[\s:]*(\d+)'
            ],
            'cholesterol': [
                r'cholesterol[\s:]*(\d+)',
                r'chol[\s:]*(\d+)',
                r'lipid[\s:]*panel.*?chol[\s:]*(\d+)',
                r'labs.*?chol[\s:]*(\d+)'
            ],
            'glucose': [
                r'glucose[\s:]*(\d+)',
                r'blood sugar[\s:]*(\d+)',
                r'fbs[\s:]*(\d+)',
                r'labs.*?glucose[\s:]*(\d+)'
            ],
            'heart_rate': [
                r'heart rate[\s:]*(\d+)',
                r'hr[\s:]*(\d+)',
                r'pulse[\s:]*(\d+)',
                r'vitals.*?hr[\s:]*(\d+)'
            ],
            'smoking': [
                r'smoking[\s:]*([yn])',
                r'smoker[\s:]*([yn])',
                r'tobacco[\s:]*([yn])',
                r'smoking[\s:]*(yes|no)',
                r'social history.*?smok(?:ing|er)[\s:]*([yn])'
            ],
            'alcohol_intake': [
                r'alcohol[\s:]*([yn])',
                r'drinking[\s:]*([yn])',
                r'alcohol[\s:]*(yes|no)',
                r'social history.*?alcohol[\s:]*([yn])'
            ],
            'physical_activity': [
                r'exercise[\s:]*([yn])',
                r'physical[\s:]*activity[\s:]*([yn])',
                r'activity[\s:]*level[\s:]*([yn])'
            ],
            'diagnosis': [
                r'diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'final diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'discharge diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
            ],
            'medications': [
                r'medications?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'discharge medications?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'meds[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
            ]
        }
        
        self.logger.info("✅ DischargeSummaryParser UPDATED for new dataset features")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        UPDATED: Extract data from discharge summaries with NEW FEATURES
        """
        self.logger.info(f"🏥 Processing discharge summary with NEW FEATURES: {image_path}")
        
        try:
            text = self._extract_text(image_path)
            extracted_data = {}
            
            # Extract structured data for NEW FEATURES
            for field, patterns in self.discharge_patterns.items():
                value = self._extract_field_enhanced(text, patterns, field)
                if value:
                    extracted_data[field] = value
            
            # Calculate BMI if height and weight available
            if 'height' in extracted_data and 'weight' in extracted_data:
                try:
                    height_cm = float(extracted_data['height'])
                    weight_kg = float(extracted_data['weight'])
                    if height_cm > 0 and weight_kg > 0:
                        height_m = height_cm / 100
                        bmi = weight_kg / (height_m ** 2)
                        extracted_data['bmi'] = round(bmi, 1)
                        self.logger.info(f"✅ BMI calculated from discharge summary: {bmi:.1f}")
                except Exception as e:
                    self.logger.warning(f"⚠️ BMI calculation failed in discharge parser: {e}")
            
            # Standardize gender format
            if 'gender' in extracted_data:
                gender = extracted_data['gender'].lower()
                if gender in ['m', 'male']:
                    extracted_data['gender'] = 'Male'
                elif gender in ['f', 'female']:
                    extracted_data['gender'] = 'Female'
            
            # Convert lifestyle factors to binary
            lifestyle_fields = ['smoking', 'alcohol_intake', 'physical_activity']
            for field in lifestyle_fields:
                if field in extracted_data:
                    value = extracted_data[field].lower()
                    if value in ['y', 'yes', '1']:
                        extracted_data[field] = 1
                    else:
                        extracted_data[field] = 0
            
            # Extract context from diagnosis for additional insights
            if 'diagnosis' in extracted_data:
                diagnosis_insights = self._extract_diagnosis_insights(extracted_data['diagnosis'])
                extracted_data.update(diagnosis_insights)
            
            extracted_data['document_type'] = 'discharge_summary'
            extracted_data['text_snippet'] = text[:300] + "..." if len(text) > 300 else text
            extracted_data['parsing_confidence'] = 'medium'
            
            self.logger.info(f"✅ Discharge summary parsed: {len(extracted_data)} NEW fields found")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing discharge summary: {e}")
            return {"error": str(e), "document_type": "discharge_summary"}
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from discharge summary"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            self.logger.debug(f"📝 Discharge summary OCR: {len(text)} chars")
            return text.lower()
        except Exception as e:
            self.logger.error(f"❌ Discharge summary OCR failed: {e}")
            return ""
    
    def _extract_field_enhanced(self, text: str, patterns: list, field_name: str):
        """Enhanced field extraction with multiple patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                self.logger.debug(f"✅ Discharge pattern matched for {field_name}: {pattern}")
                
                if field_name in ['systolic_bp', 'diastolic_bp']:
                    # Handle BP components
                    if field_name == 'systolic_bp' and match.lastindex >= 1:
                        value = match.group(1)
                    elif field_name == 'diastolic_bp' and match.lastindex >= 2:
                        value = match.group(2) if match.group(2) else match.group(1)
                    else:
                        value = match.group(1)
                    
                    if value and self._is_valid_bp_component(field_name, value):
                        return value
                
                elif field_name in ['height', 'weight']:
                    value = match.group(1)
                    if value and value.isdigit() and self._is_valid_anthropometric(field_name, value):
                        return value
                
                elif field_name == 'gender':
                    value = match.group(1).lower() if match.lastindex >= 1 else None
                    if value and value in ['m', 'f', 'male', 'female']:
                        return value
                
                elif field_name in ['age', 'cholesterol', 'glucose', 'heart_rate']:
                    value = match.group(1)
                    if value and value.isdigit() and self._is_valid_medical_value(field_name, value):
                        return value
                
                elif field_name in ['smoking', 'alcohol_intake', 'physical_activity']:
                    value = match.group(1).lower() if match.lastindex >= 1 else None
                    if value and value in ['y', 'n', 'yes', 'no']:
                        return value
                
                elif field_name in ['diagnosis', 'medications']:
                    value = match.group(1).strip() if match.lastindex >= 1 else None
                    if value and len(value) > 5:  # Reasonable length for diagnosis/meds
                        return value
                
                else:
                    return match.group(1) if match.lastindex >= 1 else None
        
        return None
    
    def _extract_diagnosis_insights(self, diagnosis_text: str) -> Dict[str, Any]:
        """Extract additional insights from diagnosis text"""
        insights = {}
        diagnosis_lower = diagnosis_text.lower()
        
        # Check for cardiovascular conditions
        cardio_terms = [
            'coronary', 'myocardial', 'heart failure', 'cardiomyopathy',
            'arrhythmia', 'tachycardia', 'hypertension', 'hyperlipidemia',
            'atherosclerosis', 'cad', 'chf'
        ]
        
        found_conditions = [term for term in cardio_terms if term in diagnosis_lower]
        if found_conditions:
            insights['cardiovascular_conditions'] = found_conditions
            insights['has_heart_condition'] = True
        else:
            insights['has_heart_condition'] = False
        
        # Check for diabetes
        if any(term in diagnosis_lower for term in ['diabetes', 'dm', 'hyperglycemia']):
            insights['has_diabetes'] = True
        else:
            insights['has_diabetes'] = False
        
        return insights
    
    def _is_valid_bp_component(self, bp_type: str, value: str) -> bool:
        """Validate blood pressure components"""
        try:
            num_val = int(value)
            if bp_type == 'systolic_bp':
                return 70 <= num_val <= 250
            elif bp_type == 'diastolic_bp':
                return 40 <= num_val <= 150
            return False
        except:
            return False
    
    def _is_valid_anthropometric(self, field: str, value: str) -> bool:
        """Validate height and weight values"""
        try:
            num_val = int(value)
            if field == 'height':
                return 100 <= num_val <= 250
            elif field == 'weight':
                return 30 <= num_val <= 200
            return False
        except:
            return False
    
    def _is_valid_medical_value(self, field: str, value: str) -> bool:
        """Validate if extracted medical values are reasonable"""
        try:
            num_val = int(value)
            
            validation_ranges = {
                'age': (1, 120),
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
    
    def get_supported_features(self) -> list:
        """Return list of supported features for the new dataset"""
        return [
            'age', 'height', 'weight', 'gender', 'systolic_bp', 'diastolic_bp',
            'cholesterol', 'glucose', 'heart_rate', 'smoking', 'alcohol_intake', 
            'physical_activity', 'bmi', 'diagnosis', 'medications'
        ]