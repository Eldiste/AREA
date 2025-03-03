curl -X POST http://127.0.0.1:8080/api/areas \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNjk2MDQwNn0.RYg9PYsqZa6WTefr8ZXC1cEjN7OZlemFRvOjlpVsUAs" \
-H "Content-Type: application/json" \
-d '{
  "action_id": 9,
  "reaction_id": 8,
  "action_config": {
    "query": "from:m.lechantre@icloud.com is:unread"
  },
  "reaction_config": {
    "to": "mateo.lechantre@free.fr",
    "subject": "Forwarded: {subject}",
    "body": "Original email from: {sender}\n\nContent: {snippet}",
    "cc": [],
    "bcc": []
  }
}'