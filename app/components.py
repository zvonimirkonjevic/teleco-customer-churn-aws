"""
Telco Customer Churn Prediction — UI Components

Reusable Streamlit UI building blocks: styles, forms, results display, sidebar.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
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
"""


def inject_styles() -> None:
    """Inject custom CSS into the Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def render_header() -> None:
    """Render the page header and subtitle."""
    st.markdown(
        '<p class="main-header">Telco Customer Churn Predictor</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">Enter customer information to predict churn probability</p>',
        unsafe_allow_html=True,
    )
    st.divider()


# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------

def render_form() -> dict | None:
    """
    Render the customer data input form.

    Returns:
        A dict of customer features if the form was submitted, else ``None``.
    """
    with st.form("prediction_form"):
        st.subheader("Customer Demographics")

        col1, col2 = st.columns(2)

        with col1:
            gender = st.selectbox(
                "Gender",
                options=["Male", "Female"],
                help="Customer's gender",
            )
            senior_citizen = st.selectbox(
                "Senior Citizen",
                options=["No", "Yes"],
                help="Whether the customer is a senior citizen (65+)",
            )
            partner = st.selectbox(
                "Partner",
                options=["Yes", "No"],
                help="Whether the customer has a partner",
            )

        with col2:
            dependents = st.selectbox(
                "Dependents",
                options=["No", "Yes"],
                help="Whether the customer has dependents",
            )
            tenure = st.number_input(
                "Tenure (months)",
                min_value=0,
                max_value=100,
                value=12,
                help="Number of months the customer has been with the company",
            )

        st.divider()
        st.subheader("Account Information")

        col3, col4 = st.columns(2)

        with col3:
            monthly_charges = st.number_input(
                "Monthly Charges ($)",
                min_value=0.0,
                max_value=200.0,
                value=50.0,
                step=0.01,
                help="Monthly charge amount in dollars",
            )
            total_charges = st.number_input(
                "Total Charges ($)",
                min_value=0.0,
                max_value=10000.0,
                value=600.0,
                step=0.01,
                help="Total charges accumulated by the customer",
            )

        with col4:
            contract = st.selectbox(
                "Contract Type",
                options=["Month-to-month", "One year", "Two year"],
                help="Type of contract the customer has",
            )
            payment_method = st.selectbox(
                "Payment Method",
                options=[
                    "Electronic check",
                    "Mailed check",
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                ],
                help="Customer's payment method",
            )
            paperless_billing = st.selectbox(
                "Paperless Billing", options=["Yes", "No"]
            )

        st.divider()
        st.subheader("Services")

        col5, col6 = st.columns(2)

        with col5:
            phone_service = st.selectbox("Phone Service", options=["Yes", "No"])
            multiple_lines = st.selectbox(
                "Multiple Lines",
                options=["Yes", "No", "No phone service"],
                help="Whether the customer has multiple phone lines",
            )
            internet_service = st.selectbox(
                "Internet Service",
                options=["DSL", "Fiber optic", "No"],
                help="Type of internet service",
            )
            online_security = st.selectbox(
                "Online Security", options=["Yes", "No", "No internet service"]
            )
            online_backup = st.selectbox(
                "Online Backup", options=["Yes", "No", "No internet service"]
            )

        with col6:
            device_protection = st.selectbox(
                "Device Protection", options=["Yes", "No", "No internet service"]
            )
            tech_support = st.selectbox(
                "Tech Support", options=["Yes", "No", "No internet service"]
            )
            streaming_tv = st.selectbox(
                "Streaming TV", options=["Yes", "No", "No internet service"]
            )
            streaming_movies = st.selectbox(
                "Streaming Movies", options=["Yes", "No", "No internet service"]
            )

        st.divider()

        submitted = st.form_submit_button(
            "Predict Churn",
            use_container_width=True,
            type="primary",
        )

    if not submitted:
        return None

    return {
        "gender": gender,
        "seniorCitizen": senior_citizen,
        "partner": partner,
        "dependents": dependents,
        "tenure": tenure,
        "monthlyCharges": monthly_charges,
        "totalCharges": total_charges,
        "contract": contract,
        "internetService": internet_service,
        "paymentMethod": payment_method,
        "phoneService": phone_service,
        "multipleLines": multiple_lines,
        "onlineSecurity": online_security,
        "onlineBackup": online_backup,
        "deviceProtection": device_protection,
        "techSupport": tech_support,
        "streamingTV": streaming_tv,
        "streamingMovies": streaming_movies,
        "paperlessBilling": paperless_billing,
    }


# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------

def render_results(result: dict) -> None:
    """Display prediction results and actionable recommendations."""
    st.success("Prediction Complete!")
    st.subheader("Prediction Results")

    col1, col2 = st.columns(2)

    with col1:
        churn_probability = result.get("churn_probability", 0) * 100
        st.metric(label="Churn Probability", value=f"{churn_probability:.1f}%")

    with col2:
        will_churn = result.get("will_churn", False)
        risk_level = "High Risk" if will_churn else "Low Risk"
        st.metric(label="Risk Level", value=risk_level)

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


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    """Render the sidebar with model info and instructions."""
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
