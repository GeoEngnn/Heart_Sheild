# ocr/config.py
OCR_SPACE_API_KEY = 'K8187508888957'  # Your API key
OCR_SPACE_API_URL = 'https://api.ocr.space/parse/image'

# Medical document specific settings
OCR_CONFIG = {
    'language': 'eng',
    'isOverlayRequired': False,
    'isTable': True,  # Important for lab reports
    'scale': True,
    'isCreateSearchablePdf': False,
    'isSearchablePdfHideTextLayer': False,
    'detectOrientation': True,
    'isEraseLines': False  # Keep lines for table structure
}