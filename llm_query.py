import aiohttp  # Library for asynchronous HTTP requests
import asyncio  # Library for handling asynchronous operations
import re  # Regular expressions for text processing
import requests  # Library for synchronous HTTP requests
import urllib.parse
from datetime import datetime, timedelta

# API key for the GROQ AI model (ensure this is stored securely in production)
GROQ_KEY = "foo_bar"
# Base URL for the GROQ AI API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# System prompt defining the model's behavior and analytical focus
SYSTEM_PROMPT = """
You are an advanced agricultural reasoning model that evaluates and compares farming techniques based on climate conditions, sustainability, efficiency, and recent climate change impacts.
Your task is to analyze a farmer’s entire crop management approach, specifically focusing on:

Soil Management Techniques
Irrigation Techniques
Climate Adaptation & Sustainability
Economic Feasibility & Environmental Impact

You must:
- Compare the current techniques the farmer uses with all available alternative techniques.
- Assess the historical and projected climate trends in the given location.
- Evaluate the resilience and efficiency of each technique in the context of recent climate change events.
- Identify the most climate-adaptive, sustainable, and economically viable approach.
- Provide a structured recommendation based on scientific, environmental, and economic reasoning.
"""

# Prompt for summarizing recommendations into an actionable decision-making format
SUMMARY_PROMPT = """
You are an agricultural decision-making assistant. Your task is to generate a **concise, detailed, and insightful summary** for a specific farmer that should adjust or maintain their current crop management techniques, considering the local climate and development conditions, and news in the area.

### **Instructions**  
- Clearly state whether each crop’s techniques should be **changed** or **kept the same**.  
- Provide a **brief yet insightful explanation** for the decision.  
- Explain why the change must be made because of dangerous factors based on past data.
- Include specific local news that could help with disaster risk assessement. Make sure to not make broad generalizations, but specific, actionalble insights.
- Use an **optimistic and forward-thinking tone** when talking to them, emphasizing improvements or strengths.  
- Keep responses **short, specific, and actionable**.

### **Example Output**  
- **Corn**: **Change** – A great opportunity to improve efficiency! Flood irrigation isn’t ideal for Boise, Idaho’s climate. Switching to drip irrigation will maximize water use and boost crop resilience.  
- **Tea Leaves**: **Keep** – Excellent choice! The current mulching techniques are well-suited for preventing soil erosion and retaining moisture, ensuring sustainable growth.  

"""

import time  # For tracking execution time


def print_status(message):
    """Prints an interactive status update with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def track_time(func):
    """Decorator to track and print execution time of functions."""

    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        print_status(f"Starting {func.__name__}...")
        result = await func(*args, **kwargs)
        end_time = time.time()
        print_status(
            f"Finished {func.__name__} in {end_time - start_time:.2f} seconds."
        )
        return result

    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        print_status(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        end_time = time.time()
        print_status(
            f"Finished {func.__name__} in {end_time - start_time:.2f} seconds."
        )
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


# Asynchronous function to get recommendations for better farming techniques from the API
@track_time
async def suggest_better_technique(session, user_crop_data: dict) -> str:
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    data = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
                The farmer is growing {user_crop_data["crop_name"]} in {user_crop_data["location"]} using:
                - Soil Management: {user_crop_data["current_soil_technique"]}
                - Irrigation: {user_crop_data["current_irrigation_technique"]}

                Compare these techniques to alternatives and recommend improvements.
            """,
            },
        ],
        "temperature": 0.7,
    }

    print_status(f"Sending request for {user_crop_data['crop_name']}...")
    async with session.post(GROQ_API_URL, headers=headers, json=data) as response:
        if response.status == 200:
            api_response = await response.json()
            if "choices" in api_response and api_response["choices"]:
                suggestion = api_response["choices"][0]["message"]["content"]
                return re.sub(
                    r"<think>.*?</think>", "", suggestion, flags=re.DOTALL
                ).strip()
        return f"Error {response.status}: {await response.text()}"


# Asynchronous function to fetch suggestions for all crops
@track_time
async def suggest_all_crops(all_user_crops_data: list):
    async with aiohttp.ClientSession() as session:
        tasks = [
            suggest_better_technique(session, crop_data)
            for crop_data in all_user_crops_data
        ]
        return await asyncio.gather(*tasks)


# Fetching suggestions asynchronously with tracking
print_status("Fetching suggestions for all crops...")


def return_all_crop_suggestions_concurrently(all_crop_data):
    all_crop_suggestions = asyncio.run(suggest_all_crops(all_crop_data))
    return all_crop_data


print_status("All suggestions received!")


# Function to summarize AI-generated suggestions
@track_time
def summarize_all_crop_suggestions(
    all_crop_suggestions: list, location_news: str
) -> str:
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SUMMARY_PROMPT},
            {
                "role": "user",
                "content": f"Crop Summaries: {all_crop_suggestions}, Location News: {location_news}",
            },
        ],
        "temperature": 0.7,
    }

    print_status("Sending summarization request...")
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        api_response = response.json()
        if "choices" in api_response and api_response["choices"]:
            return api_response["choices"][0]["message"]["content"]
    return f"Error {response.status}: {response.text()}"


# Function to fetch recent farming news
@track_time
def get_recent_farming_news(location: str, num_articles: int = 5) -> str:
    query = f"Agriculture and climate change news in {location}"
    encoded_query = urllib.parse.quote_plus(query)
    two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
    date_restrict = f"d{two_weeks_ago.strftime('%Y%m%d')}"

    api_key = "foo_bar"
    cse_id = "foo_bar"
    url = f"https://www.googleapis.com/customsearch/v1?q={encoded_query}&cx={cse_id}&key={api_key}&dateRestrict={date_restrict}"

    print_status(f"Fetching news for {location}...")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        news_items = [
            f"- **{item.get('title', 'No Title')}**\n  {item.get('snippet', 'No Snippet')}\n  [Link]({item.get('link', 'No Link')})\n"
            for item in data.get("items", [])[:num_articles]
        ]
        return "\n".join(news_items) if news_items else "No relevant news found."
    return f"Error {response.status}: {response.text()}"
