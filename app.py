from flask import Flask, request, jsonify
from utils import handle_whatsapp_webhook, validate_key
import sys

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.get_json()
    
    # Call the refactored function in utils.py to handle the webhook logic
    #reply, user_data = handle_whatsapp_webhook(data)
    
    # For testing, return the reply and current user state in the JSON response.
    # Uncomment the line below to send the message using the WhatsApp API in production.
    # send_whatsapp_message(user_data["from"], reply)
    
    #return jsonify({"reply": reply, "user_data": user_data})
    return jsonify({"reply": "Test Reply", "user_data": data})

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
