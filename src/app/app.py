"""
Telco Customer Churn Prediction - Streamlit Application

This application provides an interactive web interface for predicting customer churn
using a machine learning model deployed on AWS SageMaker.
"""

import streamlit as st
import requests
import json
from typing import Dict, Any

# Configuration
#API_ENDPOINT = st.secrets.get("API_ENDPOINT", "https://your-api-gateway-url.amazonaws.com/prod/predict")

# Page configuration
st.set_page_config(
    page_title="Telco Customer Churn Predictor",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .risk-high {
        color: #dc2626;
        font-weight: 600;
    }
    .risk-low {
        color: #16a34a;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def make_prediction(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send prediction request to the API endpoint.
    
    Args:
        payload: Customer data for prediction
        
    Returns:
        Prediction results from the API
    """
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


# Header
st.markdown('<p class="main-header">Telco Customer Churn Predictor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enter customer information to predict churn probability</p>', unsafe_allow_html=True)

# Divider
st.divider()

# Input form
with st.form("prediction_form"):
    st.subheader("Customer Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tenure = st.number_input(
            "Tenure (months)",
            min_value=0,
            max_value=100,
            value=12,
            help="Number of months the customer has been with the company"
        )
        
        monthly_charges = st.number_input(
            "Monthly Charges ($)",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=0.01,
            help="Monthly charge amount in dollars"
        )
        
        total_charges = st.number_input(
            "Total Charges ($)",
            min_value=0.0,
            max_value=10000.0,
            value=600.0,
            step=0.01,
            help="Total charges accumulated by the customer"
        )
    
    with col2:
        contract = st.selectbox(
            "Contract Type",
            options=["Month-to-month", "One year", "Two year"],
            help="Type of contract the customer has"
        )
        
        internet_service = st.selectbox(
            "Internet Service",
            options=["DSL", "Fiber optic", "No"],
            help="Type of internet service"
        )
        
        payment_method = st.selectbox(
            "Payment Method",
            options=[
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)"
            ],
            help="Customer's payment method"
        )
    
    st.divider()
    
    # Additional features
    st.subheader("Additional Services")
    
    col3, col4 = st.columns(2)
    
    with col3:
        phone_service = st.selectbox("Phone Service", options=["Yes", "No"])
        online_security = st.selectbox("Online Security", options=["Yes", "No", "No internet service"])
        online_backup = st.selectbox("Online Backup", options=["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", options=["Yes", "No", "No internet service"])
    
    with col4:
        tech_support = st.selectbox("Tech Support", options=["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", options=["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", options=["Yes", "No", "No internet service"])
        paperless_billing = st.selectbox("Paperless Billing", options=["Yes", "No"])
    
    st.divider()
    
    # Submit button
    submitted = st.form_submit_button(
        "Predict Churn",
        use_container_width=True,
        type="primary"
    )

# Handle form submission
if submitted:
    # Prepare payload
    payload = {
        "tenure": tenure,
        "monthlyCharges": monthly_charges,
        "totalCharges": total_charges,
        "contract": contract,
        "internetService": internet_service,
        "paymentMethod": payment_method,
        "phoneService": phone_service,
        "onlineSecurity": online_security,
        "onlineBackup": online_backup,
        "deviceProtection": device_protection,
        "techSupport": tech_support,
        "streamingTV": streaming_tv,
        "streamingMovies": streaming_movies,
        "paperlessBilling": paperless_billing
    }
    
    with st.spinner("Analyzing customer data..."):
        try:
            # Make prediction
            result = make_prediction(payload)
            
            # Display results
            st.success("Prediction Complete!")
            
            st.subheader("Prediction Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                churn_probability = result.get("churn_probability", 0) * 100
                st.metric(
                    label="Churn Probability",
                    value=f"{churn_probability:.1f}%"
                )
            
            with col2:
                will_churn = result.get("will_churn", False)
                risk_level = "High Risk" if will_churn else "Low Risk"
                st.metric(
                    label="Risk Level",
                    value=risk_level
                )
            
            # Recommendation
            st.divider()
            st.subheader("Recommendation")
            
            if will_churn:
                st.warning(
                    """
                    **Customer is at high risk of churning.**
                    
                    Suggested actions:
                    - Offer loyalty discounts or promotions
                    - Review contract terms for potential upgrades
                    - Proactive customer service outreach
                    - Consider bundle deals to increase value
                    """
                )
            else:
                st.info(
                    """
                    **Customer is at low risk of churning.**
                    
                    Suggested actions:
                    - Continue monitoring customer engagement
                    - Consider upselling opportunities
                    - Maintain service quality
                    """
                )
                
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            st.info("Please check your API endpoint configuration and try again.")


# Sidebar with information
with st.sidebar:
    st.header("About")
    st.write(
        """
        This application predicts customer churn probability using a 
        machine learning model deployed on AWS SageMaker.
        
        **Model Information:**
        - Algorithm: XGBoost
        - Accuracy: 85%
        - AUC: 0.88
        """
    )
    
    st.divider()
    
    st.header("Instructions")
    st.write(
        """
        1. Enter customer information in the form
        2. Click "Predict Churn" button
        3. View prediction results and recommendations
        """
    )
