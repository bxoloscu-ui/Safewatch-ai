import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_safety_summary(location, weather_data=None, news_data=None, risk_result=None):
    """
    Generate a safety summary using Gemini.

    If Gemini is unavailable, the function returns a clean rule-based fallback summary.
    """

    if not GEMINI_API_KEY:
        return fallback_summary(
            location=location,
            weather_data=weather_data,
            news_data=news_data,
            risk_result=risk_result,
            error="Gemini API key was not found."
        )

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = f"""
You are SafeWatch AI, a public safety decision-support agent.

Create a clear safety summary for the user based only on the provided data.

Important rules:
- Do not invent incidents.
- Do not exaggerate risk.
- If the data is demo data, clearly say it is demo data.
- If details are limited, say details are limited.
- Give practical safety recommendations.
- Include a check-in suggestion if the risk is High or Critical.
- Include an emergency reminder.
- Do not claim to replace emergency services.

Location:
{location}

Weather Data:
{weather_data}

Public Safety / News Data:
{news_data}

Risk Result:
{risk_result}

Write the response in this format:

### Safety Summary
Briefly explain the overall situation.

### Current Risk Level
State the risk level and why.

### Main Concerns
List the main weather and public safety concerns.

### Areas or Situations to Avoid
Explain what the user should avoid.

### Recommended Action
Give practical next steps.

### Check-In Suggestion
Suggest whether the user should check on someone in the area.

### Emergency Reminder
Remind the user to call 911 or follow official emergency instructions during immediate danger.
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return fallback_summary(
            location=location,
            weather_data=weather_data,
            news_data=news_data,
            risk_result=risk_result,
            error=str(e)
        )


def fallback_summary(location, weather_data=None, news_data=None, risk_result=None, error=None):
    """
    Clean backup summary if Gemini is unavailable.
    """

    risk_level = "Unknown"
    risk_explanation = "Risk level could not be calculated."

    if risk_result:
        risk_level = risk_result.get("risk_level", "Unknown")
        risk_explanation = risk_result.get("explanation", risk_explanation)

    weather_alert = "Weather data was not checked."
    weather_severity = "Unknown"
    weather_description = "No weather details available."
    weather_action = "Monitor official weather updates."

    if weather_data:
        weather_alert = weather_data.get("alert_type", "No major weather alert")
        weather_severity = weather_data.get("severity", "Unknown")
        weather_description = weather_data.get("description", "No weather details available.")
        weather_action = weather_data.get("recommended_action", "Monitor official weather updates.")

    safety_report = "Public safety data was not checked."
    safety_severity = "Unknown"
    safety_headline = "No headline available."
    safety_description = "No public safety details available."
    safety_action = "Monitor official local updates."

    if news_data:
        safety_report = news_data.get("report_type", "No major public safety report")
        safety_severity = news_data.get("severity", "Unknown")
        safety_headline = news_data.get("headline", "No headline available.")
        safety_description = news_data.get("description", "No public safety details available.")
        safety_action = news_data.get("recommended_action", "Monitor official local updates.")

    if risk_level in ["High", "Critical"]:
        check_in = "Consider checking on anyone you know in or near this area."
    else:
        check_in = "A check-in is not strongly recommended based on the current demo risk level."

    summary = f"""
### Safety Summary

SafeWatch AI reviewed the available demo weather and public safety data for **{location}**.

### Current Risk Level

**{risk_level}**

{risk_explanation}

### Main Concerns

**Weather Concern:**  
- Alert: {weather_alert}  
- Severity: {weather_severity}  
- Details: {weather_description}

**Public Safety Concern:**  
- Report: {safety_report}  
- Severity: {safety_severity}  
- Headline: {safety_headline}  
- Details: {safety_description}

### Areas or Situations to Avoid

- Weather: {weather_action}
- Public Safety: {safety_action}

### Recommended Action

Monitor official weather alerts, local safety updates, and emergency instructions before traveling or making decisions in this area.

### Check-In Suggestion

{check_in}

### Emergency Reminder

SafeWatch AI is a decision-support tool, not an emergency service. For immediate danger, call 911 or follow official emergency instructions.
"""

    if error:
        summary += f"""

### System Note

Gemini was unavailable, so SafeWatch AI used the fallback summary.

"""

    return summary