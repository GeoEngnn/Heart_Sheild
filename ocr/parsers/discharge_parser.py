# ocr/parsers/discharge_parser.py
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class DischargeSummaryParser:
    """
    Parser for hospital discharge summaries and medical reports
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.discharge_patterns = {
            'age': r'age[\s:]*(\d+)',
            'blood_pressure': r'bp[\s:]*(\d+)/(\d+)|blood pressure[\s:]*(\d+)/(\d+)',
            'heart_rate': r'heart rate[\s:]*(\d+)|hr[\s:]*(\d+)',
            'cholesterol': r'cholesterol[\s:]*(\d+)',
            'diagnosis': r'diagnosis[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)',
            'medications': r'medications?[:\s]*(.+?)(?=\n\n|\n[A-Z]|$)'
        }
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract data from discharge summaries
        """
        self.logger.info(f"🏥 Processing discharge summary: {image_path}")
        
        try:
            text = self._extract_text(image_path)
            extracted_data = {}
            
            # Extract structured data
            for field, pattern in self.discharge_patterns.items():
                value = self._extract_field(text, pattern, field)
                if value:
                    extracted_data[field] = value
            
            # Extract additional context
            extracted_data['document_type'] = 'discharge_summary'
            extracted_data['text_snippet'] = text[:200] + "..." if len(text) > 200 else text
            
            self.logger.info(f"✅ Discharge summary parsed: {len(extracted_data)} fields found")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing discharge summary: {e}")
            return {"error": str(e), "document_type": "discharge_summary"}
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from discharge summary"""
        image = Image.open(image_path)
        return pytesseract.image_to_string(image).lower()
    
    def _extract_field(self, text: str, pattern: str, field_name: str):
        """Extract field with multiple pattern support"""
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            groups = match.groups()
            if field_name == 'blood_pressure' and groups:
                # Handle multiple BP pattern formats
                if groups[0] and groups[1]:
                    return f"{groups[0]}/{groups[1]}"
                elif groups[2] and groups[3]:
                    return f"{groups[2]}/{groups[3]}"
            elif field_name in ['diagnosis', 'medications']:
                return groups[0].strip() if groups else None
            else:
                return groups[0] if groups else None
        return None