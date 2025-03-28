# Sentiment Analysis Pipeline with Google Cloud Functions and Pub/Sub

This project implements a sentiment analysis pipeline using Google Cloud Functions and Pub/Sub. It processes user feedback messages, analyzes their sentiment, and sends alerts to Slack channels based on the sentiment.

## Project Structure
The repository is organized as follows:
```
PUB-SUB/
├── pubsub-negative-analyzer/
│   ├── main.py
│   ├── requirements.txt
├── pubsub-positive-analyzer/
│   ├── main.py
│   ├── requirements.txt
├── pubsub-receiver/
│   ├── main.py
│   ├── requirements.txt
├── .gitattributes
├── README.md
```
- **pubsub-receiver/**: Contains the `receiver` function, which receives messages via HTTP and publishes them to a Pub/Sub topic.
- **pubsub-positive-analyzer/**: Contains the `positive_analyzer` function, which analyzes sentiment and sends Slack alerts for positive messages.
- **pubsub-negative-analyzer/**: Contains the `negative_analyzer` function, which analyzes sentiment and sends Slack alerts for negative messages.

## Workflow
1. **Receiver Function (`receiver`)**:
   - Trigger: HTTP request (e.g., via Postman).
   - Action: Receives a JSON payload with `user_id` and `message`, then publishes the message to the `feedback-topic` Pub/Sub topic without sentiment analysis.
   - Directory: `pubsub-receiver/`

2. **Positive Analyzer Function (`positive_analyzer`)**:
   - Trigger: Push subscription (`gcf-positive_analyzer-us-central1-feedback-topic`) on `feedback-topic`.
   - Action: Analyzes the sentiment of the message using Google Cloud Natural Language API. If the sentiment is positive (score > 0.25), sends a Slack alert to the `#followup` channel.
   - Directory: `pubsub-positive-analyzer/`

3. **Negative Analyzer Function (`negative_analyzer`)**:
   - Trigger: Push subscription (`gcf-negative_analyzer-us-central1-feedback-topic`) on `feedback-topic`.
   - Action: Analyzes the sentiment of the message using Google Cloud Natural Language API. If the sentiment is negative (score < -0.25), sends a Slack alert to the `#support` channel.
   - Directory: `pubsub-negative-analyzer/`

## Prerequisites
- **Google Cloud Project**: A Google Cloud project with billing enabled (e.g., `training-triggering-pipeline`).
- **APIs Enabled**:
  - Cloud Functions API
  - Cloud Pub/Sub API
  - Cloud Natural Language API
- **Slack Token**:
  - A Slack bot token stored in Google Cloud Secret Manager under the secret ID `slacktoken` in the project `training-triggering-pipeline`.
  - The bot must have permissions to post messages to the `#followup` and `#support` channels.
- **gcloud CLI**: Installed and authenticated with your Google Cloud project.

## Setup Instructions
1. **Clone the Repository**:
```
git clone <repository-url>
cd pub-sub
```

2. **Create the Pub/Sub Topic**:
```
gcloud pubsub topics create feedback-topic
```

3. **Deploy the `receiver` Function**:
```
cd pubsub-receiver
gcloud functions deploy receiver \
--runtime python39 \
--trigger-http \
--region us-central1 \
--allow-unauthenticated \
--no-gen2
```

4. **Deploy the `positive_analyzer` Function**:
```
cd ../pubsub-positive-analyzer
gcloud functions deploy positive_analyzer \
--runtime python39 \
--trigger-topic feedback-topic \
--region us-central1 \
--no-gen2
```

5. **Deploy the `negative_analyzer` Function**:
```
cd ../pubsub-negative-analyzer
gcloud functions deploy negative_analyzer \
--runtime python39 \
--trigger-topic feedback-topic \
--region us-central1 \
--no-gen2
```

## Testing the Workflow
1. **Send a Test Message via Postman**:
- **URL**: `https://us-central1-training-triggering-pipeline.cloudfunctions.net/receiver`
- **Method**: `POST`
- **Body** (raw JSON):
  - Positive message:
    ```json
    {"user_id": "test@example.com", "message": "I love this!"}
    ```
  - Neutral message:
    ```json
    {"user_id": "test@example.com", "message": "It’s okay."}
    ```
  - Negative message:
    ```json
    {"user_id": "test@example.com", "message": "This isn’t working."}
    ```

2. **Verify Slack Alerts**:
- In the `#followup` channel, you should see:
  ```
  Sentiment Alert (positive-sub): positive message from test@example.com: I love this! (Score: 0.8999999761581421)
  ```
- In the `#support` channel, you should see:
  ```
  Sentiment Alert (negative-sub): negative message from test@example.com: This isn’t working. (Score: -0.8999999761581421)
  ```
- Neutral messages will not trigger any alerts.

3. **Check Function Logs (If Needed)**:
- For `receiver`:
  ```
  gcloud functions logs read receiver --region us-central1
  ```
- For `positive_analyzer`:
  ```
  gcloud functions logs read positive_analyzer --region us-central1
  ```
- For `negative_analyzer`:
  ```
  gcloud functions logs read negative_analyzer --region us-central1
  ```

