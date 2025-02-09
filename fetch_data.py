from firebase_config import db  # Import the database object from your config
import sys
import os

from llm_query import (
    get_recent_farming_news,
    summarize_all_crop_suggestions,
    return_all_crop_suggestions_concurrently,
)

# Example: Call a function from backfill.py


def fetch_data(user_id) -> dict:
    farming_info = db.child("users").child(user_id).child("farming_info").get()
    location = (
        db.child("users")
        .child(user_id)
        .child("user_info")
        .child("location")
        .get()
        .val()
    )

    result = []

    if farming_info.each():  # Check if data exists
        for crop in farming_info.each():
            crop_data = crop.val()
            formatted_crop_data = {
                "crop_name": crop.key(),
                "current_irrigation_technique": (
                    crop_data["Irrigation"][0] if crop_data["Irrigation"] else None
                ),
                "current_soil_technique": (
                    crop_data["Soil"][0] if crop_data["Soil"] else None
                ),
                "location": location,
            }
            result.append(formatted_crop_data)

    return result


def ai_recommendation(user_id):
    user_data = fetch_data(user_id)
    all_crop_suggestions = return_all_crop_suggestions_concurrently(user_data)
    local_news = get_recent_farming_news(user_data[0]["location"])
    summary = summarize_all_crop_suggestions(
        all_crop_suggestions, location_news=local_news
    )
    return summary


user_data = fetch_data("-OIe4to_pRIboKtlZDzv")
for thing in user_data:
    print(thing)
