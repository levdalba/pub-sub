from google.cloud import language_v1
from google.cloud import secretmanager
import json
import base64
import requests

language_client = language_v1.LanguageServiceClient()

def access_secret(secret_id: str, project_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    secret_payload = response.payload.data.decode("UTF-8")
    return secret_payload

SLACK_TOKEN = access_secret("slacktoken", "training-triggering-pipeline")
SLACK_CHANNEL = "#support"

def negative_analyzer(event, context):
    # Extract the message data
    message = event["data"]
    data = base64.b64decode(message).decode("utf-8")
    message_data = json.loads(data)
    user_id = message_data["user_id"]
    text = message_data["message"]

    # Analyze sentiment using google.cloud.language_v1
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = language_client.analyze_sentiment(request={"document": document}).document_sentiment
    score = sentiment.score

    # Tag the message based on the sentiment score
    tag = "positive" if score > 0.25 else "negative" if score < -0.25 else "neutral"

    # Only send a Slack alert if the sentiment is negative
    if tag == "negative":
        slack_message = f"Sentiment Alert (negative-sub): {tag} message from {user_id}: {text} (Score: {score})"
        headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
        payload = {"channel": SLACK_CHANNEL, "text": slack_message}
        response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)
        if not response.ok:
            raise Exception(f"Error sending Slack message: {response.text}")

    return f"Processed message with sentiment: {tag}"