import requests
import json
import os
import time

# --- Configuration ---

# IMPORTANT: Replace 'YOUR_API_KEY' with your actual Gemini API key.
# This script will not run without a valid key.
API_KEY = "YOUR_API_KEY"

# The LLM model to use for structured JSON generation
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- Prompt Definition ---

# The prompt clearly defines the desired JSON structure and constraints,
# ensuring the LLM mimics the original file's format and item count (26 enemies, 35 potholes).
SYSTEM_PROMPT = (
    "You are a configuration file generator. Your response must be ONLY a single, "
    "valid JSON object. Do not include any text, markdown formatting (like ```json), "
    "or explanation outside of the JSON object itself."
)

USER_QUERY = """
Generate a new configuration file for a racing game. 
The JSON object must have two top-level keys: 'enemySpawnData' and 'potholesData'.

1.  'enemySpawnData': Must be an array of exactly 26 objects. Each object must contain the key 
    'startWaypointIndex' with an integer value that is randomly chosen between 1 and 12 (inclusive).
    Ensure the distribution of these values is varied.
2.  'potholesData': Must be an array of exactly 35 objects. Each object must have keys 'x', 'y', and 'radius'.
    - 'x' and 'y' must be new integer values between 100 and 700.
    - 'radius' must be a new integer value between 10 and 20.
"""

# Define the exact JSON schema we expect the model to return
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "enemySpawnData": {
            "type": "ARRAY",
            "description": "Exactly 26 enemy spawn points.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "startWaypointIndex": {"type": "INTEGER", "description": "Waypoint index for spawning (1-12)."}
                },
                "required": ["startWaypointIndex"]
            }
        },
        "potholesData": {
            "type": "ARRAY",
            "description": "Exactly 35 pothole positions.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "x": {"type": "INTEGER", "description": "X-coordinate (100-700)."},
                    "y": {"type": "INTEGER", "description": "Y-coordinate (100-700)."},
                    "radius": {"type": "INTEGER", "description": "Pothole radius (10-20)."}
                },
                "required": ["x", "y", "radius"]
            }
        }
    },
    "required": ["enemySpawnData", "potholesData"]
}

# --- API Call Logic ---

def generate_new_config():
    """Calls the Gemini API to generate a new game configuration JSON."""
    if API_KEY == 'YOUR_API_KEY':
        print("ERROR: Please replace 'YOUR_API_KEY' with your actual API key.")
        return

    payload = {
        "contents": [{"parts": [{"text": USER_QUERY}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "config": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            # Setting a low temperature encourages the model to strictly follow the schema
            "temperature": 0.2
        }
    }

    # Implement exponential backoff for robust API calls
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"Attempting to generate config... (Attempt {attempt + 1}/{max_retries})")
            response = requests.post(
                API_URL, 
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload)
            )
            response.raise_for_status() # Raises an exception for 4xx or 5xx status codes

            result = response.json()
            
            # Extract and parse the generated JSON text
            json_text = result['candidates'][0]['content']['parts'][0]['text']
            new_config = json.loads(json_text)
            
            print("\n--- Successfully Generated New Game Config ---")
            print(json.dumps(new_config, indent=2))
            return new_config

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            if response.status_code == 429 and attempt < max_retries - 1:
                # Handle rate limiting with exponential backoff
                wait_time = 2 ** attempt
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Failed to generate config after retries.")
                print(response.text)
                break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    generate_new_config()
