import requests


# Simple built-in city lookup for MVP testing.
# This avoids needing a paid geocoding API right now.
KNOWN_LOCATIONS = {
    "stillwater": {
        "display_name": "Stillwater, OK",
        "lat": 36.1156,
        "lon": -97.0584
    },
    "stillwater, ok": {
        "display_name": "Stillwater, OK",
        "lat": 36.1156,
        "lon": -97.0584
    },
    "tulsa": {
        "display_name": "Tulsa, OK",
        "lat": 36.1540,
        "lon": -95.9928
    },
    "tulsa, ok": {
        "display_name": "Tulsa, OK",
        "lat": 36.1540,
        "lon": -95.9928
    },
    "oklahoma city": {
        "display_name": "Oklahoma City, OK",
        "lat": 35.4676,
        "lon": -97.5164
    },
    "oklahoma city, ok": {
        "display_name": "Oklahoma City, OK",
        "lat": 35.4676,
        "lon": -97.5164
    },
    "okc": {
        "display_name": "Oklahoma City, OK",
        "lat": 35.4676,
        "lon": -97.5164
    },
    "dallas": {
        "display_name": "Dallas, TX",
        "lat": 32.7767,
        "lon": -96.7970
    },
    "dallas, tx": {
        "display_name": "Dallas, TX",
        "lat": 32.7767,
        "lon": -96.7970
    }
}


def geocode_location(location):
    """
    Convert a location string into latitude and longitude.

    For this MVP, we use a small built-in lookup table.
    Later, we can replace this with a real geocoding API.
    """

    if not location:
        return None

    location_key = location.strip().lower()

    if location_key in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[location_key]

    # Try partial matching
    for key, value in KNOWN_LOCATIONS.items():
        if key in location_key:
            return value

    return None


def map_nws_severity_to_risk(severity, event):
    """
    Convert NWS severity/event text into our SafeWatch AI risk level.
    """

    severity_text = str(severity).lower()
    event_text = str(event).lower()

    critical_keywords = [
        "tornado warning",
        "flash flood warning",
        "extreme wind warning",
        "evacuation",
        "civil emergency"
    ]

    high_keywords = [
        "tornado watch",
        "severe thunderstorm warning",
        "flood warning",
        "winter storm warning",
        "ice storm warning",
        "excessive heat warning",
        "fire warning",
        "red flag warning"
    ]

    moderate_keywords = [
        "severe thunderstorm watch",
        "flood watch",
        "wind advisory",
        "heat advisory",
        "winter weather advisory",
        "dense fog advisory",
        "special weather statement"
    ]

    for keyword in critical_keywords:
        if keyword in event_text:
            return "Critical"

    for keyword in high_keywords:
        if keyword in event_text:
            return "High"

    for keyword in moderate_keywords:
        if keyword in event_text:
            return "Moderate"

    if "extreme" in severity_text:
        return "Critical"
    elif "severe" in severity_text:
        return "High"
    elif "moderate" in severity_text:
        return "Moderate"
    elif "minor" in severity_text:
        return "Low"

    return "Low"


def get_weather_alerts(location):
    """
    Get active weather alerts from the National Weather Service API.

    Input:
        location: string, e.g. "Tulsa, OK"

    Output:
        dictionary with the same fields used by the rest of the app
    """

    coordinates = geocode_location(location)

    if coordinates is None:
        return {
            "location": location,
            "source": "National Weather Service API",
            "alert_type": "Location Not Supported Yet",
            "severity": "Low",
            "description": (
                "This MVP currently supports Stillwater, Tulsa, Oklahoma City, and Dallas. "
                "No coordinates were found for the entered location."
            ),
            "recommended_action": "Try Stillwater, OK; Tulsa, OK; Oklahoma City, OK; or Dallas, TX.",
            "url": "https://api.weather.gov"
        }

    lat = coordinates["lat"]
    lon = coordinates["lon"]
    display_name = coordinates["display_name"]

    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"

    headers = {
        "User-Agent": "SafeWatchAI/1.0 (student project)",
        "Accept": "application/geo+json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        alerts = data.get("features", [])

        if not alerts:
            return {
                "location": display_name,
                "source": "National Weather Service API",
                "alert_type": "No Active Weather Alert",
                "severity": "Low",
                "description": "No active National Weather Service weather alerts were found for this location.",
                "recommended_action": "Continue normal activity while monitoring official weather updates.",
                "url": url
            }

        # Select the first active alert.
        # Later, we can sort by severity and urgency.
        alert = alerts[0]
        properties = alert.get("properties", {})

        event = properties.get("event", "Weather Alert")
        nws_severity = properties.get("severity", "Unknown")
        headline = properties.get("headline", "")
        description = properties.get("description", "")
        instruction = properties.get("instruction", "")
        effective = properties.get("effective", "Unknown")
        expires = properties.get("expires", "Unknown")

        safewatch_severity = map_nws_severity_to_risk(nws_severity, event)

        if instruction:
            recommended_action = instruction
        else:
            recommended_action = "Monitor official National Weather Service updates and follow local emergency guidance."

        full_description = description

        if headline:
            full_description = f"{headline}\n\n{description}"

        full_description += f"\n\nEffective: {effective}\nExpires: {expires}"

        return {
            "location": display_name,
            "source": "National Weather Service API",
            "alert_type": event,
            "severity": safewatch_severity,
            "description": full_description,
            "recommended_action": recommended_action,
            "url": url
        }

    except requests.exceptions.RequestException as error:
        return {
            "location": display_name,
            "source": "National Weather Service API",
            "alert_type": "Weather API Error",
            "severity": "Low",
            "description": f"SafeWatch AI could not retrieve live weather alerts. Error: {error}",
            "recommended_action": "Check weather.gov or your local weather authority directly.",
            "url": url
        }