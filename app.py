import streamlit as st
from streamlit_folium import st_folium

from tools.weather_tool import get_weather_alerts
from tools.news_tool import get_safety_news
from tools.map_tool import create_safety_map

from agents.risk_agent import calculate_risk_level
from agents.response_agent import generate_safety_summary
from agents.checkin_agent import generate_checkin_recommendations, load_saved_locations


st.set_page_config(
    page_title="SafeWatch AI",
    page_icon="🛡️",
    layout="wide"
)

# -----------------------------
# Session State Setup
# -----------------------------

if "safety_checked" not in st.session_state:
    st.session_state.safety_checked = False

if "last_location" not in st.session_state:
    st.session_state.last_location = ""

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if "news_data" not in st.session_state:
    st.session_state.news_data = None

if "risk_result" not in st.session_state:
    st.session_state.risk_result = None

if "safety_summary" not in st.session_state:
    st.session_state.safety_summary = ""

if "checkin_result" not in st.session_state:
    st.session_state.checkin_result = None


# -----------------------------
# Header
# -----------------------------

st.title("🛡️ SafeWatch AI")
st.subheader("Location-Aware News and Safety Agent")

st.write(
    "SafeWatch AI helps users check weather alerts, public safety reports, "
    "and local safety risks for selected areas."
)


# -----------------------------
# Location Search Section
# -----------------------------

st.markdown("## Location Search")

location = st.text_input(
    "Enter a location",
    value=st.session_state.last_location,
    placeholder="Example: Stillwater, OK"
)

st.markdown("### Select safety categories")

col1, col2, col3 = st.columns(3)

with col1:
    category_weather = st.checkbox("Weather alerts", value=True)

with col2:
    category_public_safety = st.checkbox("Public safety reports", value=True)

with col3:
    category_emergency = st.checkbox("Emergency / road / fire reports", value=True)


# -----------------------------
# Button Logic
# -----------------------------

if st.button("Check Safety"):

    if location.strip() == "":
        st.warning("Please enter a location first.")
        st.stop()

    st.session_state.safety_checked = True
    st.session_state.last_location = location

    weather_data = None
    news_data = None

    with st.spinner("Checking safety information..."):

        if category_weather:
            weather_data = get_weather_alerts(location)

        if category_public_safety or category_emergency:
            news_data = get_safety_news(location)

        risk_result = calculate_risk_level(weather_data, news_data)

        checkin_result = generate_checkin_recommendations(
            search_location=location,
            risk_result=risk_result
        )

        safety_summary = generate_safety_summary(
            location=location,
            weather_data=weather_data,
            news_data=news_data,
            risk_result=risk_result
        )

    st.session_state.weather_data = weather_data
    st.session_state.news_data = news_data
    st.session_state.risk_result = risk_result
    st.session_state.checkin_result = checkin_result
    st.session_state.safety_summary = safety_summary


# -----------------------------
# Display Results
# -----------------------------

if st.session_state.safety_checked:

    location = st.session_state.last_location
    weather_data = st.session_state.weather_data
    news_data = st.session_state.news_data
    risk_result = st.session_state.risk_result
    checkin_result = st.session_state.checkin_result
    safety_summary = st.session_state.safety_summary

    st.success(f"Safety information loaded for {location}.")

    # -----------------------------
    # Weather Section
    # -----------------------------

    if weather_data:
        st.markdown("## Weather Alert")
        st.write(f"**Location:** {weather_data.get('location', 'Unknown')}")
        st.write(f"**Source:** {weather_data.get('source', 'Unknown')}")
        st.write(f"**Alert Type:** {weather_data.get('alert_type', 'Unknown')}")
        st.write(f"**Severity:** {weather_data.get('severity', 'Unknown')}")
        st.write(f"**Description:** {weather_data.get('description', 'No description available.')}")
        st.write(f"**Recommended Action:** {weather_data.get('recommended_action', 'Monitor official updates.')}")

        if "url" in weather_data:
            st.write(f"**Source Link:** {weather_data['url']}")

    # -----------------------------
    # News Section
    # -----------------------------

    if news_data:
        st.markdown("## Public Safety / News Report")
        st.write(f"**Location:** {news_data.get('location', 'Unknown')}")
        st.write(f"**Source:** {news_data.get('source', 'Unknown')}")
        st.write(f"**Report Type:** {news_data.get('report_type', 'Unknown')}")
        st.write(f"**Category:** {news_data.get('category', 'Unknown')}")
        st.write(f"**Severity:** {news_data.get('severity', 'Unknown')}")
        st.write(f"**Headline:** {news_data.get('headline', 'No headline available.')}")
        st.write(f"**Description:** {news_data.get('description', 'No description available.')}")
        st.write(f"**Recommended Action:** {news_data.get('recommended_action', 'Monitor official updates.')}")

        if "url" in news_data:
            st.write(f"**Source Link:** {news_data['url']}")

    # -----------------------------
    # Risk Section
    # -----------------------------

    if risk_result:
        st.markdown("## Current Risk Level")

        risk_level = risk_result.get("risk_level", "Unknown")

        if risk_level == "Critical":
            st.error(f"Risk Level: {risk_level}")
        elif risk_level == "High":
            st.warning(f"Risk Level: {risk_level}")
        elif risk_level == "Moderate":
            st.warning(f"Risk Level: {risk_level}")
        else:
            st.success(f"Risk Level: {risk_level}")

        st.write(f"**Risk Score:** {risk_result.get('final_score', 'Unknown')}")
        st.write(f"**Explanation:** {risk_result.get('explanation', 'No explanation available.')}")

        st.markdown("### Risk Factors")
        for factor in risk_result.get("risk_factors", []):
            st.write(f"- {factor}")

    # -----------------------------
    # Map Section
    # -----------------------------

    st.markdown("## Safety Map")

    saved_locations = load_saved_locations()

    safety_map = create_safety_map(
        search_location=location,
        risk_result=risk_result,
        saved_locations=saved_locations
    )

    if safety_map:
        st_folium(
            safety_map,
            width=900,
            height=500,
            key="safety_map"
        )
    else:
        st.info(
            "Map is not available for this location yet. "
            "Try Stillwater, OK; Tulsa, OK; Oklahoma City, OK; or Dallas, TX."
        )

    # -----------------------------
    # Check-In Recommendations
    # -----------------------------

    st.markdown("## Check-In Recommendations")

    if checkin_result:
        st.write(checkin_result.get("message", "No message available."))

        if checkin_result.get("recommendations"):
            for recommendation in checkin_result["recommendations"]:
                st.write(f"- {recommendation}")
        else:
            st.info("No check-in recommendation was generated for this location.")

    # -----------------------------
    # Safety Summary
    # -----------------------------

    st.markdown("## Safety Summary")
    st.markdown(safety_summary)


# -----------------------------
# Footer
# -----------------------------

st.markdown("---")
st.caption(
    "SafeWatch AI is a decision-support tool, not an emergency service. "
    "For immediate danger, call 911 or follow official emergency instructions."
)