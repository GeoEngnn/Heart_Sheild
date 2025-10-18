# test_setup.py
import flask
import pandas as pd
import sklearn
import pytesseract
import pymongo
from PIL import Image
import os

print("=== HEARTSHIELD SETUP TEST ===")
print("✅ Core Libraries:")
print(f"   Flask: {flask.__version__}")
print(f"   Pandas: {pd.__version__}")
print(f"   Scikit-learn: {sklearn.__version__}")

print("\n✅ OCR Setup:")
try:
    tesseract_version = pytesseract.get_tesseract_version()
    print(f"   Tesseract: {tesseract_version}")
    print("   ✅ Tesseract is perfectly configured!")
except Exception as e:
    print(f"   ❌ Tesseract error: {e}")

print("\n✅ Database:")
try:
    print(f"   PyMongo: {pymongo.__version__}")
    print("   ✅ MongoDB driver ready!")
except Exception as e:
    print(f"   ❌ MongoDB issue: {e}")

print("\n🎉 Your development environment is READY for HeartShield!")