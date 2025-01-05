import json
import requests
from confluent_kafka import Consumer

# Kafka consumer configuration
kafka_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'llm_consumer_group',
    'auto.offset.reset': 'latest',
}

# Flask server URL
LLM_SERVER_URL = "http://127.0.0.1:5000/chat"

# Initialize Kafka consumer
consumer = Consumer(kafka_conf)
consumer.subscribe(['start_conversation'])

def process_message(spoken_text, cues):
    """
    Send a message (verbal or non-verbal) from Kafka to the LLM backend and get a response.
    :param spoken_text: The spoken text to send to the LLM backend.
    :param cues: The non-verbal cues (e.g., "head nod", "eye contact").
    """
    try:
        if not spoken_text.strip() and not cues:
            print("No input provided, skipping message.")
            return

        # Decide what to send based on input
        if spoken_text.strip():
            message_to_llm = spoken_text
        else:
            # message_to_llm = f"Respond with a single short greeting to these non-verbal cues: {', '.join(cues)}"
            message_to_llm = f"Respond with a single short greeting to a person who approaches you with a {cues[0]}."

        print(f"Sending to LLM: {message_to_llm}")

        # Send POST request to the LLM server
        response = requests.post(LLM_SERVER_URL, json={'message': message_to_llm})
        if response.status_code == 200:
            llm_response = response.json().get('response', 'No response')
            print(f"LLM response: {llm_response}")
        else:
            print(f"Error from LLM server: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    print("Starting Kafka consumer...")
    try:
        while True:
            msg = consumer.poll(1.0)  # Poll for new messages (timeout 1s)
            if msg is None:  # No message, continue polling
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Decode the Kafka message
            try:
                message = msg.value().decode('utf-8')
                payload = json.loads(message)

                # Extract spoken_text and cues
                spoken_text = payload.get("spoken_text", "").strip()
                cues = payload.get("cues", [])

                # Send to LLM backend
                process_message(spoken_text, cues)

            except json.JSONDecodeError:
                print(f"Failed to decode JSON message: {msg.value().decode('utf-8')}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
