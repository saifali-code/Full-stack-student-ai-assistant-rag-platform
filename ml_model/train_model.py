import pandas as pd             
import numpy as np
from sklearn.tree import DecisionTreeClassifier  # Our ML algorithm
from sklearn.model_selection import train_test_split  # For splitting data
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import pickle  # For saving the trained model
import os

print("=" * 50)
print("TRAINING SMART STUDY ASSISTANT ML MODEL")
print("=" * 50)

# ============================================================
# STEP 1: LOAD DATA
# ============================================================
print("\n📊 Step 1: Loading data...")

# Read the CSV file into a DataFrame (like an Excel table in Python)
df = pd.read_csv('sample_data.csv')

print(f"Data loaded! Shape: {df.shape}")
# .shape gives (rows, columns) — e.g., (25, 4)

print("\nFirst 5 rows:")
print(df.head())  # Show first 5 rows

print("\nData statistics:")
print(df.describe())  # Min, max, mean, etc. for each column

print(f"\nPass/Fail distribution:")
print(df['passed'].value_counts())
# 0: 10 (failed)
# 1: 15 (passed)

# ============================================================
# STEP 2: PREPARE FEATURES AND TARGET
# ============================================================
print("\n📊 Step 2: Preparing features...")

# X = input features (what we know about the student)
# y = target variable (what we want to predict)
X = df[['study_hours', 'quiz_score', 'practice_count']]
y = df['passed']

print(f"Features (X) shape: {X.shape}")  # (25, 3)
print(f"Target (y) shape: {y.shape}")    # (25,)

# ============================================================
# STEP 3: SPLIT DATA
# ============================================================
print("\n📊 Step 3: Splitting into train/test sets...")

# We split data into:
# - Training set (80%): used to TEACH the model
# - Test set (20%): used to EVALUATE the model (data it's never seen)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,      # 20% for testing
    random_state=42     # Fixed seed for reproducibility
)

print(f"Training samples: {len(X_train)}")  # ~20
print(f"Testing samples: {len(X_test)}")   # ~5

# ============================================================
# STEP 4: SCALE FEATURES (optional but good practice)
# ============================================================
# StandardScaler makes all features on the same scale
# Without it: quiz_score (0-100) would dominate study_hours (0-10)
print("\n📊 Step 4: Scaling features...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
# fit_transform: learn the mean/std from train data and apply transformation
X_test_scaled = scaler.transform(X_test)
# transform: apply SAME transformation to test data (don't re-learn!)

# ============================================================
# STEP 5: TRAIN THE MODEL
# ============================================================
print("\n🧠 Step 5: Training Decision Tree model...")

model = DecisionTreeClassifier(
    max_depth=4,        # Maximum depth of the tree (prevents overfitting)
    random_state=42     # For reproducibility
)

# .fit() is where the actual learning happens
# The model analyzes patterns in the training data
model.fit(X_train_scaled, y_train)

print("✅ Model trained!")

# ============================================================
# STEP 6: EVALUATE THE MODEL
# ============================================================
print("\n📊 Step 6: Evaluating model performance...")

# Make predictions on the test set
y_pred = model.predict(X_test_scaled)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n🎯 Accuracy: {accuracy * 100:.1f}%")
print("(Percentage of test samples predicted correctly)")

print("\nDetailed Report:")
print(classification_report(y_test, y_pred, target_names=['FAIL', 'PASS']))

# Feature importance: which feature matters most?
print("\n📊 Feature Importance:")
feature_names = ['study_hours', 'quiz_score', 'practice_count']
for feature, importance in zip(feature_names, model.feature_importances_):
    print(f"  {feature}: {importance:.3f} ({importance*100:.1f}%)")

# ============================================================
# STEP 7: SAVE THE MODEL
# ============================================================
print("\n💾 Step 7: Saving model...")

# Save both the model AND the scaler
# We need the same scaler when making predictions later!
model_data = {
    'model': model,
    'scaler': scaler,
    'feature_names': feature_names,
    'accuracy': accuracy
}

with open('model.pkl', 'wb') as f:
    pickle.dump(model_data, f)
    # pickle.dump() converts Python object to bytes and saves to file

print("✅ Model saved as 'model.pkl'")

# ============================================================
# STEP 8: TEST A PREDICTION
# ============================================================
print("\n🔮 Step 8: Testing a prediction...")

# Test case: student who studies 3 hours, has 70% quiz score, took 8 quizzes
test_student = np.array([[3.0, 70, 8]])
test_student_scaled = scaler.transform(test_student)

prediction = model.predict(test_student_scaled)[0]
probability = model.predict_proba(test_student_scaled)[0]
# predict_proba returns [P(fail), P(pass)] — probabilities for each class

print(f"Test student: study_hours=3.0, quiz_score=70, practice_count=8")
print(f"Prediction: {'PASS ✅' if prediction == 1 else 'FAIL ❌'}")
print(f"Confidence: {max(probability) * 100:.1f}%")

print("\n" + "=" * 50)
print("TRAINING COMPLETE!")
print("=" * 50)