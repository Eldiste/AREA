#!/bin/bash

# Check if type and name are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <type> <name>"
    echo "type: trigger/action/reaction"
    echo "name: name of the component"
    exit 1
fi

TYPE=$1
NAME=$2

curl -X GET "http://127.0.0.1:8080/api/config/$TYPE/$NAME" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNjk0MTMwMX0.RD2NJr69c7aDNL0ASXEgUDmdUkPav2-WcRrAnOm2WPg" \
-H "Content-Type: application/json"