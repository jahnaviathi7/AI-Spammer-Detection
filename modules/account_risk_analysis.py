
def analyze_account(account):

    reasons = []
    risk_score = 0

    followers = account["followers"]
    following = account["following"]
    posts = account["posts"]
    age = account["account_age_days"]
    completeness = account["profile_completeness"]
    digits = account["username_digit_ratio"]
    repetitive = account["repetitive_content_ratio"]

    # 1. Account age analysis
    if age < 30:
        risk_score += 20
        reasons.append("Very newly created account")

    elif age < 90:
        risk_score += 10
        reasons.append("Account is relatively new")

    # 2. Followers and following analysis
    if following > 0:

        ratio = followers / following

        if ratio < 0.05 and following > 500:
            risk_score += 20
            reasons.append("Very low follower-to-following ratio")

    elif followers == 0:
        risk_score += 10
        reasons.append("Account has no followers")

    # 3. Post analysis
    if posts < 5:
        risk_score += 15
        reasons.append("Very low number of posts")

    # 4. Profile completeness
    if completeness < 0.3:
        risk_score += 15
        reasons.append("Incomplete account profile")

    # 5. Username analysis
    if digits > 0.5:
        risk_score += 10
        reasons.append("Username contains many digits")

    # 6. Repetitive content analysis
    if repetitive > 0.7:
        risk_score += 20
        reasons.append("Highly repetitive account content")

    risk_score = min(risk_score, 100)

    # Risk level
    if risk_score >= 60:
        risk_level = "High"

    elif risk_score >= 30:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    if not reasons:
        reasons.append("No obvious suspicious account patterns detected")

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons
    }
