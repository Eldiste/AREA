curl -X POST http://127.0.0.1:8080/api/triggers \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczMzc3OTE4MH0.STnkErLGc-ZiHgIkQcmE9622Q_mRFGGVcbUPl2VaWYI" \
-H "Content-Type: application/json" \
-d '{
  "area_id": 8,
  "name": "new_message_in_channel",
  "config": {
    "channel_id": "1315785052273250326"
  }
}'