# data_visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for better looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

print("📊 CREATING DATA VISUALIZATIONS...")

# Load our cleaned dataset
df = pd.read_csv('heart_disease_cleaned.csv')

# 1. AGE DISTRIBUTION COMPARISON
plt.figure(figsize=(15, 10))

plt.subplot(2, 3, 1)
sns.histplot(data=df, x='age', hue='heart_disease', bins=20, alpha=0.6)
plt.title('Age Distribution: Healthy vs Heart Disease')
plt.xlabel('Age (years)')
plt.ylabel('Number of Patients')

# 2. CHOLESTEROL COMPARISON
plt.subplot(2, 3, 2)
sns.boxplot(data=df, x='heart_disease', y='chol')
plt.title('Cholesterol Levels Comparison')
plt.xlabel('Heart Disease (0=No, 1=Yes)')
plt.ylabel('Cholesterol (mg/dl)')

# 3. MAX HEART RATE COMPARISON
plt.subplot(2, 3, 3)
sns.violinplot(data=df, x='heart_disease', y='thalach')
plt.title('Maximum Heart Rate Comparison')
plt.xlabel('Heart Disease (0=No, 1=Yes)')
plt.ylabel('Max Heart Rate')

# 4. GENDER DISTRIBUTION
plt.subplot(2, 3, 4)
gender_heart = pd.crosstab(df['sex'], df['heart_disease'])
gender_heart.plot(kind='bar', alpha=0.7)
plt.title('Heart Disease by Gender')
plt.xlabel('Sex (0=Female, 1=Male)')
plt.ylabel('Number of Patients')
plt.legend(['No Disease', 'Heart Disease'])

# 5. CHEST PAIN TYPE ANALYSIS
plt.subplot(2, 3, 5)
cp_heart = pd.crosstab(df['cp'], df['heart_disease'])
cp_heart.plot(kind='bar', alpha=0.7)
plt.title('Heart Disease by Chest Pain Type')
plt.xlabel('Chest Pain Type (1-4)')
plt.ylabel('Number of Patients')
plt.legend(['No Disease', 'Heart Disease'])

# 6. CORRELATION HEATMAP
plt.subplot(2, 3, 6)
# Select only numerical features for correlation
numerical_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca', 'thal', 'heart_disease']
correlation_matrix = df[numerical_features].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Feature Correlation Heatmap')

plt.tight_layout()
plt.savefig('heart_disease_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Visualizations saved as 'heart_disease_analysis.png'")

# KEY INSIGHTS SUMMARY
print("\n🔍 KEY INSIGHTS FROM VISUALIZATIONS:")
print("=" * 50)

# Age insight
young_disease = df[(df['age'] < 45) & (df['heart_disease'] == 1)]
print(f"• Young patients (<45) with heart disease: {len(young_disease)}")

# Gender insight
male_rate = df[df['sex'] == 1]['heart_disease'].mean() * 100
female_rate = df[df['sex'] == 0]['heart_disease'].mean() * 100
print(f"• Heart disease rate - Males: {male_rate:.1f}%, Females: {female_rate:.1f}%")

# Chest pain insight
cp4_rate = df[df['cp'] == 4]['heart_disease'].mean() * 100
print(f"• Patients with chest pain type 4 have {cp4_rate:.1f}% disease rate")

# Strongest correlation
strongest_corr = correlation_matrix['heart_disease'].abs().sort_values(ascending=False)[1:3]
print(f"• Strongest predictors: {list(strongest_corr.index)}")