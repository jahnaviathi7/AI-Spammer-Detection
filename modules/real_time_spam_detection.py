
import re
from urllib.parse import urlparse


SUSPICIOUS_KEYWORDS = [
    "claim now",
    "free prize",
    "you won",
    "verify your account",
    "verify",
    "password",
    "confirm password",
    "update your password",
    "urgent action",
    "immediately",
    "click here",
    "limited offer",
    "bank account",
    "account blocked",
    "account is blocked",
    "account suspended",
    "send otp",
    "share otp",
    "otp",
    "lottery",
    "congratulations",
    "update your details",
    "confirm your identity",
    "login immediately",
    "unauthorized transaction",
]


def extract_urls(message):
    pattern = r"https?://[^\s]+|www\.[^\s]+"
    found_urls = re.findall(pattern, message, re.IGNORECASE)

    # Remove punctuation commonly attached to URLs in messages.
    return [
        url.rstrip(".,!?;:)]}\"'")
        for url in found_urls
    ]


def analyze_url(url):
    url = url.strip()

    if url.lower().startswith("www."):
        url = "http://" + url

    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()

    reasons = []
    risk = 0

    if not domain:
        return {
            "url": url,
            "risk_score": 0,
            "risk_level": "Unknown",
            "reasons": ["Invalid URL"]
        }

    if parsed.scheme.lower() != "https":
        risk += 20
        reasons.append("URL does not use HTTPS")

    # Detect IP address URLs.
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        risk += 35
        reasons.append("URL uses an IP address instead of a domain")

    if "@" in parsed.netloc:
        risk += 30
        reasons.append("URL contains an unusual @ symbol")

    if domain.count("-") >= 2:
        risk += 15
        reasons.append("Domain contains multiple hyphens")

    if len(domain) > 35:
        risk += 10
        reasons.append("Unusually long domain name")

    if any(
        word in domain
        for word in ["login", "verify", "secure", "account", "bank"]
    ):
        risk += 15
        reasons.append("Domain contains a sensitive keyword")

    risk = min(risk, 100)

    if risk >= 60:
        level = "High"
    elif risk >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {
        "url": url,
        "risk_score": risk,
        "risk_level": level,
        "reasons": reasons
    }


def analyze_message_realtime(message):

    urls = extract_urls(message)
    message_lower = message.lower()

    keyword_matches = [
        keyword
        for keyword in SUSPICIOUS_KEYWORDS
        if keyword in message_lower
    ]

    url_results = [
        analyze_url(url)
        for url in urls
    ]

    score = 0

    # Suspicious keyword scoring.
    if keyword_matches:
        score += min(len(keyword_matches) * 15, 45)

    # URL risk scoring.
    if url_results:
        score += max(
            result["risk_score"]
            for result in url_results
        )

    # Excessive exclamation marks.
    if message.count("!") >= 3:
        score += 10

    # Excessive uppercase characters.
    if message:
        uppercase_ratio = (
            sum(char.isupper() for char in message) / len(message)
        )

        if uppercase_ratio > 0.5:
            score += 10

    score = min(score, 100)

    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {
        "risk_score": score,
        "risk_level": level,
        "keyword_matches": keyword_matches,
        "url_results": url_results,
        "urls_found": urls
    }
