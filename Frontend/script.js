// store_user_input.js
// Script to capture and send user form input to the backend and log it

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing script');
    
    // Set up form submission handler
    const form = document.getElementById('prediction-form');
    if (form) {
        console.log('Found prediction form - adding submit handler');
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            // Capture user data
            const userData = captureUserData();
            console.log("Captured User Input:", userData);
            
            // Clear previous results
            const resultsContainer = document.getElementById('results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '';
                
                // Create and add model info section
                const modelInfoSection = createModelInfoSection();
                resultsContainer.appendChild(modelInfoSection);
                
                // Create and add prediction result section (initially hidden)
                const predictionResultSection = createPredictionResultSection();
                resultsContainer.appendChild(predictionResultSection);
                
                // Scroll to the results
                resultsContainer.scrollIntoView({ behavior: 'smooth' });
            }
            
            // Send data to backend
            sendUserDataToBackend(userData);
        });
    } else {
        console.error('Prediction form not found!');
    }
});

// Function to create the model info section
function createModelInfoSection() {
    console.log("Creating model info section");
    const modelInfoSection = document.createElement('div');
    modelInfoSection.id = 'model-info';
    modelInfoSection.className = 'card border-0 shadow-sm mt-4';

    modelInfoSection.innerHTML = `
        <div class="card-header bg-white p-4 border-0">
            <h4 class="mb-0">
                <i class="fas fa-chart-bar me-2 text-primary"></i>Model Performance
            </h4>
            <hr class="mt-2 mb-0">
        </div>
        <div class="card-body p-4 pt-0">
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Loading model information...</p>
            </div>
        </div>
    `;

    console.log("Model info section created");
    return modelInfoSection;
}

// Function to create the prediction result section
function createPredictionResultSection() {
    const predictionResultSection = document.createElement('div');
    predictionResultSection.id = 'prediction-result';
    predictionResultSection.className = 'card border-0 shadow-sm mt-4 d-none';

    predictionResultSection.innerHTML = `
        <div class="card-header bg-white p-4 border-0">
            <h4 class="mb-0">
                <i class="fas fa-chart-pie me-2 text-primary"></i>Prediction Results
            </h4>
            <hr class="mt-2 mb-0">
        </div>
        <div class="card-body p-4 pt-0">
            <div class="alert p-4 mt-0" id="prediction-alert">
                <!-- Will be populated by JavaScript -->
            </div>
        </div>
    `;

    return predictionResultSection;
}

// Function to capture user data from the form
function captureUserData() {
    return {
        Age: parseInt(document.getElementById('Age').value),
        Education: document.getElementById('Education').value,
        MaritalStatus: document.getElementById('MaritalStatus').value,
        HasDependents: document.getElementById('HasDependents').value,
        Income: parseInt(document.getElementById('Income').value),
        CreditScore: parseInt(document.getElementById('CreditScore').value),
        DTIRatio: parseFloat(document.getElementById('DTIRatio').value),
        NumCreditLines: parseInt(document.getElementById('NumCreditLines').value),
        HasMortgage: document.getElementById('HasMortgage').value,
        HasCoSigner: document.getElementById('HasCoSigner').value,
        EmploymentType: document.getElementById('EmploymentType').value,
        LoanPurpose: document.getElementById('LoanPurpose').value
    };
}

// Function to send user data to the backend (Flask)
function sendUserDataToBackend(userData) {
    console.log("Sending data to backend:", userData);

    // Show API endpoint in console for debugging
    console.log("API endpoint: http://localhost:5000/save_user_data");

    fetch('http://localhost:5000/save_user_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        console.log("Response status:", response.status);
        console.log("Response headers:", [...response.headers.entries()]);

        // Even if response is not OK, try to parse it as JSON first
        return response.json().then(data => {
            if (!response.ok) {
                // If server returned an error message, use it
                if (data && data.error) {
                    throw new Error(data.error);
                }
                // Otherwise use the status text
                throw new Error(`Server responded with status ${response.status}: ${response.statusText}`);
            }
            return data;
        }).catch(err => {
            // If JSON parsing fails, fall back to the original error
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}: ${response.statusText}`);
            }
            throw err;
        });
    })
    .then(data => {
        console.log("✅ Prediction result received:", data);
        console.log("Loan eligibility:", data.loan_eligibility);
        console.log("Will default?", data.loan_eligibility);

        // Update both sections with the received data
        updateModelInfoSection(data);
        updatePredictionResultSection(data);
    })
    .catch(error => {
        console.error("❌ Error sending user data:", error.message);
        console.error("Error details:", error);

        // Try to check if the server is running at all
        checkServerStatus().then(isRunning => {
            let errorMsg = error.message;
            if (!isRunning) {
                errorMsg = "Cannot connect to the server. Please make sure the application is running.";
            } else if (error.message.includes("404")) {
                errorMsg = "The API endpoint '/save_user_data' was not found. Please check server configuration.";
            }

            // Show error in the prediction result section
            showError(errorMsg);
        });
    });
}

// Function to check if the server is running
function checkServerStatus() {
    console.log("Checking server status...");
    return fetch('http://localhost:5000/api/status', { method: 'GET' })
        .then(response => {
            console.log("Server status response:", response.status);
            return response.ok;
        })
        .catch(error => {
            console.error("Server status check failed:", error);
            return false;
        });
}

// Function to update the model info section with data
function updateModelInfoSection(data) {
    const modelInfoSection = document.getElementById('model-info');
    if (!modelInfoSection) {
        console.error("Model info section not found");
        return;
    }

    console.log("Updating model info with data:", data);
    const performanceSummary = data.performance_summary || {};
    console.log("Performance summary:", performanceSummary);

    // Create HTML for the model metrics table
    let tableRows = '';
    for (const [modelName, metrics] of Object.entries(performanceSummary)) {
        console.log(`Processing model ${modelName} with metrics:`, metrics);
        
        // Highlight the best model
        const rowClass = modelName === data.best_model ? 'table-success' : '';

        // Add CV accuracy if available
        let cvAccuracy = '<td>N/A</td>';
        if (metrics.cv_accuracy !== undefined && metrics.cv_accuracy !== null) {
            console.log(`CV accuracy for ${modelName}:`, metrics.cv_accuracy);
            cvAccuracy = `<td>${(metrics.cv_accuracy * 100).toFixed(2)}%</td>`;
        }

        tableRows += `
            <tr class="${rowClass}">
                <td>${modelName}</td>
                <td>${(metrics.accuracy * 100).toFixed(2)}%</td>
                <td>${(metrics.precision * 100).toFixed(2)}%</td>
                <td>${(metrics.recall * 100).toFixed(2)}%</td>
                <td>${(metrics.f1_score * 100).toFixed(2)}%</td>
                ${cvAccuracy}
            </tr>
        `;
    }

    // Create HTML for confusion matrices
    let confusionMatricesHTML = '';
    for (const [modelName, metrics] of Object.entries(performanceSummary)) {
        console.log(`Checking confusion matrix for ${modelName}:`, metrics.confusion_matrix);
        if (metrics.confusion_matrix) {
            const matrix = metrics.confusion_matrix;
            confusionMatricesHTML += `
                <div class="col-md-6 col-lg-3 mb-3">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <h6 class="mb-0">${modelName} - Confusion Matrix</h6>
                        </div>
                        <div class="card-body">
                            <table class="table table-sm table-bordered text-center">
                                <thead>
                                    <tr>
                                        <th colspan="2" class="text-center">Predicted</th>
                                    </tr>
                                    <tr>
                                        <th></th>
                                        <th>Not Default (0)</th>
                                        <th>Default (1)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <th>Actual No Default (0)</th>
                                        <td class="table-success">${matrix[0][0]}</td>
                                        <td class="table-danger">${matrix[0][1]}</td>
                                    </tr>
                                    <tr>
                                        <th>Actual Default (1)</th>
                                        <td class="table-danger">${matrix[1][0]}</td>
                                        <td class="table-success">${matrix[1][1]}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } else {
            console.warn(`No confusion matrix found for ${modelName}`);
        }
    }

    // Update the model info content
    const modelInfoContent = `
        <div class="row">
            <div class="col-12">
                <h5 class="mb-3">Model Performance Metrics</h5>
                <div class="table-responsive">
                    <table class="table table-bordered table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Model</th>
                                <th>Accuracy</th>
                                <th>Precision</th>
                                <th>Recall</th>
                                <th>F1 Score</th>
                                <th>CV Accuracy</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                        </tbody>
                    </table>
                </div>
                <p class="mt-3"><strong>Best Model:</strong> ${data.best_model || 'Unknown'}</p>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <h5 class="mb-3">Confusion Matrices</h5>
            </div>
            ${confusionMatricesHTML}
        </div>
    `;
    
    console.log("Setting model info content");
    modelInfoSection.querySelector('.card-body').innerHTML = modelInfoContent;
    console.log("Model info content set");
}

// Function to update the prediction result section with data
function updatePredictionResultSection(data) {
    const resultDiv = document.getElementById('prediction-result');
    if (!resultDiv) return;

    // Determine styles based on default prediction
    // "No" means no default risk (good), "Yes" means default risk (bad)
    const willDefault = data.loan_eligibility === "Yes"; 
    
    const alertClass = willDefault ? "alert-danger" : "alert-success";
    const resultIcon = willDefault ? "fa-times-circle" : "fa-check-circle";
    const resultText = willDefault ?
        "Warning: This loan is predicted to default." :
        "Good news! This loan is predicted not to default.";
    const resultColor = willDefault ? "#dc3545" : "#28a745"; // Red or green

    // Update the alert
    const predictionAlert = document.getElementById('prediction-alert');
    if (predictionAlert) {
        predictionAlert.className = `alert p-4 mt-0 ${alertClass}`;
        predictionAlert.innerHTML = `
            <h4 class="alert-heading"><i class="fas ${resultIcon} me-2"></i>${resultText}</h4>
            <div class="result-highlight my-3 p-3 text-center" style="background-color: rgba(255,255,255,0.8); border-radius: 8px; border: 2px solid ${resultColor};">
                <h2 style="color: ${resultColor}; font-size: 2rem; font-weight: 700; margin: 0;">
                    <i class="fas ${resultIcon} me-2"></i>
                    Will this loan default? ${data.loan_eligibility}
                </h2>
            </div>
            <p class="mt-3 mb-0"><strong>Best Model:</strong> ${data.best_model}</p>
        `;
    }

    // Show the result card
    resultDiv.classList.remove('d-none');
}

// Function to show error in the prediction result section
function showError(errorMessage) {
    console.error("Showing error:", errorMessage);
    
    // Find the prediction result section
    const resultDiv = document.getElementById('prediction-result');
    if (resultDiv) {
        // Show the result card
        resultDiv.classList.remove('d-none');
        
        // Update the alert
        const predictionAlert = document.getElementById('prediction-alert');
        if (predictionAlert) {
            predictionAlert.className = 'alert alert-danger p-4 mt-0';
            predictionAlert.innerHTML = `
                <h4 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Error</h4>
                <p>Failed to get prediction: ${errorMessage}</p>
                <p>Please try again or contact support if the problem persists.</p>
                <div class="mt-3">
                    <h5>Troubleshooting Steps:</h5>
                    <ol>
                        <li>Make sure the Flask server is running at http://localhost:5000</li>
                        <li>Check that the API endpoint '/save_user_data' exists in app.py</li>
                        <li>Look at the browser console (F12) for more detailed error information</li>
                    </ol>
                </div>
            `;
        }
    }
    
    // Also update the model info section to show the error
    const modelInfoSection = document.getElementById('model-info');
    if (modelInfoSection) {
        const modelInfoBody = modelInfoSection.querySelector('.card-body');
        if (modelInfoBody) {
            modelInfoBody.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Could not load model information due to an error.
                </div>
            `;
        }
    }
}

