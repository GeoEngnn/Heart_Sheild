# ml/train_model.py - COMPLETE FIXED VERSION
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

print("🧠 STARTING HEARTSHIELD ML MODEL TRAINING...")

# Load our cleaned dataset - CORRECTED PATH
try:
    # Try to load from current directory (if running from ml folder)
    df = pd.read_csv('heart_disease_cleaned.csv')
    print(f"✅ Dataset loaded: {df.shape[0]} patients, {df.shape[1]} features")
except FileNotFoundError:
    try:
        # Try to load from ml folder (if running from main folder)
        df = pd.read_csv('ml/heart_disease_cleaned.csv')
        print(f"✅ Dataset loaded from ml folder: {df.shape[0]} patients")
    except FileNotFoundError:
        print("❌ CSV file not found in any location!")
        print("📁 Current directory:", os.getcwd())
        print("📁 Files here:", os.listdir('.'))
        if os.path.exists('ml'):
            print("📁 Files in ml folder:", os.listdir('ml'))
        exit(1)

# Prepare features and target
X = df.drop(['target', 'heart_disease'], axis=1)  # Features
y = df['heart_disease']  # Target (0 = healthy, 1 = heart disease)

print(f"📊 Features: {list(X.columns)}")
print(f"🎯 Target distribution: {y.value_counts().to_dict()}")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"📈 Training set: {X_train.shape[0]} samples")
print(f"📊 Testing set: {X_test.shape[0]} samples")

# Initialize models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
}

# Train and evaluate models
best_model = None
best_score = 0
model_results = {}

print("\n🔬 TRAINING MODELS...")
print("=" * 50)

for name, model in models.items():
    print(f"\n🏃 Training {name}...")
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    model_results[name] = {
        'model': model,
        'accuracy': accuracy,
        'predictions': y_pred
    }
    
    print(f"✅ {name} Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Update best model
    if accuracy > best_score:
        best_score = accuracy
        best_model = name

print("\n" + "=" * 50)
print(f"🏆 BEST MODEL: {best_model} with {best_score:.3f} accuracy")

# Save the best model
best_model_obj = model_results[best_model]['model']
joblib.dump(best_model_obj, 'heart_disease_model.pkl')
print("💾 Model saved as 'heart_disease_model.pkl'")

# Feature importance (for Random Forest)
if hasattr(best_model_obj, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model_obj.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔍 TOP 10 MOST IMPORTANT FEATURES:")
    print(feature_importance.head(10))

# Detailed classification report
print(f"\n📋 DETAILED PERFORMANCE REPORT FOR {best_model}:")
print(classification_report(y_test, model_results[best_model]['predictions']))

# Confusion matrix
cm = confusion_matrix(y_test, model_results[best_model]['predictions'])
print(f"🎯 CONFUSION MATRIX:")
print(f"True Negatives: {cm[0][0]} | False Positives: {cm[0][1]}")
print(f"False Negatives: {cm[1][0]} | True Positives: {cm[1][1]}")

# Test prediction on a sample patient
sample_patient = X_test.iloc[0:1]  # First test patient
prediction = best_model_obj.predict(sample_patient)[0]
probability = best_model_obj.predict_proba(sample_patient)[0]

print(f"\n🧪 SAMPLE PREDICTION TEST:")
print(f"Actual: {'Heart Disease' if y_test.iloc[0] == 1 else 'Healthy'}")
print(f"Predicted: {'Heart Disease' if prediction == 1 else 'Healthy'}")
print(f"Confidence: {max(probability):.2%}")

print("\n🎉 HEARTSHIELD ML MODEL TRAINING COMPLETED!")
print("🚀 Next: Integrate this model with our Flask app!")