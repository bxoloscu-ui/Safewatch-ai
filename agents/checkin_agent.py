import json
import os


def load_saved_locations(file_path="data/saved_locations.json"):
    """
    Load saved people/places from a JSON file.
    """

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        return []


def normalize_location(location):
    """
    Make location text easier to compare.
    """

    if not location:
        return ""

    return location.lower().replace(",", "").strip()


def locations_match(search_location, saved_location):
    """
    Check if the searched location matches a saved location.

    This is a simple MVP matching method.
    Later, this can be improved using latitude/longitude distance.
    """

    search = normalize_location(search_location)
    saved = normalize_location(saved_location)

    if search == saved:
        return True

    if search in saved:
        return True

    if saved in search:
        return True

    # City-level matching
    search_city = search.split()[0] if search else ""
    saved_city = saved.split()[0] if saved else ""

    if search_city and saved_city and search_city == saved_city:
        return True

    return False


def generate_checkin_recommendations(search_location, risk_result):
    """
    Generate check-in recommendations based on saved locations and risk level.
    """

    saved_locations = load_saved_locations()

    if not saved_locations:
        return {
            "recommendations": [],
            "message": "No saved locations were found."
        }

    risk_level = "Unknown"

    if risk_result:
        risk_level = risk_result.get("risk_level", "Unknown")

    matching_locations = []

    for item in saved_locations:
        saved_location = item.get("location", "")

        if locations_match(search_location, saved_location):
            matching_locations.append(item)

    recommendations = []

    for item in matching_locations:
        name = item.get("name", "Saved contact")
        location = item.get("location", "Unknown location")
        relationship = item.get("relationship", "Saved location")

        if risk_level in ["Critical", "High"]:
            recommendation = (
                f"Check on {name} ({relationship}) in {location}. "
                f"The current risk level for this area is {risk_level}."
            )
        elif risk_level == "Moderate":
            recommendation = (
                f"Consider checking on {name} ({relationship}) in {location}, "
                "especially if they may be traveling or outdoors."
            )
        else:
            recommendation = (
                f"{name} ({relationship}) is connected to this location, "
                "but no urgent check-in is recommended based on the current risk level."
            )

        recommendations.append(recommendation)

    if not recommendations:
        return {
            "recommendations": [],
            "message": "No saved people or places matched this searched location."
        }

    return {
        "recommendations": recommendations,
        "message": "Check-in recommendations were generated from saved locations."
    }