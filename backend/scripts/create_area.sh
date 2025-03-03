curl -X POST http://127.0.0.1:8080/api/areas \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczMzc3OTE4MH0.STnkErLGc-ZiHgIkQcmE9622Q_mRFGGVcbUPl2VaWYI" \
-H "Content-Type: application/json" \
-d '{
  "action_id": 4,
  "reaction_id": 3,
  "action_config": {
    "channel_id": "1315785052273250326"
  },
  "reaction_config": {
    "channel_id": "1315785052273250326"
  }
}'