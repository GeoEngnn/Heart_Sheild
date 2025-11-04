# test_ocr_space.py (create in project root)
import sys
import os

# Add OCR module to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ocr'))

from ocr.universal_reader import UniversalOCRReader

def test_ocr_space():
    print("🧪 Testing OCR.space API Integration...")
    
    # Initialize the OCR reader
    reader = UniversalOCRReader()
    
    # Test with your lab report image
    test_image_path = "path/to/your/lab_report.png"  # Replace with actual path
    
    print(f"📷 Processing image: {test_image_path}")
    
    try:
        # Extract text using OCR.space
        text = reader.extract_text(test_image_path)
        
        print("✅ OCR.space Test Results:")
        print("=" * 50)
        print(f"📄 First 1000 characters:")
        print(text[:1000] if text else "No text extracted")
        print("=" * 50)
        print(f"📊 Total characters extracted: {len(text)}")
        print(f"🔍 Text preview: {text[:200]}..." if text else "No text")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_space()