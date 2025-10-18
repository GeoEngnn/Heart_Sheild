# create_test_document.py
from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple medical document image
img = Image.new('RGB', (600, 400), color='white')
d = ImageDraw.Draw(img)

# Add medical document text
medical_text = [
    "MEDICAL LAB REPORT",
    "Patient: John Doe",
    "Age: 45 years",
    "Blood Pressure: 120/80 mmHg", 
    "Cholesterol: 200 mg/dL",
    "Heart Rate: 72 bpm",
    "Glucose: 95 mg/dL",
    "Date: 2024-01-15"
]

y_position = 50
for line in medical_text:
    d.text((50, y_position), line, fill='black')
    y_position += 40

# Save the test image
img.save('test_medical_document.png')
print("✅ Test medical document created: test_medical_document.png")