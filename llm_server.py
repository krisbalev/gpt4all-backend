from flask import Flask, request, jsonify
from gpt4all import GPT4All

# Path to your model file
MODEL_PATH = r"C:\Users\Asus\AppData\Local\nomic.ai\GPT4All"

# Initialize GPT4All with the local model
print("Loading GPT4All model...")
gpt = GPT4All(model_name="gpt4all-falcon-newbpe-q4_0", model_path=MODEL_PATH, allow_download=False)

# Create Flask app
app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to process incoming messages and generate responses.
    Example input: { "message": "Hello!" }
    """
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Generate response using GPT4All
    print(f"User: {user_message}")
    response = gpt.generate(user_message, max_tokens=200)
    print(f"GPT4All: {response}")

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
