from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pickle
import pandas as pd
from werkzeug.exceptions import HTTPException
import traceback
import os
import numpy as np

# Define the EnsembleModel class needed for loading the ensemble model
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

app = Flask(__name__, static_folder='Frontend', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

print(f"Flask app initialized with static_folder='{app.static_folder}' and static_url_path='{app.static_url_path}'")

# Load saved artifacts
try:
    feature_names = pickle.load(open("feature_names.pkl", "rb"))
    scaler = joblib.load("scaler.pkl")
    results = joblib.load("model_results.pkl")
    best_model = joblib.load("model.pkl")

    model_files = {
        'Logistic Regression': 'logistic_regression.pkl',
        'Random Forest': 'random_forest.pkl',
        'XGBoost': 'xgboost.pkl',
        'Ensemble': 'ensemble.pkl'
    }

    models = {name: joblib.load(path) for name, path in model_files.items()}
except Exception as e:
    print(f"Error loading model files: {str(e)}")
    # Initialize empty dictionaries/lists to prevent errors
    feature_names = []
    models = {}
    results = {}
    best_model = None
    scaler = None

@app.before_request
def log_request_info():
    if not hasattr(app, '_printed_routes'):
        print("\n----- REGISTERED ROUTES -----")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            print(f"{rule} ({methods})")
        print("-----------------------------\n")
        app._printed_routes = True

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    response.data = jsonify({
        "error": f"{e.name}: {e.description}",
        "status_code": e.code
    }).get_data()
    response.content_type = "application/json"
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled exception: {str(e)}")
    traceback.print_exc()
    return jsonify({
        "error": f"Server error: {str(e)}",
        "status_code": 500
    }), 500

@app.route('/save_user_data', methods=['POST'])
def save_user_data():
    try:
        print("\n----- REQUEST RECEIVED at /save_user_data -----")
        print(f"Time: {pd.Timestamp.now()}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request content type: {request.content_type}")

        if not request.data:
            print("WARNING: Request has no data")
            return jsonify({"error": "No data provided"}), 400

        try:
            user_data = request.get_json()
            if user_data:
                print(f"Successfully parsed JSON data: {user_data}")
            else:
                print("WARNING: Parsed JSON is None or empty")
                return jsonify({"error": "No data provided"}), 400
        except Exception as json_error:
            print(f"ERROR parsing JSON: {str(json_error)}")
            return jsonify({"error": f"Invalid JSON data: {str(json_error)}"}), 400

        # Print the test case for debugging
        print(f"Test case received: {user_data}")
        
        df = pd.DataFrame([user_data])
        print(f"Created DataFrame with shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")

        # Preprocessing
        print("Starting data preprocessing...")

        required_columns = [
            "HasMortgage", "HasDependents", "HasCoSigner",
            "Education", "EmploymentType", "MaritalStatus", "LoanPurpose"
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"ERROR: Missing required columns: {missing_columns}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing_columns)}"}), 400

        # Define mappings
        binary_map = {'Yes': 1, 'No': 0}
        edu_map = {
            'High School': 0,
            "Bachelor's": 1,
            "Master's": 2,
            'PhD': 3
        }

        # Helper to apply mapping safely
        def apply_mapping(column, mapping, field_name):
            df[column] = df[column].str.strip().map(mapping)
            if df[column].isnull().any():
                bad_values = df[column][df[column].isnull()].tolist()
                print(f"ERROR: Invalid value(s) for {field_name}: {bad_values}")
                raise ValueError(f"Invalid value for {field_name}. Expected: {list(mapping.keys())}")

        try:
            apply_mapping("HasMortgage", binary_map, "HasMortgage")
            apply_mapping("HasDependents", binary_map, "HasDependents")
            apply_mapping("HasCoSigner", binary_map, "HasCoSigner")
            apply_mapping("Education", edu_map, "Education")
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

        # Clean whitespace before encoding
        for col in ['EmploymentType', 'MaritalStatus', 'LoanPurpose']:
            df[col] = df[col].str.strip()

        # One-hot encoding
        print("One-hot encoding categorical variables...")
        categorical_columns = ['EmploymentType', 'MaritalStatus', 'LoanPurpose']
        expected_values = {
            'EmploymentType': ['Full-time', 'Part-time', 'Self-employed', 'Unemployed'],
            'MaritalStatus': ['Single', 'Married', 'Divorced'],
            'LoanPurpose': ['Auto', 'Business', 'Education', 'Home', 'Other']
        }
        for col in categorical_columns:
            if df[col].iloc[0] not in expected_values[col]:
                print(f"ERROR: Invalid value for {col}: {df[col].iloc[0]}")
                return jsonify({"error": f"Invalid value for {col}: {df[col].iloc[0]}. Expected: {expected_values[col]}"}), 400

        df = pd.get_dummies(df, columns=categorical_columns, dtype=int)
        print(f"After one-hot encoding, DataFrame columns: {df.columns.tolist()}")

        # Ensure all required features exist
        missing_cols = [col for col in feature_names if col not in df.columns]
        if missing_cols:
            print(f"Adding {len(missing_cols)} missing columns: {missing_cols}")
            for col in missing_cols:
                df[col] = 0

        df = df[feature_names]
        print(f"Final DataFrame shape: {df.shape}")
        print(f"Final DataFrame columns: {df.columns.tolist()}")
        print(f"Final DataFrame values: {df.iloc[0].to_dict()}")  # Log the processed input

        # Scaling
        print("Scaling input data...")
        try:
            input_scaled = scaler.transform(df)
            print(f"Scaled input shape: {input_scaled.shape}")
        except Exception as scale_error:
            print(f"ERROR during scaling: {str(scale_error)}")
            return jsonify({"error": f"Data scaling failed: {str(scale_error)}"}), 500

        # Predict
        print("Making prediction...")
        try:
            # Debug the input data
            print(f"Input data after preprocessing: {df.head()}")
            print(f"Input scaled shape: {input_scaled.shape}")
            print(f"First few values of scaled input: {input_scaled[0][:5]}")

            # Check model details
            print(f"Best model type: {type(best_model).__name__}")

            # Use all models to get predictions and probabilities
            all_predictions = {}
            all_probas = {}
            for model_name, model in models.items():
                model_pred = model.predict(input_scaled)[0]
                model_proba = model.predict_proba(input_scaled)[0]
                all_predictions[model_name] = model_pred
                all_probas[model_name] = model_proba
                print(f"{model_name} prediction: {model_pred}")
                print(f"{model_name} probabilities: {model_proba}")

            # Get prediction from best model with probabilities
            probabilities = best_model.predict_proba(input_scaled)[0]
            print(f"Best model probabilities: {probabilities}")

            # Adjust threshold for ensemble model
            threshold = 0.4 if isinstance(best_model, EnsembleModel) else 0.5
            prediction = 1 if probabilities[1] >= threshold else 0
            print(f"Applied threshold: {threshold}")

            # If probabilities are very close to threshold, log a warning
            if 0.45 <= probabilities[1] <= 0.55:
                print("WARNING: Prediction is very close to decision boundary")

            # Default risk interpretation: 0 = No risk, 1 = Yes risk
            loan_result = "No" if prediction == 0 else "Yes"
            print(f"Prediction result: {prediction} (Default Risk: {loan_result})")

            # Add probability information to response
            prediction_probability = float(probabilities[1])  # Probability of class 1 (default)
            print(f"Probability of default: {prediction_probability:.4f}")

        except Exception as pred_error:
            print(f"ERROR during prediction: {str(pred_error)}")
            traceback.print_exc()
            return jsonify({"error": f"Prediction failed: {str(pred_error)}"}), 500

        # Identify best model name based on accuracy
        best_model_name = max(results, key=lambda x: results[x]['accuracy'])
        print(f"Best model (by accuracy): {best_model_name}")

        # Performance metrics
        performance_summary = {}
        for name, metrics in results.items():
            performance_summary[name] = {
                'accuracy': round(metrics['accuracy'], 4),
                'precision': round(metrics['precision'], 4),
                'recall': round(metrics['recall'], 4),
                'f1_score': round(metrics['f1_score'], 4)
            }

            # Add CV accuracy if available
            if 'cv_accuracy' in metrics:
                performance_summary[name]['cv_accuracy'] = round(metrics['cv_accuracy'], 4)

            # Add confusion matrix if available
            if 'confusion_matrix' in metrics:
                performance_summary[name]['confusion_matrix'] = metrics['confusion_matrix']

            print(f"Model {name} metrics: {performance_summary[name]}")

        response_data = {
            'loan_eligibility': loan_result,
            'best_model': best_model_name,
            'default_probability': round(float(prediction_probability), 4),
            'performance_summary': performance_summary
        }

        print(f"Sending response: {response_data}")
        print("----- REQUEST COMPLETED -----\n")
        return jsonify(response_data)

    except Exception as e:
        print(f"ERROR in save_user_data: {str(e)}")
        traceback.print_exc()
        print("----- REQUEST FAILED -----\n")
        return jsonify({"error": f"Failed to process loan application: {str(e)}"}), 500

@app.route('/')
def serve_index():
    print(f"Serving index.html at {pd.Timestamp.now()}")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status', methods=['GET'])
def api_status():
    print(f"API status check at {pd.Timestamp.now()}")
    return jsonify({"status": "API is running"})

if __name__ == '__main__':
    app.run(debug=True)
