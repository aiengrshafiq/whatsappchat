import re
import sys
import openai
import requests
from config import OPENAI_API_KEY, CRM_API_URL

# Try to import the AuthenticationError from openai.errors.
try:
    from openai.errors import AuthenticationError
except ModuleNotFoundError:
    # Fallback: define a generic exception to catch if the module isn't available.
    AuthenticationError = Exception

# Initialize the OpenAI API key.
openai.api_key = OPENAI_API_KEY

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None

def extract_phone(text):
    phone_pattern = r"(\+?\d{1,3}[\s-]?)?(\d{10})"
    matches = re.findall(phone_pattern, text)
    if matches:
        # Join the captured groups of the first match.
        return ''.join(matches[0])
    return None

def extract_name(text):
    # TODO: Implement name extraction if needed.
    return None

# In-memory user state (for demo purposes)
user_states = {}

def update_user_state(user_id, message):
    email = extract_email(message)
    phone = extract_phone(message)
    name = extract_name(message)
    
    if user_id not in user_states:
        user_states[user_id] = {"name": None, "email": None, "phone": None}
    
    if email:
        user_states[user_id]["email"] = email
    if phone:
        user_states[user_id]["phone"] = phone
    if name:
        user_states[user_id]["name"] = name
    
    return user_states[user_id]

def generate_response(prompt):
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a friendly chatbot. Always ask the user to provide their name, email, and phone number. If the user gives unrelated information, gently prompt them to provide these details."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error in generate_response:", e, file=sys.stderr)
        return "Sorry, an error occurred."

def send_to_crm(user_data):
    try:
        response = requests.post(CRM_API_URL, json=user_data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def process_user_state(user_id):
    state = user_states.get(user_id)
    if state and state["name"] and state["email"] and state["phone"]:
        crm_response = send_to_crm(state)
        # Clear the state after sending data to CRM.
        user_states.pop(user_id, None)
        return crm_response
    return None

def validate_key():
    """
    Validate the OpenAI API key by attempting to list available models.
    Returns a dictionary indicating whether the key is valid.
    """
    api_key = OPENAI_API_KEY
    openai.api_key = api_key
    try:
        openai.Model.list()  # This call requires a valid API key.
        return {"valid": True, "message": "API key is valid."}
    except AuthenticationError:
        return {"valid": False, "message": "Invalid API key."}
    except Exception as e:
        return {"valid": False, "message": f"An error occurred: {e}"}
