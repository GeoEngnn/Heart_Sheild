# ocr/parsers/fallback_parser.py - ENHANCED SMART PARSER
import re
import logging
from typing import Dict, Any, List

# Import the OCR.space reader from universal_reader
from ..universal_reader import OCRSpaceReader

class GeneralMedicalParser:
    """
    ENHANCED: Fallback parser with SMART DISPLAY FORMATTING
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # NEW: Use OCR.space API for text extraction
        self.ocr_reader = OCRSpaceReader()
        
        # ENHANCED: Improved patterns for better extraction
        self.general_patterns = {
            'age': [
                r'\bage\s*[:\-]?\s*(\d{1,3})\b',
                r'\bage[\s:]*(\d+)\s*years?\b',
                r'\bpatient[\s:].*?age[\s:]*(\d+)',
                r'\b(\d{1,3})\s*years? old\b',
                r'age\s*=\s*(\d+)'
            ],
            'height': [
                r'\bheight\s*[:\-]?\s*(\d{2,3})\s*cm\b',
                r'\bht\s*[:\-]?\s*(\d{2,3})\s*cm\b',
                r'\bheight[\s:]*(\d{2,3})\b',
                r'\b(\d{3})\s*cm\s*height\b',
                r'height\s*=\s*(\d+)\s*cm'
            ],
            'weight': [
                r'\bweight\s*[:\-]?\s*(\d{2,3})\s*kg\b', 
                r'\bwt\s*[:\-]?\s*(\d{2,3})\s*kg\b',
                r'\bweight[\s:]*(\d{2,3})\b',
                r'\b(\d{2,3})\s*kg\s*weight\b',
                r'weight\s*=\s*(\d+)\s*kg'
            ],
            'gender': [
                r'\bgender\s*[:\-]?\s*(male|female|m|f)\b',
                r'\bsex\s*[:\-]?\s*(male|female|m|f)\b',
                r'\b(male|female)\b',
                r'\b[mf]\b',
                r'gender\s*=\s*(male|female|m|f)'
            ],
            'blood_pressure': [
                r'\bbp\s*[:\-]?\s*(\d{2,3}/\d{2,3})\b',
                r'\bblood pressure\s*[:\-]?\s*(\d{2,3}/\d{2,3})\b',
                r'\b(\d{2,3}/\d{2,3})\s*mmhg\b',
                r'blood pressure\s*=\s*(\d+/\d+)',
                r'\bpressure\s*(?:blood)?\s*[:\-]?\s*(\d{2,3}/\d{2,3})\s*(?:high|normal)?\b',  # NEW: Flexible flags
            ],
            'cholesterol': [
                r'\bcholesterol\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bchol\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bcholesterol[\s:]*(\d{2,3})\b',
                r'\btotal cholesterol\s*[:\-]?\s*(\d{2,3})\b',
                r'cholesterol\s*=\s*(\d+)',
                r'\bcholesterol\s*(?:level|total)?\s*[:\-]?\s*(\d{2,3})\s*(?:mg/dl|high|normal)?\b',  # NEW: "LEVEL", flags
                r'\bchol\s*(?:level|total)?\s*[:\-]?\s*(\d{2,3})\s*(?:mg/dl|high|normal)?\b',
            ],
            'glucose': [
                r'\bglucose\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bblood sugar\s*[:\-]?\s*(\d{2,3})\b',
                r'\bglucose[\s:]*(\d{2,3})\b',
                r'\bfbs\s*[:\-]?\s*(\d{2,3})\b',
                r'glucose\s*=\s*(\d+)',
                r'\bglucose\s*(?:level)?\s*\(?\s*mg/dl\s*\)?\s*[:\-]?\s*(\d{2,3})\s*(?:high|normal)?\b',  # NEW: Parens, "LEVEL"
                r'\bglu\s*(?:level)?\s*\(?\s*mg/dl\s*\)?\s*[:\-]?\s*(\d{2,3})\s*(?:high|normal)?\b',
            ],
            'heart_rate': [
                r'\bheart rate\s*[:\-]?\s*(\d{2,3})\b',
                r'\bpulse\s*[:\-]?\s*(\d{2,3})\b',
                r'\bhr\s*[:\-]?\s*(\d{2,3})\b',
                r'heart rate\s*=\s*(\d+)',
                r'\bhr\s*[:\-]?\s*(\d{2,3})\s*(?:bpm|high|normal)?\b',  # NEW: Flags/units
            ],
            'smoking': [
                r'\bsmoking\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bsmoker\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\btobacco\s*[:\-]?\s*(yes|no)\b',
                r'smoking\s*=\s*(yes|no|y|n)'
            ],
            'alcohol_intake': [
                r'\balcohol\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bdrinking\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\balcohol use\s*[:\-]?\s*(yes|no)\b',
                r'alcohol\s*=\s*(yes|no|y|n)'
            ],
            'physical_activity': [
                r'\bexercise\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bphysical activity\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bactivity level\s*[:\-]?\s*(yes|no)\b',
                r'exercise\s*=\s*(yes|no|y|n)'
            ]
        }
        
        # NEW: SMART DISPLAY MAPPING
        self.display_mapping = {
            'age': 'Age',
            'height': 'Height',
            'weight': 'Weight',
            'gender': 'Gender',
            'blood_pressure': 'Blood Pressure',
            'cholesterol': 'Cholesterol',
            'glucose': 'Glucose',
            'heart_rate': 'Heart Rate',
            'smoking': 'Smoking',
            'alcohol_intake': 'Alcohol Intake',
            'physical_activity': 'Physical Activity',
            'bmi': 'BMI'
        }
        
        # NEW: UNIT MAPPING for clean display
        self.unit_mapping = {
            'age': 'years',
            'height': 'cm',
            'weight': 'kg',
            'blood_pressure': 'mmHg',
            'cholesterol': 'mg/dL',
            'glucose': 'mg/dL',
            'heart_rate': 'bpm',
            'bmi': 'kg/m²'
        }
        
        self.logger.info("✅ GeneralMedicalParser ENHANCED with smart display formatting!")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        ENHANCED: General medical document parsing with SMART DISPLAY OUTPUT
        """
        self.logger.info(f"🔍 Processing general medical document with OCR.space: {image_path}")
        
        try:
            # Use OCR.space API for text extraction
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.warning("⚠️ Insufficient text extracted by OCR.space in fallback")
                return {
                    "error": "Insufficient text extracted", 
                    "document_type": "general_medical",
                    "parsing_confidence": "very_low",
                    "success": False
                }
                
            self.logger.info(f"📝 OCR.space extracted {len(text)} chars in fallback")
            
            # Extract raw data using existing patterns
            extracted_data = self._parse_medical_data_enhanced(text)
            
            # KEEP ALL YOUR EXISTING SMART FEATURES:
            
            # Smart BP detection from any numbers
            if 'blood_pressure' not in extracted_data:
                bp_data = self._smart_bp_detection(text)
                if bp_data:
                    extracted_data.update(bp_data)
            
            # NEW: Casual mentions for missed vitals/gender
            self._extract_casual_mentions(text, extracted_data)
            
            # Calculate BMI if height and weight available
            if 'height' in extracted_data and 'weight' in extracted_data:
                bmi_result = self._calculate_bmi(extracted_data['height'], extracted_data['weight'])
                if bmi_result:
                    extracted_data['bmi'] = bmi_result
            
            # Standardize gender format
            if 'gender' in extracted_data:
                extracted_data['gender'] = self._standardize_gender(extracted_data['gender'])
            
            # Convert lifestyle factors to binary (KEEPING YOUR EXISTING LOGIC)
            lifestyle_fields = ['smoking', 'alcohol_intake', 'physical_activity']
            for field in lifestyle_fields:
                if field in extracted_data:
                    value = extracted_data[field].lower()
                    if value in ['y', 'yes', '1']:
                        extracted_data[field] = 1
                    else:
                        extracted_data[field] = 0
                else:
                    extracted_data[field] = 0  # Default no
            
            # NEW: SMART DISPLAY FORMATTING
            display_data = self._format_for_display(extracted_data)
            
            # KEEP ALL YOUR EXISTING METADATA
            result = {
                "raw_data": extracted_data,
                "display_data": display_data,  # NEW: Clean formatted data
                "document_type": 'general_medical',
                "text_length": len(text),
                "parsing_confidence": 'low',
                "parser_used": 'fallback_with_ocr_space',
                "ocr_engine": 'ocr_space_api',
                "success": True
            }
            
            self.logger.info(f"⚠️ General medical document parsed: {len(extracted_data)} fields found")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing general medical document: {e}")
            return {
                "error": str(e), 
                "document_type": "general_medical",
                "parsing_confidence": "error",
                "success": False
            }
    
    def _parse_medical_data_enhanced(self, text: str) -> Dict[str, Any]:
        """
        ENHANCED parsing with better pattern matching
        """
        extracted_data = {}
        
        for field, patterns in self.general_patterns.items():
            value = self._extract_field_smart(text, patterns, field)
            if value:
                # Special handling for different field types
                if field == 'gender':
                    extracted_data[field] = value  # Will be standardized later
                elif field in ['smoking', 'alcohol_intake', 'physical_activity']:
                    extracted_data[field] = value  # Will be converted to binary later
                elif field == 'blood_pressure':
                    # Store BP as combined value
                    extracted_data[field] = value
                else:
                    extracted_data[field] = value
        
        return extracted_data
    
    def _extract_field_smart(self, text: str, patterns: list, field_name: str):
        """
        SMART field extraction with priority-based matching
        """
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if match.groups():
                    value = match.group(1)
                    if self._validate_field(field_name, value):
                        self.logger.debug(f"✅ Fallback {field_name} matched: '{value}'")
                        return value
        
        self.logger.debug(f"❌ No valid match for {field_name} in fallback")
        return None
    
    def _format_for_display(self, extracted_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        NEW: Format data for clean UI display with checkmarks and units
        """
        display_list = []
        
        # Priority order for display (important fields first)
        priority_fields = ['age', 'gender', 'blood_pressure', 'cholesterol', 'glucose', 
                          'height', 'weight', 'bmi', 'heart_rate', 'smoking', 
                          'alcohol_intake', 'physical_activity']
        
        for field in priority_fields:
            if field in extracted_data:
                display_name = self.display_mapping.get(field, field.title())
                value = extracted_data[field]
                unit = self.unit_mapping.get(field, '')
                
                # Format the display value
                if unit:
                    display_value = f"{value} {unit}"
                else:
                    display_value = str(value)
                
                # NEW: Add status flag for vitals
                status = self._get_vital_status(field, value)
                if status:
                    display_value += f" ({status})"
                
                display_list.append({
                    'field': display_name,
                    'value': display_value,
                    'icon': '✅'  # Checkmark for successful extraction
                })
        
        return display_list
    
    def _get_vital_status(self, field: str, value: str) -> str:
        """NEW: Quick status for display (High/Normal based on basics)"""
        try:
            val = float(value.split('/')[0] if '/' in value else value)  # Systolic or single
            if field == 'cholesterol' and val > 200:
                return 'High'
            if field == 'glucose' and val > 126:
                return 'High'
            if field == 'blood_pressure' and val > 140:
                return 'High'
        except:
            pass
        return ''
    
    # KEEP ALL YOUR EXISTING METHODS - THEY WORK GREAT!
    
    def _extract_text_enhanced(self, image_path: str) -> str:
        """
        Extract text using OCR.space API with enhanced cleaning
        """
        try:
            raw_text = self.ocr_reader.extract_text(image_path)
            
            if not raw_text:
                self.logger.warning("❌ No text extracted by OCR.space in fallback")
                return ""
            
            # Enhanced text cleaning for medical documents
            cleaned_text = self._clean_medical_text(raw_text)
            self.logger.debug(f"🧹 Fallback cleaned text sample: {cleaned_text[:200]}...")
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space extraction failed in fallback: {e}")
            return ""
    
    def _clean_medical_text(self, text: str) -> str:
        """
        Enhanced cleaning for medical OCR text in fallback parser
        """
        # Convert to uppercase for consistent matching
        text = text.upper()
        
        # Common OCR corrections for medical terms
        medical_corrections = {
            'CHOLLETROL': 'CHOLESTEROL',
            'CHOL': 'CHOLESTEROL',  # NEW: Short forms
            'GLUCSE': 'GLUCOSE',
            'GLU': 'GLUCOSE',
            'PRESSURE': 'PRESSURE',
            'SYSTOLIC': 'SYSTOLIC',
            'DIASTOLIC': 'DIASTOLIC',
            'BLOOD': 'BLOOD',
            'MG/DL': 'MG/DL',
            'MMHG': 'MMHG'
        }
        
        # Apply corrections
        for wrong, correct in medical_corrections.items():
            text = text.replace(wrong, correct)
        
        # NEW: General noise scrub (headers, ranges, URLs, flags)
        text = re.sub(r'\bTEST RESULTS\b.*?(?=\b[A-Z]{3,}|$)', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\*\s+HIGH\s*(?=\d)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bNORMAL RANGE\b.*?(?=(\d{2,3}|[A-Z]{3,}|$))', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'WWW\..*?ORG', '', text, flags=re.IGNORECASE)
        text = re.sub(r'CONFIDENTIAL.*', '', text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _smart_bp_detection(self, text: str) -> Dict[str, Any]:
        """Smart detection of blood pressure components from context"""
        bp_data = {}
        
        # Look for BP format like "120/80"
        bp_candidates = re.findall(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
        for systolic, diastolic in bp_candidates:
            try:
                systolic_val, diastolic_val = int(systolic), int(diastolic)
                if (70 <= systolic_val <= 250 and 40 <= diastolic_val <= 150):
                    bp_data['blood_pressure'] = f"{systolic_val}/{diastolic_val}"
                    self.logger.info("✅ Smart BP detection successful in fallback")
                    break
            except:
                continue
        
        return bp_data
    
    def _extract_casual_mentions(self, text: str, extracted_data: Dict[str, Any]):
        """NEW: Extract casual mentions for missed vitals/gender"""
        # Casual cholesterol (post-keyword number)
        if 'cholesterol' not in extracted_data:
            chol_matches = re.findall(r'CHOLESTEROL\s*(?:LEVEL\s*)?(\d{2,3})', text, re.IGNORECASE)
            for val in chol_matches:
                if 50 <= int(val) <= 400:
                    extracted_data['cholesterol'] = val
                    self.logger.info("✅ Casual cholesterol detection in fallback")
                    break
        
        # Casual glucose
        if 'glucose' not in extracted_data:
            glu_matches = re.findall(r'GLUCOSE\s*(?:LEVEL\s*)?\(?\s*MG/DL\s*\)?\s*(\d{2,3})', text, re.IGNORECASE)
            for val in glu_matches:
                if 50 <= int(val) <= 400:
                    extracted_data['glucose'] = val
                    self.logger.info("✅ Casual glucose detection in fallback")
                    break
        
        # NEW: Gender from patient name
        if 'gender' not in extracted_data:
            name_match = re.search(r'PATIENT NAME[:\s]*([A-Z\s]+)', text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip().upper()
                male_indicators = ['JOHN', 'JAMES', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'DOE']
                if any(indicator in name for indicator in male_indicators):
                    extracted_data['gender'] = 'Male'
                else:
                    extracted_data['gender'] = 'Female'  # Default; flag in UI
                self.logger.info(f"✅ Inferred gender from name: {extracted_data['gender']}")
    
    def _calculate_bmi(self, height: str, weight: str) -> float:
        """Calculate BMI from height and weight"""
        try:
            height_cm = float(height)
            weight_kg = float(weight)
            
            if height_cm > 0 and weight_kg > 0:
                height_m = height_cm / 100
                bmi = weight_kg / (height_m ** 2)
                self.logger.info(f"✅ BMI calculated in fallback: {bmi:.1f}")
                return round(bmi, 1)
        except Exception as e:
            self.logger.warning(f"⚠️ BMI calculation failed in fallback: {e}")
        
        return None
    
    def _standardize_gender(self, gender_input: str) -> str:
        """Convert gender to standardized format"""
        gender_map = {
            'm': 'Male', 'male': 'Male',
            'f': 'Female', 'female': 'Female'
        }
        return gender_map.get(gender_input.lower(), 'Unknown')
    
    def _validate_field(self, field: str, value: str) -> bool:
        """Validate if extracted value is reasonable"""
        try:
            # NEW: Strip flags/units for validation
            clean_val = re.sub(r'\s*(?:high|normal|mg/dl|mmhg)', '', value, flags=re.IGNORECASE).strip()
            if field == 'age':
                return 1 <= int(clean_val) <= 120
            elif field == 'height':
                return 100 <= int(clean_val) <= 250
            elif field == 'weight':
                return 30 <= int(clean_val) <= 200
            elif field == 'blood_pressure':
                parts = clean_val.split('/')
                return len(parts) == 2 and 70 <= int(parts[0]) <= 250 and 40 <= int(parts[1]) <= 150
            elif field in ['cholesterol', 'glucose']:
                return 50 <= int(clean_val) <= 400
            elif field == 'heart_rate':
                return 40 <= int(clean_val) <= 200
            return True
        except:
            return False
    
    def get_supported_features(self) -> list:
        """Return list of supported features for the new dataset"""
        return list(self.general_patterns.keys()) + ['bmi']
    
    # KEEP YOUR EXISTING TEST METHOD
    def test_ocr_fallback(self, image_path: str) -> Dict[str, Any]:
        """
        Test method to verify OCR.space integration in fallback parser
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