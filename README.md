# 💳 Loan Prediction System

A sophisticated web-based application that leverages **Machine Learning** to predict the likelihood of **loan default** based on an applicant's financial and personal information.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-Gradient%20Boosting-green.svg)
![License](https://img.shields.io/badge/License-Educational-lightgrey.svg)

---

# 📋 Overview

The **Loan Prediction System** is a full-stack web application that combines multiple machine learning models to estimate whether a loan applicant is likely to default.

The application provides:

- 🌐 Responsive web interface
- 🤖 Multiple Machine Learning models
- 📊 Real-time loan risk prediction
- 📈 Model comparison and evaluation
- 🔒 Secure server-side data processing

---

# ✨ Features

- ✅ Modern and responsive user interface
- ✅ Multiple ML algorithms
- ✅ Ensemble prediction model
- ✅ Real-time prediction with confidence score
- ✅ Detailed model performance metrics
- ✅ Financial and personal information analysis
- ✅ Secure backend processing

---

# 🛠️ Technology Stack

## Backend

- Flask
- Scikit-learn
- XGBoost
- Joblib
- Pandas
- NumPy

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Font Awesome
- Google Fonts

---

# 📁 Project Structure

```text
Loan-Prediction-System/
│
├── Frontend/
│   ├── home.html
│   ├── predict.html
│   ├── about.html
│   ├── styles.css
│   └── script.js
│
├── app.py
├── model.py
├── ML.ipynb
├── Loan_default.csv
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Loan-Prediction-System.git

cd Loan-Prediction-System
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Train the Machine Learning Models

```bash
python model.py
```

This will:

- Preprocess the dataset
- Train all ML models
- Save trained models as `.pkl` files

---

## 5. Run the Flask Application

```bash
python app.py
```

---

## 6. Open the Website

```
http://localhost:5000/home.html
```

Available pages:

- `/home.html`
- `/predict.html`
- `/about.html`

---

# 📊 How It Works

## Data Preprocessing

The system performs:

- Categorical value mapping
- One-Hot Encoding
- Feature Scaling
- SMOTE for class balancing

---

## Machine Learning Models

- Logistic Regression
- Random Forest
- XGBoost
- Ensemble Model

---

## Prediction Pipeline

1. User enters loan information.
2. Data is preprocessed.
3. All models generate predictions.
4. Ensemble prediction is calculated.
5. Results are displayed with:

- Loan default prediction
- Default probability
- Model comparison
- Performance metrics

---

# 🔗 API Endpoint

## POST `/save_user_data`

### Request

```json
{
  "Age": 35,
  "Education": "Bachelor's",
  "MaritalStatus": "Married",
  "HasDependents": "Yes",
  "Income": 75000,
  "CreditScore": 680,
  "DTIRatio": 0.35,
  "NumCreditLines": 5,
  "HasMortgage": "No",
  "HasCoSigner": "No",
  "EmploymentType": "Full-time",
  "LoanPurpose": "Home"
}
```

### Response

```json
{
  "loan_eligibility": "No",
  "best_model": "Random Forest",
  "default_probability": 0.2345,
  "performance_summary": {}
}
```

---

# 🎯 Understanding the Results

| Output | Meaning |
|---------|---------|
| **Loan Eligibility = No** | Low default risk |
| **Loan Eligibility = Yes** | High default risk |
| **Default Probability** | Probability (0–1) of loan default |

---

# 📈 Model Performance

| Model | Accuracy | Precision | Recall | F1 Score |
|--------|---------:|----------:|-------:|---------:|
| Logistic Regression | 85.2% | 72.1% | 68.3% | 70.2% |
| Random Forest | **88.3%** | **75.6%** | **72.4%** | **74.0%** |
| XGBoost | 87.9% | 74.8% | 71.9% | 73.3% |
| Ensemble | 88.1% | 75.2% | 72.1% | 73.6% |

---

# 🔧 Customization

### Add a New Model

1. Edit `model.py`
2. Train the new model
3. Save it as `.pkl`
4. Update `app.py`

---

### Modify the Website

- HTML → Content
- CSS → Styling
- JavaScript → Frontend Logic

---

# 🧪 Testing

## Run Test Cases

Example:

```python
test_case = {
    "Age": 56,
    "Education": "Bachelor's",
    "Income": 85994,
    "CreditScore": 520
}
```

## Manual Testing

1. Open `/predict.html`
2. Enter applicant information
3. Submit the form
4. View prediction results

---

# 🐛 Troubleshooting

## Port 5000 Already in Use

### Windows

```bash
netstat -ano | findstr :5000
```

### Linux / macOS

```bash
lsof -i :5000
```

---

## Missing Dependencies

```bash
pip install -r requirements.txt
```

---

## Missing Model Files

```bash
python model.py
```

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to GitHub

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 👥 Team

| Member | GitHub |
|---------|--------|
| **Hany Ziad** | https://github.com/hanyzead123 |
| **Mennatullah Mohamed** | https://github.com/Mennatullah122 |
| **Hoda Mahmoud** | https://github.com/HodaMahmoud-2005 |

---

# 📄 License

This project was developed for **educational purposes** as part of coursework at **Alamein International University**.
