# SafeWatch AI

SafeWatch AI is a location-aware news and safety agent designed as an "Agent for Good." It helps users check weather alerts, public safety reports, and local safety risks for selected areas.

## Project Purpose

People often receive safety information from scattered sources such as weather services, local news, emergency alerts, and public safety reports. SafeWatch AI brings these sources together and converts them into a clear safety summary, risk level, map view, and check-in recommendation.

## What the Agent Does

SafeWatch AI can:

- Check real weather alerts from the National Weather Service API
- Search recent public safety news using GDELT
- Classify safety risk as Low, Moderate, High, or Critical
- Generate a safety summary using Gemini when available
- Fall back to a built-in response agent when Gemini quota is unavailable
- Show a safety map for supported locations
- Recommend who or what location the user may need to check on

## Main Features

- Location-based safety search
- Weather alert monitoring
- Public safety news search
- Risk scoring agent
- Safety summary agent
- Saved places/check-in recommendation
- Interactive safety map
- Emergency disclaimer and safety guardrails

## Tools and Technologies

- Python
- Streamlit
- National Weather Service API
- GDELT API
- Gemini API
- Folium
- Streamlit-Folium
- JSON-based saved locations

## Project Structure

```text
SafeWatch-ai/
├── app.py
├── requirements.txt
├── README.md
├── agents/
│   ├── risk_agent.py
│   ├── response_agent.py
│   └── checkin_agent.py
├── tools/
│   ├── weather_tool.py
│   ├── news_tool.py
│   └── map_tool.py
├── data/
│   └── saved_locations.json
└── screenshots/


## How to Run Locally

1. Clone the repository:

```bash
git clone https://github.com/bxoloscu-ui/SafeWatch-ai.git
cd SafeWatch-ai

2. Create a virtual env and activate it:

python3 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Create a .env file in the main project folder:

GEMINI_API_KEY=your_gemini_api_key_here

5. Run the app

python -m streamlit run app.py

##Supported MVP Locations

The current MVP supports map lookup for:

* Stillwater, OK
* Tulsa, OK
* Oklahoma City, OK
* Dallas, TX

##Safety and Ethical Guardrails

SafeWatch AI is a decision-support tool, not an emergency service. It does not replace 911, official emergency alerts, police departments, fire departments, or local government instructions.

The agent is designed to:

* Avoid inventing incidents
* Show source information when available
* Use cautious language for unverified news
* Recommend official sources for confirmation
* Avoid labeling neighborhoods or communities as inherently dangerous
* Use saved places only from user-provided data

##Limitations

* GDELT news results may sometimes be broad or imperfect.
* Gemini may be unavailable due to quota limits, so the app includes a fallback response agent.
* The current map uses a small built-in location list for the MVP.
* Public safety news is not the same as official emergency communication.
* The app should not be used as the only source for urgent safety decisions.

##Future Improvements

* Add more supported cities
* Add real geocoding for any address
* Add live emergency feeds from official city/county sources
* Add SMS or email alerts
* Add route safety analysis
* Improve news filtering and source reliability scoring
* Add user authentication for saved places
* Deploy the app online

Emergency Reminder

For immediate danger, call 911 or follow official emergency instructions.