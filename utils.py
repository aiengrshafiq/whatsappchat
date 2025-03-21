import re
import sys
import openai
import requests
from config import OPENAI_API_KEY, CRM_API_URL, WHATSAPP_API_URL, WHATSAPP_ACCESS_TOKEN

openai.api_key = OPENAI_API_KEY

# Extract name, email, phone (existing code from utils.py)
def extract_email(text):
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None

def extract_phone(text):
    phone_pattern = r"(\+?\d{1,3}[\s-]?)?(\d{10})"
    matches = re.findall(phone_pattern, text)
    if matches:
        return ''.join(matches[0])
    return None

def extract_name(text):
    # Implement name extraction logic here, if needed.
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

# Generate response using OpenAI API
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

# Send to CRM
def send_to_crm(user_data):
    try:
        response = requests.post(CRM_API_URL, json=user_data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Process user state and send to CRM if complete
def process_user_state(user_id):
    state = user_states.get(user_id)
    if state and state["name"] and state["email"] and state["phone"]:
        crm_response = send_to_crm(state)
        user_states.pop(user_id, None)  # Clear the user state after sending to CRM
        return crm_response
    return None

# Validate OpenAI API key
def validate_key():
    api_key = OPENAI_API_KEY
    openai.api_key = api_key
    try:
        openai.Model.list()
        return {"valid": True, "message": "API key is valid."}
    except Exception as e:
        return {"valid": False, "message": f"An error occurred: {e}"}

# Simulate sending a message via WhatsApp
def send_whatsapp_message(recipient, message):
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print("Error sending message:", e)
        return {"error": str(e)}

# Handle the logic for the WhatsApp webhook
def handle_whatsapp_webhook(data):
    user_id = data.get("from")
    message_text = data.get("message")
    
    # Update the conversation state for the user
    user_data = update_user_state(user_id, message_text)
    
    # Check if all required details have been provided
    if user_data["name"] and user_data["email"] and user_data["phone"]:
        # Process state and simulate sending data to CRM
        crm_response = process_user_state(user_id)
        reply = "Thank you! Your details have been recorded."
    else:
        reply = generate_response(message_text)
        missing = []
        if not user_data["name"]:
            missing.append("name")
        if not user_data["email"]:
            missing.append("email")
        if not user_data["phone"]:
            missing.append("phone")
        if missing:
            reply += f"\nCould you please provide your {', '.join(missing)}?"
    
    return reply, user_data
