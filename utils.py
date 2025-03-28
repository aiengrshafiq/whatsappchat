import re
import sys
import openai
import requests
import pyodbc
from flask import jsonify
from config import OPENAI_API_KEY, CRM_API_URL, WHATSAPP_API_URL, WHATSAPP_ACCESS_TOKEN,PHONE_NUMBER_ID,PIPEDRIVE_API_TOKEN,AZ_ACCESS_TOKEN

from databricks import sql

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
    api_key = OPENAI_API_KEY  # Ensure this is set correctly
    client = openai.OpenAI(api_key=api_key)  # Create an OpenAI client instance

    try:
        response = client.models.list()  # Fetch available models
        return {"valid": True, "message": "API key is valid."}
    except openai.OpenAIError as e:
        return {"valid": False, "message": f"An error occurred: {e}"}

# Simulate sending a message(any plan message) via WhatsApp business api
def send_whatsapp_message_text(recipient, message):
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }
    try:
        response = requests.post(f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages', headers=headers, json=data)
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

#handle_whatsapp_precall_message_pipedrive to sent whatsapp message(template based) from pipedrive
def handle_whatsapp_precall_message_pipedrive(data):
    customer_name = data.get('name')
    customer_phone = data.get('phone').lstrip('+').strip()

    url = f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'

    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": customer_phone,
        "type": "template",
        "template": {
            "name": "precall_confirmation_new",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name}
                    ]
                }
            ]
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    print('Status Code:', response.status_code)
    print('Response JSON:', response.json())

    if response.status_code == 200:
        return jsonify({"status": "success", "response": response.json()}), 200
    else:
        return jsonify({"status": "error", "details": response.json()}), response.status_code



# Update Pipedrive notes via API
def update_pipedrive_notes(phone, customer_name, reply_text):
    # Search Pipedrive for Person by phone
    search_url = f'https://{PIPEDRIVE_COMPANY_DOMAIN}/api/v1/persons/search'
    params = {
        'term': phone,
        'fields': 'phone',
        'api_token': PIPEDRIVE_API_TOKEN
    }

    response = requests.get(search_url, params=params).json()

    if response.get('data', {}).get('items'):
        person_id = response['data']['items'][0]['item']['id']

        # Add a note to the Person in Pipedrive
        note_url = f'https://{PIPEDRIVE_COMPANY_DOMAIN}/api/v1/notes?api_token={PIPEDRIVE_API_TOKEN}'
        note_payload = {
            "content": f"WhatsApp Communication with Customer {customer_name} ({phone}):\n\n{reply_text}",
            "person_id": person_id
        }

        note_response = requests.post(note_url, json=note_payload)

        if note_response.status_code == 201:
            print("Note added successfully in Pipedrive.")
        else:
            print("Failed to add note in Pipedrive:", note_response.text)
    else:
        print("Person not found in Pipedrive.")

# Function to handle incoming WhatsApp messages
def handle_incoming_message(message_data):
    messages = message_data.get('messages', [])
    contacts = message_data.get('contacts', [])

    if not (messages and contacts):
        return {"status": "skipped", "reason": "No messages or contacts found"}

    message = messages[0]
    contact = contacts[0]

    customer_phone = contact['wa_id']
    customer_name = contact['profile']['name']
    customer_reply = message.get('text', {}).get('body', '')

    #save chat to DB
    from datetime import datetime
    timestamp = datetime.utcnow().isoformat()
    insert_message_to_db(customer_phone, customer_name, customer_reply, timestamp)

    availability_status = None
    preferred_time = None

    reply_lower = customer_reply.lower()

    if "yes" in reply_lower:
        availability_status = "Available"
    elif "morning" in reply_lower:
        availability_status = "Not Available"
        preferred_time = "Morning"
    elif "afternoon" in reply_lower:
        availability_status = "Not Available"
        preferred_time = "Afternoon"
    elif "evening" in reply_lower:
        availability_status = "Not Available"
        preferred_time = "Evening"
    else:
        return {"status": "skipped", "reason": "Customer reply unclear"}

    if availability_status:
        person_id = get_person_id(None, customer_phone, customer_name)
        if person_id:
            result = update_pipedrive_deal(person_id, availability_status, preferred_time, customer_reply)
            return {"status": "processed", "pipedrive": result}
        else:
            return {"status": "error", "reason": "Failed to find/create person in Pipedrive"}
    
    


        
def handle_message_status(status_data):
    statuses = status_data.get('statuses', [])
    status_logs = []

    for status in statuses:
        message_id = status.get('id')
        message_status = status.get('status')
        recipient_id = status.get('recipient_id')
        timestamp = status.get('timestamp')
        errors = status.get('errors', [])
        error_details = errors[0] if errors else None

        status_log = {
            "message_id": message_id,
            "status": message_status,
            "recipient_id": recipient_id,
            "timestamp": timestamp,
            "error_details": error_details
        }

        print("📌 WhatsApp Message Status Update:", status_log)
        status_logs.append(status_log)

    return {"status": "logged", "statuses": status_logs}


def get_person_id(email, phone, name):
    person_id = None

    # Try to find a person by email first (if provided).
    if email:
        search_url = f"https://api.pipedrive.com/v1/persons/search?term={email}&fields=email&api_token={PIPEDRIVE_API_TOKEN}"
        response = requests.get(search_url)
        if response.status_code == 200:
            items = response.json().get("data", {}).get("items", [])
            if items:
                person_id = items[0]["item"]["id"]

    # If not found by email, search by phone (without exact_match).
    if not person_id and phone:
        formatted_phone = phone if phone.startswith('+') else f"+{phone}"
        search_url = f"https://api.pipedrive.com/v1/persons/search?term={formatted_phone}&fields=phone&api_token={PIPEDRIVE_API_TOKEN}"
        response = requests.get(search_url)
        if response.status_code == 200:
            items = response.json().get("data", {}).get("items", [])
            if items:
                person_id = items[0]["item"]["id"]

    # If still not found, create a new person.
    if not person_id:
        create_url = f"https://api.pipedrive.com/v1/persons?api_token={PIPEDRIVE_API_TOKEN}"
        person_payload = {
            "name": name,
            "email": email,
            "phone": formatted_phone
        }
        create_response = requests.post(create_url, json=person_payload)
        if create_response.status_code in (200, 201):
            person_data = create_response.json().get("data")
            if person_data and "id" in person_data:
                person_id = person_data["id"]

    return person_id



# Function to update Pipedrive deal with availability status
def update_pipedrive_deal(person_id, availability_status, preferred_time, customer_reply):
    deals_by_person_url = f"https://api.pipedrive.com/v1/persons/{person_id}/deals?api_token={PIPEDRIVE_API_TOKEN}"
    deal_response = requests.get(deals_by_person_url)

    if deal_response.status_code != 200:
        return {"status": "error", "reason": f"Failed fetching deals: {deal_response.text}"}

    deal_data = deal_response.json().get("data", [])
    if not deal_data:
        return {"status": "error", "reason": f"No deal associated with this person {person_id}"}

    deal_id = deal_data[0]["id"]
    update_url = f"https://api.pipedrive.com/v1/deals/{deal_id}?api_token={PIPEDRIVE_API_TOKEN}"
    update_data = {
        "b930a0d856be833986f5a959852687060741c7eb": availability_status,
    }
    if preferred_time:
        update_data["3d8b10e34ccb7db8ab4cb39f65031cfde9d71c23"] = preferred_time

    update_response = requests.put(update_url, json=update_data)

    if update_response.status_code != 200:
        return {"status": "error", "reason": f"Failed updating deal: {update_response.text}"}

    note_result = add_note_to_deal(deal_id, customer_reply)

    return {
        "status": "success",
        "deal_updated": True,
        "note_added": note_result
    }

def add_note_to_deal(deal_id, customer_reply):
    note_url = f"https://api.pipedrive.com/v1/notes?api_token={PIPEDRIVE_API_TOKEN}"
    note_payload = {
        "deal_id": deal_id,
        "content": f"Customer replied via WhatsApp: '{customer_reply}'"
    }
    response = requests.post(note_url, json=note_payload)

    if response.status_code in (200, 201):
        return True
    else:
        return False


def insert_message_to_db(customer_phone, customer_name, customer_reply, timestamp):
    server_hostname = "adb-1738127852431756.16.azuredatabricks.net"  
    http_path = "/sql/1.0/warehouses/8cddc035c463a758"  
    access_token = AZ_ACCESS_TOKEN

    catalog_name = "whatsapp_catalog"
    schema_name = "whatsapp_messages"
    table_name = "whatsappmessages"

    insert_query = f"""
        INSERT INTO {catalog_name}.{schema_name}.{table_name}
        (CustomerPhone, CustomerName, Message, Timestamp, SentimentStatus)
        VALUES (?, ?, ?, ?, 'Pending')
    """

    with sql.connect(server_hostname=server_hostname,
                     http_path=http_path,
                     access_token=access_token) as connection:
        with connection.cursor() as cursor:
            cursor.execute(insert_query, 
                           (customer_phone, customer_name, customer_reply, timestamp))
            connection.commit()

