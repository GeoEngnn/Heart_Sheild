# ocr/parsers/lab_report_parser.py
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class LabReportParser:
    """
    SUPER-ENHANCED parser for laboratory reports and blood test results
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # SUPER-ENHANCED MEDICAL PATTERNS - Maximum coverage!
        self.medical_patterns = {
            'age': [
                r'age[\s:]*(\d+)',
                r'age[\s:]*(\d+)\s*years',
                r'patient[\s:]*.*age[\s:]*(\d+)',
                r'dob[^:]*age[\s:]*(\d+)',  # Date of birth context
                r'age\s*[=:]?\s*(\d+)'  # Handles "Age = 45"
            ],
            'cholesterol': [
                # Basic patterns
                r'chol[\s:]*(\d+)',
                r'cholesterol[\s:]*(\d+)',
                r'total chol[\s:]*(\d+)', 
                r'total cholesterol[\s:]*(\d+)',
                
                # With punctuation variations
                r'chol\.?[\s:]*(\d+)',
                r'cholesterol\.?[\s:]*(\d+)',
                
                # Common abbreviations and typos
                r'cholest?[\s:]*(\d+)',
                r'chol[\s]*esterol[\s:]*(\d+)',
                
                # With units and labels
                r'cholesterol[\s:]*(\d+)\s*mg/dl',
                r'chol[\s:]*(\d+)\s*mg',
                r'total[\s]+chol[\s:]*(\d+)',
                
                # OCR error resistant patterns
                r'ch[o0]l[\s:]*(\d+)',  # Handles o/0 confusion
                r'cholesterol[\s:]*[^\d]*(\d+)',  # Handles extra characters
                r'cholest[ae]rol[\s:]*(\d+)',  # Handles a/e OCR errors
                
                # Very permissive pattern as last resort
                r'chol[^\d]{0,5}(\d{2,4})',  # Matches "chol" followed by numbers within 2-4 digits
                
                # Context-based patterns
                r'cholesterol\s*result[\s:]*(\d+)',
                r'chol\s*level[\s:]*(\d+)',
                
                # Final fallback - look for numbers near "chol"
                r'chol[^\d]*?(\d{2,4})(?=\s*(mg|$))'
            ],
            'blood_pressure': [
                r'bp[\s:]*(\d+)/(\d+)',
                r'blood pressure[\s:]*(\d+)/(\d+)',
                r'blood[\s:]*pressure[\s:]*(\d+)/(\d+)',
                r'pressure[\s:]*(\d+)/(\d+)',
                r'b[\s]?p[\s:]*(\d+)/(\d+)',  # Handles "b p: 120/80"
                r'bp\s*[=:]?\s*(\d+)/(\d+)'  # Handles "BP = 120/80"
            ],
            'heart_rate': [
                r'hr[\s:]*(\d+)',
                r'heart rate[\s:]*(\d+)',
                r'heart[\s:]*rate[\s:]*(\d+)',
                r'pulse[\s:]*(\d+)',
                r'pulse rate[\s:]*(\d+)',
                r'heart\s*rate\s*[=:]?\s*(\d+)'
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
            'hdl': [
                r'hdl[\s:]*(\d+)',
                r'hdl cholesterol[\s:]*(\d+)',
                r'hdl[\s:]*(\d+)\s*mg/dl',
                r'high-density lipoprotein[\s:]*(\d+)'
            ],
            'ldl': [
                r'ldl[\s:]*(\d+)', 
                r'ldl cholesterol[\s:]*(\d+)',
                r'ldl[\s:]*(\d+)\s*mg/dl',
                r'low-density lipoprotein[\s:]*(\d+)'
            ]
        }
        
        self.logger.info("🎯 SUPER-ENHANCED LabReportParser initialized with maximum pattern coverage!")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract medical data from lab report images using super-enhanced pattern matching
        """
        self.logger.info(f"🔬 Processing lab report: {image_path}")
        
        try:
            # Extract text using OCR
            text = self._extract_text(image_path)
            self.logger.info(f"📝 Raw text extracted: {len(text)} characters")
            
            # DEBUG: Log what patterns are matching
            self._debug_pattern_matching(text)
            
            # Parse medical data using enhanced pattern matching
            extracted_data = {}
            for field, patterns in self.medical_patterns.items():
                value = self._extract_field_enhanced(text, patterns, field)
                if value:
                    extracted_data[field] = value
            
            # Additional smart extraction for common medical formats
            if 'blood_pressure' not in extracted_data:
                bp_casual = self._extract_casual_bp(text)
                if bp_casual:
                    extracted_data['blood_pressure'] = bp_casual
                    self.logger.info("✅ Casual BP extraction successful")
            
            # Final cholesterol fallback - aggressive search
            if 'cholesterol' not in extracted_data:
                chol_fallback = self._aggressive_cholesterol_search(text)
                if chol_fallback:
                    extracted_data['cholesterol'] = chol_fallback
                    self.logger.info("✅ Aggressive cholesterol search successful")
            
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
            return text.lower()  # Convert to lowercase for easier matching
        except Exception as e:
            self.logger.error(f"❌ OCR extraction failed: {e}")
            return ""
    
    def _extract_field_enhanced(self, text: str, patterns: list, field_name: str):
        """
        Enhanced field extraction - tries multiple patterns with priority
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.logger.debug(f"✅ Pattern matched for {field_name}: {pattern}")
                
                if field_name == 'blood_pressure':
                    # Handle blood pressure format
                    systolic, diastolic = match.group(1), match.group(2)
                    if self._is_valid_bp(systolic, diastolic):
                        return f"{systolic}/{diastolic}"
                
                elif field_name in ['age', 'cholesterol', 'heart_rate', 'glucose', 'hdl', 'ldl']:
                    # Return the first captured group for numeric values
                    value = match.group(1)
                    if value and value.isdigit():
                        # Validate reasonable ranges
                        if self._is_valid_medical_value(field_name, value):
                            return value
                
                else:
                    # For other fields, return the first match
                    return match.group(1)
        
        self.logger.debug(f"❌ No pattern matched for {field_name}")
        return None
    
    def _aggressive_cholesterol_search(self, text: str):
        """
        SUPER-AGGRESSIVE cholesterol search as final fallback
        """
        # Look for any 3-digit number near cholesterol-related terms
        aggressive_patterns = [
            r'chol[^\d]{0,10}(\d{3})',  # "chol" followed by 3-digit number within 10 chars
            r'cholest[^\d]{0,10}(\d{3})',
            r'lipid[^\d]{0,15}(\d{3})',  # "lipid" context
            r'(\d{3})(?=\s*(mg|mg/dl|mg\s*dl))'  # 3-digit number followed by mg units
        ]
        
        for pattern in aggressive_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1)
                if value.isdigit() and 100 <= int(value) <= 400:  # Reasonable cholesterol range
                    self.logger.info(f"🎯 Aggressive cholesterol found: {value}")
                    return value
        
        return None
    
    def _extract_casual_bp(self, text: str):
        """
        Extract blood pressure mentioned in casual format like "120/80"
        """
        bp_pattern = r'(\d{2,3})\s*/\s*(\d{2,3})'
        matches = re.findall(bp_pattern, text)
        
        for systolic, diastolic in matches:
            if self._is_valid_bp(systolic, diastolic):
                self.logger.debug(f"✅ Casual BP found: {systolic}/{diastolic}")
                return f"{systolic}/{diastolic}"
        
        return None
    
    def _is_valid_bp(self, systolic: str, diastolic: str) -> bool:
        """
        Validate if the numbers are reasonable blood pressure values
        """
        try:
            sys_val = int(systolic)
            dia_val = int(diastolic)
            
            # Reasonable BP ranges
            return (70 <= sys_val <= 250) and (40 <= dia_val <= 150)
        except:
            return False
    
    def _is_valid_medical_value(self, field: str, value: str) -> bool:
        """
        Validate if extracted medical values are reasonable
        """
        try:
            num_val = int(value)
            
            validation_ranges = {
                'age': (1, 120),
                'cholesterol': (100, 400),
                'heart_rate': (40, 200),
                'glucose': (50, 300),
                'hdl': (20, 100),
                'ldl': (50, 300)
            }
            
            if field in validation_ranges:
                min_val, max_val = validation_ranges[field]
                return min_val <= num_val <= max_val
            
            return True  # No validation for other fields
            
        except:
            return False
    
    def _debug_pattern_matching(self, text: str):
        """
        Debug method to see what patterns are matching
        """
        self.logger.info("🔍 DEBUG - Pattern Matching Analysis:")
        
        for field, patterns in self.medical_patterns.items():
            matched = False
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    self.logger.info(f"  ✅ {field}: '{pattern}' → '{match.group(1)}'")
                    matched = True
                    break
            
            if not matched:
                self.logger.info(f"  ❌ {field}: No pattern matched")
    
    def get_extraction_stats(self, text: str) -> Dict[str, Any]:
        """
        Detailed extraction statistics for debugging
        """
        stats = {
            'total_patterns': 0,
            'matched_patterns': 0,
            'pattern_details': {}
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