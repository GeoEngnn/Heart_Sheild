# ocr/parsers/clinic_notes_parser.py - UPDATED WITH OCR.SPACE API
import re
import logging
from typing import Dict, Any

# Import the OCR.space reader from universal_reader
from ..universal_reader import OCRSpaceReader

class ClinicNotesParser:
    """
    UPDATED: Parser for clinic notes and progress notes - NOW WITH OCR.SPACE API
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # NEW: Use OCR.space API for text extraction
        self.ocr_reader = OCRSpaceReader()
        
        # UPDATED: Clinic notes patterns for NEW FEATURES
        self.clinic_patterns = {
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
                r'current weight[\s:]*(\d+)'
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
                r'vitals.*?bp[\s:]*(\d+)/(\d+)',
                r'today.*?bp[\s:]*(\d+)/(\d+)'
            ],
            'diastolic_bp': [
                r'bp[\s:]*\d+/(\d+)',
                r'blood pressure[\s:]*\d+/(\d+)',
                r'diastolic[\s:]*(\d+)'
            ],
            'cholesterol': [
                r'cholesterol[\s:]*(\d+)',
                r'chol[\s:]*(\d+)',
                r'lipid[\s:]*(\d+)',
                r'recent.*?chol[\s:]*(\d+)'
            ],
            'glucose': [
                r'glucose[\s:]*(\d+)',
                r'blood sugar[\s:]*(\d+)',
                r'sugar[\s:]*(\d+)',
                r'fbs[\s:]*(\d+)',
                r'fasting[\s:]*glucose[\s:]*(\d+)'
            ],
            'heart_rate': [
                r'heart rate[\s:]*(\d+)',
                r'hr[\s:]*(\d+)',
                r'pulse[\s:]*(\d+)',
                r'vitals.*?pulse[\s:]*(\d+)'
            ],
            'smoking': [
                r'smoking[\s:]*([yn])',
                r'smoker[\s:]*([yn])',
                r'tobacco[\s:]*([yn])',
                r'smoking[\s:]*(yes|no)',
                r'denies.*?smoking',
                r'quit.*?smoking'
            ],
            'alcohol_intake': [
                r'alcohol[\s:]*([yn])',
                r'drinking[\s:]*([yn])',
                r'alcohol[\s:]*(yes|no)',
                r'denies.*?alcohol',
                r'social.*?alcohol[\s:]*([yn])'
            ],
            'physical_activity': [
                r'exercise[\s:]*([yn])',
                r'physical[\s:]*activity[\s:]*([yn])',
                r'activity[\s:]*level[\s:]*([yn])',
                r'walks?[\s:]*([yn])',
                r'exercises?[\s:]*(yes|no)'
            ],
            'symptoms': [
                r'symptoms?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'complains?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'complaints?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
            ],
            'assessment': [
                r'assessment[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'impression[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
            ],
            'plan': [
                r'plan[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'recommendations?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'treatment[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
            ]
        }
        
        self.logger.info("✅ ClinicNotesParser UPDATED with OCR.space API")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        UPDATED: Extract data from clinic notes with OCR.SPACE API
        """
        self.logger.info(f"📋 Processing clinic notes with OCR.space: {image_path}")
        
        try:
            # NEW: Use OCR.space API for text extraction
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.warning("⚠️ Insufficient text extracted by OCR.space in clinic notes parser")
                return {
                    "error": "Insufficient text extracted", 
                    "document_type": "clinic_notes",
                    "parsing_confidence": "very_low"
                }
                
            self.logger.info(f"📝 OCR.space extracted {len(text)} chars from clinic notes")
            
            extracted_data = {}
            
            # Extract structured data for NEW FEATURES
            for field, patterns in self.clinic_patterns.items():
                value = self._extract_field_enhanced(text, patterns, field)
                if value:
                    extracted_data[field] = value
            
            # For clinic notes, also look for free-form mentions of NEW FEATURES
            self._extract_casual_mentions(text, extracted_data)
            
            # Calculate BMI if height and weight available
            if 'height' in extracted_data and 'weight' in extracted_data:
                try:
                    height_cm = float(extracted_data['height'])
                    weight_kg = float(extracted_data['weight'])
                    if height_cm > 0 and weight_kg > 0:
                        height_m = height_cm / 100
                        bmi = weight_kg / (height_m ** 2)
                        extracted_data['bmi'] = round(bmi, 1)
                        self.logger.info(f"✅ BMI calculated from clinic notes: {bmi:.1f}")
                except Exception as e:
                    self.logger.warning(f"⚠️ BMI calculation failed in clinic notes: {e}")
            
            # Standardize gender format
            if 'gender' in extracted_data:
                gender = extracted_data['gender'].lower()
                if gender in ['m', 'male']:
                    extracted_data['gender'] = 'Male'
                elif gender in ['f', 'female']:
                    extracted_data['gender'] = 'Female'
            
            # Convert lifestyle factors to binary with context awareness
            self._process_lifestyle_factors(text, extracted_data)
            
            # Extract clinical insights from symptoms and assessment
            if 'symptoms' in extracted_data or 'assessment' in extracted_data:
                clinical_insights = self._extract_clinical_insights(extracted_data, text)
                extracted_data.update(clinical_insights)
            
            extracted_data['document_type'] = 'clinic_notes'
            extracted_data['has_clinical_data'] = len([k for k in extracted_data.keys() if k not in ['document_type', 'has_clinical_data']]) > 2
            extracted_data['parsing_confidence'] = 'medium'
            extracted_data['ocr_engine'] = 'ocr_space_api'
            
            self.logger.info(f"✅ Clinic notes parsed: {len(extracted_data)} fields found")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing clinic notes: {e}")
            return {
                "error": str(e), 
                "document_type": "clinic_notes",
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
                self.logger.warning("❌ No text extracted by OCR.space in clinic notes parser")
                return ""
            
            # Enhanced text cleaning for medical documents
            cleaned_text = self._clean_medical_text(raw_text)
            self.logger.debug(f"🧹 Clinic notes cleaned text sample: {cleaned_text[:200]}...")
            
            return cleaned_text.lower()
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space extraction failed in clinic notes parser: {e}")
            return ""
    
    def _clean_medical_text(self, text: str) -> str:
        """
        NEW: Enhanced cleaning for medical OCR text in clinic notes
        """
        # Common OCR corrections for medical terms in clinic notes
        medical_corrections = {
            'ro5': 'tsh', 'Go1': 'glucose', 'prise': 'profile',
            'coc': 'cbc', 'trh': 'tsh', 'fo': 'fbs',
            'dias': 'diastolic', 'sys': 'systolic',
            'chol': 'cholesterol', 'fbs': 'fasting blood sugar',
            'hr': 'heart rate', 'wt': 'weight', 'ht': 'height',
            'bp': 'blood pressure', 'hgt': 'height', 'wgt': 'weight',
            'yrs': 'years', 'yr': 'year', 'kg': 'kg', 'cm': 'cm',
            'male': 'm', 'female': 'f',  # Standardize gender
            'yes': 'y', 'no': 'n',  # Standardize lifestyle factors
            'complains': 'complaints', 'complains of': 'complaints of',
            'denies': 'denies', 'negative for': 'negative for',
            'positive for': 'positive for', 'ros': 'review of systems',
            'pmh': 'past medical history', 'fh': 'family history',
            'sh': 'social history', 'soap': 'soap note'
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
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                self.logger.debug(f"✅ Clinic notes pattern matched for {field_name}: {pattern}")
                
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
                
                elif field_name in ['symptoms', 'assessment', 'plan']:
                    value = match.group(1).strip() if match.lastindex >= 1 else None
                    if value and len(value) > 3:  # Reasonable length for clinical text
                        return value
                
                else:
                    return match.group(1) if match.lastindex >= 1 else None
        
        return None
    
    def _extract_casual_mentions(self, text: str, extracted_data: Dict[str, Any]):
        """Extract casual mentions of medical values in clinic notes"""
        # Look for casual BP mentions
        if 'systolic_bp' not in extracted_data or 'diastolic_bp' not in extracted_data:
            bp_candidates = re.findall(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
            for systolic, diastolic in bp_candidates:
                try:
                    systolic_val, diastolic_val = int(systolic), int(diastolic)
                    if (70 <= systolic_val <= 250 and 40 <= diastolic_val <= 150):
                        extracted_data['systolic_bp'] = systolic_val
                        extracted_data['diastolic_bp'] = diastolic_val
                        self.logger.info("✅ Casual BP detection in clinic notes")
                        break
                except:
                    continue
        
        # Look for casual mentions of lifestyle factors
        if 'smoking' not in extracted_data:
            if re.search(r'denies.*?smoking', text):
                extracted_data['smoking'] = 0
            elif re.search(r'smokes?', text):
                extracted_data['smoking'] = 1
        
        if 'alcohol_intake' not in extracted_data:
            if re.search(r'denies.*?alcohol', text):
                extracted_data['alcohol_intake'] = 0
            elif re.search(r'drinks?.*?alcohol', text):
                extracted_data['alcohol_intake'] = 1
    
    def _process_lifestyle_factors(self, text: str, extracted_data: Dict[str, Any]):
        """Process lifestyle factors with context awareness"""
        lifestyle_fields = ['smoking', 'alcohol_intake', 'physical_activity']
        
        for field in lifestyle_fields:
            if field in extracted_data:
                value = extracted_data[field]
                if isinstance(value, str):
                    value_lower = value.lower()
                    if value_lower in ['y', 'yes', '1']:
                        extracted_data[field] = 1
                    else:
                        extracted_data[field] = 0
            else:
                # Default to 0 (no) if not mentioned
                extracted_data[field] = 0
    
    def _extract_clinical_insights(self, extracted_data: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Extract clinical insights from symptoms and assessment"""
        insights = {}
        text_lower = text.lower()
        
        # Check for cardiovascular symptoms
        cardio_symptoms = [
            'chest pain', 'shortness of breath', 'palpitations', 'edema',
            'fatigue', 'dizziness', 'syncope', 'angina'
        ]
        
        found_symptoms = [symptom for symptom in cardio_symptoms if symptom in text_lower]
        if found_symptoms:
            insights['cardiovascular_symptoms'] = found_symptoms
            insights['has_cardio_symptoms'] = True
        else:
            insights['has_cardio_symptoms'] = False
        
        # Check for risk factors in assessment
        risk_keywords = [
            'hypertension', 'hyperlipidemia', 'diabetes', 'obesity',
            'overweight', 'sedentary', 'family history'
        ]
        
        found_risks = [risk for risk in risk_keywords if risk in text_lower]
        if found_risks:
            insights['identified_risk_factors'] = found_risks
        
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
            'physical_activity', 'bmi', 'symptoms', 'assessment', 'plan'
        ]
    
    def test_ocr_clinic_notes(self, image_path: str) -> Dict[str, Any]:
        """
        NEW: Test method to verify OCR.space integration in clinic notes parser
        """
        self.logger.info(f"🧪 Testing OCR.space clinic notes parser with: {image_path}")
        
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
                "parser_type": "clinic_notes_with_ocr_space",
                "text_preview": cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space clinic notes test failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "parser_type": "clinic_notes_with_ocr_space"
            }