
import re
from urllib.parse import urlparse


SUSPICIOUS_KEYWORDS = [
    "free prize",
    "you won",
    "claim now",
    "click here",
    "urgent",
    "limited offer",
    "verify your account",
    "send password",
    "bank details",
    "lottery",
    "cash reward",
    "congratulations",
    "act now",
    "account suspended",
    "win money"
]


def detect_urls(message):

    pattern = r"https?://\S+|www\.\S+"

    return re.findall(pattern, message, flags=re.IGNORECASE)


def detect_suspicious_keywords(message):

    message_lower = message.lower()

    found_keywords = [
        word for word in SUSPICIOUS_KEYWORDS
        if word in message_lower
    ]

    return found_keywords


def analyze_message(message):

    urls = detect_urls(message)

    keywords = detect_suspicious_keywords(message)

    reasons = []
    risk_score = 0

    # Suspicious keywords
    if keywords:

        risk_score += min(len(keywords) * 15, 45)

        reasons.append(
            "Suspicious keywords found: " + ", ".join(keywords)
        )

    # URL detection
    if urls:

        risk_score += 15

        reasons.append(
            "Message contains a URL"
        )

        for url in urls:

            cleaned_url = url.rstrip(".,!?;:)")

            if cleaned_url.lower().startswith("www."):
                cleaned_url = "https://" + cleaned_url

            domain = urlparse(cleaned_url).hostname or ""

            if re.search(r"\d+\.\d+\.\d+\.\d+", domain):
                risk_score += 25

                reasons.append(
                    "URL uses an IP address instead of a domain name"
                )

            if domain.startswith("xn--") or ".xn--" in domain:
                risk_score += 20

                reasons.append(
                    "URL contains an internationalized domain name"
                )

            if "@" in cleaned_url:
                risk_score += 20

                reasons.append(
                    "URL contains an unusual @ symbol"
                )

    # Excessive exclamation marks
    if message.count("!") >= 3:

        risk_score += 10

        reasons.append(
            "Excessive exclamation marks"
        )

    # Excessive capital letters
    letters = [c for c in message if c.isalpha()]

    if len(letters) >= 10:

        uppercase_ratio = (
            sum(c.isupper() for c in letters) / len(letters)
        )

        if uppercase_ratio > 0.7:

            risk_score += 10

            reasons.append(
                "Unusually high use of capital letters"
            )

    risk_score = min(risk_score, 100)

    if risk_score >= 60:

        risk_level = "High"

    elif risk_score >= 30:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    if not reasons:

        reasons.append(
            "No obvious suspicious patterns detected"
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "urls": urls,
        "keywords": keywords,
        "reasons": reasons
    }
