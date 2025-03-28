from google.cloud import pubsub_v1
from google.cloud import language_v1
import json

publisher = pubsub_v1.PublisherClient()
language_client = language_v1.LanguageServiceClient()
topic_path = publisher.topic_path("training-triggering-pipeline", "feedback-topic")

def receiver(request):
    if request.method != "POST":
        return "Method not allowed", 405

    data = request.get_json()
    if not data or "user_id" not in data or "message" not in data:
        return "Invalid request: user_id and message are required", 400

    text = data["message"]
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = language_client.analyze_sentiment(request={"document": document}).document_sentiment
    score = sentiment.score

    tag = "positive" if score > 0.25 else "negative" if score < -0.25 else "neutral"

    message_data = json.dumps(data).encode("utf-8")
    try:
        publisher.publish(topic_path, message_data, sentiment=tag)
        return "Message published successfully", 200
    except Exception as e:
        return f"Error publishing message: {str(e)}", 500