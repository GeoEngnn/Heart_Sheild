# ocr/parsers/clinic_notes_parser.py
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class ClinicNotesParser:
    """
    Parser for clinic notes and progress notes - handles less structured data
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clinic_patterns = {
            'age': r'age[\s:]*(\d+)',
            'blood_pressure': r'bp[\s:]*(\d+)/(\d+)',
            'heart_rate': r'hr[\s:]*(\d+)|heart rate[\s:]*(\d+)',
            'symptoms': r'symptoms?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
            'assessment': r'assessment[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
        }
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract data from clinic notes - more flexible parsing
        """
        self.logger.info(f"📋 Processing clinic notes: {image_path}")
        
        try:
            text = self._extract_text(image_path)
            extracted_data = {}
            
            # Try to extract structured data
            for field, pattern in self.clinic_patterns.items():
                value = self._extract_field(text, pattern, field)
                if value:
                    extracted_data[field] = value
            
            # For clinic notes, also look for free-form mentions
            if 'blood_pressure' not in extracted_data:
                bp_casual = self._extract_casual_bp(text)
                if bp_casual:
                    extracted_data['blood_pressure'] = bp_casual
            
            extracted_data['document_type'] = 'clinic_notes'
            extracted_data['has_clinical_data'] = len(extracted_data) > 1
            
            self.logger.info(f"✅ Clinic notes parsed: {len(extracted_data)} fields found")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing clinic notes: {e}")
            return {"error": str(e), "document_type": "clinic_notes"}
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from clinic notes"""
        image = Image.open(image_path)
        return pytesseract.image_to_string(image).lower()
    
    def _extract_field(self, text: str, pattern: str, field_name: str):
        """Extract field with flexible matching"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if field_name == 'blood_pressure':
                return f"{match.group(1)}/{match.group(2)}"
            return match.group(1)
        return None
    
    def _extract_casual_bp(self, text: str):
        """Extract blood pressure mentioned casually in text"""
        casual_bp_pattern = r'(\d+)\s*/\s*(\d+)'
        match = re.search(casual_bp_pattern, text)
        if match:
            systolic, diastolic = int(match.group(1)), int(match.group(2))
            if 50 <= systolic <= 250 and 30 <= diastolic <= 150:
                return f"{systolic}/{diastolic}"
        return None