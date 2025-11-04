# ocr/parsers/fallback_parser.py - UPDATED WITH OCR.SPACE API
import re
import logging
from typing import Dict, Any

# Import the OCR.space reader from universal_reader
from ..universal_reader import OCRSpaceReader

class GeneralMedicalParser:
    """
    UPDATED: Fallback parser for any medical document - NOW WITH OCR.SPACE API
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # NEW: Use OCR.space API for text extraction
        self.ocr_reader = OCRSpaceReader()
        
        # UPDATED: General patterns for NEW FEATURES
        self.general_patterns = {
            'age': [
                r'age[\s:]*(\d+)',
                r'age[\s:]*(\d+)\s*years',
                r'patient[\s:]*.*age[\s:]*(\d+)'
            ],
            'height': [
                r'height[\s:]*(\d+)\s*cm',
                r'height[\s:]*(\d+)',
                r'ht[\s:]*(\d+)\s*cm'
            ],
            'weight': [
                r'weight[\s:]*(\d+)\s*kg', 
                r'weight[\s:]*(\d+)',
                r'wt[\s:]*(\d+)\s*kg'
            ],
            'gender': [
                r'gender[\s:]*([mf])',
                r'sex[\s:]*([mf])',
                r'([mf])/f'
            ],
            'systolic_bp': [
                r'bp[\s:]*(\d+)/(\d+)',
                r'blood pressure[\s:]*(\d+)/(\d+)',
                r'systolic[\s:]*(\d+)'
            ],
            'diastolic_bp': [
                r'bp[\s:]*\d+/(\d+)',
                r'blood pressure[\s:]*\d+/(\d+)',
                r'diastolic[\s:]*(\d+)'
            ],
            'cholesterol': [
                r'chol[\s:]*(\d+)',
                r'cholesterol[\s:]*(\d+)',
                r'total chol[\s:]*(\d+)'
            ],
            'glucose': [
                r'glucose[\s:]*(\d+)',
                r'blood sugar[\s:]*(\d+)',
                r'sugar[\s:]*(\d+)'
            ],
            'heart_rate': [
                r'heart rate[\s:]*(\d+)',
                r'pulse[\s:]*(\d+)',
                r'hr[\s:]*(\d+)'
            ],
            'smoking': [
                r'smoking[\s:]*([yn])',
                r'smoker[\s:]*([yn])',
                r'tobacco[\s:]*([yn])'
            ],
            'alcohol_intake': [
                r'alcohol[\s:]*([yn])',
                r'drinking[\s:]*([yn])',
                r'alcohol[\s:]*(yes|no)'
            ],
            'physical_activity': [
                r'exercise[\s:]*([yn])',
                r'physical[\s:]*activity[\s:]*([yn])',
                r'activity[\s:]*level[\s:]*([yn])'
            ]
        }
        
        self.logger.info("✅ GeneralMedicalParser UPDATED with OCR.space API")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        UPDATED: General medical document parsing with OCR.space API
        """
        self.logger.info(f"🔍 Processing general medical document with OCR.space: {image_path}")
        
        try:
            # NEW: Use OCR.space API for text extraction
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.warning("⚠️ Insufficient text extracted by OCR.space in fallback")
                return {
                    "error": "Insufficient text extracted", 
                    "document_type": "general_medical",
                    "parsing_confidence": "very_low"
                }
                
            self.logger.info(f"📝 OCR.space extracted {len(text)} chars in fallback")
            
            extracted_data = {}
            
            # Try all patterns for NEW FEATURES
            for field, patterns in self.general_patterns.items():
                value = self._extract_field_enhanced(text, patterns, field)
                if value:
                    extracted_data[field] = value
            
            # Smart BP detection from any numbers
            if 'systolic_bp' not in extracted_data or 'diastolic_bp' not in extracted_data:
                bp_data = self._smart_bp_detection(text)
                if bp_data:
                    extracted_data.update(bp_data)
            
            # Calculate BMI if height and weight available
            if 'height' in extracted_data and 'weight' in extracted_data:
                try:
                    height_cm = float(extracted_data['height'])
                    weight_kg = float(extracted_data['weight'])
                    if height_cm > 0 and weight_kg > 0:
                        height_m = height_cm / 100
                        bmi = weight_kg / (height_m ** 2)
                        extracted_data['bmi'] = round(bmi, 1)
                        self.logger.info(f"✅ BMI calculated in fallback: {bmi:.1f}")
                except Exception as e:
                    self.logger.warning(f"⚠️ BMI calculation failed in fallback: {e}")
            
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
            
            extracted_data['document_type'] = 'general_medical'
            extracted_data['text_length'] = len(text)
            extracted_data['parsing_confidence'] = 'low'
            extracted_data['parser_used'] = 'fallback_with_ocr_space'
            extracted_data['ocr_engine'] = 'ocr_space_api'
            
            self.logger.info(f"⚠️ General medical document parsed: {len(extracted_data)} fields found")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing general medical document: {e}")
            return {
                "error": str(e), 
                "document_type": "general_medical",
                "parsing_confidence": "error"
            }
    
    def _extract_text_enhanced(self, image_path: str) -> str:
        """
        NEW: Extract text using OCR.space API with enhanced cleaning
        """
        try:
            # Use OCR.space API for superior text extraction
            raw_text = self.ocr_reader.extract_text(image_path)
            
            if not raw_text:
                self.logger.warning("❌ No text extracted by OCR.space in fallback")
                return ""
            
            # Enhanced text cleaning for medical documents
            cleaned_text = self._clean_medical_text(raw_text)
            self.logger.debug(f"🧹 Fallback cleaned text sample: {cleaned_text[:200]}...")
            
            return cleaned_text.lower()
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space extraction failed in fallback: {e}")
            return ""
    
    def _clean_medical_text(self, text: str) -> str:
        """
        NEW: Enhanced cleaning for medical OCR text in fallback parser
        """
        # Common OCR corrections for medical terms
        medical_corrections = {
            'ro5': 'tsh', 'Go1': 'glucose', 'prise': 'profile',
            'coc': 'cbc', 'trh': 'tsh', 'fo': 'fbs',
            'dias': 'diastolic', 'sys': 'systolic',
            'chol': 'cholesterol', 'fbs': 'fasting blood sugar',
            'hr': 'heart rate', 'wt': 'weight', 'ht': 'height',
            'bp': 'blood pressure', 'hgt': 'height', 'wgt': 'weight',
            'yrs': 'years', 'yr': 'year', 'kg': 'kg', 'cm': 'cm',
            'male': 'm', 'female': 'f',  # Standardize gender
            'yes': 'y', 'no': 'n'  # Standardize lifestyle factors
        }
        
        cleaned_text = text.lower()
        
        # Apply medical term corrections
        for wrong, correct in medical_corrections.items():
            cleaned_text = cleaned_text.replace(wrong.lower(), correct)
        
        # Remove extra whitespace but preserve structure
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text
    
    def _extract_field_enhanced(self, text: str, patterns: list, field_name: str):
        """Enhanced field extraction with multiple patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.logger.debug(f"✅ Fallback pattern matched for {field_name}: {pattern}")
                
                if field_name in ['systolic_bp', 'diastolic_bp']:
                    value = match.group(1)
                    if self._is_valid_bp_component(field_name, value):
                        return value
                
                elif field_name in ['height', 'weight']:
                    value = match.group(1)
                    if value and value.isdigit() and self._is_valid_anthropometric(field_name, value):
                        return value
                
                elif field_name == 'gender':
                    value = match.group(1).lower()
                    return value
                
                elif field_name in ['age', 'cholesterol', 'glucose', 'heart_rate']:
                    value = match.group(1)
                    if value and value.isdigit() and self._is_valid_medical_value(field_name, value):
                        return value
                
                elif field_name in ['smoking', 'alcohol_intake', 'physical_activity']:
                    value = match.group(1).lower()
                    return value
                
                else:
                    return match.group(1)
        
        return None
    
    def _smart_bp_detection(self, text: str) -> Dict[str, Any]:
        """Smart detection of blood pressure components from context"""
        bp_data = {}
        
        # Look for BP format like "120/80"
        bp_candidates = re.findall(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
        for systolic, diastolic in bp_candidates:
            try:
                systolic_val, diastolic_val = int(systolic), int(diastolic)
                if (70 <= systolic_val <= 250 and 40 <= diastolic_val <= 150):
                    bp_data['systolic_bp'] = systolic_val
                    bp_data['diastolic_bp'] = diastolic_val
                    self.logger.info("✅ Smart BP detection successful in fallback")
                    break
            except:
                continue
        
        return bp_data
    
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
    
    def test_ocr_fallback(self, image_path: str) -> Dict[str, Any]:
        """
        NEW: Test method to verify OCR.space integration in fallback parser
        """
        self.logger.info(f"🧪 Testing OCR.space fallback with: {image_path}")
        
        try:
            # Extract raw text using OCR.space
            raw_text = self.ocr_reader.extract_text(image_path)
            
            # Clean the text
            cleaned_text = self._clean_medical_text(raw_text)
            
            # Try to extract data
            extracted_data = self.extract_data(image_path)
            
            return {
                "status": "success",
                "raw_text_length": len(raw_text),
                "cleaned_text_length": len(cleaned_text),
                "extracted_fields": list(extracted_data.keys()) if isinstance(extracted_data, dict) else [],
                "parser_type": "fallback_with_ocr_space",
                "text_preview": cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space fallback test failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "parser_type": "fallback_with_ocr_space"
            }