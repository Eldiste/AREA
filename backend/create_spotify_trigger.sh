#!/bin/bash

curl -X POST http://127.0.0.1:8080/api/triggers \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNzMxNzQ3MH0.alNkOmw2PvZpQHWhLzlkpJzj4-SU_ztdNe1J707YLtc" \
-d '{
    "area_id": 3,
    "name": "track_played",
    "config": {
        "interval": 15
    }
}' 