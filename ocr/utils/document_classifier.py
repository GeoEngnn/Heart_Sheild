# ocr/utils/document_classifier.py - UPDATED WITH OCR.SPACE API
import re
import logging
from typing import Dict, Any

# Import the OCR.space reader from universal_reader
from ..universal_reader import OCRSpaceReader

class DocumentClassifier:
    """
    UPDATED: Classifies medical documents using OCR.space API for better accuracy
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # NEW: Use OCR.space API for text extraction
        self.ocr_reader = OCRSpaceReader()
        
        # UPDATED: Enhanced keywords for document type classification
        self.document_keywords = {
            'lab_report': [
                'laboratory', 'lab report', 'test results', 'bun', 'creatinine',
                'blood test', 'chemistry', 'cbc', 'lipid profile', 'glucose',
                'reference range', 'normal range', 'specimen', 'hematology',
                'biochemistry', 'urinalysis', 'wbc', 'rbc', 'platelet',
                'hemoglobin', 'cholesterol', 'triglyceride', 'tsh', 'fbs',
                'investigation', 'observed values', 'units', 'lab:'
            ],
            'discharge_summary': [
                'discharge', 'admission', 'hospital course', 'discharged',
                'admitted', 'final diagnosis', 'discharge medications',
                'follow up', 'condition on discharge', 'hospital stay',
                'discharge summary', 'admission date', 'discharge date',
                'history of present illness', 'hospital course',
                'discharge instructions', 'disposition'
            ],
            'clinic_notes': [
                'clinic', 'follow-up', 'progress note', 'assessment',
                'subjective', 'objective', 'plan', 'soap', 'chief complaint',
                'physical exam', 'vital signs', 'clinic visit', 'progress note',
                'office visit', 'consultation', 'review of systems',
                'past medical history', 'family history', 'social history',
                'medications', 'allergies', 'physical examination'
            ]
        }
        
        # NEW: Document structure patterns for additional confidence
        self.structure_patterns = {
            'lab_report': [
                r'reference\s+range', r'normal\s+values?', r'test\s+result',
                r'observed\s+value', r'units?\s*reference', r'lab\s*data'
            ],
            'discharge_summary': [
                r'admission\s+date.*discharge\s+date', 
                r'discharge\s+diagnosis', r'hospital\s+course',
                r'discharge\s+medications', r'follow.?up'
            ],
            'clinic_notes': [
                r'subjective.*objective.*assessment.*plan',
                r'chief\s+complaint', r'review\s+of\s+systems',
                r'physical\s+exam', r'assessment.*plan'
            ]
        }
        
        self.logger.info("✅ DocumentClassifier UPDATED with OCR.space API")
    
    def classify_document_type(self, image_path: str) -> str:
        """
        UPDATED: Classify document type using OCR.space API for better accuracy
        Returns: 'lab_report', 'discharge_summary', 'clinic_notes', or 'fallback'
        """
        self.logger.info(f"🔍 Classifying document with OCR.space: {image_path}")
        
        try:
            # NEW: Use OCR.space API for superior text extraction
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.warning("⚠️ Insufficient text for classification")
                return 'fallback'
                
            text_lower = text.lower()
            self.logger.info(f"📝 OCR.space extracted {len(text)} chars for classification")
            
            # Calculate scores for each document type
            scores = {}
            for doc_type, keywords in self.document_keywords.items():
                keyword_score = self._calculate_keyword_score(text_lower, keywords)
                structure_score = self._calculate_structure_score(text_lower, doc_type)
                total_score = keyword_score + structure_score
                scores[doc_type] = total_score
            
            # Determine the best match
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            self.logger.info(f"📊 Enhanced classification scores: {scores}")
            
            # Apply confidence threshold (higher due to better OCR quality)
            if best_score >= 3:  # At least 3 combined matches
                self.logger.info(f"✅ Document classified as: {best_type} (score: {best_score})")
                return best_type
            else:
                self.logger.info(f"⚠️ Low confidence ({best_score}), using fallback parser")
                return 'fallback'
                
        except Exception as e:
            self.logger.error(f"❌ Error classifying document: {e}")
            return 'fallback'
    
    def _extract_text_enhanced(self, image_path: str) -> str:
        """
        NEW: Extract text using OCR.space API with enhanced cleaning
        """
        try:
            # Use OCR.space API for superior text extraction
            raw_text = self.ocr_reader.extract_text(image_path)
            
            if not raw_text:
                self.logger.warning("❌ No text extracted by OCR.space for classification")
                return ""
            
            # Enhanced text cleaning for classification
            cleaned_text = self._clean_classification_text(raw_text)
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"❌ OCR.space extraction failed during classification: {e}")
            return ""
    
    def _clean_classification_text(self, text: str) -> str:
        """
        NEW: Enhanced cleaning for classification text
        """
        # Common OCR corrections for medical document classification
        classification_corrections = {
            'lab0ratory': 'laboratory', 'rep0rt': 'report', 'resu1ts': 'results',
            'discarge': 'discharge', 'admision': 'admission', 'c1inic': 'clinic',
            'diagrosis': 'diagnosis', 'med1cation': 'medication', 'physica1': 'physical'
        }
        
        cleaned_text = text.lower()
        
        # Apply classification-specific corrections
        for wrong, correct in classification_corrections.items():
            cleaned_text = cleaned_text.replace(wrong.lower(), correct)
        
        # Remove extra whitespace but preserve structure
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text
    
    def _calculate_keyword_score(self, text: str, keywords: list) -> int:
        """Calculate how many keywords are found in the text"""
        score = 0
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                score += 1
                self.logger.debug(f"✅ Keyword matched: {keyword}")
        return score
    
    def _calculate_structure_score(self, text: str, doc_type: str) -> int:
        """Calculate score based on document structure patterns"""
        score = 0
        if doc_type in self.structure_patterns:
            for pattern in self.structure_patterns[doc_type]:
                if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                    score += 2  # Structure patterns are more valuable
                    self.logger.debug(f"✅ Structure pattern matched for {doc_type}: {pattern}")
        return score
    
    def get_classification_confidence(self, image_path: str) -> Dict[str, Any]:
        """
        UPDATED: Get detailed classification confidence scores using OCR.space
        """
        try:
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                return {
                    'best_type': 'fallback',
                    'confidence_scores': {},
                    'error': 'Insufficient text for classification',
                    'ocr_engine': 'ocr_space_api'
                }
                
            text_lower = text.lower()
            
            confidence_scores = {}
            for doc_type, keywords in self.document_keywords.items():
                keyword_score = self._calculate_keyword_score(text_lower, keywords)
                structure_score = self._calculate_structure_score(text_lower, doc_type)
                total_score = keyword_score + structure_score
                max_possible = len(keywords) + (len(self.structure_patterns.get(doc_type, [])) * 2)
                
                confidence = (total_score / max_possible) * 100 if max_possible > 0 else 0
                confidence_scores[doc_type] = {
                    'keyword_score': keyword_score,
                    'structure_score': structure_score,
                    'total_score': total_score,
                    'max_possible': max_possible,
                    'confidence_percent': round(confidence, 2)
                }
            
            # Determine best match
            best_type = max(confidence_scores, 
                          key=lambda x: confidence_scores[x]['confidence_percent'])
            
            return {
                'best_type': best_type,
                'confidence_scores': confidence_scores,
                'text_sample': text[:500] + "..." if len(text) > 500 else text,
                'ocr_engine': 'ocr_space_api',
                'text_length': len(text)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating confidence: {e}")
            return {
                'best_type': 'fallback', 
                'error': str(e),
                'ocr_engine': 'ocr_space_api'
            }
    
    def is_medical_document(self, image_path: str) -> bool:
        """
        UPDATED: Enhanced check if document appears to be medical using OCR.space
        """
        try:
            text = self._extract_text_enhanced(image_path)
            
            if not text or len(text.strip()) < 10:
                return False
                
            text_lower = text.lower()
            
            medical_indicators = [
                'patient', 'doctor', 'hospital', 'clinic', 'medical',
                'health', 'diagnosis', 'treatment', 'medication',
                'blood', 'pressure', 'heart', 'cholesterol', 'glucose',
                'laboratory', 'test', 'result', 'vital', 'signs',
                'prescription', 'symptom', 'assessment', 'plan'
            ]
            
            matches = sum(1 for indicator in medical_indicators 
                         if re.search(r'\b' + re.escape(indicator) + r'\b', text_lower))
            
            is_medical = matches >= 2  # At least 2 medical indicators
            self.logger.info(f"🏥 Medical document check: {is_medical} ({matches} indicators)")
            
            return is_medical
            
        except Exception as e:
            self.logger.error(f"❌ Error checking if medical document: {e}")
            return False
    
    def test_classification(self, image_path: str) -> Dict[str, Any]:
        """
        NEW: Test method to verify classification with OCR.space
        """
        self.logger.info(f"🧪 Testing document classification with: {image_path}")
        
        try:
            # Get detailed confidence analysis
            confidence_data = self.get_classification_confidence(image_path)
            
            # Perform classification
            doc_type = self.classify_document_type(image_path)
            
            # Check if medical document
            is_medical = self.is_medical_document(image_path)
            
            return {
                "status": "success",
                "classified_as": doc_type,
                "is_medical_document": is_medical,
                "confidence_analysis": confidence_data,
                "ocr_engine": "ocr_space_api"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Classification test failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "ocr_engine": "ocr_space_api"
            }