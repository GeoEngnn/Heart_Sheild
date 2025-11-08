# check_model_files.py
import os
import pickle
from datetime import datetime

def check_model_files():
    print("🔍 CHECKING MODEL FILES:")
    
    # Check feature_names.pkl
    if os.path.exists('feature_names.pkl'):
        try:
            with open('feature_names.pkl', 'rb') as f:
                features = pickle.load(f)
            print(f"✅ feature_names.pkl FOUND - Features: {features}")
        except Exception as e:
            print(f"❌ feature_names.pkl CORRUPTED - Error: {e}")
    else:
        print("❌ feature_names.pkl NOT FOUND")
    
    # Check for model files
    model_files = []
    for file in os.listdir('.'):
        if file.endswith('.pkl') and 'model' in file.lower():
            model_files.append(file)
        if file.endswith('.h5') or file.endswith('.keras'):
            model_files.append(file)
    
    if model_files:
        print("✅ MODEL FILES FOUND:")
        for file in model_files:
            size = os.path.getsize(file) / 1024  # KB
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"   📁 {file} ({size:.1f} KB, modified: {mod_time})")
    else:
        print("❌ NO MODEL FILES FOUND")
    
    # Check ml folder
    if os.path.exists('ml'):
        ml_files = os.listdir('ml')
        print(f"📁 ml/ folder contents: {ml_files}")

if __name__ == '__main__':
    check_model_files()