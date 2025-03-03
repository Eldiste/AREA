curl -X POST http://127.0.0.1:8080/api/areas \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3MzM3MDIyMzN9.07UKpIn2pK6l9p9Bm0Kq-K2OlCQSSl5QGcU7Rg5crDE" \
-H "Content-Type: application/json" \
-d '{
  "action_id": 4,
  "reaction_id": 3,
  "action_config": {
    "channel_id": "1047186801829347401"
  },
  "reaction_config": {
    "channel_id": "1047186801829347401",
    "message_content": "A new message was detected in your channel!"
  }
}'
