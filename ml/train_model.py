# ml/train_model.py - FIXED FOR CATEGORICAL DATA
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os

print("🧠 STARTING HEARTSHIELD ML MODEL TRAINING WITH REAL DATASET...")

# Load YOUR REAL DATASET from the exact path
dataset_path = r'C:\Users\GEO THOMAS\HeartShield\ml\heartshield_dataset.csv'

try:
    # Load your real dataset
    df = pd.read_csv(dataset_path)
    print(f"✅ YOUR REAL DATASET LOADED: {df.shape[0]} patients, {df.shape[1]} features")
    print(f"📋 Dataset columns: {list(df.columns)}")
    
except FileNotFoundError:
    print(f"❌ Dataset not found at: {dataset_path}")
    print("❌ Please check the file path and make sure the file exists")
    exit()
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit()

# Auto-detect target column
possible_targets = ['Cardiovascular_Disease', 'HeartDisease', 'heart_disease', 'target', 'Heart_Disease', 'heartdisease', 'HeartDiseaseFlag']
target_column = None

for col in possible_targets:
    if col in df.columns:
        target_column = col
        print(f"🎯 Using target column: '{target_column}'")
        break

print(f"🎯 FINAL TARGET COLUMN: '{target_column}'")

# Define expected features for NEW dataset
expected_features = ['Age', 'Height', 'Weight', 'Gender', 'Systolic_BP', 'Diastolic_BP', 
                   'Cholesterol', 'Glucose', 'Smoking', 'Alcohol_Intake', 'Physical_Activity']

# Check which expected features are available
available_features = []
for feature in expected_features:
    if feature in df.columns:
        available_features.append(feature)
    else:
        print(f"⚠️  Expected feature '{feature}' not found in dataset")

# Add BMI feature
if 'Height' in df.columns and 'Weight' in df.columns:
    if 'BMI' not in df.columns:
        df['BMI'] = df['Weight'] / (df['Height']/100) ** 2
        print("✅ BMI feature calculated from Height/Weight")
    available_features.append('BMI')
else:
    print("⚠️  Cannot calculate BMI - Height or Weight columns missing")

print(f"🔧 Initial features: {available_features}")

# Handle categorical variables (like 'Gender')
label_encoders = {}
categorical_features = []

for feature in available_features:
    if df[feature].dtype == 'object':  # If it's string data
        print(f"🔤 Encoding categorical feature: '{feature}'")
        le = LabelEncoder()
        df[feature] = le.fit_transform(df[feature])
        label_encoders[feature] = le
        categorical_features.append(feature)
        print(f"   Encoded values: {dict(zip(le.classes_, le.transform(le.classes_)))}")

print(f"✅ Encoded {len(categorical_features)} categorical features: {categorical_features}")

# Prepare features and target
X = df[available_features]
y = df[target_column]

print(f"📊 Dataset shape: {df.shape}")
print(f"🎯 Target distribution: {y.value_counts().to_dict()}")

# Check for missing values
if X.isnull().sum().sum() > 0:
    print("⚠️  Missing values detected. Handling missing values...")
    # Fill numeric columns with median
    for col in X.columns:
        if X[col].dtype in ['int64', 'float64']:
            X[col].fillna(X[col].median(), inplace=True)
    print("✅ Missing values handled")

# Check data types
print(f"🔍 Final data types:")
for col in X.columns:
    print(f"   {col}: {X[col].dtype}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"📚 Training set: {X_train.shape[0]} samples")
print(f"🧪 Testing set: {X_test.shape[0]} samples")

# Train model
print("\n🏃 Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"✅ Model Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")

# Save model and encoders
model_filename = 'heart_disease_model.pkl'
joblib.dump(model, model_filename)
joblib.dump(available_features, 'feature_names.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')  # Save encoders for prediction
print(f"💾 Model saved as '{model_filename}'")
print(f"💾 Feature names saved as 'feature_names.pkl'")
print(f"💾 Label encoders saved as 'label_encoders.pkl'")

# Verify model can be loaded
try:
    test_model = joblib.load(model_filename)
    test_pred = test_model.predict(X_test.iloc[:1])
    print(f"🧪 Model verification: Prediction = {test_pred[0]}")
    print("✅ Model saved and loaded successfully!")
except Exception as e:
    print(f"❌ Model verification failed: {e}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': available_features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🔍 FEATURE IMPORTANCE:")
print(feature_importance)

print("\n📋 CLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred))

print("\n🎉 HEARTSHIELD ML MODEL TRAINING COMPLETED!")
print("🚀 Model is ready for use in the Flask app!")