from flask import Flask, request, jsonify
from utils import update_user_state, generate_response, process_user_state,validate_key
from config import WHATSAPP_API_URL, WHATSAPP_ACCESS_TOKEN
import requests
import sys


app = Flask(__name__)

# Simulated function to send messages via WhatsApp (for production use)
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

@app.route('/')
def hello_world():
    return 'Hello, World!'
    
    
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.get_json()
    # For testing, we expect JSON with 'from' and 'message' fields.
    user_id = data.get("from")
    message_text = data.get("message")
    
    # Update the conversation state for the user.
    user_data = update_user_state(user_id, message_text)
    
    # Check if all required details have been provided.
    if user_data["name"] and user_data["email"] and user_data["phone"]:
        # Process state and simulate sending data to CRM.
        process_user_state(user_id)
        reply = "Thank you! Your details have been recorded."
    else:
        # Generate a response with GPT-4.
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
    
    # For testing, we simply return the reply and current user state in the JSON response.
    # Uncomment the line below to send the message using the WhatsApp API in production.
    # send_whatsapp_message(user_id, reply)
    
    return jsonify({"reply": reply, "user_data": user_data})


@app.route('/validate_key')
def validate_key_endpoint():
    result = validate_key()
    return jsonify(result)

@app.route('/test')
def test():
    return 'Hello, test!'


if __name__ == "__main__":
    print("Flask app is running...", file=sys.stderr)
    app.run(host="0.0.0.0", port=8000, debug=True)

