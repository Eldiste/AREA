#!/bin/bash

curl -X POST http://127.0.0.1:8080/api/areas \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNzMxNzQ3MH0.alNkOmw2PvZpQHWhLzlkpJzj4-SU_ztdNe1J707YLtc" \
-H "Content-Type: application/json" \
-d '{
  "action_id": 16,
  "reaction_id": 11,
  "action_config": {},
  "reaction_config": {
    "playlist_id": "07cnSh7EQYWpMfguu3OShZ",
    "position": 0
  }
}' 