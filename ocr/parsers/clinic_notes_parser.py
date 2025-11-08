# ocr/parsers/clinic_notes_parser.py - ENHANCED SMART PARSER
import re
import logging
from typing import Dict, Any, List

# Import the OCR.space reader from universal_reader
from ..universal_reader import OCRSpaceReader

class ClinicNotesParser:
    """
    ENHANCED: Parser for clinic notes and progress notes with SMART DISPLAY FORMATTING
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # NEW: Use OCR.space API for text extraction
        self.ocr_reader = OCRSpaceReader()
        
        # ENHANCED: Improved patterns for better extraction
        self.clinic_patterns = {
            'age': [
                r'\bage\s*[:\-]?\s*(\d{1,3})\b',
                r'\bage[\s:]*(\d+)\s*years?\b',
                r'\bpatient[\s:].*?age[\s:]*(\d+)',
                r'\b(\d{1,3})\s*years? old\b',
            ],
            'height': [
                r'\bheight\s*[:\-]?\s*(\d{2,3})\s*cm\b',
                r'\bht\s*[:\-]?\s*(\d{2,3})\s*cm\b',
                r'\bheight[\s:]*(\d{2,3})\b',
                r'\b(\d{3})\s*cm\s*height\b',
            ],
            'weight': [
                r'\bweight\s*[:\-]?\s*(\d{2,3})\s*kg\b',
                r'\bwt\s*[:\-]?\s*(\d{2,3})\s*kg\b',
                r'\bweight[\s:]*(\d{2,3})\b',
                r'\bcurrent weight\s*[:\-]?\s*(\d{2,3})\b',
            ],
            'gender': [
                r'\bgender\s*[:\-]?\s*(male|female|m|f)\b',
                r'\bsex\s*[:\-]?\s*(male|female|m|f)\b',
                r'\b(male|female)\b',
                r'\b[mf]\b',
            ],
            'blood_pressure': [
                r'\bbp\s*[:\-]?\s*(\d{2,3}/\d{2,3})\b',
                r'\bblood pressure\s*[:\-]?\s*(\d{2,3}/\d{2,3})\b',
                r'\bvitals.*?bp\s*[:\-]?\s*(\d{2,3}/\d{2,3})\b',
                r'\b(\d{2,3}/\d{2,3})\s*mmhg\b',
                r'\bpressure\s*[:\-]?\s*(\d{2,3}/\d{2,3})\s*(?:high|normal)?\b',  # NEW: Flexible for "PRESSURE 125/85 HIGH"
            ],
            'cholesterol': [
                r'\bcholesterol\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bchol\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bcholesterol[\s:]*(\d{2,3})\b',
                r'\brecent.*?chol\s*[:\-]?\s*(\d{2,3})\b',
                r'\bcholesterol\s*(?:level|total)?\s*[:\-]?\s*(\d{2,3})\s*(?:mg/dl|high|normal)?\b',  # NEW: Allows "LEVEL" intervene, flags
                r'\bchol\s*(?:level|total)?\s*[:\-]?\s*(\d{2,3})\s*(?:mg/dl|high|normal)?\b',
            ],
            'glucose': [
                r'\bglucose\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bblood sugar\s*[:\-]?\s*(\d{2,3})\b',
                r'\bglucose[\s:]*(\d{2,3})\b',
                r'\bfbs\s*[:\-]?\s*(\d{2,3})\b',
                r'\bglucose\s*(?:level)?\s*\(?\s*mg/dl\s*\)?\s*[:\-]?\s*(\d{2,3})\s*(?:high|normal)?\b',  # NEW: Handles "(MG/DL)", "LEVEL"
                r'\bglu\s*(?:level)?\s*\(?\s*mg/dl\s*\)?\s*[:\-]?\s*(\d{2,3})\s*(?:high|normal)?\b',
            ],
            'heart_rate': [
                r'\bheart rate\s*[:\-]?\s*(\d{2,3})\b',
                r'\bhr\s*[:\-]?\s*(\d{2,3})\b',
                r'\bpulse\s*[:\-]?\s*(\d{2,3})\b',
                r'\bhr\s*[:\-]?\s*(\d{2,3})\s*(?:bpm|high|normal)?\b',  # NEW: Flags/units
            ],
            'smoking': [
                r'\bsmoking\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bsmoker\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\btobacco\s*[:\-]?\s*(yes|no)\b',
            ],
            'alcohol_intake': [
                r'\balcohol\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bdrinking\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\balcohol use\s*[:\-]?\s*(yes|no)\b',
            ],
            'physical_activity': [
                r'\bexercise\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bphysical activity\s*[:\-]?\s*(yes|no|y|n)\b',
                r'\bactivity level\s*[:\-]?\s*(yes|no)\b',
            ],
            'symptoms': [
                r'\bsymptoms?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bcomplains?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bcomplaints?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
            ],
            'assessment': [
                r'\bassessment[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bimpression[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bdiagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
            ],
            'plan': [
                r'\bplan[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\brecommendations?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\btreatment[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
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
            'bmi': 'BMI',
            'symptoms': 'Symptoms',
            'assessment': 'Assessment',
            'plan': 'Treatment Plan'
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
        
        self.logger.info("✅ ClinicNotesParser ENHANCED with smart display formatting!")
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        ENHANCED: Extract data from clinic notes with SMART DISPLAY OUTPUT
        """
        self.logger.info(f"📋 Processing clinic notes with OCR.space: {image_path}")
        
        try:
            # Use OCR.space API for text extraction
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.warning("⚠️ Insufficient text extracted by OCR.space in clinic notes parser")
                return {
                    "error": "Insufficient text extracted", 
                    "document_type": "clinic_notes",
                    "parsing_confidence": "very_low",
                    "success": False
                }
                
            self.logger.info(f"📝 OCR.space extracted {len(text)} chars from clinic notes")
            
            # Extract structured data using enhanced parsing
            extracted_data = self._parse_clinic_data_enhanced(text)
            
            # KEEP ALL YOUR EXISTING SMART FEATURES:
            
            # For clinic notes, also look for free-form mentions of NEW FEATURES
            self._extract_casual_mentions(text, extracted_data)
            
            # Calculate BMI if height and weight available
            if 'height' in extracted_data and 'weight' in extracted_data:
                bmi_result = self._calculate_bmi(extracted_data['height'], extracted_data['weight'])
                if bmi_result:
                    extracted_data['bmi'] = bmi_result
            
            # Standardize gender format
            if 'gender' in extracted_data:
                extracted_data['gender'] = self._standardize_gender(extracted_data['gender'])
            
            # Convert lifestyle factors to binary with context awareness
            self._process_lifestyle_factors(text, extracted_data)
            
            # Extract clinical insights from symptoms and assessment
            if 'symptoms' in extracted_data or 'assessment' in extracted_data:
                clinical_insights = self._extract_clinical_insights(extracted_data, text)
                extracted_data.update(clinical_insights)
            
            # NEW: SMART DISPLAY FORMATTING
            display_data = self._format_for_display(extracted_data)
            
            # KEEP ALL YOUR EXISTING METADATA
            result = {
                "raw_data": extracted_data,
                "display_data": display_data,  # NEW: Clean formatted data
                "document_type": 'clinic_notes',
                "has_clinical_data": len([k for k in extracted_data.keys() if k not in ['document_type', 'has_clinical_data']]) > 2,
                "parsing_confidence": 'medium',
                "ocr_engine": 'ocr_space_api',
                "success": True
            }
            
            self.logger.info(f"✅ Clinic notes parsed: {len(extracted_data)} fields found")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing clinic notes: {e}")
            return {
                "error": str(e), 
                "document_type": "clinic_notes",
                "parsing_confidence": "error",
                "success": False
            }
    
    def _parse_clinic_data_enhanced(self, text: str) -> Dict[str, Any]:
        """
        ENHANCED parsing with better pattern matching
        """
        extracted_data = {}
        
        for field, patterns in self.clinic_patterns.items():
            value = self._extract_field_smart(text, patterns, field)
            if value:
                # Special handling for different field types
                if field == 'gender':
                    extracted_data[field] = value  # Will be standardized later
                elif field in ['smoking', 'alcohol_intake', 'physical_activity']:
                    extracted_data[field] = value  # Will be processed later
                elif field in ['symptoms', 'assessment', 'plan']:
                    # Clean up text fields
                    extracted_data[field] = self._clean_text_field(value)
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
                        self.logger.debug(f"✅ Clinic notes {field_name} matched: '{value}'")
                        return value
        
        self.logger.debug(f"❌ No valid match for {field_name} in clinic notes")
        return None
    
    def _format_for_display(self, extracted_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        NEW: Format data for clean UI display with checkmarks and units
        """
        display_list = []
        
        # Priority order for display (vitals first, then clinical info)
        priority_fields = [
            'age', 'gender', 'blood_pressure', 'cholesterol', 'glucose', 
            'height', 'weight', 'bmi', 'heart_rate', 'smoking', 
            'alcohol_intake', 'physical_activity', 'symptoms', 'assessment', 'plan'
        ]
        
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
                
                # NEW: Add status flag for vitals (e.g., High if threshold breach)
                status = self._get_vital_status(field, value)
                if status:
                    display_value += f" ({status})"
                
                # Special handling for long text fields
                if field in ['symptoms', 'assessment', 'plan'] and len(display_value) > 100:
                    display_value = display_value[:100] + "..."
                
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
    
    def _clean_text_field(self, text: str) -> str:
        """Clean up text fields like symptoms, assessment, and plan"""
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    # KEEP ALL YOUR EXISTING METHODS - THEY WORK GREAT!
    
    def _extract_text_enhanced(self, image_path: str) -> str:
        """
        Extract text using OCR.space API with enhanced cleaning
        """
        try:
            raw_text = self.ocr_reader.extract_text(image_path)
            
            if not raw_text:
                self.logger.warning("❌ No text extracted by OCR.space in clinic notes parser")
                return ""
            
            # Enhanced text cleaning for medical documents
            cleaned_text = self._clean_medical_text(raw_text)
            self.logger.debug(f"🧹 Clinic notes cleaned text sample: {cleaned_text[:200]}...")
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space extraction failed in clinic notes parser: {e}")
            return ""
    
    def _clean_medical_text(self, text: str) -> str:
        """
        Enhanced cleaning for medical OCR text in clinic notes
        """
        # Convert to uppercase for consistent matching
        text = text.upper()
        
        # Common OCR corrections for medical terms in clinic notes
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
            'MMHG': 'MMHG',
            'COMPLAINS': 'COMPLAINTS',
            'DENIES': 'DENIES',
            'SYMPTOMS': 'SYMPTOMS',
            'ASSESSMENT': 'ASSESSMENT',
            'TREATMENT': 'TREATMENT'
        }
        
        # Apply corrections
        for wrong, correct in medical_corrections.items():
            text = text.replace(wrong, correct)
        
        # NEW: Strip common noise like "* HIGH" but keep values (non-greedy)
        text = re.sub(r'\*\s+HIGH\s*(?=\d)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'WWW\..*?ORG', '', text, flags=re.IGNORECASE)  # URLs
        text = re.sub(r'CONFIDENTIAL.*', '', text, flags=re.IGNORECASE)  # Boilerplate
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _extract_casual_mentions(self, text: str, extracted_data: Dict[str, Any]):
        """Extract casual mentions of medical values in clinic notes"""
        # Look for casual BP mentions
        if 'blood_pressure' not in extracted_data:
            bp_candidates = re.findall(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
            for systolic, diastolic in bp_candidates:
                try:
                    systolic_val, diastolic_val = int(systolic), int(diastolic)
                    if (70 <= systolic_val <= 250 and 40 <= diastolic_val <= 150):
                        extracted_data['blood_pressure'] = f"{systolic_val}/{diastolic_val}"
                        self.logger.info("✅ Casual BP detection in clinic notes")
                        break
                except:
                    continue
        
        # NEW: Casual cholesterol hunt (near keyword, first plausible number)
        if 'cholesterol' not in extracted_data:
            chol_matches = re.findall(r'CHOLESTEROL\s*.*?(\d{2,3})', text, re.IGNORECASE)
            for val in chol_matches:
                if 50 <= int(val) <= 400:
                    extracted_data['cholesterol'] = val
                    self.logger.info("✅ Casual cholesterol detection in clinic notes")
                    break
        
        # NEW: Casual glucose hunt
        if 'glucose' not in extracted_data:
            glu_matches = re.findall(r'GLUCOSE\s*.*?(\d{2,3})', text, re.IGNORECASE)
            for val in glu_matches:
                if 50 <= int(val) <= 400:
                    extracted_data['glucose'] = val
                    self.logger.info("✅ Casual glucose detection in clinic notes")
                    break
        
        # NEW: Gender from patient name (heuristic on common names)
        if 'gender' not in extracted_data:
            name_match = re.search(r'PATIENT NAME[:\s]*([A-Z\s]+)', text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip().upper()
                male_indicators = ['JOHN', 'JAMES', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'DOE']  # Expand as needed
                if any(indicator in name for indicator in male_indicators):
                    extracted_data['gender'] = 'Male'
                else:
                    extracted_data['gender'] = 'Female'  # Default; flag in UI
                self.logger.info(f"✅ Inferred gender from name: {extracted_data['gender']}")
        
        # Look for casual mentions of lifestyle factors
        if 'smoking' not in extracted_data:
            if re.search(r'denies.*?smoking', text, re.IGNORECASE):
                extracted_data['smoking'] = 0
            elif re.search(r'smokes?', text, re.IGNORECASE):
                extracted_data['smoking'] = 1
        
        if 'alcohol_intake' not in extracted_data:
            if re.search(r'denies.*?alcohol', text, re.IGNORECASE):
                extracted_data['alcohol_intake'] = 0
            elif re.search(r'drinks?.*?alcohol', text, re.IGNORECASE):
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
    
    def _calculate_bmi(self, height: str, weight: str) -> float:
        """Calculate BMI from height and weight"""
        try:
            height_cm = float(height)
            weight_kg = float(weight)
            
            if height_cm > 0 and weight_kg > 0:
                height_m = height_cm / 100
                bmi = weight_kg / (height_m ** 2)
                self.logger.info(f"✅ BMI calculated from clinic notes: {bmi:.1f}")
                return round(bmi, 1)
        except Exception as e:
            self.logger.warning(f"⚠️ BMI calculation failed in clinic notes: {e}")
        
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
            if field == 'age':
                return 1 <= int(value) <= 120
            elif field == 'height':
                return 100 <= int(value) <= 250
            elif field == 'weight':
                return 30 <= int(value) <= 200
            elif field == 'blood_pressure':
                parts = value.split('/')
                return len(parts) == 2 and 70 <= int(parts[0]) <= 250 and 40 <= int(parts[1]) <= 150
            elif field in ['cholesterol', 'glucose']:
                # NEW: Strip flags like " HIGH" for validation
                clean_val = re.sub(r'\s*(high|normal)', '', value).strip()
                return 50 <= int(clean_val) <= 400
            elif field == 'heart_rate':
                return 40 <= int(value) <= 200
            elif field in ['symptoms', 'assessment', 'plan']:
                return len(value.strip()) > 3  # Reasonable length for clinical text
            return True
        except:
            return False
    
    def get_supported_features(self) -> list:
        """Return list of supported features for the new dataset"""
        return list(self.clinic_patterns.keys()) + ['bmi', 'has_cardio_symptoms', 'identified_risk_factors']
    
    # KEEP YOUR EXISTING TEST METHOD
    def test_ocr_clinic_notes(self, image_path: str) -> Dict[str, Any]:
        """
        Test method to verify OCR.space integration in clinic notes parser
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