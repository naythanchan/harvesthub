import streamlit as st
import os
from firebase_config import db
import pandas as pd
import requests
from map import display_map
from fetch_data import ai_recommendation


def dashboard():
    user_info = st.session_state.user_info
    localId = st.session_state.localId

    name = user_info.get("name")
    location = user_info.get("location")

    county, state = location.split(", ")

    st.set_page_config(layout="wide")
    st.write(f"👤 {name}\n\n📍 {location}")

    API_KEY = "foo_bar"

    def get_weather(location, api_key):
        # Weatherstack API endpoint
        url = "http://api.weatherstack.com/current"

        # API parameters
        params = {
            "access_key": api_key,
            "query": location,  # Location name
        }

        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if "current" in data:
                # Extract weather details
                temperature = data["current"]["temperature"]  # Temperature in Celsius
                humidity = data["current"]["humidity"]  # Humidity in percentage
                rainfall = data["current"].get(
                    "precip", 0
                )  # Rainfall in mm (default 0)
                return temperature, humidity, rainfall
            else:
                # Handle location not found or invalid response
                return None, None, None
        else:
            # Handle API errors
            return None, None, None

    # Local weather data
    # temperature, humidity, rainfall = get_weather(location, API_KEY)
    temperature, humidity, rainfall = -5, 61, 5

    # Custom CSS for better spacing and alignment
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #f0f0f0;
                padding: 20px;
            }
            .title-text {
                color: #44944c;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
            }
            .dropdown-label, .input-label {
                color: #4a4a4a;
            }
            [data-testid="stSidebar"] {
                background-color: #C2DB9E !important;
            }
            .full-width {
                width: 100%;
            }
            .sidebar-image {
                text-align: center;
            }
            .stSelectbox, .stMultiselect {
                font-size: 14px !important;
                max-width: 200px !important;
                padding: 2px !important;
                margin: 5px 0px !important;
                background-color: #C2DB9E !important; /* Light green background */
                color: #44944c !important; /* Green text */
            }
            .sidebar-image img {
                max-width: 120px;
                display: block;
                margin: 0 auto;
            }
            .info-card {
                background: white;
                padding: 9px 15px; /* Add dynamic padding: 20px top/bottom, 15px left/right */
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                text-align: center; /* Ensure text remains horizontally centered */
                min-width: 160px; /* Minimum width for the card */
                display: flex;
                flex-direction: column;
                justify-content: center; /* Center content vertically */
                align-items: center; /* Center content horizontally */
            }
            .info-card .top-text {
                align-self: center; /* Ensure top text is horizontally centered */
                font-size: 18px; /* Heading font size */
                font-weight: bold;
                margin-bottom: 0px; /* Space below top text */
            }
        .info-row {
            margin-bottom: 20px; /* Add space below the row of boxes */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar for user input
    with st.sidebar:
        st.markdown("<div class='sidebar-image'>", unsafe_allow_html=True)
        # st.image("frontend/logo.png", width=120)
        st.markdown("</div>", unsafe_allow_html=True)
        st.title("Settings")

        # Crop selection
        st.subheader("Which crops are you growing?")
        crops = ["Rice", "Coffee Beans", "Tea Leaves", "Corn"]
        selected_crops = st.multiselect(
            "Select your crops", crops, key="selected_crops"
        )

        # Techniques
        irrigation_options = [
            "None",
            "Drip Irrigation",
            "Flood Irrigation",
            "Rainwater Harvesting",
            "Subsurface Irrigation",
            "Sprinkler Systems",
        ]
        soil_options = [
            "None",
            "Cover Cropping",
            "Mulching",
            "Composting & Organic Amendments",
            "No-Till Farming",
            "Crop Rotation",
        ]

        crop_data = {}

        if selected_crops:
            st.subheader("Choose which farming techniques you use")
            for crop in selected_crops:
                st.markdown(f"**{crop}**")

                irrigation_choice = st.multiselect(
                    "Irrigation Technique", irrigation_options, key=f"irrigation_{crop}"
                )
                soil_choice = st.multiselect(
                    "Soil Management Technique", soil_options, key=f"soil_{crop}"
                )

                # Store data
                crop_data[crop] = {"Irrigation": irrigation_choice, "Soil": soil_choice}

        # Save button
        if st.button("Save Techniques"):
            db.child("users").child(localId).child("farming_info").set(crop_data)
            st.success("Techniques saved successfully!")

    # Main Layout
    st.markdown(
        f"<div class='title-text'>Weather Data For {county}</div>",
        unsafe_allow_html=True,
    )

    # Information Display Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class='info-card'>
                <div class='top-text'>{temperature}°C / {(temperature * 9/5) + 32}°F</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class='info-card'>
                <div class='top-text'>{humidity}% Humidity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class='info-card'>
                <div class='top-text'>{rainfall}% Chance of Rain</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='info-row'>", unsafe_allow_html=True)

    give_recommendation = st.button("Give recommendation")
    farm_info = db.child("users").child("farm_info").get()

    if give_recommendation:
        st.write(ai_recommendation(localId))

    # Map Section
    st.subheader("See What Farmers Near You Are Doing!")
    display_map(state, county)
    st.subheader("Recent Changes in Your Community 😊")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(
            """
    <div class='info-card'>
        <div class='top-text'>
            Lauren Scott switched from Sprinkler Systems to No-Till Farming
    </div>
    """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
            <div class='info-card'>
                <div class='top-text'>Brian Smith switched from Drip Irrigation to Subsurface Irrigation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f"""
            <div class='info-card'>
                <div class='top-text'>Linda Robinaon switched from Rainwater Harvesting to Cover Cropping</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
