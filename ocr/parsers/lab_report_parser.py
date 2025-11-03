# ocr/parsers/lab_report_parser.py - UPDATED FOR NEW DATASET
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class LabReportParser:
    """
    UPDATED parser for laboratory reports - NOW WITH NEW DATASET FEATURES
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # UPDATED MEDICAL PATTERNS FOR NEW FEATURES
        self.medical_patterns = {
            'age': [
                r'age[\s:]*(\d+)',
                r'age[\s:]*(\d+)\s*years',
                r'patient[\s:]*.*age[\s:]*(\d+)',
                r'dob[^:]*age[\s:]*(\d+)',
                r'age\s*[=:]?\s*(\d+)'
            ],
            'height': [
                r'height[\s:]*(\d+)\s*cm',
                r'height[\s:]*(\d+)',
                r'ht[\s:]*(\d+)\s*cm',
                r'height[\s:]*(\d+)\s*centimeters',
                r'height\s*[=:]?\s*(\d+)\s*cm',
                r'(\d+)\s*cm\s*height',  # "170 cm height"
                r'height[^\d]{0,10}(\d{3})'  # Aggressive search
            ],
            'weight': [
                r'weight[\s:]*(\d+)\s*kg',
                r'weight[\s:]*(\d+)',
                r'wt[\s:]*(\d+)\s*kg',
                r'weight[\s:]*(\d+)\s*kilograms',
                r'weight\s*[=:]?\s*(\d+)\s*kg',
                r'(\d+)\s*kg\s*weight',  # "70 kg weight"
                r'weight[^\d]{0,10}(\d{2,3})'  # Aggressive search
            ],
            'gender': [
                r'gender[\s:]*([mf])',
                r'sex[\s:]*([mf])',
                r'patient[\s:]*.*([mf])ale',
                r'([mf])/f',  # M/F format
                r'gender\s*[=:]?\s*(male|female)',
                r'sex\s*[=:]?\s*(male|female)'
            ],
            'systolic_bp': [
                r'bp[\s:]*(\d+)/(\d+)',
                r'blood pressure[\s:]*(\d+)/(\d+)',
                r'systolic[\s:]*(\d+)',
                r'sys[\s:]*(\d+)',
                r'blood[\s:]*pressure[\s:]*(\d+)\s*/\s*\d+',  # Capture systolic only
                r'(\d{2,3})/\d+\s*mmhg',  # "120/80 mmHg" - capture 120
                r'systolic\s*[=:]?\s*(\d+)'
            ],
            'diastolic_bp': [
                r'bp[\s:]*\d+/(\d+)',
                r'blood pressure[\s:]*\d+/(\d+)',
                r'diastolic[\s:]*(\d+)',
                r'dias[\s:]*(\d+)',
                r'blood[\s:]*pressure[\s:]*\d+\s*/\s*(\d+)',  # Capture diastolic only
                r'\d+/(\d+)\s*mmhg',  # "120/80 mmHg" - capture 80
                r'diastolic\s*[=:]?\s*(\d+)'
            ],
            'cholesterol': [
                r'chol[\s:]*(\d+)',
                r'cholesterol[\s:]*(\d+)',
                r'total chol[\s:]*(\d+)',
                r'total cholesterol[\s:]*(\d+)',
                r'chol\.?[\s:]*(\d+)',
                r'cholesterol[\s:]*(\d+)\s*mg/dl',
                r'chol[\s:]*(\d+)\s*mg',
                r'ch[o0]l[\s:]*(\d+)'
            ],
            'glucose': [
                r'glucose[\s:]*(\d+)',
                r'blood sugar[\s:]*(\d+)',
                r'fbs[\s:]*(\d+)',
                r'fasting glucose[\s:]*(\d+)',
                r'sugar[\s:]*(\d+)',
                r'glucose\s*level[\s:]*(\d+)',
                r'blood\s*glucose[\s:]*(\d+)'
            ],
            'heart_rate': [
                r'hr[\s:]*(\d+)',
                r'heart rate[\s:]*(\d+)',
                r'pulse[\s:]*(\d+)',
                r'pulse rate[\s:]*(\d+)',
                r'heart\s*rate\s*[=:]?\s*(\d+)'
            ],
            'smoking': [
                r'smoking[\s:]*([yn])',
                r'smoker[\s:]*([yn])',
                r'tobacco[\s:]*([yn])',
                r'smoking\s*status[\s:]*([yn])',
                r'smoking[\s:]*(yes|no)',
                r'smoker[\s:]*(yes|no)'
            ],
            'alcohol_intake': [
                r'alcohol[\s:]*([yn])',
                r'drinking[\s:]*([yn])',
                r'alcohol[\s:]*(yes|no)',
                r'drinking[\s:]*(yes|no)',
                r'alcohol\s*use[\s:]*([yn])'
            ],
            'physical_activity': [
                r'exercise[\s:]*([yn])',
                r'physical[\s:]*activity[\s:]*([yn])',
                r'activity[\s:]*level[\s:]*([yn])',
                r'exercise[\s:]*(yes|no)',
                r'active[\s:]*lifestyle[\s:]*([yn])'
            ]
        }
        
        self.logger.info("🎯 UPDATED LabReportParser initialized for NEW DATASET FEATURES!")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract medical data from lab report images - UPDATED FOR NEW FEATURES
        """
        self.logger.info(f"🔬 Processing lab report: {image_path}")
        
        try:
            # Extract text using OCR
            text = self._extract_text(image_path)
            self.logger.info(f"📝 Raw text extracted: {len(text)} characters")
            
            # Parse medical data using updated pattern matching
            extracted_data = {}
            for field, patterns in self.medical_patterns.items():
                value = self._extract_field_enhanced(text, patterns, field)
                if value:
                    extracted_data[field] = value
            
            # Calculate BMI if height and weight are available
            if 'height' in extracted_data and 'weight' in extracted_data:
                try:
                    height_cm = float(extracted_data['height'])
                    weight_kg = float(extracted_data['weight'])
                    if height_cm > 0 and weight_kg > 0:
                        height_m = height_cm / 100
                        bmi = weight_kg / (height_m ** 2)
                        extracted_data['bmi'] = round(bmi, 1)
                        self.logger.info(f"✅ BMI calculated: {bmi:.1f}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not calculate BMI: {e}")
            
            # Convert gender to standardized format
            if 'gender' in extracted_data:
                extracted_data['gender'] = self._standardize_gender(extracted_data['gender'])
            
            # Convert lifestyle factors to binary (0/1)
            lifestyle_fields = ['smoking', 'alcohol_intake', 'physical_activity']
            for field in lifestyle_fields:
                if field in extracted_data:
                    extracted_data[field] = self._convert_to_binary(extracted_data[field])
            
            self.logger.info(f"✅ Lab report parsed: {len(extracted_data)} fields found")
            self.logger.info(f"📋 Extracted fields: {list(extracted_data.keys())}")
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing lab report: {e}")
            return {"error": str(e)}
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            self.logger.debug(f"Raw OCR text: {text}")
            return text.lower()
        except Exception as e:
            self.logger.error(f"❌ OCR extraction failed: {e}")
            return ""
    
    def _extract_field_enhanced(self, text: str, patterns: list, field_name: str):
        """
        Enhanced field extraction for new features
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.logger.debug(f"✅ Pattern matched for {field_name}: {pattern}")
                
                if field_name in ['systolic_bp', 'diastolic_bp']:
                    # Handle blood pressure components
                    value = match.group(1)
                    if self._is_valid_bp_component(field_name, value):
                        return value
                
                elif field_name in ['height', 'weight']:
                    # Handle height/weight with validation
                    value = match.group(1)
                    if value and value.isdigit():
                        if self._is_valid_anthropometric(field_name, value):
                            return value
                
                elif field_name == 'gender':
                    # Handle gender extraction
                    value = match.group(1).lower()
                    if len(value) == 1:  # Single char (m/f)
                        return value
                    else:  # Full word (male/female)
                        return value[0]  # Return first char
                
                elif field_name in ['smoking', 'alcohol_intake', 'physical_activity']:
                    # Handle lifestyle factors
                    value = match.group(1).lower()
                    return value
                
                elif field_name in ['age', 'cholesterol', 'glucose', 'heart_rate']:
                    # Handle numeric medical values
                    value = match.group(1)
                    if value and value.isdigit():
                        if self._is_valid_medical_value(field_name, value):
                            return value
                
                else:
                    # For other fields
                    return match.group(1)
        
        self.logger.debug(f"❌ No pattern matched for {field_name}")
        return None
    
    def _standardize_gender(self, gender_input: str) -> str:
        """Convert gender input to standardized format"""
        gender_map = {
            'm': 'Male', 'male': 'Male',
            'f': 'Female', 'female': 'Female'
        }
        standardized = gender_map.get(gender_input.lower(), 'Male')  # Default to Male
        self.logger.info(f"🔤 Gender standardized: {gender_input} → {standardized}")
        return standardized
    
    def _convert_to_binary(self, value: str) -> int:
        """Convert yes/no to binary (1/0)"""
        binary_map = {
            'y': 1, 'yes': 1, '1': 1,
            'n': 0, 'no': 0, '0': 0
        }
        result = binary_map.get(value.lower(), 0)  # Default to 0 (No)
        self.logger.info(f"🔢 Binary conversion: {value} → {result}")
        return result
    
    def _is_valid_bp_component(self, field: str, value: str) -> bool:
        """Validate blood pressure components"""
        try:
            num_val = int(value)
            if field == 'systolic_bp':
                return 70 <= num_val <= 250
            elif field == 'diastolic_bp':
                return 40 <= num_val <= 150
            return False
        except:
            return False
    
    def _is_valid_anthropometric(self, field: str, value: str) -> bool:
        """Validate height and weight values"""
        try:
            num_val = int(value)
            if field == 'height':
                return 100 <= num_val <= 250  # 100cm to 250cm
            elif field == 'weight':
                return 30 <= num_val <= 200   # 30kg to 200kg
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
            'physical_activity', 'bmi'
        ]
    
    def _debug_pattern_matching(self, text: str):
        """Debug method to see what patterns are matching"""
        self.logger.info("🔍 DEBUG - Pattern Matching Analysis:")
        
        for field, patterns in self.medical_patterns.items():
            matched = False
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    self.logger.info(f"  ✅ {field}: '{pattern}' → '{match.group()}'")
                    matched = True
                    break
            
            if not matched:
                self.logger.info(f"  ❌ {field}: No pattern matched")
    
    def get_extraction_stats(self, text: str) -> Dict[str, Any]:
        """Detailed extraction statistics for debugging"""
        stats = {
            'total_patterns': 0,
            'matched_patterns': 0,
            'pattern_details': {},
            'supported_features': self.get_supported_features()
        }
        
        for field, patterns in self.medical_patterns.items():
            stats['total_patterns'] += len(patterns)
            stats['pattern_details'][field] = {}
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, text, re.IGNORECASE)
                stats['pattern_details'][field][f'pattern_{i}'] = {
                    'pattern': pattern,
                    'matched': bool(match),
                    'value': match.group(1) if match else None
                }
                if match:
                    stats['matched_patterns'] += 1
        
        return stats