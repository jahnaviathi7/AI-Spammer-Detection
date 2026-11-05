
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import sqlite3
import hashlib
import secrets
import hmac

from pathlib import Path
from datetime import datetime

from modules.report_generator import generate_pdf_report
from modules.model_evaluation import show_model_evaluation
from modules.advanced_spam_detection import analyze_message
from modules.account_risk_analysis import analyze_account
from modules.real_time_spam_detection import analyze_message_realtime


# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Spammer Detection System",
    page_icon="🛡️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "spam_detection.db"
MODEL_DIR = BASE_DIR / "models"

ACCOUNT_FEATURES = [
    "account_age_days",
    "followers",
    "following",
    "posts",
    "profile_completeness",
    "Real-Time Spam Detection",
    "URL Extraction and Phishing Risk Analysis",
    "Suspicious Keyword Detection",
    "username_digit_ratio",
    "repetitive_content_ratio"
]


# =====================================================
# DATABASE
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_type TEXT,
            input_data TEXT,
            prediction TEXT,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_history(detection_type, input_data, prediction, score):
    conn = get_connection()

    conn.execute("""
        INSERT INTO history
        (detection_type, input_data, prediction, score, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        detection_type,
        str(input_data),
        str(prediction),
        float(score),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# =====================================================
# AUTHENTICATION
# =====================================================

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310000
    ).hex()

    return password_hash, salt


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if "@" not in email or "." not in email:
        return False, "Enter a valid email address."

    password_hash, salt = hash_password(password)

    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO users
            (username, email, password_hash, salt)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, salt))

        conn.commit()
        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

    finally:
        conn.close()


def authenticate_user(username, password):
    conn = get_connection()

    user = conn.execute("""
        SELECT id, username, email, password_hash, salt
        FROM users
        WHERE username = ?
    """, (username.strip(),)).fetchone()

    conn.close()

    if user is None:
        return False, None

    user_id, saved_username, email, saved_hash, salt = user

    entered_hash, _ = hash_password(password, salt)

    if hmac.compare_digest(entered_hash, saved_hash):
        return True, {
            "id": user_id,
            "username": saved_username,
            "email": email
        }

    return False, None


# =====================================================
# LOAD MODELS
# =====================================================

@st.cache_resource
def load_models():
    account_model = joblib.load(
        MODEL_DIR / "account_model.pkl"
    )

    text_model = joblib.load(
        MODEL_DIR / "text_model.pkl"
    )

    vectorizer = joblib.load(
        MODEL_DIR / "vectorizer.pkl"
    )

    return account_model, text_model, vectorizer


initialize_database()

try:
    account_model, text_model, vectorizer = load_models()
except Exception as error:
    st.error(f"Model loading error: {error}")
    st.stop()


# =====================================================
# SESSION STATE
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "bulk_results" not in st.session_state:
    st.session_state.bulk_results = None


# =====================================================
# LOGIN AND REGISTRATION
# =====================================================

if not st.session_state.logged_in:

    st.title("🛡️ AI Spammer Detection System")
    st.subheader("User Authentication")

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    with login_tab:

        st.subheader("Login")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            if not username or not password:
                st.warning("Enter username and password.")

            else:
                success, user = authenticate_user(
                    username,
                    password
                )

                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with register_tab:

        st.subheader("Create Account")

        new_username = st.text_input(
            "Choose Username",
            key="register_username"
        )

        new_email = st.text_input(
            "Email Address",
            key="register_email"
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button("Register", use_container_width=True):

            if new_password != confirm_password:
                st.error("Passwords do not match.")

            else:
                success, message = register_user(
                    new_username,
                    new_email,
                    new_password
                )

                if success:
                    st.success(message)
                    st.info("Please log in now.")
                else:
                    st.error(message)

    st.stop()


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("🛡️ AI Spammer Detection")

st.sidebar.success(
    f"Welcome, {st.session_state.user['username']}!"
)

st.sidebar.caption(
    st.session_state.user["email"]
)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Admin Dashboard",
        "Fake User Detection",
        "Spam Message Detection",
        "Real-Time Spam & Phishing Analysis",
        "Bulk Account Analysis",
        "Prediction History",
        "Model Evaluation",
        "About Project"
    ]
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.bulk_results = None
    st.rerun()


# =====================================================
# DASHBOARD
# =====================================================

if menu == "Dashboard":

    st.title("🛡️ AI Spammer Detection Dashboard")

    st.write(
        "Machine Learning and NLP based social media "
        "spam and fake account detection system."
    )

    conn = get_connection()

    history = pd.read_sql_query(
        "SELECT * FROM history ORDER BY id DESC",
        conn
    )

    conn.close()

    total = len(history)

    spam_count = (
        history["detection_type"]
        .eq("Spam Message Detection")
        .sum()
        if total else 0
    )

    fake_count = (
        history[
            history["detection_type"] == "Fake User Detection"
        ]["prediction"]
        .eq("Fake User")
        .sum()
        if total else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Predictions", total)
    col2.metric("Spam Checks", int(spam_count))
    col3.metric("Fake Accounts", int(fake_count))

    if not history.empty:

        st.subheader("Recent Predictions")

        st.dataframe(
            history.head(10),
            use_container_width=True
        )

    else:
        st.info("No predictions available yet.")


# =====================================================
# ADMIN DASHBOARD
# =====================================================

elif menu == "Admin Dashboard":

    st.title("👨‍💼 Admin Analytics Dashboard")

    st.write(
        "System-level statistics for registered users "
        "and spam detection activity."
    )

    conn = get_connection()

    users_df = pd.read_sql_query(
        "SELECT id, username, created_at FROM users",
        conn
    )

    history_df = pd.read_sql_query(
        "SELECT * FROM history ORDER BY id DESC",
        conn
    )

    conn.close()

    total_users = len(users_df)
    total_predictions = len(history_df)

    spam_df = history_df[
        history_df["detection_type"] == "Spam Message Detection"
    ]

    account_df = history_df[
        history_df["detection_type"] == "Fake User Detection"
    ]

    spam_detected = (
        spam_df["prediction"] == "Spam"
    ).sum()

    fake_detected = (
        account_df["prediction"] == "Fake User"
    ).sum()

    genuine_messages = (
        spam_df["prediction"] == "Genuine"
    ).sum()

    genuine_accounts = (
        account_df["prediction"] == "Genuine User"
    ).sum()

    st.subheader("📊 Overall System Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Registered Users", total_users)
    col2.metric("Total Predictions", total_predictions)
    col3.metric("Spam Messages Detected", int(spam_detected))

    col4, col5, col6 = st.columns(3)

    col4.metric("Fake Accounts Detected", int(fake_detected))
    col5.metric("Genuine Messages", int(genuine_messages))
    col6.metric("Genuine Accounts", int(genuine_accounts))

    st.divider()

    st.subheader("📈 Detection Activity")

    if not history_df.empty:

        detection_counts = (
            history_df["detection_type"]
            .value_counts()
            .reset_index()
        )

        detection_counts.columns = [
            "Detection Type",
            "Count"
        ]

        fig1 = px.bar(
            detection_counts,
            x="Detection Type",
            y="Count",
            title="Predictions by Detection Type",
            text="Count"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.subheader("Prediction Distribution")

        prediction_counts = (
            history_df["prediction"]
            .value_counts()
            .reset_index()
        )

        prediction_counts.columns = [
            "Prediction",
            "Count"
        ]

        fig2 = px.pie(
            prediction_counts,
            names="Prediction",
            values="Count",
            title="Fake, Genuine and Spam Predictions"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.subheader("📅 Prediction Activity Over Time")

        history_df["created_at"] = pd.to_datetime(
            history_df["created_at"],
            errors="coerce"
        )

        date_counts = (
            history_df.dropna(subset=["created_at"])
            .assign(Date=lambda df: df["created_at"].dt.date)
            .groupby("Date")
            .size()
            .reset_index(name="Predictions")
        )

        if not date_counts.empty:

            fig3 = px.line(
                date_counts,
                x="Date",
                y="Predictions",
                markers=True,
                title="Daily Prediction Activity"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

    else:

        st.info(
            "No prediction data available. "
            "Run some detections to generate analytics."
        )

    st.divider()

    st.subheader("👥 Registered User Statistics")

    st.metric(
        "Total Registered Users",
        total_users
    )

    if not users_df.empty:

        st.write(
            "User registration information is summarized below."
        )

        registration_counts = (
            users_df.assign(
                RegistrationDate=pd.to_datetime(
                    users_df["created_at"],
                    errors="coerce"
                ).dt.date
            )
            .dropna(subset=["RegistrationDate"])
            .groupby("RegistrationDate")
            .size()
            .reset_index(name="New Users")
        )

        if not registration_counts.empty:

            fig4 = px.bar(
                registration_counts,
                x="RegistrationDate",
                y="New Users",
                title="New User Registrations"
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

    st.caption(
        "Analytics are available to all logged-in users. "
        "This is not a restricted administrator-only page."
    )


# =====================================================
# FAKE USER DETECTION
# =====================================================

elif menu == "Fake User Detection":

    st.title("👤 Fake User Detection")

    with st.form("account_form"):

        col1, col2 = st.columns(2)

        with col1:

            account_age_days = st.number_input(
                "Account Age (Days)",
                min_value=0,
                value=365
            )

            followers = st.number_input(
                "Followers",
                min_value=0,
                value=100
            )

            following = st.number_input(
                "Following",
                min_value=0,
                value=150
            )

            posts = st.number_input(
                "Posts",
                min_value=0,
                value=50
            )

        with col2:

            profile_completeness = st.slider(
                "Profile Completeness",
                0.0, 100.0, 80.0
            )

            username_digit_ratio = st.slider(
                "Username Digit Ratio",
                0.0, 1.0, 0.1
            )

            repetitive_content_ratio = st.slider(
                "Repetitive Content Ratio",
                0.0, 1.0, 0.1
            )

        submitted = st.form_submit_button(
            "🔍 Predict Account",
            use_container_width=True
        )

    if submitted:

        account_data = {
            "account_age_days": account_age_days,
            "followers": followers,
            "following": following,
            "posts": posts,
            "profile_completeness": profile_completeness,
            "username_digit_ratio": username_digit_ratio,
            "repetitive_content_ratio": repetitive_content_ratio
        }

        features = pd.DataFrame(
            [account_data],
            columns=ACCOUNT_FEATURES
        )

        prediction = account_model.predict(features)[0]
        probabilities = account_model.predict_proba(features)[0]

        confidence = float(max(probabilities))

        is_fake = str(prediction).lower() in [
            "1", "true", "fake"
        ]

        label = "Fake User" if is_fake else "Genuine User"

        risk = analyze_account(account_data)

        if is_fake:
            st.error("🚨 Prediction: Fake User")
        else:
            st.success("✅ Prediction: Genuine User")

        col1, col2 = st.columns(2)

        col1.metric(
            "ML Confidence",
            f"{confidence * 100:.2f}%"
        )

        col2.metric(
            "Rule-Based Risk Score",
            risk["risk_score"]
        )

        st.write("Risk Level:", risk["risk_level"])

        for reason in risk["reasons"]:
            st.write("- " + reason)

        save_history(
            "Fake User Detection",
            account_data,
            label,
            confidence
        )

        pdf_data = generate_pdf_report(
            "Fake User Detection",
            account_data,
            label,
            confidence
        )

        st.download_button(
            "📄 Download PDF Report",
            data=pdf_data,
            file_name="fake_user_report.pdf",
            mime="application/pdf"
        )


# =====================================================
# SPAM MESSAGE DETECTION
# =====================================================

elif menu == "Spam Message Detection":

    st.title("📩 Spam Message Detection")

    message = st.text_area(
        "Enter Your Message",
        height=150
    )

    if st.button("🔍 Detect Spam", use_container_width=True):

        if not message.strip():

            st.warning("Please enter a message.")

        else:

            transformed = vectorizer.transform([message])

            prediction = text_model.predict(transformed)[0]

            probabilities = text_model.predict_proba(transformed)[0]

            confidence = float(max(probabilities))

            is_spam = str(prediction).lower() in [
                "spam", "1", "true"
            ]

            label = "Spam" if is_spam else "Genuine"

            analysis = analyze_message(message)

            if is_spam:
                st.error("🚨 Prediction: Spam")
            else:
                st.success("✅ Prediction: Genuine")

            col1, col2 = st.columns(2)

            col1.metric(
                "ML Confidence",
                f"{confidence * 100:.2f}%"
            )

            col2.metric(
                "Rule-Based Risk Score",
                analysis["risk_score"]
            )

            st.write(
                "Risk Level:",
                analysis["risk_level"]
            )

            st.subheader("Advanced Analysis")

            for reason in analysis["reasons"]:
                st.write("- " + reason)

            if analysis["urls"]:
                st.write("Detected URLs:")
                for url in analysis["urls"]:
                    st.write("- " + url)

            save_history(
                "Spam Message Detection",
                message,
                label,
                confidence
            )

            pdf_data = generate_pdf_report(
                "Spam Message Detection",
                message,
                label,
                confidence
            )

            st.download_button(
                "📄 Download PDF Report",
                data=pdf_data,
                file_name="spam_message_report.pdf",
                mime="application/pdf"
            )
            # =====================================================
# REAL-TIME SPAM AND PHISHING ANALYSIS
# =====================================================

elif menu == "Real-Time Spam & Phishing Analysis":

    st.title("🚨 Real-Time Spam & Phishing Analysis")

    st.write(
        "Analyze messages, identify suspicious keywords, "
        "extract URLs, and calculate potential phishing risk."
    )

    st.info(
        "This feature uses rule-based analysis. "
        "It does not verify URLs against live threat databases."
    )

    message = st.text_area(
        "Enter a message to analyze",
        height=180,
        placeholder=(
            "Example: Congratulations! You won a free prize. "
            "Click here: http://example.com"
        ),
        key="realtime_message"
    )

    if st.button(
        "🔍 Analyze Message",
        use_container_width=True
    ):

        if not message.strip():
            st.warning("Please enter a message.")

        else:
            try:
                result = analyze_message_realtime(message)

                risk_score = result["risk_score"]
                risk_level = result["risk_level"]

                st.divider()
                st.subheader("📊 Message Risk Analysis")

                col1, col2 = st.columns(2)

                col1.metric("Risk Score", f"{risk_score}/100")
                col2.metric("Risk Level", risk_level)

                st.progress(risk_score / 100)

                if risk_level == "High":
                    st.error(
                        "🚨 High Risk: Multiple suspicious indicators detected."
                    )

                elif risk_level == "Medium":
                    st.warning(
                        "⚠️ Medium Risk: Review this message carefully."
                    )

                else:
                    st.success(
                        "✅ Low Risk: Few suspicious indicators detected."
                    )

                st.divider()
                st.subheader("🔎 Suspicious Keyword Detection")

                keywords = result["keyword_matches"]

                if keywords:
                    st.write(
                        f"Detected {len(keywords)} suspicious keywords:"
                    )

                    for keyword in keywords:
                        st.write("- " + keyword)

                else:
                    st.success("No suspicious keywords detected.")

                st.divider()
                st.subheader("🌐 URL and Phishing Analysis")

                urls = result["url_results"]

                if urls:

                    for index, url_data in enumerate(urls, start=1):

                        st.write(f"**URL {index}**")
                        st.code(url_data["url"])

                        col1, col2 = st.columns(2)

                        col1.metric(
                            "URL Risk Score",
                            f'{url_data["risk_score"]}/100'
                        )

                        col2.metric(
                            "URL Risk Level",
                            url_data["risk_level"]
                        )

                        for reason in url_data["reasons"]:
                            st.write("- " + reason)

                        st.divider()

                else:
                    st.info("No URLs found in this message.")

                save_history(
                    "Real-Time Spam & Phishing Analysis",
                    message,
                    risk_level,
                    risk_score
                )

                pdf_data = generate_pdf_report(
                    "Real-Time Spam & Phishing Analysis",
                    message,
                    risk_level,
                    risk_score
                )

                st.download_button(
                    "📄 Download Analysis PDF",
                    data=pdf_data,
                    file_name="realtime_spam_analysis.pdf",
                    mime="application/pdf"
                )

                st.success("Analysis completed successfully!")

            except Exception as error:
                st.error(f"Analysis error: {error}")


# =====================================================
# BULK ACCOUNT ANALYSIS
# =====================================================

elif menu == "Bulk Account Analysis":

    st.title("📊 Bulk Account Analysis")

    uploaded_file = st.file_uploader(
        "Upload Account CSV",
        type=["csv"]
    )

    if uploaded_file:

        try:

            data = pd.read_csv(uploaded_file)

            st.subheader("Uploaded Dataset")

            st.dataframe(
                data.head(),
                use_container_width=True
            )

            missing = [
                col for col in ACCOUNT_FEATURES
                if col not in data.columns
            ]

            if missing:

                st.error(
                    f"Missing columns: {missing}"
                )

            elif st.button("🚀 Run Bulk Analysis"):

                features = data[ACCOUNT_FEATURES].copy()

                if features.isnull().any().any():
                    st.error(
                        "Dataset contains missing values."
                    )

                else:

                    predictions = account_model.predict(features)

                    probabilities = account_model.predict_proba(features)

                    results = data.copy()

                    results["Prediction"] = [
                        "Fake User"
                        if str(value).lower() in [
                            "1", "true", "fake"
                        ]
                        else "Genuine User"
                        for value in predictions
                    ]

                    results["ML Confidence"] = (
                        probabilities.max(axis=1) * 100
                    ).round(2)

                    risk_results = features.apply(
                        lambda row: analyze_account(row.to_dict()),
                        axis=1
                    )

                    results["Risk Score"] = [
                        result["risk_score"]
                        for result in risk_results
                    ]

                    results["Risk Level"] = [
                        result["risk_level"]
                        for result in risk_results
                    ]

                    st.session_state.bulk_results = results

                    st.success("Bulk analysis completed!")

            if st.session_state.bulk_results is not None:

                results = st.session_state.bulk_results

                st.dataframe(
                    results,
                    use_container_width=True
                )

                col1, col2, col3 = st.columns(3)

                col1.metric("Total Accounts", len(results))

                col2.metric(
                    "Fake Accounts",
                    int((results["Prediction"] == "Fake User").sum())
                )

                col3.metric(
                    "Genuine Accounts",
                    int((results["Prediction"] == "Genuine User").sum())
                )

                st.download_button(
                    "⬇️ Download Analysis CSV",
                    data=results.to_csv(index=False).encode("utf-8"),
                    file_name="bulk_account_analysis.csv",
                    mime="text/csv"
                )

        except Exception as error:
            st.error(f"CSV processing error: {error}")


# =====================================================
# PREDICTION HISTORY
# =====================================================

elif menu == "Prediction History":

    st.title("📜 Prediction History")

    conn = get_connection()

    history = pd.read_sql_query(
        "SELECT * FROM history ORDER BY id DESC",
        conn
    )

    conn.close()

    if not history.empty:

        st.dataframe(
            history,
            use_container_width=True
        )

        st.download_button(
            "⬇️ Download History CSV",
            data=history.to_csv(index=False).encode("utf-8"),
            file_name="prediction_history.csv",
            mime="text/csv"
        )

    else:
        st.info("No prediction history available.")


# =====================================================
# MODEL EVALUATION
# =====================================================

elif menu == "Model Evaluation":

    st.title("📈 Model Evaluation")

    try:
        show_model_evaluation()

    except Exception as error:
        st.error(f"Model evaluation error: {error}")


# =====================================================
# ABOUT PROJECT
# =====================================================

elif menu == "About Project":

    st.title("ℹ️ About Project")

    st.subheader(
        "AI-Based Spammer Detection and Fake User Identification"
    )

    st.write("""
    This project uses Machine Learning and Natural Language
    Processing to detect spam messages and suspicious
    social media accounts.
    """)

    st.subheader("Main Features")

    features = [
        "User Registration and Login",
        "Fake User Detection using Random Forest",
        "Spam Message Detection using NLP and TF-IDF",
        "Advanced Spam Risk Analysis",
        "Fake Account Risk Analysis",
        "Bulk Account Analysis",
        "Prediction History using SQLite",
        "PDF Report Generation",
        "Model Evaluation",
        "Admin Analytics Dashboard"
    ]

    for feature in features:
        st.write("✅ " + feature)

    st.subheader("Technologies Used")

    st.write("""
    - Python
    - Streamlit
    - Machine Learning
    - Natural Language Processing
    - Scikit-learn
    - Pandas
    - Plotly
    - SQLite
    - Joblib
    - ReportLab
    """)

    st.subheader("Project Objective")

    st.write("""
    The objective is to identify suspicious social media
    accounts and unwanted spam messages using machine
    learning techniques.
    """)

    st.divider()

    st.caption(
        "AI Spammer Detection System | Final Year Project"
    )
