# pyrefly: ignore [missing-import]
import folium


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
    },
    "oklahoma state university": {
        "display_name": "Oklahoma State University, Stillwater, OK",
        "lat": 36.1270,
        "lon": -97.0737
    },
    "oklahoma state university, stillwater, ok": {
        "display_name": "Oklahoma State University, Stillwater, OK",
        "lat": 36.1270,
        "lon": -97.0737
    }
}


def geocode_for_map(location):
    """
    Convert location text to map coordinates using a simple MVP lookup table.
    """

    if not location:
        return None

    location_key = location.strip().lower()

    if location_key in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[location_key]

    for key, value in KNOWN_LOCATIONS.items():
        if key in location_key:
            return value

    return None


def risk_to_marker_color(risk_level):
    """
    Convert risk level to a folium marker color.
    """

    if not risk_level:
        return "blue"

    risk_level = risk_level.lower()

    if risk_level == "critical":
        return "red"
    elif risk_level == "high":
        return "orange"
    elif risk_level == "moderate":
        return "cadetblue"
    elif risk_level == "low":
        return "green"
    else:
        return "blue"


def create_safety_map(search_location, risk_result=None, saved_locations=None):
    """
    Create a map showing the searched location and matching saved places.
    """

    coordinates = geocode_for_map(search_location)

    if coordinates is None:
        return None

    risk_level = "Unknown"

    if risk_result:
        risk_level = risk_result.get("risk_level", "Unknown")

    marker_color = risk_to_marker_color(risk_level)

    safety_map = folium.Map(
        location=[coordinates["lat"], coordinates["lon"]],
        zoom_start=11
    )

    folium.Marker(
        location=[coordinates["lat"], coordinates["lon"]],
        popup=f"Searched Location: {coordinates['display_name']} | Risk: {risk_level}",
        tooltip=f"{coordinates['display_name']} - {risk_level}",
        icon=folium.Icon(color=marker_color, icon="info-sign")
    ).add_to(safety_map)

    # Add an approximate risk radius around searched location
    radius_color = "green"

    if risk_level == "Critical":
        radius_color = "red"
    elif risk_level == "High":
        radius_color = "orange"
    elif risk_level == "Moderate":
        radius_color = "blue"

    folium.Circle(
        location=[coordinates["lat"], coordinates["lon"]],
        radius=5000,
        popup=f"Approximate safety awareness zone for {coordinates['display_name']}",
        color=radius_color,
        fill=True,
        fill_opacity=0.15
    ).add_to(safety_map)

    if saved_locations:
        for item in saved_locations:
            saved_name = item.get("name", "Saved Location")
            saved_location = item.get("location", "")
            relationship = item.get("relationship", "Saved place")

            saved_coordinates = geocode_for_map(saved_location)

            if saved_coordinates:
                folium.Marker(
                    location=[saved_coordinates["lat"], saved_coordinates["lon"]],
                    popup=f"{saved_name} ({relationship}) - {saved_coordinates['display_name']}",
                    tooltip=f"{saved_name}: {saved_coordinates['display_name']}",
                    icon=folium.Icon(color="purple", icon="home")
                ).add_to(safety_map)

    return safety_map