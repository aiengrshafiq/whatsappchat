from flask import Flask, request, jsonify
from utils import handle_whatsapp_webhook, validate_key, handle_incoming_message,handle_whatsapp_precall_message_pipedrive
import sys

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/webhook', methods=['GET'])
def whatsapp_webhook_get():
    if request.method == 'GET':  # Meta Webhook Verification
        challenge = request.args.get("hub.challenge")
        verify_token = request.args.get("hub.verify_token")

        if verify_token == VERIFY_TOKEN:
            return challenge  # Meta expects the raw challenge value as response
        else:
            return "Verification failed", 403


@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    if 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    message_data = change['value']
                    handle_incoming_message(message_data)
    return jsonify(success=True), 200

    # Call the refactored function in utils.py to handle the webhook logic
    #reply, user_data = handle_whatsapp_webhook(data)
    
    # For testing, return the reply and current user state in the JSON response.
    # Uncomment the line below to send the message using the WhatsApp API in production.
    # send_whatsapp_message(user_data["from"], reply)
    
    #return jsonify({"reply": reply, "user_data": user_data})
    #return jsonify({"reply": "Test Reply", "user_data": data})

@app.route('/send_whatsapp_precall_message_pipedrive', methods=['POST'])
def send_whatsapp_message():
    data = request.get_json()
    rsponse = handle_whatsapp_precall_message_pipedrive(data)
    return rsponse


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
