from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("training-triggering-pipeline", "feedback-topic")

def receiver(request):
    request_json = request.get_json()
    if not request_json or "user_id" not in request_json or "message" not in request_json:
        return "Invalid request", 400

    user_id = request_json["user_id"]
    text = request_json["message"]

    # Prepare the message to publish
    message_data = json.dumps({"user_id": user_id, "message": text}).encode("utf-8")

    # Publish the message to the feedback-topic without sentiment analysis
    publisher.publish(topic_path, message_data)

    return "Message published to feedback-topic", 200