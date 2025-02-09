import random
from faker import Faker
from firebase_config import db

fake = Faker()


def generate_fake_users(county, state, num_users):
    crops = ["Rice", "Coffee Beans", "Tea Leaves", "Corn"]
    irrigation_options = [
        "Drip Irrigation",
        "Flood Irrigation",
        "Rainwater Harvesting",
        "Subsurface Irrigation",
        "Sprinkler Systems",
    ]
    soil_options = [
        "Cover Cropping",
        "Mulching",
        "Composting & Organic Amendments",
        "No-Till Farming",
        "Crop Rotation",
    ]

    for _ in range(num_users):
        name = fake.name()
        # location = f"{fake.city()}, {fake.state()}"
        # county, state = location.split(", ")

        farming_info = {}
        selected_crops = random.sample(crops, k=random.randint(1, len(crops)))

        for crop in selected_crops:
            farming_info[crop] = {
                "Irrigation": random.sample(irrigation_options, k=random.randint(1, 3)),
                "Soil": random.sample(soil_options, k=random.randint(1, 3)),
            }

        user_info = {
            "email": "fake@gmail.com",
            "location": f"{county}, {state}",
            "name": name,
        }

        # Push to Firebase
        user_data = {
            "user_info": user_info,
            "farming_info": farming_info,
        }

        db.child("users").push(user_data)
        print(f"Generated user: {user_data}")


# Call the function to generate fake users
generate_fake_users("Beaver Creek", "Minnesota", 5)
