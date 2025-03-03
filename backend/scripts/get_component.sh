#!/bin/bash

echo "Getting Actions..."
curl -X GET "http://127.0.0.1:8080/api/actions" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNjk0MTMwMX0.RD2NJr69c7aDNL0ASXEgUDmdUkPav2-WcRrAnOm2WPg" \
-H "Content-Type: application/json"

echo -e "\nGetting Reactions..."
curl -X GET "http://127.0.0.1:8080/api/reactions" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNjk0MTMwMX0.RD2NJr69c7aDNL0ASXEgUDmdUkPav2-WcRrAnOm2WPg" \
-H "Content-Type: application/json"

echo -e "\nGetting Triggers..."
curl -X GET "http://127.0.0.1:8080/api/triggers" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGdtYWlsLmNvbSIsImV4cCI6MTczNjk0MTMwMX0.RD2NJr69c7aDNL0ASXEgUDmdUkPav2-WcRrAnOm2WPg" \
-H "Content-Type: application/json"