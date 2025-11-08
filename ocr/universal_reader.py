# ocr/universal_reader.py - ENHANCED WITH SMART DISPLAY SUPPORT
import requests
import logging
from typing import Dict, Any
from PIL import Image
import pytesseract

# Import OCR.space configuration
from .config import OCR_SPACE_API_KEY, OCR_SPACE_API_URL, OCR_CONFIG

# Import from the CORRECT paths
from .utils.document_classifier import DocumentClassifier
from .utils.data_validator import DataValidator
from .parsers.lab_report_parser import LabReportParser
from .parsers.discharge_parser import DischargeSummaryParser
from .parsers.clinic_notes_parser import ClinicNotesParser
from .parsers.fallback_parser import GeneralMedicalParser

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OCRSpaceReader:
    """
    OCR.space API integration for superior text extraction
    """
    def __init__(self):
        self.api_key = OCR_SPACE_API_KEY
        self.api_url = OCR_SPACE_API_URL
        self.logger = logging.getLogger(__name__)
        
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using OCR.space API with fallback to Tesseract
        """
        try:
            self.logger.info(f"🔍 Using OCR.space API for: {image_path}")
            
            with open(image_path, 'rb') as image_file:
                response = requests.post(
                    self.api_url,
                    files={'image': image_file},
                    data=OCR_CONFIG,
                    headers={'apikey': self.api_key}
                )
            
            if response.status_code == 200:
                result = response.json()
                if result['IsErroredOnProcessing']:
                    error_msg = result['ErrorMessage'][0] if result['ErrorMessage'] else "Unknown API error"
                    self.logger.error(f"❌ OCR.space API error: {error_msg}")
                    return self._fallback_to_tesseract(image_path)
                
                # Extract text from all parsed results
                text = self._parse_ocr_result(result)
                self.logger.info(f"✅ OCR.space extracted {len(text)} characters")
                return text
            else:
                self.logger.error(f"❌ API request failed: {response.status_code}")
                return self._fallback_to_tesseract(image_path)
                
        except Exception as e:
            self.logger.error(f"❌ OCR.space processing failed: {e}")
            return self._fallback_to_tesseract(image_path)
    
    def _parse_ocr_result(self, result: Dict[str, Any]) -> str:
        """
        Parse OCR.space API response and extract text
        """
        text_parts = []
        
        if 'ParsedResults' in result:
            for parsed_result in result['ParsedResults']:
                if 'ParsedText' in parsed_result:
                    text_parts.append(parsed_result['ParsedText'].strip())
        
        full_text = '\n'.join(text_parts)
        self.logger.debug(f"📄 Raw OCR.space text: {full_text[:500]}...")
        return full_text
    
    def _fallback_to_tesseract(self, image_path: str) -> str:
        """
        Fallback to Tesseract if OCR.space fails
        """
        self.logger.info("🔄 Falling back to Tesseract OCR")
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            self.logger.info(f"✅ Tesseract extracted {len(text)} characters")
            return text
        except Exception as e:
            self.logger.error(f"❌ Tesseract fallback also failed: {e}")
            return ""

class UniversalMedicalReader:
    """
    ENHANCED: Universal medical document reader with SMART DISPLAY support
    """
    def __init__(self):
        """Initializes the OCR reader, classifier, parsers, and validator"""
        # Use OCR.space API for text extraction
        self.ocr_reader = OCRSpaceReader()
        
        self.classifier = DocumentClassifier()
        self.parsers = {
            'lab_report': LabReportParser(),
            'discharge_summary': DischargeSummaryParser(), 
            'clinic_notes': ClinicNotesParser(),
            'fallback': GeneralMedicalParser()
        }
        self.validator = DataValidator()
        
        # Define required features for the new model
        self.required_features = [
            'Age', 'Height', 'Weight', 'Gender', 'Systolic_BP', 'Diastolic_BP',
            'Cholesterol', 'Glucose', 'Smoking', 'Alcohol_Intake', 'Physical_Activity', 'BMI'
        ]
        
        logging.info("✅ UniversalMedicalReader ENHANCED with smart display support!")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Direct text extraction using OCR.space API
        """
        return self.ocr_reader.extract_text(image_path)
    
    def process_any_document(self, image_path: str) -> Dict[str, Any]:
        """
        ENHANCED: Process any medical document with SMART DISPLAY output
        """
        logging.info(f"🚀 Starting to process document with OCR.space: {image_path}")
        try:
            # First extract text using OCR.space API
            extracted_text = self.extract_text_from_image(image_path)
            logging.info(f"📄 OCR.space extracted {len(extracted_text)} characters")
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                logging.warning("⚠️ Insufficient text extracted from document")
                return {
                    "status": "error",
                    "message": "Could not extract sufficient text from document",
                    "extracted_text_preview": extracted_text[:200] if extracted_text else "None",
                    "success": False
                }

            # 1. Classify the document type
            doc_type = self.classifier.classify_document_type(image_path)
            logging.info(f"📄 Document classified as: '{doc_type}'")

            # 2. Select the appropriate parser
            parser = self.parsers.get(doc_type, self.parsers['fallback'])
            logging.info(f"🔧 Using parser: {parser.__class__.__name__}")

            # 3. Extract data using the selected parser (now returns display_data)
            parser_result = parser.extract_data(image_path)
            logging.info(f"🔍 Data extracted: {list(parser_result.keys())}")

            # Check if parser returned success
            if not parser_result.get('success', True):
                logging.warning(f"⚠️ Parser returned error: {parser_result.get('error', 'Unknown error')}")
                return {
                    "status": "error",
                    "message": parser_result.get('error', 'Parser failed'),
                    "document_type": doc_type,
                    "success": False
                }

            # Extract both raw and display data
            extracted_data = parser_result.get('raw_data', {})
            display_data = parser_result.get('display_data', [])  # NEW: Smart display data
            
            # If no display_data, create basic display from raw data
            if not display_data and extracted_data:
                display_data = self._create_basic_display(extracted_data)

            # 4. Validate and prepare the data for NEW FEATURES prediction
            validation_result = self.validator.validate_and_prepare_prediction(extracted_data)
            logging.info(f"🛡️ Validation complete. Status: {validation_result.get('status', 'UNKNOWN')}")

            # 5. MAKE PREDICTION with NEW FEATURES if data is ready!
            prediction_result = None
            if validation_result.get('status') == 'READY_FOR_PREDICTION':
                try:
                    # Import ML predictor
                    from ml.predictor import predictor
                    
                    # Prepare data for new ML model
                    ml_input = self._prepare_for_new_ml_model(validation_result)
                    
                    if ml_input:
                        prediction_result = predictor.predict_risk(ml_input)
                        logging.info(f"🎯 ML Prediction made with NEW FEATURES: {prediction_result.get('risk_category', 'Unknown')}")
                    else:
                        logging.warning("⚠️ Could not prepare data for ML model")
                        prediction_result = {"error": "Data preparation failed", "message": "Insufficient data for new model"}
                        
                except ImportError as e:
                    logging.warning(f"⚠️ ML predictor import failed: {e}")
                    prediction_result = {"error": "ML model unavailable", "message": str(e)}
                except Exception as e:
                    logging.warning(f"⚠️ Prediction failed: {e}")
                    prediction_result = {"error": "Prediction unavailable", "message": str(e)}

            # NEW: Enhanced return with display_data
            result = {
                "status": "success",
                "document_type": doc_type,
                "parser_used": parser.__class__.__name__,
                "raw_data": extracted_data,
                "display_data": display_data,  # NEW: Clean formatted data for UI
                "validation_result": validation_result,
                "prediction_result": prediction_result,
                "model_features": self.required_features,
                "ocr_engine": "OCR.space API",
                "text_length": len(extracted_text),
                "success": True
            }
            
            # Add feature coverage info
            coverage = self.check_feature_coverage(extracted_data)
            result["feature_coverage"] = coverage
            
            return result
            
        except Exception as e:
            logging.error(f"❌ An error occurred during document processing: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "document_type": None,
                "raw_data": None,
                "display_data": [],
                "validation_result": None,
                "prediction_result": None,
                "model_features": self.required_features,
                "ocr_engine": "Unknown",
                "success": False
            }
    
    def _create_basic_display(self, extracted_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Create basic display data if parser doesn't provide it
        """
        display_list = []
        
        # Simple mapping for display
        display_mapping = {
            'age': 'Age',
            'height': 'Height',
            'weight': 'Weight',
            'gender': 'Gender',
            'blood_pressure': 'Blood Pressure',
            'systolic_bp': 'Systolic BP',
            'diastolic_bp': 'Diastolic BP',
            'cholesterol': 'Cholesterol',
            'glucose': 'Glucose',
            'heart_rate': 'Heart Rate',
            'bmi': 'BMI'
        }
        
        unit_mapping = {
            'age': 'years',
            'height': 'cm',
            'weight': 'kg',
            'blood_pressure': 'mmHg',
            'systolic_bp': 'mmHg',
            'diastolic_bp': 'mmHg',
            'cholesterol': 'mg/dL',
            'glucose': 'mg/dL',
            'heart_rate': 'bpm',
            'bmi': 'kg/m²'
        }
        
        for field, value in extracted_data.items():
            if field in display_mapping and value not in [None, '']:
                display_name = display_mapping[field]
                unit = unit_mapping.get(field, '')
                
                if unit:
                    display_value = f"{value} {unit}"
                else:
                    display_value = str(value)
                
                display_list.append({
                    'field': display_name,
                    'value': display_value,
                    'icon': '✅'
                })
        
        return display_list
    
    def _prepare_for_new_ml_model(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare extracted data for the NEW ML model with new features
        """
        try:
            extracted_data = validation_result.get('validated_data', {})
            prepared_data = {}
            
            # Map OCR extracted data to ML model expected format
            mapping = {
                'age': 'Age',
                'height': 'Height', 
                'weight': 'Weight',
                'gender': 'Gender',
                'systolic_bp': 'Systolic_BP',
                'diastolic_bp': 'Diastolic_BP', 
                'cholesterol': 'Cholesterol',
                'glucose': 'Glucose',
                'smoking': 'Smoking',
                'alcohol_intake': 'Alcohol_Intake',
                'physical_activity': 'Physical_Activity',
                'bmi': 'BMI'
            }
            
            # Apply mapping
            for ocr_key, ml_key in mapping.items():
                if ocr_key in extracted_data:
                    prepared_data[ml_key] = extracted_data[ocr_key]
            
            # Calculate BMI if not provided but height/weight available
            if 'BMI' not in prepared_data and 'Height' in prepared_data and 'Weight' in prepared_data:
                try:
                    height_m = prepared_data['Height'] / 100
                    prepared_data['BMI'] = prepared_data['Weight'] / (height_m ** 2)
                    logging.info(f"✅ BMI calculated: {prepared_data['BMI']:.1f}")
                except Exception as e:
                    logging.warning(f"⚠️ BMI calculation failed: {e}")
            
            # Ensure Gender is properly formatted
            if 'Gender' in prepared_data:
                gender = str(prepared_data['Gender']).lower()
                if gender in ['m', 'male']:
                    prepared_data['Gender'] = 'Male'
                elif gender in ['f', 'female']:
                    prepared_data['Gender'] = 'Female'
                else:
                    prepared_data['Gender'] = 'Male'  # Default
            
            # Ensure lifestyle factors are integers
            lifestyle_fields = ['Smoking', 'Alcohol_Intake', 'Physical_Activity']
            for field in lifestyle_fields:
                if field in prepared_data:
                    try:
                        prepared_data[field] = int(prepared_data[field])
                    except (ValueError, TypeError):
                        prepared_data[field] = 0  # Default to no
            
            # Provide defaults for missing critical fields
            defaults = {
                'Age': 50,
                'Height': 170,
                'Weight': 70, 
                'Gender': 'Male',
                'Systolic_BP': 120,
                'Diastolic_BP': 80,
                'Cholesterol': 200,
                'Glucose': 100,
                'Smoking': 0,
                'Alcohol_Intake': 0,
                'Physical_Activity': 1,
                'BMI': 24.2
            }
            
            for field, default_value in defaults.items():
                if field not in prepared_data:
                    prepared_data[field] = default_value
                    logging.info(f"⚠️ Using default for {field}: {default_value}")
            
            logging.info(f"🔧 Prepared ML input: {list(prepared_data.keys())}")
            return prepared_data
            
        except Exception as e:
            logging.error(f"❌ Error preparing ML data: {e}")
            return None
    
    def get_required_features(self) -> list:
        """Return the features required by the new ML model"""
        return self.required_features.copy()
    
    def check_feature_coverage(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check how well the extracted data covers required features
        """
        coverage = {
            'total_required': len(self.required_features),
            'extracted_count': 0,
            'missing_features': [],
            'coverage_percentage': 0.0
        }
        
        extracted_keys = [key.lower() for key in extracted_data.keys()]
        
        for feature in self.required_features:
            feature_lower = feature.lower()
            # Check direct match or partial match
            if (feature_lower in extracted_keys or 
                any(feature_lower in key for key in extracted_keys)):
                coverage['extracted_count'] += 1
            else:
                coverage['missing_features'].append(feature)
        
        coverage['coverage_percentage'] = (coverage['extracted_count'] / coverage['total_required']) * 100
        
        return coverage

# Create a global instance for easy import
universal_reader = UniversalMedicalReader()