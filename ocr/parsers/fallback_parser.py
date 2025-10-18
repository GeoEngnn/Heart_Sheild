# ocr/parsers/fallback_parser.py
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class GeneralMedicalParser:
    """
    Fallback parser for any medical document - uses general medical term extraction
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.general_patterns = {
            'age': r'age[\s:]*(\d+)',
            'blood_pressure': r'(\d+)/(\d+)',
            'cholesterol': r'chol[\s:]*(\d+)',
            'heart_rate': r'(\d+)\s*bpm',
            'any_numbers': r'\b(\d{2,3})\b'  # Catch any 2-3 digit numbers that might be medical values
        }
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        General medical document parsing - tries to extract any medical data found
        """
        self.logger.info(f"🔍 Processing general medical document: {image_path}")
        
        try:
            text = self._extract_text(image_path)
            extracted_data = {}
            
            # Try all patterns
            for field, pattern in self.general_patterns.items():
                if field == 'any_numbers':
                    continue  # Special handling
                value = self._extract_field(text, pattern, field)
                if value:
                    extracted_data[field] = value
            
            # Smart BP detection from any numbers
            if 'blood_pressure' not in extracted_data:
                bp = self._smart_bp_detection(text)
                if bp:
                    extracted_data['blood_pressure'] = bp
            
            extracted_data['document_type'] = 'general_medical'
            extracted_data['text_length'] = len(text)
            extracted_data['parsing_confidence'] = 'low'
            
            self.logger.info(f"⚠️ General medical document parsed: {len(extracted_data)} fields found")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing general medical document: {e}")
            return {"error": str(e), "document_type": "general_medical"}
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from any document"""
        image = Image.open(image_path)
        return pytesseract.image_to_string(image).lower()
    
    def _extract_field(self, text: str, pattern: str, field_name: str):
        """Extract field with general matching"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if field_name == 'blood_pressure':
                # Validate it's a reasonable BP
                systolic, diastolic = int(match.group(1)), int(match.group(2))
                if 70 <= systolic <= 250 and 40 <= diastolic <= 150:
                    return f"{systolic}/{diastolic}"
            else:
                return match.group(1)
        return None
    
    def _smart_bp_detection(self, text: str):
        """Smart detection of blood pressure from context"""
        # Look for numbers in BP range that appear together
        bp_candidates = re.findall(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
        for systolic, diastolic in bp_candidates:
            systolic, diastolic = int(systolic), int(diastolic)
            if 70 <= systolic <= 250 and 40 <= diastolic <= 150:
                return f"{systolic}/{diastolic}"
        return None