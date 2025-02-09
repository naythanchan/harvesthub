# at the end, set the default to satelite view (to save costs)
# to-do: replace local text with frontent boxes from dashboard,py.
#   communicating with farmers in the area and speaking with them about what they are doing , make it interactive
import streamlit as st
import requests
from firebase_config import db
import random

# Google Maps API Key (Replace with your key)
GOOGLE_MAPS_API_KEY = "AIzaSyCfh5Da3d6Mx4_8uLxjHTO9CdPKXlkqmaI"


# # Location, Name, Crop, Techinque
# # User input for location search
# state = st.text_input("Enter a State:", "New Jersey")
# county = st.text_input("Enter Your County: ", "Passaic")  # nyc default


# get data from input city
def get_lat_lng(state, county):
    address = f"{county}, {state}"
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(geocode_url).json()

    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        # catch error
        return 40.7128, -74.0060


# Function to Fetch Farmers from Firebase
def fetch_farmers(state, county, lat, lng):
    farmers = db.child("users").get()
    farmer_list = []

    if farmers.each():
        for farmer in farmers.each():
            data = farmer.val()

            # Extract farming info if present
            farming_info = data.get("farming_info", {})
            user_info = data.get("user_info", {})

            for crop, techniques in farming_info.items():
                irrigation = techniques.get("Irrigation", ["Still Deciding"])
                farmer_entry = {
                    "state": state,
                    "county": county,
                    "name": user_info.get("name", data.get("name", "Jane Doe")),
                    "crop": crop,  # Crop name
                    "irrigation": ", ".join(
                        techniques.get("Irrigation", ["Still Deciding"])
                    ),
                    "soil": ", ".join(techniques.get("Soil", ["Still Deciding"])),
                    "lat": lat,  # Latitude
                    "lng": lng,  # Longitude
                }
                farmer_list.append(farmer_entry)
    return farmer_list


def display_map(state, county):
    lat, lng = get_lat_lng(state, county)
    farmers_data = fetch_farmers(state, county, lat, lng)

    # markers for farmers generation
    markers_js = ""

    for i, farmer in enumerate(farmers_data):

        markers_js += f"""
            var infoWindow{i} = new google.maps.InfoWindow({{
                content: "<div style='font-size:14px; font-weight:bold;'>👤 Name: {farmer['name']}<br>📍 Location: {farmer['county']}, {farmer['state']}<br>🌾 Crops: {farmer['crop']}<br>💧 Irrigation: {farmer['irrigation']}<br>🪴 Soil: {farmer['soil']}</div>"
            }});
            var marker{i} = new google.maps.Marker({{
                position: {{ lat: {farmer['lat'] + random.uniform(-0.1, 0.1)}, lng: {farmer['lng'] + random.uniform(-0.1, 0.1)} }},
                map: map,
                title: "Farmer {farmer['name']}",
                icon: {{
                    url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                }}
            }});
            marker{i}.addListener("click", function() {{
                infoWindow{i}.open(map, marker{i});
            }});
        """

    # HTML Template for Google Maps
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
        <script>
            function initMap() {{
                var map = new google.maps.Map(document.getElementById('map'), {{
                    center: {{lat: {lat}, lng: {lng} }},
                    zoom: 12,
                    mapTypeId: "satellite"
                }});
                {markers_js}
            }}
        </script>
    </head>
    <body>
        <div id="map" style="width: 100%; height: 500px;"></div>
    </body>
    </html>
    """

    st.components.v1.html(map_html, height=500)
