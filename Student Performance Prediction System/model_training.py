import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv('student_performance_dataset_final.csv')

print("Dataset Info:")
print(f"Total samples: {len(df)}")
print("\nGPA Category Distribution:")
print(df['final_gpa_category'].value_counts())

# Check if we have enough samples in each category
category_counts = df['final_gpa_category'].value_counts()
print("\n" + "="*50)

# Check for classes with too few samples
insufficient_classes = category_counts[category_counts < 2].index.tolist()
if insufficient_classes:
    print(
        f"Warning: Classes with insufficient samples: {insufficient_classes}")
    print("Removing these classes for training...")
    df = df[~df['final_gpa_category'].isin(insufficient_classes)]

# Prepare features and target
X = df.drop('final_gpa_category', axis=1)
y = df['final_gpa_category']

print(f"\nAfter cleaning:")
print(f"Total samples: {len(df)}")
print("Class distribution:")
print(y.value_counts())

# Encode target variable
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print(f"\nClasses after encoding: {le.classes_}")

# Check if we still have enough classes
if len(np.unique(y_encoded)) < 2:
    print("Error: Need at least 2 classes for classification")
    exit()

# Try stratified split, but if it fails, use regular split
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print("Successfully used stratified split")
except ValueError as e:
    print(f"Stratified split failed: {e}")
    print("Using regular train-test split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=10,
    min_samples_split=5,
    class_weight='balanced'  # Handle class imbalance
)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# Save model and preprocessing objects
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(le, 'encoder.pkl')

print("\nModel saved successfully!")
print(f"Feature names: {list(X.columns)}")

# Also save the cleaned class names
class_names = le.classes_.tolist()
print(f"Class names: {class_names}")

# Save feature names for later use
feature_names = list(X.columns)
joblib.dump(feature_names, 'feature_names.pkl')
joblib.dump(class_names, 'class_names.pkl')

# ... (existing code) ...

# Define GPA ranges for each category based on typical grading scales
gpa_ranges = {
    'Poor': {'range': '0.0 - 2.0', 'description': 'Below average performance', 'color': '#e74c3c'},
    'Average': {'range': '2.0 - 3.0', 'description': 'Satisfactory performance', 'color': '#f39c12'},
    'Good': {'range': '3.0 - 3.7', 'description': 'Above average performance', 'color': '#27ae60'},
    'Excellent': {'range': '3.7 - 4.0', 'description': 'Outstanding performance', 'color': '#2980b9'}
}

# Save GPA ranges
joblib.dump(gpa_ranges, 'gpa_ranges.pkl')

print("\nGPA Ranges by Category:")
for category, info in gpa_ranges.items():
    if category in le.classes_:
        print(f"  {category}: GPA {info['range']} - {info['description']}")

print("\nAll files saved successfully!")
