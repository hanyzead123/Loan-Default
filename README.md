# Loan-Default-Prediction-System
💰 Loan Default Prediction System

## 📌 Overview
This project is a **classification task** aimed at predicting whether a borrower is likely to **default on a loan** using **financial and demographic data**.  
It follows a complete machine learning workflow including **data preprocessing**, **feature engineering**, and **training classification models** for better lending decisions and reduced financial risk.

The dataset used is a **Loan Default Dataset** (can be your own CSV or publicly available datasets).

---

## 🎯 Problem Definition
Predict whether a borrower will **default on a loan** based on financial and demographic features.

**Evaluation Metrics:**
- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC Score

---

## 📊 Dataset Information
- **Source:** Local CSV / Financial Dataset  
- **Number of Records:** Variable (255348)  
- **Number of Features:** Variable (18)  
- **Target Variable:** `Default` (binary: 0 = No, 1 = Yes)  
- **Format:** CSV


## 🛠 Data Preprocessing

### 1️⃣ Data Cleaning
- Standardized inconsistent categorical values  
  - `Marital_Status`: Married, married → Married
  - `Education_Level`: Graduate, grad → Graduate

### 2️⃣ Missing Values Handling
- Numerical columns: Imputed using **mean**  
- Categorical columns: Imputed using **mode**

### 3️⃣ Handling Outliers
- Used **IQR method** to detect and clip extreme values in features like `Income` and `Loan_Amount`

### 4️⃣ Encoding & Scaling
- **Label Encoding / One-Hot Encoding** for categorical features  
- **StandardScaler** applied to numerical features

---


## 🧠 Model Architecture

| Model | Purpose |
|-------|--------|
| Logistic Regression | Baseline model |
| Random Forest Classifier | Handles non-linearities and interactions |
| XGBoost Classifier | Gradient boosting for improved performance |

- **Hyperparameter Tuning:** Grid Search / Random Search  
- **Evaluation:** Used cross-validation on training data

## 📌 Observations & Conclusion
- Model performance improved after feature engineering and tuning  
- Tree-based models (Random Forest, XGBoost) outperform Logistic Regression  
- ROC-AUC = 0.92 shows strong ability to distinguish between defaulters and non-defaulters  
- Can assist lenders in **risk assessment and decision-making**


## 👩‍💻 Team Members
- [Hoda Mahmoud](https://github.com/HodaMahmoud-2005)
- [Menna Hossny](https://github.com/Mennatullah122)
- [Hany Ziad](https://github.com/hanyzead123)


---

## 📚 References
- Kaggle: Loan Default Prediction Datasets  
- Scikit-learn Documentation: [https://scikit-learn.org](https://scikit-learn.org)  
- XGBoost Documentation: [https://xgboost.readthedocs.io](https://xgboost.readthedocs.io)
