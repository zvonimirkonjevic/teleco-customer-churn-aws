# Telco Customer Churn Prediction

Production-ready machine learning system for predicting customer churn using AWS SageMaker, deployed as a REST API with full-stack web application.

## Overview

This project implements an end-to-end machine learning pipeline that predicts whether a telecommunications customer will churn (leave the service) based on their usage patterns, contract details, and demographics. The system processes customer data through a trained machine learning model and returns a churn probability score via a REST API.

**Business Impact**: Enables telecom companies to identify at-risk customers and implement proactive retention strategies, potentially preventing millions in lost revenue.

## Key Features

- **Multi-Algorithm Comparison**: Evaluated 5 different ML algorithms (XGBoost, Random Forest, SVM, KNN, Linear Learner)
- **High Accuracy**: Best-performing model (XGBoost) achieves 0.84 AUC-ROC with comprehensive evaluation metrics
- **Cloud-Native Architecture**: Fully deployed on AWS with serverless infrastructure
- **Production-Ready API**: Secure REST endpoint with IAM authentication via Lambda proxy pattern
- **Cost-Optimized**: Serverless inference for pay-per-use pricing model
- **Interactive Web Application**: Streamlit-based interface for real-time predictions


```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  SageMaker   │
│ Application │      │  (REST API)  │      │  Function   │      │   Endpoint   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                                         │
                                                                         │
                                                                         ▼
                                                                  ┌─────────────┐
                                                                  │     S3      │
                                                                  │   Bucket    │
                                                                  └─────────────┘
```

**How it works**: User submits customer data → API Gateway receives request → Lambda authenticates and forwards to SageMaker → ML model predicts churn probability → Result returned to user.

## Tech Stack

### Machine Learning & Data Science
- **AWS SageMaker**: Model training and deployment
- **Python 3.8+**: Core programming language
- **Pandas & NumPy**: Data manipulation and analysis
- **Scikit-Learn**: Preprocessing and model evaluation
- **XGBoost**: Best-performing algorithm (0.84 AUC-ROC, 0.63 F1-Score)
- **Matplotlib & Seaborn**: Data visualization
- **SMOTE**: Handling class imbalance

### Cloud Infrastructure (AWS)
- **S3**: Data storage and model artifacts
- **SageMaker Notebooks**: Development environment (Jupyter)
- **SageMaker Endpoints**: Model serving (serverless inference)
- **Lambda**: API authentication and request handling
- **API Gateway**: Public REST API
- **IAM**: Security and access control

### Application Layer
- **Streamlit**: Interactive web application framework
- **Boto3**: AWS SDK for Python (SageMaker integration)
- **Pandas**: Data handling and preprocessing
- **AWS SDK**: Cloud service integration

### Development Tools
- **uv**: Fast Python package installer and resolver (replaces pip/pip-tools)
- **pyproject.toml**: Modern Python project configuration
- **Docker**: Containerization for consistent deployment

## Model Performance

Trained and evaluated 5 different algorithms on the telco churn dataset (ranked by F1-Score):

| Rank | Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC | MCC |
|------|-------|----------|-----------|--------|----------|---------|-----|
| 1 | **XGBoost** | **0.7686** | **0.5480** | **0.7326** | **0.6270** | **0.8402** | **0.4746** |
| 2 | Random Forest | 0.7700 | 0.5510 | 0.7219 | 0.6250 | 0.8383 | 0.4723 |
| 3 | SVM | 0.7516 | 0.5227 | 0.7380 | 0.6120 | 0.8311 | 0.4511 |
| 4 | KNN | 0.7452 | 0.5143 | 0.7193 | 0.5998 | N/A | 0.4331 |
| 5 | Linear Learner | 0.7949 | 0.6300 | 0.5508 | 0.5877 | 0.8294 | 0.4538 |

**Selected Model**: XGBoost was chosen for production deployment based on the best F1-Score (0.6270) and AUC-ROC (0.8402), balancing precision and recall for churn detection.

> **Note**: SVM achieved the highest Recall (0.7380). Consider it if maximizing churn detection (minimizing missed churners) is the priority. Linear Learner had the highest raw Accuracy (0.7949) and Precision (0.6300) but at the cost of lower Recall.

## Data Science Pipeline

### 1. Exploratory Data Analysis (`01_eda_preprocessing.ipynb`)
Comprehensive statistical analysis to understand customer behavior and identify churn patterns:

**Key Insights:**
- **Churn Rate**: 26.5% of customers churned
- **High-Risk Factors**: 
  - Month-to-month contracts: ~42% churn rate
  - Fiber optic internet: ~42% churn rate
  - Electronic check payment: ~45% churn rate
  - No online security/tech support: Higher churn
  - Short tenure (<12 months): Higher risk

**Analysis Performed:**
- Target variable distribution and class imbalance assessment
- Demographic analysis (gender, senior citizen, partner, dependents)
- Service usage patterns (internet service, contract type, additional services)
- Financial analysis (monthly charges, total charges, payment methods)
- Correlation analysis and feature relationships
- Customer segmentation visualization

**Visualizations Created:**
- Churn distribution charts (bar and pie charts)
- Demographic breakdowns with stacked bar charts
- Tenure distribution and box plots
- Service usage heatmaps
- Financial analysis histograms
- Correlation matrix
- Customer segmentation scatter plots

### 2. Data Preprocessing (`02_data_preprocessing.ipynb`)
Comprehensive data preparation pipeline for model training:

**Data Cleaning:**
- Converted `TotalCharges` to numeric (11 missing values found)
- Imputed missing values with `MonthlyCharges` for new customers
- Removed `customerID` (not predictive)

**Feature Engineering:**
- `AvgMonthlySpend`: TotalCharges / (tenure + 1)
- `TenureGroup`: Binned tenure into 4 groups (0-1yr, 1-2yr, 2-4yr, 4-6yr)
- `TotalServices`: Count of subscribed services (0-6)

**Encoding:**
- **Binary encoding**: gender, Partner, Dependents, PhoneService, PaperlessBilling, Churn
- **One-Hot encoding**: MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaymentMethod, TenureGroup
- **Result**: 46 features after encoding

**Scaling:**
- StandardScaler applied to: tenure, MonthlyCharges, TotalCharges, AvgMonthlySpend, TotalServices
- All features normalized to mean=0, std=1

**Class Imbalance Handling:**
- **Original distribution**: 5,174 No (73.5%), 1,869 Yes (26.5%)
- **Train/Test split**: 80/20 stratified split
- **SMOTE applied**: Training set balanced to 4,139 samples per class
- **Final datasets**:
  - Training (with SMOTE): 8,278 samples
  - Training (original): 5,634 samples
  - Test: 1,409 samples

**Output Files:**
- `data/processed/train_smote.csv`: Balanced training data
- `data/processed/train_original.csv`: Original training data
- `data/processed/test.csv`: Test data
- `data/processed/scaler.pkl`: Fitted StandardScaler
- `data/processed/feature_names.pkl`: Feature column names

### 3. Model Training & Evaluation
Five different algorithms were trained and compared:
- **SageMaker Built-in Algorithms**: XGBoost, Linear Learner, K-Nearest Neighbors
- **Scikit-Learn Script Mode**: Random Forest, Support Vector Machine

Each model underwent hyperparameter tuning using grid search, 5-fold cross-validation for robust evaluation, and comprehensive metric tracking through SageMaker Experiments for reproducibility.

## Deployment Architecture

### Challenge Solved
SageMaker endpoints require AWS IAM authentication (SigV4 signing), which is complex for client applications to implement directly.

### Solution
The **Lambda Proxy Pattern** was implemented to solve this challenge. A Lambda function acts as an intermediary that:
- Receives JSON requests from API Gateway
- Handles IAM authentication automatically
- Forwards requests to the SageMaker endpoint
- Processes the prediction response
- Returns formatted results to the client

This Lambda function is exposed via Amazon API Gateway as a public REST API endpoint, making it accessible to any client application without requiring complex AWS authentication logic.

### API Endpoint Structure
The REST API accepts POST requests with customer data (tenure, monthly charges, contract type, internet service, payment method) and returns a JSON response containing the churn probability and a binary prediction (will_churn: true/false).

## Web Application

### Streamlit Interface

The application uses Streamlit to provide an interactive web interface for making churn predictions. The interface features a clean, user-friendly design that allows users to input customer information and receive instant predictions.

**User Interface Components:**
- **Input Form**: Two-column layout with input fields for customer data including tenure, monthly charges, total charges, contract type, internet service, and payment method
- **Prediction Display**: Visual metrics showing churn probability percentage and risk level (High Risk/Low Risk)
- **Real-time Processing**: Instant API calls to the Lambda/API Gateway endpoint
- **Error Handling**: User-friendly error messages for failed requests

**Workflow:**
1. User enters customer information through the form
2. Application sends POST request to API Gateway endpoint
3. Lambda function processes request and calls SageMaker
4. Prediction results are displayed with visual metrics
5. Users can make multiple predictions in the same session

### Key Features
- **Interactive UI**: User-friendly form with input validation
- **Real-time Predictions**: Instant results via API Gateway
- **Visual Metrics**: Clear display of churn probability and risk level
- **Error Handling**: Graceful error messages for failed requests

## Getting Started

### Prerequisites
- AWS Account with SageMaker, Lambda, and API Gateway access
- Python 3.12+ (required by project configuration)
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker (optional, for containerized deployment)
- AWS CLI configured

### Quick Start

**1. Clone the Repository**
Download the project repository from GitHub to your local machine.

**2. Set Up AWS Resources**
Create an S3 bucket for data storage and upload the telco churn dataset to the bucket. This bucket will store training data and model artifacts.

**3. Launch SageMaker Notebook**
Navigate to the AWS SageMaker Console and create a Notebook Instance using the ml.t3.medium instance type for cost-effective development. Upload the provided Jupyter notebooks to the instance.

**4. Run Notebooks in Order**
Execute the notebooks sequentially:
- Data exploration and preprocessing
- Model training with multiple algorithms
- Model evaluation and comparison
- Deployment to SageMaker endpoint

**5. Deploy Lambda & API Gateway**
Deploy the Lambda function that handles authentication and request forwarding. Configure API Gateway to create a public REST endpoint.

**6. Configure and Run Streamlit Application**

Set up the API endpoint configuration:
```bash
cd app
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your API Gateway endpoint URL
```

**Option A: Run with Docker (Recommended)**
```bash
cd environment
docker-compose up -d
```
Access the application at `http://localhost:8501`

**Option B: Run Locally with uv**

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management. uv automatically manages dependencies and virtual environments.

```bash
# Install dependencies and create virtual environment
uv sync

# Run the Streamlit application
uv run streamlit run app.py
```

Access the application at `http://localhost:8501`

> **Why uv?** uv is 10-100x faster than pip, provides deterministic dependency resolution, and seamlessly manages virtual environments. It reads from `pyproject.toml` to ensure consistent development and production environments.

## Project Structure

```
teleco-customer-churn-aws/
│
├── lambda/                                 # AWS Lambda function
│   └── predict/                            #   SageMaker inference proxy (handler.py)
│
├── app/                                    # Streamlit web application (deployed on EC2)
│   ├── app.py                              #   Entry point — wires components together
│   ├── config.py                           #   Settings, constants, secrets access
│   ├── api_client.py                       #   API Gateway communication layer
│   ├── components.py                       #   Reusable UI components (form, results, sidebar)
│   ├── .streamlit/                         #   Streamlit config & secrets
│   └── environment/                        #   Docker & compose for local development
│
├── infra/                                  # Infrastructure as Code
│   └── terraform/
│       ├── main.tf                         #   Core resource definitions (all AWS resources)
│       ├── variables.tf                    #   Input variables (region, tags, etc.)
│       ├── outputs.tf                      #   Output values (API URL, instance ID, etc.)
│       ├── providers.tf                    #   AWS provider & version constraints
│       └── terraform.tfvars                #   Variable values for this deployment
│
├── buildspec/                              # AWS CodeBuild buildspec files
│   ├── buildspec_app.yml                   #   Build & deploy Streamlit to EC2
│   ├── buildspec_lambda.yml                #   Package & deploy Lambda function
│   └── buildspec_infra.yml                 #   Terraform plan & apply
│
├── data/                                   # Datasets
│   ├── teleco-customer-churn.csv           #   Original dataset
│   ├── teleco-customer-churn-cleaned.csv   #   Cleaned dataset from EDA
│   └── processed/                          #   Preprocessed data for modeling
│       ├── train_smote.csv
│       ├── train_original.csv
│       └── test.csv
│
├── notebooks/                              # Jupyter notebooks (preprocessing, training, eval)
│   ├── 01_eda_preprocessing.ipynb
│   ├── 02_data_preprocessing.ipynb
│   └── 03_model_training_and_evaluation.ipynb
│
├── scripts/                                # SageMaker training scripts (used by notebooks)
│   ├── rf_train.py
│   └── svm_train.py
│
├── tests/                                  # Test suites
│   ├── unit/                               #   Fast isolated tests (no AWS calls)
│   └── integration/                        #   Tests with real/mocked AWS services
│
├── docs/                                   # Architecture docs, runbooks, API spec
│
├── pyproject.toml                          # Python project config & dependencies
└── README.md
```

## Key Learnings

- **End-to-end ML workflow**: From data exploration to production deployment
- **AWS SageMaker**: Training, tuning, and deploying ML models at scale
- **Cloud architecture**: Designing secure, scalable, and cost-effective solutions
- **API design**: Building production-ready REST APIs with proper authentication
- **Full-stack integration**: Connecting ML models with web applications
- **Best practices**: Experiment tracking, model versioning, and monitoring