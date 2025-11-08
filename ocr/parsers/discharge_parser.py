# ocr/parsers/discharge_parser.py - ENHANCED SMART PARSER
import re
import logging
from typing import Dict, Any, List

# Import the OCR.space reader from universal_reader
from ..universal_reader import OCRSpaceReader


class DischargeSummaryParser:
    """
    ENHANCED: Parser for hospital discharge summaries with SMART DISPLAY FORMATTING
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # OCR engine
        self.ocr_reader = OCRSpaceReader()

        # ------------------------------------------------------------------
        # 1. MASTER PATTERN SET – handles every real-world variation
        # ------------------------------------------------------------------
        self.discharge_patterns = {
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
                r'\badmission weight\s*[:\-]?\s*(\d{2,3})\b',
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
                r'\badmission bp\s*[:\-]?\s*(\d{2,3}/\d{2,3})\b',
                r'\b(\d{2,3}/\d{2,3})\s*mmhg\b',
                r'blood pressure\s*=\s*(\d+/\d+)',
                r'\bpressure\s*(?:blood)?\s*[:\-]?\s*(\d{2,3}/\d{2,3})\s*(?:high|normal)?\b',
            ],
            'cholesterol': [
                r'\bcholesterol\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bchol\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bcholesterol[\s:]*(\d{2,3})\b',
                r'\blipid panel.*?chol\s*[:\-]?\s*(\d{2,3})\b',
                r'cholesterol\s*=\s*(\d+)',
                r'\bcholesterol\s*(?:level|total)?\s*[:\-]?\s*(\d{2,3})\s*(?:mg/dl|high|normal)?\b',
                r'\bchol\s*(?:level|total)?\s*[:\-]?\s*(\d{2,3})\s*(?:mg/dl|high|normal)?\b',
            ],
            'glucose': [
                r'\bglucose\s*[:\-]?\s*(\d{2,3})\s*mg/dl\b',
                r'\bblood sugar\s*[:\-]?\s*(\d{2,3})\b',
                r'\bglucose[\s:]*(\d{2,3})\b',
                r'\bfbs\s*[:\-]?\s*(\d{2,3})\b',
                r'glucose\s*=\s*(\d+)',
                r'\bglucose\s*(?:level)?\s*\(?\s*mg/dl\s*\)?\s*[:\-]?\s*(\d{2,3})\s*(?:high|normal)?\b',
                r'\bglu\s*(?:level)?\s*\(?\s*mg/dl\s*\)?\s*[:\-]?\s*(\d{2,3})\s*(?:high|normal)?\b',
            ],
            'heart_rate': [
                r'\bheart rate\s*[:\-]?\s*(\d{2,3})\b',
                r'\bhr\s*[:\-]?\s*(\d{2,3})\b',
                r'\bpulse\s*[:\-]?\s*(\d{2,3})\b',
                r'heart rate\s*=\s*(\d+)',
                r'\bhr\s*[:\-]?\s*(\d{2,3})\s*(?:bpm|high|normal)?\b',
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
            ],
            'diagnosis': [
                r'\bdiagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bfinal diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bdischarge diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
            ],
            'medications': [
                r'\bmedications?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bdischarge medications?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
                r'\bmeds[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
            ]
        }

        # ------------------------------------------------------------------
        # 2. DISPLAY & UNIT MAPPINGS
        # ------------------------------------------------------------------
        self.display_mapping = {
            'age': 'Age', 'height': 'Height', 'weight': 'Weight', 'gender': 'Gender',
            'blood_pressure': 'Blood Pressure', 'cholesterol': 'Cholesterol',
            'glucose': 'Glucose', 'heart_rate': 'Heart Rate',
            'smoking': 'Smoking', 'alcohol_intake': 'Alcohol Intake',
            'physical_activity': 'Physical Activity', 'bmi': 'BMI',
            'diagnosis': 'Diagnosis', 'medications': 'Medications'
        }

        self.unit_mapping = {
            'age': 'years', 'height': 'cm', 'weight': 'kg',
            'blood_pressure': 'mmHg', 'cholesterol': 'mg/dL',
            'glucose': 'mg/dL', 'heart_rate': 'bpm', 'bmi': 'kg/m²'
        }

        self.logger.info("DischargeSummaryParser ENHANCED with smart display formatting!")

    # ----------------------------------------------------------------------
    # MAIN ENTRY POINT
    # ----------------------------------------------------------------------
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        self.logger.info(f"Processing discharge summary: {image_path}")

        try:
            text = self._extract_text_enhanced(image_path)

            if not text or len(text.strip()) < 10:
                return self._error_response("Insufficient text extracted")

            extracted_data = self._parse_discharge_data_enhanced(text)

            # Casual fallback for anything the strict patterns missed
            self._extract_casual_mentions(text, extracted_data)

            # BMI
            if extracted_data.get('height') and extracted_data.get('weight'):
                bmi = self._calculate_bmi(extracted_data['height'], extracted_data['weight'])
                if bmi:
                    extracted_data['bmi'] = bmi

            # Gender standardisation
            if 'gender' in extracted_data:
                extracted_data['gender'] = self._standardize_gender(extracted_data['gender'])

            # Lifestyle → binary (default 0 if missing)
            for field in ['smoking', 'alcohol_intake', 'physical_activity']:
                val = extracted_data.get(field, 'n').lower()
                extracted_data[field] = 1 if val in ['y', 'yes', '1'] else 0

            # Diagnosis insights
            if extracted_data.get('diagnosis'):
                extracted_data.update(self._extract_diagnosis_insights(extracted_data['diagnosis']))

            # UI-ready list
            display_data = self._format_for_display(extracted_data)

            return {
                "raw_data": extracted_data,
                "display_data": display_data,
                "document_type": "discharge_summary",
                "text_snippet": text[:300] + "..." if len(text) > 300 else text,
                "parsing_confidence": "high" if len(extracted_data) > 8 else "medium",
                "ocr_engine": "ocr_space_api",
                "success": True
            }

        except Exception as e:
            self.logger.error(f"Error parsing discharge summary: {e}")
            return self._error_response(str(e))

    # ----------------------------------------------------------------------
    # CORE PARSING
    # ----------------------------------------------------------------------
    def _parse_discharge_data_enhanced(self, text: str) -> Dict[str, Any]:
        data = {}
        for field, patterns in self.discharge_patterns.items():
            value = self._extract_field_smart(text, patterns, field)
            if value:
                if field in ['diagnosis', 'medications']:
                    data[field] = self._clean_text_field(value)
                else:
                    data[field] = value
        return data

    def _extract_field_smart(self, text: str, patterns: list, field_name: str):
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
                if match.groups():
                    raw = match.group(1).strip()
                    # Strip flags for numeric fields before validation
                    clean = re.sub(r'\s*(high|low|normal|mg/dl|mmhg|bpm).*', '', raw, flags=re.I)
                    if self._validate_field(field_name, clean):
                        self.logger.debug(f"{field_name} matched: '{raw}'")
                        return raw
        return None

    # ----------------------------------------------------------------------
    # CASUAL MENTIONS (fallback when strict patterns fail)
    # ----------------------------------------------------------------------
    def _extract_casual_mentions(self, text: str, data: Dict[str, Any]):
        # BP
        if 'blood_pressure' not in data:
            if m := re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text):
                s, d = int(m.group(1)), int(m.group(2))
                if 70 <= s <= 250 and 40 <= d <= 150:
                    data['blood_pressure'] = f"{s}/{d}"

        # Cholesterol
        if 'cholesterol' not in data:
            if m := re.search(r'cholesterol.*?(\d{2,3})', text, re.I):
                val = int(m.group(1))
                if 50 <= val <= 400:
                    data['cholesterol'] = str(val)

        # Glucose
        if 'glucose' not in data:
            if m := re.search(r'glucose.*?(\d{2,3})', text, re.I):
                val = int(m.group(1))
                if 50 <= val <= 400:
                    data['glucose'] = str(val)

        # Gender from patient name header
        if 'gender' not in data:
            if m := re.search(r'patient\s+name[:\s]*([A-Z\s]+)', text, re.I):
                name = m.group(1).upper()
                male_names = ['JOHN', 'JAMES', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'RICHARD', 'JOSEPH']
                if any(n in name for n in male_names):
                    data['gender'] = 'Male'
                else:
                    data['gender'] = 'Female'

    # ----------------------------------------------------------------------
    # DISPLAY FORMATTING WITH STATUS FLAGS
    # ----------------------------------------------------------------------
    def _format_for_display(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        order = [
            'age', 'gender', 'blood_pressure', 'cholesterol', 'glucose',
            'height', 'weight', 'bmi', 'heart_rate',
            'smoking', 'alcohol_intake', 'physical_activity',
            'diagnosis', 'medications'
        ]
        out = []
        for field in order:
            if field not in data:
                continue
            name = self.display_mapping.get(field, field.title())
            raw = data[field]
            unit = self.unit_mapping.get(field, '')

            value = f"{raw} {unit}".strip() if unit else str(raw)
            status = self._get_vital_status(field, raw)
            if status:
                value += f" ({status})"

            if field in ['diagnosis', 'medications'] and len(value) > 100:
                value = value[:100] + "..."

            out.append({
                'field': name,
                'value': value,
                'icon': 'Checkmark'
            })
        return out

    def _get_vital_status(self, field: str, value: str) -> str:
        try:
            num = float(re.sub(r'\D.*$', '', value.split('/')[0] if '/' in value else value))
            if field == 'blood_pressure' and num > 140:
                return 'High'
            if field == 'cholesterol' and num > 200:
                return 'High'
            if field == 'glucose' and num > 126:
                return 'High'
            if field == 'bmi' and num >= 30:
                return 'Obese'
        except:
            pass
        return ''

    # ----------------------------------------------------------------------
    # TEXT CLEANING & OCR
    # ----------------------------------------------------------------------
    def _extract_text_enhanced(self, image_path: str) -> str:
        raw = self.ocr_reader.extract_text(image_path)
        if not raw:
            return ""
        return self._clean_medical_text(raw)

    def _clean_medical_text(self, text: str) -> str:
        text = text.upper()

        corrections = {
            'CHOLLETROL': 'CHOLESTEROL', 'CHOL': 'CHOLESTEROL',
            'GLUCSE': 'GLUCOSE', 'GLU': 'GLUCOSE',
            'MEDS': 'MEDICATIONS', 'DX': 'DIAGNOSIS',
            'DC': 'DISCHARGE', 'HX': 'HISTORY'
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)

        # Remove typical discharge headers & footers
        text = re.sub(r'\bDISCHARGE\s+SUMMARY\b.*?(?=\b[A-Z]{3,})', '', text, flags=re.I | re.DOTALL)
        text = re.sub(r'CONFIDENTIAL.*|WWW\..*?COM', '', text, flags=re.I)
        text = re.sub(r'\*\s+HIGH\s*', ' ', text, flags=re.I)

        return re.sub(r'\s+', ' ', text).strip()

    # ----------------------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------------------
    def _clean_text_field(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.strip())

    def _calculate_bmi(self, height: str, weight: str) -> float:
        try:
            h = float(height) / 100
            w = float(weight)
            bmi = round(w / (h * h), 1)
            self.logger.info(f"BMI calculated: {bmi}")
            return bmi
        except:
            return None

    def _standardize_gender(self, g: str) -> str:
        return {'m': 'Male', 'f': 'Female'}.get(g.lower(), g.title())

    def _validate_field(self, field: str, value: str) -> bool:
        try:
            clean = re.sub(r'\s*(high|low|normal|mg/dl|mmhg|bpm).*', '', value, flags=re.I)
            if field == 'age':
                return 1 <= int(clean) <= 120
            if field == 'height':
                return 100 <= int(clean) <= 250
            if field == 'weight':
                return 30 <= int(clean) <= 200
            if field == 'blood_pressure':
                a, b = map(int, clean.split('/'))
                return 70 <= a <= 250 and 40 <= b <= 150
            if field in ['cholesterol', 'glucose']:
                return 50 <= int(clean) <= 400
            if field == 'heart_rate':
                return 40 <= int(clean) <= 200
            return True
        except:
            return False

    def _extract_diagnosis_insights(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        cardio = ['coronary', 'myocardial', 'heart failure', 'cad', 'chf', 'hypertension']
        diabetes = ['diabetes', 'dm', 'hyperglycemia']
        return {
            'has_heart_condition': any(k in lower for k in cardio),
            'has_diabetes': any(k in lower for k in diabetes)
        }

    def _error_response(self, msg: str) -> Dict[str, Any]:
        return {
            "error": msg,
            "document_type": "discharge_summary",
            "parsing_confidence": "error",
            "success": False
        }

    # ----------------------------------------------------------------------
    # TEST METHOD
    # ----------------------------------------------------------------------
    def test_ocr_discharge(self, image_path: str) -> Dict[str, Any]:
        self.logger.info(f"Testing discharge parser on {image_path}")
        try:
            raw = self.ocr_reader.extract_text(image_path)
            cleaned = self._clean_medical_text(raw)
            result = self.extract_data(image_path)
            return {
                "status": "success",
                "raw_length": len(raw),
                "cleaned_length": len(cleaned),
                "extracted": list(result.get("raw_data", {}).keys()),
                "preview": cleaned[:500] + "..." if len(cleaned) > 500 else cleaned
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}