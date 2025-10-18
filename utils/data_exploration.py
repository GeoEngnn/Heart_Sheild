# data_exploration.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("🔍 Loading Heart Disease Dataset...")

# Load the Cleveland heart disease dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"

# Column names as per the dataset documentation
column_names = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
]

# Load the data
df = pd.read_csv(url, names=column_names, na_values='?')
print("✅ Dataset loaded successfully!")


print("\n📊 BASIC DATASET INFO:")
print(f"Shape: {df.shape}")  # (rows, columns)
print(f"Columns: {list(df.columns)}")

print("\n👀 FIRST 5 ROWS:")
print(df.head())

print("\n📈 DATASET SUMMARY:")
print(df.info())

print("\n🔢 STATISTICAL SUMMARY:")
print(df.describe())
# data_exploration.py - ADD THIS SECTION

print("\n🎯 TARGET VARIABLE ANALYSIS:")
print("Target value counts:")
print(df['target'].value_counts().sort_index())

print("\n🧬 UNDERSTANDING THE TARGET:")
print("0: No disease | 1-4: Various levels of heart disease presence")

# Convert target to binary for simpler classification (common approach)
df['heart_disease'] = df['target'].apply(lambda x: 1 if x > 0 else 0)

print(f"\n🔬 Binary Classification:")
print(f"Heart Disease: {df['heart_disease'].sum()} patients")
print(f"No Heart Disease: {len(df) - df['heart_disease'].sum()} patients")
print(f"Disease Rate: {(df['heart_disease'].sum()/len(df))*100:.1f}%")

print("\n❓ MISSING VALUES:")
missing_data = df.isnull().sum()
print(missing_data[missing_data > 0])
# data_exploration.py - ADD THIS SECTION

print("\n🏥 MEDICAL FEATURE EXPLANATION:")
feature_descriptions = {
    'age': 'Age in years',
    'sex': 'Sex (1 = male; 0 = female)',
    'cp': 'Chest pain type (1-4)',
    'trestbps': 'Resting blood pressure (mm Hg)',
    'chol': 'Serum cholesterol (mg/dl)',
    'fbs': 'Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)',
    'restecg': 'Resting electrocardiographic results',
    'thalach': 'Maximum heart rate achieved',
    'exang': 'Exercise induced angina (1 = yes; 0 = no)',
    'oldpeak': 'ST depression induced by exercise',
    'slope': 'Slope of peak exercise ST segment',
    'ca': 'Number of major vessels (0-3) colored by fluoroscopy',
    'thal': 'Thalassemia (3 = normal; 6 = fixed defect; 7 = reversible defect)'
}

for feature, description in feature_descriptions.items():
    print(f"  {feature}: {description}")

print("\n📊 COMPARING HEALTHY vs HEART DISEASE PATIENTS:")
healthy = df[df['heart_disease'] == 0]
disease = df[df['heart_disease'] == 1]

print(f"\n🧍 HEALTHY PATIENTS (n={len(healthy)}):")
print(f"  Average Age: {healthy['age'].mean():.1f} years")
print(f"  Average Cholesterol: {healthy['chol'].mean():.1f} mg/dl")
print(f"  Average Max Heart Rate: {healthy['thalach'].mean():.1f}")

print(f"\n❤️ HEART DISEASE PATIENTS (n={len(disease)}):")
print(f"  Average Age: {disease['age'].mean():.1f} years")
print(f"  Average Cholesterol: {disease['chol'].mean():.1f} mg/dl")
print(f"  Average Max Heart Rate: {disease['thalach'].mean():.1f}")
# data_exploration.py - ADD THIS FINAL SECTION

print("\n🧹 DATA CLEANING PROCESS:")
print(f"Initial dataset size: {df.shape}")

# Your chosen approach - Option B: Fill missing values with median
df_clean = df.fillna(df.median())

print(f"After cleaning: {df_clean.shape}")
print("✅ Missing values handled using median imputation!")

# Verify no missing values remain
print(f"Remaining missing values: {df_clean.isnull().sum().sum()}")

print("\n💾 SAVING CLEANED DATASET:")
df_clean.to_csv('heart_disease_cleaned.csv', index=False)
print("✅ Saved as 'heart_disease_cleaned.csv'")

print("\n🎯 FINAL DATASET READY FOR ML:")
print(f"Total patients: {len(df_clean)}")
print(f"Features available: {len(df_clean.columns) - 2}")  # excluding target and heart_disease
print(f"Heart disease prevalence: {df_clean['heart_disease'].mean()*100:.1f}%")