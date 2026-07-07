def severity_to_score(severity):
    """
    Convert severity text into a numeric score.
    """

    if severity is None:
        return 0

    severity = severity.lower()

    if severity == "critical":
        return 10
    elif severity == "high":
        return 7
    elif severity == "moderate":
        return 4
    elif severity == "low":
        return 1
    else:
        return 0


def calculate_risk_level(weather_data=None, news_data=None):
    """
    Calculate the final safety risk level using weather and public safety data.

    Input:
        weather_data: dictionary from weather_tool.py
        news_data: dictionary from news_tool.py

    Output:
        dictionary containing final risk score, risk level, and explanation
    """

    weather_score = 0
    news_score = 0
    risk_factors = []

    # Score weather data
    if weather_data:
        weather_severity = weather_data.get("severity", "Low")
        weather_score = severity_to_score(weather_severity)

        alert_type = weather_data.get("alert_type", "Weather Alert")
        risk_factors.append(f"Weather: {alert_type} ({weather_severity})")

    # Score news/public safety data
    if news_data:
        news_severity = news_data.get("severity", "Low")
        news_score = severity_to_score(news_severity)

        report_type = news_data.get("report_type", "Public Safety Report")
        risk_factors.append(f"Public Safety: {report_type} ({news_severity})")

    # Use the highest score as the main risk score
    # This is safer than averaging because one critical alert should not be reduced by a low-risk item.
    final_score = max(weather_score, news_score)

    # Add small combined-risk adjustment
    # If both weather and news risks are moderate or higher, increase the score.
    if weather_score >= 4 and news_score >= 4:
        final_score += 1

    # Convert score to final risk level
    if final_score >= 10:
        risk_level = "Critical"
        explanation = "A critical safety condition may be present. Immediate caution is recommended."
    elif final_score >= 7:
        risk_level = "High"
        explanation = "A high-risk condition may be present. Avoid affected areas if possible."
    elif final_score >= 4:
        risk_level = "Moderate"
        explanation = "A moderate safety concern is present. Stay alert and monitor updates."
    else:
        risk_level = "Low"
        explanation = "No major safety concern was found in the available demo data."

    return {
        "final_score": final_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "explanation": explanation
    }


def get_risk_color(risk_level):
    """
    Return a display color label for Streamlit.
    """

    risk_level = risk_level.lower()

    if risk_level == "critical":
        return "red"
    elif risk_level == "high":
        return "orange"
    elif risk_level == "moderate":
        return "yellow"
    else:
        return "green"