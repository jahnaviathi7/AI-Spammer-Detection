import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

import os

os.makedirs("models", exist_ok=True)

# =================================
# 1. FAKE USER DETECTION
# =================================

df = pd.read_csv("data/account_dataset.csv")

features = [
    "account_age_days",
    "followers",
    "following",
    "posts",
    "profile_completeness",
    "username_digit_ratio",
    "repetitive_content_ratio"
]

X = df[features]
y = df["is_fake"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

account_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    class_weight="balanced"
)

account_model.fit(X_train, y_train)

pred = account_model.predict(X_test)

print("\n========== FAKE USER DETECTION ==========")
print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))

joblib.dump(account_model, "models/account_model.pkl")


# =================================
# 2. SPAM MESSAGE DETECTION
# =================================

spam_df = pd.read_csv("data/spam_messages.csv")

X_text = spam_df["message"].astype(str)
y_text = spam_df["is_spam"]

Xtr, Xte, ytr, yte = train_test_split(
    X_text, y_text,
    test_size=0.2,
    random_state=42,
    stratify=y_text
)

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2)
)

Xtr_vec = vectorizer.fit_transform(Xtr)
Xte_vec = vectorizer.transform(Xte)

text_model = MultinomialNB()

text_model.fit(Xtr_vec, ytr)

text_pred = text_model.predict(Xte_vec)

print("\n========== SPAM MESSAGE DETECTION ==========")
print("Accuracy:", accuracy_score(yte, text_pred))
print(classification_report(yte, text_pred))

joblib.dump(text_model, "models/text_model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

print("\n================================")
print("BOTH MODELS TRAINED SUCCESSFULLY")
print("================================")