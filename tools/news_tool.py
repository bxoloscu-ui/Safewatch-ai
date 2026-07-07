import requests
from datetime import datetime, timedelta
from urllib.parse import quote


SAFETY_KEYWORDS = [
    "shooting",
    "police activity",
    "assault",
    "robbery",
    "fire",
    "explosion",
    "evacuation",
    "road closure",
    "hazmat",
    "protest",
    "riot",
    "flooding",
    "storm damage",
    "emergency"
]


def classify_news_category(title, description):
    """
    Classify the safety category based on article title and description.
    """

    text = f"{title} {description}".lower()

    if any(word in text for word in ["shooting", "assault", "robbery", "police", "homicide", "stabbing"]):
        return "Public Safety"

    if any(word in text for word in ["fire", "explosion", "smoke"]):
        return "Fire / Emergency"

    if any(word in text for word in ["road closure", "crash", "traffic", "accident", "highway"]):
        return "Road / Traffic Safety"

    if any(word in text for word in ["flood", "storm", "tornado", "weather", "hail", "wind"]):
        return "Weather-Related Safety"

    if any(word in text for word in ["evacuation", "hazmat", "chemical", "gas leak"]):
        return "Emergency / Hazard"

    return "General Safety"


def estimate_news_severity(title, description, category):
    """
    Estimate severity from safety keywords.
    """

    text = f"{title} {description}".lower()

    critical_terms = [
        "active shooter",
        "mass shooting",
        "evacuation order",
        "tornado warning",
        "flash flood emergency",
        "explosion",
        "hazmat"
    ]

    high_terms = [
        "shooting",
        "homicide",
        "stabbing",
        "large fire",
        "police activity",
        "flash flood",
        "road closed",
        "evacuation",
        "dangerous"
    ]

    moderate_terms = [
        "crash",
        "traffic delay",
        "road closure",
        "investigation",
        "storm damage",
        "firefighters responded",
        "police responded"
    ]

    for term in critical_terms:
        if term in text:
            return "Critical"

    for term in high_terms:
        if term in text:
            return "High"

    for term in moderate_terms:
        if term in text:
            return "Moderate"

    if category in ["Public Safety", "Fire / Emergency", "Emergency / Hazard"]:
        return "Moderate"

    return "Low"


def build_gdelt_query(location):
    """
    Build a GDELT search query using location and safety keywords.
    """

    keyword_query = " OR ".join([f'"{keyword}"' for keyword in SAFETY_KEYWORDS])
    query = f'"{location}" ({keyword_query})'

    return query


def get_safety_news(location):
    """
    Search recent safety-related news using the GDELT API.

    Input:
        location: string, e.g. "Tulsa, OK"

    Output:
        dictionary with same structure used by the app
    """

    if not location or location.strip() == "":
        return {
            "location": location,
            "source": "GDELT API",
            "report_type": "No Location Provided",
            "category": "General Safety",
            "severity": "Low",
            "headline": "No location was entered",
            "description": "SafeWatch AI could not search safety news because no location was provided.",
            "recommended_action": "Enter a city and state, such as Tulsa, OK.",
            "url": "https://www.gdeltproject.org/"
        }

    query = build_gdelt_query(location)

    # Search articles from the last 7 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    start_datetime = start_time.strftime("%Y%m%d%H%M%S")
    end_datetime = end_time.strftime("%Y%m%d%H%M%S")

    encoded_query = quote(query)

    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={encoded_query}"
        "&mode=artlist"
        "&format=json"
        "&maxrecords=10"
        "&sort=datedesc"
        f"&startdatetime={start_datetime}"
        f"&enddatetime={end_datetime}"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return {
                "location": location,
                "source": "GDELT API",
                "report_type": "No Recent Safety News Found",
                "category": "General Safety",
                "severity": "Low",
                "headline": "No recent safety-related news found",
                "description": (
                    "No recent safety-related news articles were found for this location "
                    "using the current GDELT search query."
                ),
                "recommended_action": "Continue monitoring official local alerts and trusted local news sources.",
                "url": "https://www.gdeltproject.org/"
            }

        # Use the most recent article
        article = articles[0]

        title = article.get("title", "No title available")
        article_url = article.get("url", "https://www.gdeltproject.org/")
        source_name = article.get("sourceCommonName", "GDELT News Source")
        date_seen = article.get("seendate", "Unknown date")
        domain = article.get("domain", source_name)

        description = (
            f"Recent article found from {source_name}. "
            f"Date seen: {date_seen}. "
            f"Domain: {domain}."
        )

        category = classify_news_category(title, description)
        severity = estimate_news_severity(title, description, category)

        return {
            "location": location,
            "source": f"GDELT API / {source_name}",
            "report_type": category,
            "category": category,
            "severity": severity,
            "headline": title,
            "description": description,
            "recommended_action": (
                "Review the linked article and verify with official local sources before making safety decisions."
            ),
            "url": article_url
        }

    except requests.exceptions.RequestException as error:
        return {
            "location": location,
            "source": "GDELT API",
            "report_type": "News API Error",
            "category": "General Safety",
            "severity": "Low",
            "headline": "Could not retrieve safety news",
            "description": f"SafeWatch AI could not retrieve recent news from GDELT. Error: {error}",
            "recommended_action": "Check trusted local news and official city/county alerts directly.",
            "url": "https://www.gdeltproject.org/"
        }

    except ValueError as error:
        return {
            "location": location,
            "source": "GDELT API",
            "report_type": "News Data Error",
            "category": "General Safety",
            "severity": "Low",
            "headline": "Could not parse safety news response",
            "description": f"SafeWatch AI received an unreadable response from GDELT. Error: {error}",
            "recommended_action": "Try again later or check trusted local sources directly.",
            "url": "https://www.gdeltproject.org/"
        }