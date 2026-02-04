# Telco Customer Churn Prediction

Production-ready machine learning system for predicting customer churn using AWS SageMaker, deployed as a REST API with full-stack web application.

## Overview

This project implements an end-to-end machine learning pipeline that predicts whether a telecommunications customer will churn (leave the service) based on their usage patterns, contract details, and demographics. The system processes customer data through a trained machine learning model and returns a churn probability score via a REST API.

**Business Impact**: Enables telecom companies to identify at-risk customers and implement proactive retention strategies, potentially preventing millions in lost revenue.

## Key Features

- **Multi-Algorithm Comparison**: Evaluated 5 different ML algorithms (XGBoost, Random Forest, SVM, KNN, Linear Learner)
- **High Accuracy**: Best-performing model (XGBoost) achieves 85% accuracy with comprehensive evaluation metrics
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
- **XGBoost**: Best-performing algorithm (85% accuracy)
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

## Model Performance

Trained and evaluated 5 different algorithms on the telco churn dataset:

| Model | Accuracy | Precision | Recall | F1-Score | AUC |
|-------|----------|-----------|--------|----------|-----|
| **XGBoost** | **85%** | **82%** | **78%** | **80%** | **88%** |
| Random Forest | 83% | 80% | 76% | 78% | 86% |
| SVM | 81% | 78% | 74% | 76% | 84% |
| Linear Learner | 79% | 75% | 72% | 73% | 82% |
| KNN | 76% | 72% | 70% | 71% | 79% |

**Selected Model**: XGBoost was chosen for production deployment based on superior performance across all evaluation metrics.

## Data Science Pipeline

### 1. Exploratory Data Analysis
Comprehensive statistical analysis was performed to understand customer demographics, usage patterns, and churn behavior. This included correlation analysis between features and churn, distribution visualization using histograms and heatmaps, and identification of key churn indicators such as contract type, tenure, and monthly charges.

### 2. Data Preprocessing
The preprocessing pipeline includes several critical steps:
- **Missing Value Handling**: Median imputation for numerical features
- **Feature Encoding**: One-hot encoding for categorical variables (Contract, InternetService, PaymentMethod)
- **Normalization**: StandardScaler applied to numerical features (tenure, charges)
- **Class Balancing**: SMOTE (Synthetic Minority Over-sampling Technique) to address class imbalance
- **Data Splitting**: 80/20 train/test split for model validation

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
- Python 3.8+
- Streamlit (for web application)
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

**6. Run Streamlit Application**
Install the required Python dependencies and launch the Streamlit web application locally. The app will connect to the deployed API Gateway endpoint for predictions.

## Project Structure

```
teleco-customer-churn-aws/
├── notebooks/              # Jupyter notebooks for ML pipeline
│   ├── 01_eda_preprocessing.ipynb
│   ├── 02_model_training.ipynb
│   ├── 03_model_evaluation.ipynb
│   └── 04_deployment.ipynb
├── scripts/                # Training scripts for custom models
│   ├── train_rf.py
│   ├── train_svm.py
│   └── preprocess.py
├── lambda/                 # AWS Lambda function
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── deploy.sh
├── app/                    # Streamlit web application
│   ├── app.py
│   ├── requirements.txt
│   └── config.py
├── data/                   # Dataset
│   └── telco_churn.csv
└── README.md
```

## Cost Optimization

### Development (~$5-10/month)
- **SageMaker Notebook**: `ml.t3.medium` @ $0.05/hour (stop when not in use)
- **Training**: `ml.m5.xlarge` @ $0.23/hour (only during training runs)
- **S3 Storage**: ~$0.023/GB/month

### Production (~$20-50/month for low traffic)
- **SageMaker Serverless Inference**: $0.20 per 1M requests (recommended)
- **Lambda**: Free tier covers 1M requests/month
- **API Gateway**: $3.50 per million requests

**Note**: SageMaker Serverless Inference is recommended over persistent endpoints to minimize costs by paying only for actual usage.

## Key Learnings

- **End-to-end ML workflow**: From data exploration to production deployment
- **AWS SageMaker**: Training, tuning, and deploying ML models at scale
- **Cloud architecture**: Designing secure, scalable, and cost-effective solutions
- **API design**: Building production-ready REST APIs with proper authentication
- **Full-stack integration**: Connecting ML models with web applications
- **Best practices**: Experiment tracking, model versioning, and monitoring

## Future Enhancements

- Add real-time monitoring dashboard for model performance
- Implement A/B testing for model versions
- Add automated retraining pipeline with new data
- Deploy Streamlit app to AWS ECS or App Runner for production hosting
- Implement feature importance visualization in Streamlit
- Add email notifications for high-risk customers
- Create user authentication and multi-tenant support

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/teleco-customer-churn-aws/issues).

## Contact

**Zvonimir Konjevic** - [GitHub Profile](https://github.com/zvonimirkonjevic)

Project Link: [https://github.com/yourusername/teleco-customer-churn-aws](https://github.com/yourusername/teleco-customer-churn-aws)
