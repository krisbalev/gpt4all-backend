from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
from gpt4all import GPT4All

# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ElevenLabs API configuration
ELEVENLABS_API_KEY = "sk_d355d3f12d5827eb53a0ce3cde15b55cca576255a0df7aae"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
VOICE_ID = "iP95p4xoKVk53GoZ742B"  # Your provided voice ID

# Initialize GPT4All
MODEL_PATH = r"C:\Users\Asus\AppData\Local\nomic.ai\GPT4All"
gpt = GPT4All(model_name="gpt4all-falcon-newbpe-q4_0", model_path=MODEL_PATH, allow_download=False)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to handle incoming chat messages.
    Returns a response for the chat message.
    """
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Generate a response using GPT4All
    try:
        print(f"User: {user_message}")
        response = gpt.generate(user_message, max_tokens=200)
        print(f"GPT4All: {response}")

        # Emit the response to WebSocket clients
        socketio.emit("new_message", {"message": user_message, "response": response})
        return jsonify({"response": response})
    except Exception as e:
        print("Error generating LLM response:", str(e))
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route('/tts', methods=['POST'])
def tts():
    """Generate TTS audio using ElevenLabs."""
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Send TTS request to ElevenLabs
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.9
            }
        }

        response = requests.post(
            f"{ELEVENLABS_API_URL}/{VOICE_ID}",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            audio_path = "output.mp3"
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)

            return send_file(audio_path, mimetype="audio/mpeg")
        else:
            print("ElevenLabs response:", response.text)
            return jsonify({"error": "TTS generation failed", "details": response.text}), 500

    except Exception as e:
        print("Error in /tts endpoint:", str(e))
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
