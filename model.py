import pandas as pd
import pickle
pd.set_option("display.max_columns",75)
import warnings
warnings.filterwarnings('ignore')
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, recall_score, precision_score, roc_auc_score
import joblib
import numpy as np

# Load and prepare data
df = pd.read_csv('Loan_default.csv')
df = df.drop(["LoanID"], axis=1, errors='ignore')
df["HasMortgage"] = df["HasMortgage"].map({'Yes': 1, 'No': 0})
df["HasDependents"] = df["HasDependents"].map({'Yes': 1, 'No': 0})
df["HasCoSigner"] = df["HasCoSigner"].map({'Yes': 1, 'No': 0})
df["Education"] = df["Education"].str.strip()
edu_map = {
    'High School': 0,
    "Bachelor's": 1,
    "Master's": 2,
    'PhD': 3
}
df["Education"] = df["Education"].map(edu_map)
df["EmploymentType"] = df["EmploymentType"].str.strip()
df["MaritalStatus"] = df["MaritalStatus"].str.strip()
df["LoanPurpose"] = df["LoanPurpose"].str.strip()
df = pd.get_dummies(df, columns=['EmploymentType', 'MaritalStatus', 'LoanPurpose'], dtype=int)

# Split features and target
inputs = df.drop('Default', axis='columns')
target = df.Default

# Save feature names for prediction
feature_names = list(inputs.columns)
pickle.dump(feature_names, open("feature_names.pkl", "wb"))

# Split data into train and test sets
X_train, X_test, Y_train, Y_test = train_test_split(inputs, target, test_size=0.3, random_state=22)

# Apply SMOTE for class imbalance
smote = SMOTE(random_state=42)
X_train_resampled, Y_train_resampled = smote.fit_resample(X_train, Y_train)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, "scaler.pkl")

# Dictionary to store model results
results = {}

# 1. Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_scaled, Y_train_resampled)
y_pred_lr = lr.predict(X_test_scaled)
scores_lr = cross_val_score(lr, X_train_scaled, Y_train_resampled, cv=5)
conf_matrix_lr = confusion_matrix(Y_test, y_pred_lr)
results['Logistic Regression'] = {
    'accuracy': accuracy_score(Y_test, y_pred_lr),
    'precision': precision_score(Y_test, y_pred_lr),
    'recall': recall_score(Y_test, y_pred_lr),
    'f1_score': f1_score(Y_test, y_pred_lr),
    'cv_accuracy': scores_lr.mean(),
    'confusion_matrix': conf_matrix_lr.tolist()
}

joblib.dump(lr, "logistic_regression.pkl")

# Print confusion matrix and CV score
print("\nLogistic Regression - Confusion Matrix:")
print(conf_matrix_lr)
print("Logistic Regression - Mean CV Accuracy:", scores_lr.mean())

# 2. Random Forest Classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, Y_train_resampled)
y_pred_rf = rf.predict(X_test_scaled)
scores_rf = cross_val_score(rf, X_train_scaled, Y_train_resampled, cv=5)
conf_matrix_rf = confusion_matrix(Y_test, y_pred_rf)
results['Random Forest'] = {
    'accuracy': accuracy_score(Y_test, y_pred_rf),
    'precision': precision_score(Y_test, y_pred_rf),
    'recall': recall_score(Y_test, y_pred_rf),
    'f1_score': f1_score(Y_test, y_pred_rf),
    'cv_accuracy': scores_rf.mean(),
    'confusion_matrix': conf_matrix_rf.tolist()
}
joblib.dump(rf, "random_forest.pkl")

# Print confusion matrix and CV score
print("\nRandom Forest - Confusion Matrix:")
print(conf_matrix_rf)
print("Random Forest - Mean CV Accuracy:", scores_rf.mean())

# 3. XGBoost Classifier
xgb = XGBClassifier(random_state=42)
xgb.fit(X_train_scaled, Y_train_resampled)
y_pred_xgb = xgb.predict(X_test_scaled)
scores_xgb = cross_val_score(xgb, X_train_scaled, Y_train_resampled, cv=5)
conf_matrix_xgb = confusion_matrix(Y_test, y_pred_xgb)
results['XGBoost'] = {
    'accuracy': accuracy_score(Y_test, y_pred_xgb),
    'precision': precision_score(Y_test, y_pred_xgb),
    'recall': recall_score(Y_test, y_pred_xgb),
    'f1_score': f1_score(Y_test, y_pred_xgb),
    'cv_accuracy': scores_xgb.mean(),
    'confusion_matrix': conf_matrix_xgb.tolist()
}
joblib.dump(xgb, "xgboost.pkl")

# Print confusion matrix and CV score
print("\nXGBoost - Confusion Matrix:")
print(conf_matrix_xgb)
print("XGBoost - Mean CV Accuracy:", scores_xgb.mean())

# 4. Create a simple ensemble (voting classifier)
ensemble_probs = np.zeros((len(Y_test), 2))

lr_probs = lr.predict_proba(X_test_scaled)
rf_probs = rf.predict_proba(X_test_scaled)
xgb_probs = xgb.predict_proba(X_test_scaled)

ensemble_probs = (lr_probs + rf_probs + xgb_probs) / 3
ensemble_preds = np.argmax(ensemble_probs, axis=1)

class EnsembleModel:
    def __init__(self, models):
        self.models = models

    def predict(self, X):
        probs = np.zeros((X.shape[0], 2))
        for model in self.models:
            probs += model.predict_proba(X)
        probs /= len(self.models)
        return np.argmax(probs, axis=1)

    def predict_proba(self, X):
        probs = np.zeros((X.shape[0], 2))
        for model in self.models:
            probs += model.predict_proba(X)
        probs /= len(self.models)
        return probs

ensemble = EnsembleModel([lr, rf, xgb])
joblib.dump(ensemble, "ensemble.pkl")

# Calculate ensemble metrics
conf_matrix_ensemble = confusion_matrix(Y_test, ensemble_preds)
# For ensemble, we'll use the average of the CV scores from the individual models
scores_ensemble = (scores_lr + scores_rf + scores_xgb) / 3
results['Ensemble'] = {
    'accuracy': accuracy_score(Y_test, ensemble_preds),
    'precision': precision_score(Y_test, ensemble_preds),
    'recall': recall_score(Y_test, ensemble_preds),
    'f1_score': f1_score(Y_test, ensemble_preds),
    'cv_accuracy': scores_ensemble.mean(),
    'confusion_matrix': conf_matrix_ensemble.tolist()
}

# Print confusion matrix and CV score
print("\nEnsemble - Confusion Matrix:")
print(conf_matrix_ensemble)
print("Ensemble - Mean CV Accuracy:", scores_ensemble.mean())

# Save results
joblib.dump(results, "model_results.pkl")

# Find best model based on accuracy
best_model_name = max(results, key=lambda x: results[x]['accuracy'])
best_model = None

if best_model_name == 'Logistic Regression':
    best_model = lr
elif best_model_name == 'Random Forest':
    best_model = rf
elif best_model_name == 'XGBoost':
    best_model = xgb
elif best_model_name == 'Ensemble':
    best_model = ensemble

# Save best model
joblib.dump(best_model, "model.pkl")

# Print model performance
print("Model Performance Summary:\n")
for name, metrics in results.items():
    print(f"{name}:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}\n")

print(f"✅ Best Model: {best_model_name}\n")

print("\nLoan Default Risk Interpretation:")
print("--------------------------------")
print("Prediction = 0 / Default Risk: No (Customer is not likely to default)")
print("Prediction = 1 / Default Risk: Yes (Customer is likely to default)")
print("\nNote: In our dataset, 0 means the customer did not default (good credit risk),")
print("      so they have low default risk. 1 means they defaulted (bad credit risk),")
print("      so they have high default risk.")

# Test cases for prediction
print("\n----- TEST CASES -----")

# Test case 1: Higher income, higher credit score but high DTI and many credit lines
test_case_1 = {
    'Age': 56,
    'Education': "Bachelor's",
    'MaritalStatus': 'Divorced',
    'HasDependents': 'Yes',
    'Income': 85994,
    'CreditScore': 520,
    'DTIRatio': 0.44,
    'NumCreditLines': 520,
    'HasMortgage': 'Yes',
    'HasCoSigner': 'No',
    'EmploymentType': 'Full-time',
    'LoanPurpose': 'Auto'
}

# Test case 2: Similar income, lower credit score, unemployed
test_case_2 = {
    'Age': 46,
    'Education': "Master's",
    'MaritalStatus': 'Divorced',
    'HasDependents': 'Yes',
    'Income': 84208,
    'CreditScore': 451,
    'DTIRatio': 0.31,
    'NumCreditLines': 3,
    'HasMortgage': 'Yes',
    'HasCoSigner': 'No',
    'EmploymentType': 'Unemployed',
    'LoanPurpose': 'Auto'
}

# Function to preprocess and predict
def predict_loan_default(user_data):
    # Create DataFrame from user data
    df_test = pd.DataFrame([user_data])

    # Apply same preprocessing as training data
    df_test["HasMortgage"] = df_test["HasMortgage"].map({'Yes': 1, 'No': 0})
    df_test["HasDependents"] = df_test["HasDependents"].map({'Yes': 1, 'No': 0})
    df_test["HasCoSigner"] = df_test["HasCoSigner"].map({'Yes': 1, 'No': 0})

    edu_map = {
        'High School': 0,
        "Bachelor's": 1,
        "Master's": 2,
        'PhD': 3
    }
    df_test["Education"] = df_test["Education"].map(edu_map)

    # One-hot encoding
    df_test = pd.get_dummies(df_test, columns=['EmploymentType', 'MaritalStatus', 'LoanPurpose'], dtype=int)

    # Ensure all required features exist
    missing_cols = [col for col in feature_names if col not in df_test.columns]
    for col in missing_cols:
        df_test[col] = 0

    # Select only the features used in training
    df_test = df_test[feature_names]

    # Scale features
    X_test_scaled = scaler.transform(df_test)

    # Get predictions from all models
    results = {}
    for name, model in [('Logistic Regression', lr), ('Random Forest', rf), ('XGBoost', xgb), ('Ensemble', ensemble)]:
        pred = model.predict(X_test_scaled)[0]
        proba = model.predict_proba(X_test_scaled)[0]
        results[name] = {
            'prediction': int(pred),
            'default_probability': float(proba[1])
        }

    # Use Logistic Regression model for prediction instead of best model
    lr_pred = lr.predict(X_test_scaled)[0]
    lr_proba = lr.predict_proba(X_test_scaled)[0]

    return {
        'best_model_prediction': int(lr_pred),  # Using Logistic Regression instead of best_model
        'default_probability': float(lr_proba[1]),
        'model_predictions': results
    }

# Run test cases
print("\nTest Case 1 Results:")
print(f"Input: {test_case_1}")
test_result_1 = predict_loan_default(test_case_1)
default_risk_1 = "Yes" if test_result_1['best_model_prediction'] == 1 else "No"
print(f"Best model prediction: {test_result_1['best_model_prediction']} (Default Risk: {default_risk_1})")
print(f"Default probability: {test_result_1['default_probability']:.4f}")
print("Individual model predictions:")
for model, result in test_result_1['model_predictions'].items():
    model_risk = "Yes" if result['prediction'] == 1 else "No"
    print(f"  {model}: {result['prediction']} (Default Risk: {model_risk}, Probability: {result['default_probability']:.4f})")

print("\nTest Case 2 Results:")
print(f"Input: {test_case_2}")
test_result_2 = predict_loan_default(test_case_2)
default_risk_2 = "Yes" if test_result_2['best_model_prediction'] == 1 else "No"
print(f"Best model prediction: {test_result_2['best_model_prediction']} (Default Risk: {default_risk_2})")
print(f"Default probability: {test_result_2['default_probability']:.4f}")
print("Individual model predictions:")
for model, result in test_result_2['model_predictions'].items():
    model_risk = "Yes" if result['prediction'] == 1 else "No"
    print(f"  {model}: {result['prediction']} (Default Risk: {model_risk}, Probability: {result['default_probability']:.4f})")
