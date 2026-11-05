# 🛡️ AI-Based Spammer Detection & Fake User Identification

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/NLP-TF--IDF-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-red?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/Status-Deployed-success?style=for-the-badge" />
</p>

<p align="center">
  <b>🔍 Detect Spam. Identify Fake Accounts. Analyze Phishing Risks.</b>
</p>

<p align="center">
  An intelligent machine learning and NLP-powered web application designed to identify suspicious social media accounts, detect spam messages, and analyze potentially dangerous URLs.
</p>

<p align="center">
  <a href="https://ai-spammer-detection-123.streamlit.app/">
    <img src="https://img.shields.io/badge/🚀_LIVE_DEMO-Launch_Application-00C853?style=for-the-badge" />
  </a>
</p>

---

## 🌐 Live Application

🚀 **Try the project here:**

👉 https://ai-spammer-detection-123.streamlit.app/

Explore the application and test its spam detection, fake account identification, and phishing risk analysis features.

---

## 📌 Project Overview

Social media platforms face increasing challenges from spam messages, fake profiles, fraudulent links, and phishing attempts.

This project introduces an AI-based detection system that combines Machine Learning, Natural Language Processing (NLP), and rule-based security analysis to identify suspicious online activities.

The application provides a user-friendly dashboard where users can analyze individual accounts, messages, bulk account datasets, and suspicious URLs.

## ✨ Key Features

### 1. 👤 Fake User Detection
- Identifies potentially fake social media accounts.
- Uses a Random Forest classification model.
- Analyzes account-related features.
- Displays prediction results and model confidence.

### 2. 💬 Spam Message Detection
- Classifies messages as Spam or Genuine.
- Uses TF-IDF text vectorization.
- Uses Multinomial Naive Bayes classification.
- Displays prediction results and probability scores.

### 3. 🚨 Real-Time Spam & Phishing Analysis
- Detects suspicious keywords and phrases.
- Identifies potentially suspicious URLs.
- Extracts URLs from messages.
- Analyzes HTTPS usage and IP-based links.
- Calculates message and URL risk scores.
- Categorizes risks as Low, Medium, or High.

### 4. 📂 Bulk Account Analysis
- Upload account datasets in CSV format.
- Analyze multiple accounts together.
- Generate predictions for uploaded records.

### 5. 📊 Model Evaluation
- Displays machine learning model performance.
- Provides evaluation metrics and visualizations.
- Helps understand classification performance.

### 6. 🗂️ Prediction History
- Stores previous detection results using SQLite.
- Displays historical predictions.
- Helps review previously analyzed messages and accounts.

### 7. 📄 PDF Report Generation
- Generates downloadable PDF analysis reports.
- Includes detection information and prediction results.

### 8. 🔐 User Authentication
- User registration and login.
- Password hashing for secure password storage.
- Session-based access to the application.

### 9. 📈 Analytics Dashboard
- Displays detection statistics.
- Provides visual insights into spam and fake account analysis.

---

## 🧠 Machine Learning Approach

| Module | Algorithm / Technique |
|---|---|
| Fake User Detection | Random Forest Classifier |
| Spam Message Detection | TF-IDF + Multinomial Naive Bayes |
| Text Processing | Natural Language Processing |
| Phishing Risk Analysis | Rule-Based Detection |
| URL Analysis | URL Parsing and Pattern Matching |
| Model Evaluation | Scikit-learn Metrics |

### 🔄 System Workflow

```text
             USER INPUT
                 |
        +--------+--------+
        |                 |
   Account Data      Text Message
        |                 |
        v                 v
 Random Forest       TF-IDF Vectorizer
        |                 |
        v                 v
 Fake User          Naive Bayes
 Detection          Classification
        |                 |
        v                 v
 Prediction         Spam / Genuine
        |                 |
        +--------+--------+
                 |
                 v
       Real-Time Risk Analysis
                 |
                 v
       Suspicious Keyword & URL
              Detection
                 |
                 v
         Results & Risk Score
                 |
        +--------+--------+
        |                 |
        v                 v
   SQLite History     PDF Reports
```

---

## 🛠️ Technology Stack

### Programming Language
- Python

### Machine Learning & NLP
- Scikit-learn
- Pandas
- NumPy
- TF-IDF
- Random Forest
- Multinomial Naive Bayes
- NLTK

### Frontend & Visualization
- Streamlit
- Plotly

### Database
- SQLite

### Model Storage
- Joblib

### Report Generation
- ReportLab

### Deployment & Version Control
- Streamlit Community Cloud
- Git
- GitHub

---

## 📁 Project Structure

```text
AI-Spammer-Detection/
│
├── app.py
├── train_model.py
├── config.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── account_dataset.csv
│   └── spam_messages.csv
│
├── models/
│   ├── account_model.pkl
│   ├── text_model.pkl
│   └── vectorizer.pkl
│
├── modules/
│   ├── account_detection.py
│   ├── spam_detection.py
│   ├── database.py
│   ├── report_generator.py
│   ├── model_evaluation.py
│   ├── advanced_spam_detection.py
│   ├── account_risk_analysis.py
│   └── real_time_spam_detection.py
│
└── reports/
```

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### Step 1: Clone the repository

```bash
git clone https://github.com/jahnaviathi7/AI-Spammer-Detection.git
```

### Step 2: Navigate to the project folder

```bash
cd AI-Spammer-Detection
```

### Step 3: Create a virtual environment

```bash
python -m venv venv
```

### Step 4: Activate the environment

**Windows:**

```powershell
venv\Scripts\activate
```

### Step 5: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 6: Run the application

```bash
python -m streamlit run app.py
```

### Step 7: Open the application

```text
http://localhost:8501
```

---

## 📊 Application Highlights

The application provides:

- Interactive Streamlit dashboard.
- Individual and bulk prediction capabilities.
- Spam and phishing risk analysis.
- Prediction history tracking.
- Model performance visualizations.
- Downloadable PDF reports.
- User authentication.

---

## 🔮 Future Enhancements

- Integration with authorized social media APIs.
- Advanced deep learning-based spam classification.
- More comprehensive phishing URL intelligence.
- Improved detection using larger real-world datasets.
- Advanced fake account behavior analysis.
- Automated suspicious activity monitoring.
- Multilingual spam detection.

---

## ⚠️ Disclaimer

This project is developed for educational and research purposes.

The predictions and risk scores are intended as indicators for further investigation, not definitive proof that an account, message, or URL is malicious. Model performance depends on the quality and representativeness of the training data. Rule-based URL analysis does not verify links against live threat intelligence databases.

---

## 👩‍💻 Developer

**Athi Jahnavi**

B.Tech – Final Year

**Areas of Interest:**
- Software Development
- Artificial Intelligence
- Machine Learning
- Web Development
- Natural Language Processing

### 🔗 Connect With Me

- 💻 GitHub: https://github.com/jahnaviathi7
- 🔗 LinkedIn: https://www.linkedin.com/in/jahnavi-athi-a0a0063a0
- 📧 Email: jahnaviathi7@gmail.com

---

<p align="center">
  <b>⭐ If you find this project interesting, consider giving it a star on GitHub!</b>
</p>

<p align="center">
  Built with ❤️ using Python, Machine Learning, NLP and Streamlit.
</p>
