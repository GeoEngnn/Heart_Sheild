# ocr/universal_reader.py
import logging
from typing import Dict, Any

# Import from the CORRECT paths
from .utils.document_classifier import DocumentClassifier
from .utils.data_validator import DataValidator
from .parsers.lab_report_parser import LabReportParser
from .parsers.discharge_parser import DischargeSummaryParser
from .parsers.clinic_notes_parser import ClinicNotesParser
from .parsers.fallback_parser import GeneralMedicalParser

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UniversalMedicalReader:
    """
    Orchestrates the end-to-end process of reading a medical document image,
    classifying its type, parsing its content, and validating the data.
    """
    def __init__(self):
        """Initializes the classifier, parsers, and validator."""
        self.classifier = DocumentClassifier()
        self.parsers = {
            'lab_report': LabReportParser(),
            'discharge_summary': DischargeSummaryParser(), 
            'clinic_notes': ClinicNotesParser(),
            'fallback': GeneralMedicalParser()
        }
        self.validator = DataValidator()
        logging.info("✅ UniversalMedicalReader initialized.")
    
    def process_any_document(self, image_path: str) -> Dict[str, Any]:
        """
        Enhanced to include ML predictions when data is complete
        """
        logging.info(f"🚀 Starting to process document: {image_path}")
        try:
            # 1. Classify the document type
            doc_type = self.classifier.classify_document_type(image_path)
            logging.info(f"📄 Document classified as: '{doc_type}'")

            # 2. Select the appropriate parser
            parser = self.parsers.get(doc_type, self.parsers['fallback'])
            logging.info(f"🔧 Using parser: {parser.__class__.__name__}")

            # 3. Extract data using the selected parser
            extracted_data = parser.extract_data(image_path)
            logging.info(f"🔍 Data extracted: {list(extracted_data.keys())}")

            # 4. Validate and prepare the data for prediction
            validation_result = self.validator.validate_and_prepare_prediction(extracted_data)
            logging.info(f"🛡️ Validation complete. Status: {validation_result.get('status', 'UNKNOWN')}")

            # 5. NEW: MAKE PREDICTION if data is ready!
            prediction_result = None
            if validation_result.get('status') == 'READY_FOR_PREDICTION':
                try:
                    # Import ML predictor
                    from ml.predictor import predictor
                    ml_input = self.validator.prepare_for_ml_model(validation_result)
                    
                    if ml_input:
                        prediction_result = predictor.predict_risk(ml_input)
                        logging.info(f"🎯 ML Prediction made: {prediction_result.get('risk_category', 'Unknown')}")
                except Exception as e:
                    logging.warning(f"⚠️ Prediction failed: {e}")
                    prediction_result = {"error": "Prediction unavailable", "message": str(e)}

            return {
                "status": "success",
                "document_type": doc_type,
                "extracted_data": extracted_data,
                "validation_result": validation_result,
                "prediction_result": prediction_result  # NEW: Include prediction!
            }
            
        except Exception as e:
            logging.error(f"❌ An error occurred during document processing: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "document_type": None,
                "extracted_data": None,
                "validation_result": None,
                "prediction_result": None
            }