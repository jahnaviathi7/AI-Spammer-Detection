
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"


def show_metrics(y_true, y_pred, model_name):

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    st.subheader(model_name + " Performance")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Accuracy", f"{accuracy:.2%}")
    c2.metric("Precision", f"{precision:.2%}")
    c3.metric("Recall", f"{recall:.2%}")
    c4.metric("F1 Score", f"{f1:.2%}")

    return {
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }


def show_confusion_matrix(y_true, y_pred, model_name):

    cm = confusion_matrix(y_true, y_pred)

    fig = px.imshow(
        cm,
        text_auto=True,
        x=["Genuine", "Fake/Spam"],
        y=["Genuine", "Fake/Spam"],
        labels={
            "x": "Predicted Label",
            "y": "Actual Label",
            "color": "Count"
        },
        title=model_name + " Confusion Matrix",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, use_container_width=True)


def show_model_evaluation():

    st.header("Model Evaluation Dashboard")

    # -------------------------------
    # LOAD ACCOUNT DATA
    # -------------------------------

    account_path = DATA_DIR / "account_dataset.csv"
    spam_path = DATA_DIR / "spam_messages.csv"

    account_data = pd.read_csv(account_path)
    spam_data = pd.read_csv(spam_path)

    account_features = [
        "account_age_days",
        "followers",
        "following",
        "posts",
        "profile_completeness",
        "username_digit_ratio",
        "repetitive_content_ratio"
    ]

    account_target = "is_fake"

    X_account = account_data[account_features]
    y_account = account_data[account_target]

    Xa_train, Xa_test, ya_train, ya_test = train_test_split(
        X_account,
        y_account,
        test_size=0.2,
        random_state=42,
        stratify=y_account
    )

    account_model = joblib.load(
        MODEL_DIR / "account_model.pkl"
    )

    account_pred = account_model.predict(Xa_test)

    # -------------------------------
    # ACCOUNT EVALUATION
    # -------------------------------

    st.divider()

    account_metrics = show_metrics(
        ya_test,
        account_pred,
        "Fake User Detection"
    )

    show_confusion_matrix(
        ya_test,
        account_pred,
        "Fake User Detection"
    )

    # Feature importance

    st.subheader("Fake User Detection - Feature Importance")

    importance = pd.DataFrame({
        "Feature": account_features,
        "Importance": account_model.feature_importances_
    }).sort_values(
        by="Importance",
        ascending=False
    )

    fig = px.bar(
        importance,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Account Model Feature Importance"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # SPAM MESSAGE EVALUATION
    # -------------------------------

    st.divider()

    text_model = joblib.load(
        MODEL_DIR / "text_model.pkl"
    )

    vectorizer = joblib.load(
        MODEL_DIR / "vectorizer.pkl"
    )

    # Automatically identify text and target columns
    text_column = next(
        (c for c in spam_data.columns
         if c.lower() in ["message", "text", "message_text"]),
        None
    )

    target_column = next(
        (c for c in spam_data.columns
         if c.lower() in ["label", "category", "is_spam"]),
        None
    )

    if text_column is None or target_column is None:

        st.error(
            "Could not identify message and label columns "
            "in spam_messages.csv. Check the CSV column names."
        )

        return

    X_text = spam_data[text_column].fillna("").astype(str)
    y_text = spam_data[target_column]

    Xt_train, Xt_test, yt_train, yt_test = train_test_split(
        X_text,
        y_text,
        test_size=0.2,
        random_state=42,
        stratify=y_text
    )

    Xt_test_vector = vectorizer.transform(Xt_test)

    text_pred = text_model.predict(Xt_test_vector)

    # -------------------------------
    # TEXT MODEL METRICS
    # -------------------------------

    text_metrics = show_metrics(
        yt_test,
        text_pred,
        "Spam Message Detection"
    )

    show_confusion_matrix(
        yt_test,
        text_pred,
        "Spam Message Detection"
    )

    # -------------------------------
    # ROC CURVE
    # -------------------------------

    st.subheader("ROC Curve Analysis")

    account_probability = account_model.predict_proba(
        Xa_test
    )[:, 1]

    text_probability = text_model.predict_proba(
        Xt_test_vector
    )[:, 1]

    fig_roc = px.line(
        title="ROC Curve - Model Comparison"
    )

    for y_true, probability, name in [
        (ya_test, account_probability, "Fake User Model"),
        (yt_test, text_probability, "Spam Message Model")
    ]:

        fpr, tpr, _ = roc_curve(
            y_true,
            probability,
            pos_label=1
        )

        roc_auc = auc(fpr, tpr)

        fig_roc.add_scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"{name} (AUC={roc_auc:.3f})"
        )

    fig_roc.add_scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Random Classifier",
        line=dict(dash="dash")
    )

    fig_roc.update_layout(
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate"
    )

    st.plotly_chart(
        fig_roc,
        use_container_width=True
    )

    # -------------------------------
    # MODEL COMPARISON
    # -------------------------------

    st.divider()

    st.subheader("Model Performance Comparison")

    comparison = pd.DataFrame([
        account_metrics,
        text_metrics
    ])

    st.dataframe(
        comparison.style.format({
            "Accuracy": "{:.2%}",
            "Precision": "{:.2%}",
            "Recall": "{:.2%}",
            "F1 Score": "{:.2%}"
        }),
        use_container_width=True
    )

    chart_data = comparison.melt(
        id_vars="Model",
        var_name="Metric",
        value_name="Score"
    )

    fig_comparison = px.bar(
        chart_data,
        x="Metric",
        y="Score",
        color="Model",
        barmode="group",
        title="Model Performance Comparison",
        range_y=[0, 1]
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )

    # -------------------------------
    # CLASSIFICATION REPORT
    # -------------------------------

    st.divider()

    st.subheader("Detailed Classification Reports")

    tab1, tab2 = st.tabs([
        "Fake User Model",
        "Spam Message Model"
    ])

    with tab1:

        st.code(
            classification_report(
                ya_test,
                account_pred,
                zero_division=0
            )
        )

    with tab2:

        st.code(
            classification_report(
                yt_test,
                text_pred,
                zero_division=0
            )
        )

    st.info(
        "Evaluation uses the project's held-out test datasets. "
        "If the datasets are synthetic, these scores do not "
        "establish real-world detection performance."
    )
