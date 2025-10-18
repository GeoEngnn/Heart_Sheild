# ocr/utils/document_classifier.py
import re
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any

class DocumentClassifier:
    """
    Classifies medical documents into specific types for targeted parsing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keywords for document type classification
        self.document_keywords = {
            'lab_report': [
                'laboratory', 'lab report', 'test results', 'bun', 'creatinine',
                'blood test', 'chemistry', 'cbc', 'lipid profile', 'glucose',
                'reference range', 'normal range', 'specimen'
            ],
            'discharge_summary': [
                'discharge', 'admission', 'hospital course', 'discharged',
                'admitted', 'final diagnosis', 'discharge medications',
                'follow up', 'condition on discharge', 'hospital stay'
            ],
            'clinic_notes': [
                'clinic', 'follow-up', 'progress note', 'assessment',
                'subjective', 'objective', 'plan', 'soap', 'chief complaint',
                'physical exam', 'vital signs', 'clinic visit'
            ]
        }
        
        self.logger.info("✅ DocumentClassifier initialized")
    
    def classify_document_type(self, image_path: str) -> str:
        """
        Classify document type based on content analysis
        Returns: 'lab_report', 'discharge_summary', 'clinic_notes', or 'fallback'
        """
        self.logger.info(f"🔍 Classifying document: {image_path}")
        
        try:
            # Extract text from image
            text = self._extract_text(image_path)
            text_lower = text.lower()
            
            # Calculate scores for each document type
            scores = {}
            for doc_type, keywords in self.document_keywords.items():
                score = self._calculate_keyword_score(text_lower, keywords)
                scores[doc_type] = score
            
            # Determine the best match
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            self.logger.info(f"📊 Classification scores: {scores}")
            
            # Apply confidence threshold
            if best_score >= 2:  # At least 2 keyword matches
                self.logger.info(f"✅ Document classified as: {best_type}")
                return best_type
            else:
                self.logger.info("⚠️ Low confidence, using fallback parser")
                return 'fallback'
                
        except Exception as e:
            self.logger.error(f"❌ Error classifying document: {e}")
            return 'fallback'
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            self.logger.info(f"📝 Extracted {len(text)} characters for classification")
            return text
        except Exception as e:
            self.logger.error(f"❌ OCR failed during classification: {e}")
            return ""
    
    def _calculate_keyword_score(self, text: str, keywords: list) -> int:
        """Calculate how many keywords are found in the text"""
        score = 0
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                score += 1
        return score
    
    def get_classification_confidence(self, image_path: str) -> Dict[str, Any]:
        """
        Get detailed classification confidence scores
        """
        try:
            text = self._extract_text(image_path)
            text_lower = text.lower()
            
            confidence_scores = {}
            for doc_type, keywords in self.document_keywords.items():
                score = self._calculate_keyword_score(text_lower, keywords)
                max_possible = len(keywords)
                confidence = (score / max_possible) * 100 if max_possible > 0 else 0
                confidence_scores[doc_type] = {
                    'score': score,
                    'max_possible': max_possible,
                    'confidence_percent': round(confidence, 2)
                }
            
            # Determine best match
            best_type = max(confidence_scores, 
                          key=lambda x: confidence_scores[x]['confidence_percent'])
            
            return {
                'best_type': best_type,
                'confidence_scores': confidence_scores,
                'text_sample': text[:500] + "..." if len(text) > 500 else text
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating confidence: {e}")
            return {'best_type': 'fallback', 'error': str(e)}
    
    def is_medical_document(self, image_path: str) -> bool:
        """
        Basic check if document appears to be medical
        """
        try:
            text = self._extract_text(image_path)
            text_lower = text.lower()
            
            medical_indicators = [
                'patient', 'doctor', 'hospital', 'clinic', 'medical',
                'health', 'diagnosis', 'treatment', 'medication',
                'blood', 'pressure', 'heart', 'cholesterol'
            ]
            
            matches = sum(1 for indicator in medical_indicators 
                         if re.search(r'\b' + re.escape(indicator) + r'\b', text_lower))
            
            is_medical = matches >= 2  # At least 2 medical indicators
            self.logger.info(f"🏥 Medical document check: {is_medical} ({matches} indicators)")
            
            return is_medical
            
        except Exception as e:
            self.logger.error(f"❌ Error checking if medical document: {e}")
            return False